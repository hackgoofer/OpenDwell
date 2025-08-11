import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from database import DatabaseManager
from utils import (
    set_wide_page,
    get_value_comparisons,
    is_user_valid,
    show_login,
    is_user_subscriber,
)

set_wide_page(st)
from streamlit_extras.switch_page_button import switch_page
from value_examinor import ValueExaminor
import os
import streamlit_analytics
from datetime import datetime
import collections

load_dotenv()


# Initialize database manager
db_manager = DatabaseManager()


def clean_text_for_display(text):
    text = text.replace("_", " ")
    return text


## LOGIC
def verdict_conversion(verdict, reverse=False):
    verdict_dict = {
        "🫡 agree": "confirmed",
        "👎 disagree": "rejected",
        "🤷‍♀️ undecided": "undecided",
    }
    if reverse:
        verdict_dict = {v: k for k, v in verdict_dict.items()}

    return verdict_dict[verdict]


def get_incompleted_entries(user_id):
    # Get all entry ids from ValueComparisons
    value_comparisons = db_manager.get_value_comparison_instances(user_id)
    value_comparison_entry_ids = [
        v["entry_id"] for v in value_comparisons if v["entry_id"] is not None
    ]
    # Get all entries that are not in ValueComparisons
    user_id = st.session_state["session_data"]["user"]["id"]
    entries = db_manager.get_entries(user_id, not_in_ids=value_comparison_entry_ids)
    return entries


def fetch_values_fromDB():
    values = db_manager.get_human_values()
    return {value["name"]: value for value in values}, {
        value["id"]: value for value in values
    }


def fetch_value_comparisons(values_id_DB):
    user_id = st.session_state["session_data"]["user"]["id"]
    value_comparisons_entries_DB = db_manager.get_value_comparison_from_entries(user_id)
    value_comparisons_threads_DB = db_manager.get_value_comparison_from_threads(user_id)
    value_comparisons_DB = value_comparisons_entries_DB + value_comparisons_threads_DB
    undecided_rows = []
    decided_rows = []
    decided_timestamp_to_rows = collections.defaultdict(list)
    undecided_dict = {}
    decided_dict = {}
    for value_comp in value_comparisons_DB:
        row = {
            "verdict": verdict_conversion(value_comp["user_sentiment"], reverse=True),
            "superior": clean_text_for_display(
                values_id_DB[value_comp["superior_value_id"]]["name"]
            ),
            "inferior": clean_text_for_display(
                values_id_DB[value_comp["inferior_value_id"]]["name"]
            ),
            "reason": value_comp["reason"],
            "ref": value_comp["data"]["entry_extract"],
            "date": value_comp["date"],
        }

        if value_comp["user_sentiment"] == "undecided":
            undecided_dict[value_comp["id"]] = value_comp
            undecided_rows.append(row)
        else:
            decided_dict[value_comp["id"]] = value_comp
            decided_rows.append(row)
            decided_timestamp_to_rows[value_comp["date"]].append(row)
    return (
        decided_rows,
        undecided_rows,
        undecided_dict,
        decided_dict,
        decided_timestamp_to_rows,
    )


def conflict_handler(nodes, comparisons):
    st.markdown(
        f'<p style="color:red;">*Conflict detected: { " > ".join(nodes)}</p>',
        unsafe_allow_html=True,
    )
    with st.expander("Show details"):
        for i in range(len(nodes) - 1):
            pair = (nodes[i], nodes[i + 1])
            st.markdown(
                f'<p style="color:red;">*{pair[0]} > {pair[1]}</p>',
                unsafe_allow_html=True,
            )
            st.markdown(f'<p style="color:red;">*Reasons: </p>', unsafe_allow_html=True)
            st.write("\n".join([f"{t[0]}, {t[1]}" for t in comparisons[pair]]))
        st.text_area(
            "Can you briefly describe to resolve your conflict?",
            key=f"conflict_handler_{'_'.join(nodes)}",
        )


def app():
    values_name_DB, values_id_DB = fetch_values_fromDB()
    (
        decided_rows,
        undecided_rows,
        undecided_dict,
        decided_dict,
        decided_timestamp_to_rows,
    ) = fetch_value_comparisons(values_id_DB)

    st.markdown("## Calculate Demonstrated Values")
    user_id = st.session_state["session_data"]["user"]["id"]
    new_entries = get_incompleted_entries(user_id)
    if len(new_entries) > 0:
        st.write(
            f"Found {len(new_entries)} new entries on {[e['date'] for e in new_entries]} that was not included in calculating values."
        )
        if st.button(label="Analyze values (takes 1 minute)"):
            for new_entry in new_entries:
                # prompt_suffix = st.text_area("Work on your values", "Based on the journal entries, make list of value comparisons such as superior A > inferior B (A not equal to B), updated where necessary by specific evidence in activities happened in the journal. Use each value's desc to see what they mean. Only include if there is sufficient evidence. ", key=f'custom_values_analysis_prompt')
                value_comparisons = []
                result = get_value_comparisons(new_entry["what_happened"])
                for value_comp in result:
                    value_comparisons.append(
                        {
                            "verdict": "🤷‍♀️ Undecided",
                            "superior": clean_text_for_display(
                                value_comp.superior.name.value
                            ),
                            "inferior": clean_text_for_display(
                                value_comp.inferior.name.value
                            ),
                            "reason": value_comp.reason,
                            "ref": value_comp.ref,
                            "date": str(new_entry["date"]),
                        }
                    )
                    new_value_comparison = db_manager.add_value_comparison_instance(
                        value_comp,
                        new_entry,
                        values_name_DB[value_comp.superior.name.value]["id"],
                        values_name_DB[value_comp.inferior.name.value]["id"],
                    )
                    undecided_dict.update(
                        {new_value_comparison["id"]: new_value_comparison}
                    )

                undecided_rows += value_comparisons
    else:
        st.write("No new values to review. Head to create a New Entry!")
        yesno = st.button("Create a New Entry!")
        if yesno:
            switch_page("new entry")

    st.markdown("## Demostrated Values")

    value_examinor = ValueExaminor()
    orders = value_examinor.derive_orders(
        [
            (
                decided_row["superior"],
                decided_row["inferior"],
                decided_row["reason"],
                decided_row["date"],
            )
            for decided_row in decided_rows
            if decided_row["verdict"] == "🫡 agree"
        ],
        conflict_handler,
    )
    graphviz_texts = []
    for order in orders:
        graphviz_texts.append(" -> ".join(["_".join(t.split(" ")) for t in order]))
    graphviz_text = "\n".join(graphviz_texts)
    st.graphviz_chart("digraph {" + graphviz_text + "}")

    # RENDERING
    st.markdown("## Daily Review")
    if len(undecided_rows) > 0:
        edited_df = st.data_editor(
            pd.DataFrame(undecided_rows),
            column_config={
                "superior": st.column_config.TextColumn(
                    "Superior",
                    disabled=True,
                    help="The superior value",
                    width="medium",
                ),
                "inferior": st.column_config.TextColumn(
                    "Inferior",
                    disabled=True,
                    help="The inferior value",
                    width="medium",
                ),
                "reason": st.column_config.TextColumn(
                    "Reason",
                    disabled=True,
                    help="The summary text describing the value comparison",
                    width=None,
                ),
                "verdict": st.column_config.SelectboxColumn(
                    "User Verdict",
                    help="Do you agree with this assessment?",
                    width="medium",
                    options=[
                        "🫡 agree",
                        "👎 disagree",
                        "🤷‍♀️ undecided",
                    ],
                    required=True,
                ),
                "ref": st.column_config.TextColumn(
                    "Reference",
                    disabled=True,
                    help="The reference to the journal entry or thread",
                    width=None,
                ),
                "date": st.column_config.TextColumn(
                    "date",
                    disabled=True,
                    help="The date of the entry/thread",
                    width=None,
                ),
            },
            key="VALUES_table",
            hide_index=True,
            num_rows="fixed",
        )

        if "VALUES_table" in st.session_state:
            edited = st.session_state["VALUES_table"]
            if any(
                any(v != "🤷‍♀️ undecided" for v in row.values())
                for row in edited["edited_rows"].values()
            ):
                if st.button(label="Save changes"):
                    undecided_dict_keys = list(undecided_dict.keys())
                    undecided_dict_values = list(undecided_dict.values())
                    for i, row in edited["edited_rows"].items():
                        db_manager.edit_value_comparison_instance(
                            undecided_dict_keys[i],
                            {"user_sentiment": verdict_conversion(row["verdict"])},
                        )
                    st.write("Changes saved!")
                    st.rerun()

    for reviewed_date, rows in decided_timestamp_to_rows.items():
        st.write(f"Reviewed: {reviewed_date}")
        edited_df = st.data_editor(
            pd.DataFrame(rows).drop(columns=["date"]),
            column_config={
                "superior": st.column_config.TextColumn(
                    "Superior",
                    disabled=True,
                    help="The superior value",
                    width="medium",
                ),
                "inferior": st.column_config.TextColumn(
                    "Inferior",
                    disabled=True,
                    help="The inferior value",
                    width="medium",
                ),
                "reason": st.column_config.TextColumn(
                    "Reason",
                    disabled=True,
                    help="The summary text describing the value comparison",
                    width=None,
                ),
                "ref": st.column_config.TextColumn(
                    "Reference",
                    disabled=True,
                    help="The reference to the journal entry or thread",
                    width=None,
                ),
                "verdict": st.column_config.SelectboxColumn(
                    "User Verdict",
                    help="Do you agree with this assessment?",
                    width="medium",
                    disabled=True,
                    options=[
                        "🫡 agree",
                        "👎 disagree",
                        "🤷‍♀️ undecided",
                    ],
                    required=True,
                ),
            },
            key=f"ACTIVITIES_table_reviewed_{reviewed_date}",
            hide_index=True,
            num_rows="fixed",
        )

    # if "VALUES_table" in st.session_state:
    #     st.write(st.session_state["VALUES_table"])


user_valid, user_email = is_user_valid(st)
current_date = datetime.now().strftime("%Y-%m-%d")

if not user_valid:
    show_login(st)
elif is_user_subscriber(st, user_email):
    if not os.path.exists(f"analytics/{user_email}"):
        os.makedirs(f"analytics/{user_email}")

    app()

## RENDERING

# with st.form(key=f'new_entry_analysis_form'):
#     # Check if user_values.txt exists, if not, skip reading and set user_values to empty list
#     if os.path.exists('user_values.txt'):
#         file = open('user_values.txt', 'r').read()
#         user_values = [line.split(": ") for line in file.split('\n')]
#         st.table(pd.DataFrame(user_values, columns=["Value", "Description"]))
#     else:
#         user_values = []

#     prompt_suffix = st.text_area("Work on your values", "Based on the journal entries, make a new short list of values sorted from most to least important, updated where necessary by specific evidence or word choice in the journal entry, but otherwise leave their descriptions unchanged. Be on the lookout for new values not previously expressed in the existing value set, and rank them accordingly.", key=f'custom_values_analysis_prompt')
#     custom_prompt = f"""The user's stated values are:
# {file if user_values else 'No initial values found.'}

# {prompt_suffix}
# """
#     entries = session.query(Entry).order_by(Entry.timestamp.asc()).all()
#     serialized_data = "\n".join([entry.what_happened for entry in entries])
#     if st.form_submit_button(label="Run analysis (takes 1 minute)"):
#         import instructor
#         from openai import OpenAI
#         from pydantic import BaseModel
#         client = instructor.patch(OpenAI(
#             # This is the default and can be omitted
#             api_key=os.getenv("OPENAI_API_KEY"),
#             base_url="https://oai.hconeai.com/v1",
#             default_headers={
#                 "Helicone-Auth": os.getenv("HELICONE_AUTH"),
#             }
#         ))
#         from pydantic import Field, BaseModel
#         from typing import List

#         class Value(BaseModel):
#             name: str
#             description: str

#         class Values(BaseModel):
#             values: List[Value] = Field(..., description="Numbered list of values and their descriptions, up to 10 at most")

#         result = client.chat.completions.create(
#             model="gpt-4",
#             response_model=Values,
#             messages=[
#                 {"role": "system", "content": custom_prompt},
#                 {"role": "user", "content": serialized_data},
#             ]
#         )

#         st.write("## Demonstrated Values")

#         # Get the names of the values from user_values and result.values
#         old_values = [value[0] for value in user_values[:10]] if user_values else []
#         new_values = [value.name for value in result.values[:10]]

#         # Find the differences between the old and new values
#         added_values = list(set(new_values) - set(old_values))
#         removed_values = list(set(old_values) - set(new_values)) if old_values else []

#         # Check if the order of the values has changed
#         order_changed = old_values != new_values if old_values else False

#         # Highlight the changes
#         if added_values:
#             added_values_indices = [new_values.index(value) + 1 for value in added_values]
#             added_values_with_indices = [f"{value} @ {index}" for value, index in zip(added_values, added_values_indices)]
#             st.markdown(f"**🆕 New values added:** {', '.join(added_values_with_indices)}")
#         if removed_values:
#             st.markdown(f"**❌ Values removed:** {', '.join(removed_values)}")
#         if order_changed:
#             st.markdown("**Order of values has changed.**")
#             changes = []
#             for i in range(len(old_values)):
#                 if old_values[i] != new_values[i] and old_values[i] not in removed_values and new_values[i] not in added_values:
#                     old_index = old_values.index(old_values[i])
#                     new_index = new_values.index(old_values[i])
#                     if old_index < new_index:
#                         changes.append(f"{old_values[i]} 🔻 ({old_index+1} -> {new_index+1})")
#                     elif old_index > new_index:
#                         changes.append(f"{old_values[i]} 🔼 ({old_index+1} -> {new_index+1})")
#             st.markdown("Changes: " + ', '.join(changes))

#         print(result)
#         for i in range(len(result.values[:10])):
#             col1, col2 = st.columns([1, 3])
#             with col1:
#                 result.values[i].name = st.text_input(f"Value {i+1}", result.values[i].name, label_visibility="hidden")
#             with col2:
#                 result.values[i].description = st.text_area(f"description {i+1}", result.values[i].description, label_visibility="hidden")

#         if st.form_submit_button(label="Update saved values"):
#             analysis_str = "\n".join([f"{value.name}: {value.description}" for value in result.values])
#             analysis_final = st.text_area("Values analysis", analysis_str, key=f'custom_analysis_result')
#             with open('user_values.txt', 'w') as f:
#                 f.write(analysis_final)
#             st.write("Updated `user_values.txt`!")
