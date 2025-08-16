import streamlit as st
import pandas as pd
import numpy as np
from database import DatabaseManager
import enum
import os
from dotenv import load_dotenv
import json
from streamlit_extras.switch_page_button import switch_page
from utils import (
    set_wide_page,
    get_activities_emotions,
    is_user_valid,
    show_login,
    is_user_subscriber,
)
from collections import defaultdict
import streamlit_analytics
from datetime import datetime
import plotly.express as px
import collections
from datetime import datetime
import plotly.graph_objects as go

set_wide_page(st)

load_dotenv()

# Initialize database manager
db_manager = DatabaseManager()


def emotions_metadata():
    with open("emotions_with_desc.json") as f:
        return json.load(f)


def render_switch_page_component(i, activity, emotions):
    with st.form(key=f"ACTIVITIES_feel_better_form_{i}"):
        st.write(
            f"You are feeling {emotions} during the event: {activity}. What do you wish to accomplish in the chat session?"
        )
        goal = st.text_input(
            label="Goal:",
            placeholder="Help me feel Better? Help me understand how I feel? etc",
        )
        st.session_state[f"ACTIVITIES_HOWTOFEEL"] = {
            "goal": goal if goal else "Help me feel better",
            "emotions": emotions,
            "activity": activity,
        }
        if st.form_submit_button(label="Start Chat"):
            switch_page("How_to_Feel")


def full_app():
    # Create elements to be used in the appcreated_at
    user_id = st.session_state["session_data"]["user"]["id"]
    activities_tuple_from_db = db_manager.get_activities_and_entries(user_id)
    activity_timestamps = list(set([date for _, date in activities_tuple_from_db]))
    activities_from_db = {
        activity["id"]: activity for activity, _ in activities_tuple_from_db
    }
    activities_reviewed_from_db = {}
    activities_not_reviewed_from_db = {}

    activity_rows = []
    reviewed_entries = defaultdict(list)

    for i, (act_db, entry_timestamp) in enumerate(activities_tuple_from_db):
        activity_row = {
            "Reviewed": False,
            "Delete": False,
            "Dive": False,
            "Activity": act_db.get("activity"),
            "Emotions": act_db.get("emotions"),
            "Activity Raw": act_db.get("activity_raw"),
            "Date": entry_timestamp,
        }
        data = None
        if act_db["data"]:
            data = act_db["data"]

        if data and "reviewed" in data and data["reviewed"]:
            activity_row.update({"Reviewed": True})
            reviewed_entries[str(entry_timestamp)].append(activity_row)
            activities_reviewed_from_db[act_db["id"]] = act_db
        else:
            activity_rows.append(activity_row)
            activities_not_reviewed_from_db[act_db["id"]] = act_db

    st.markdown("## Activities & Emotions")
    print(f"activity_timestamps: {activity_timestamps}")
    user_id = st.session_state["session_data"]["user"]["id"]
    new_entries = db_manager.get_entries(user_id, not_in_timestamps=activity_timestamps)
    if len(new_entries) > 0:
        st.write(
            f"Found {len(new_entries)} new entries on {[e['date'] for e in new_entries]} that was not included in calculating emotions."
        )
        if st.button(label="Analyze emotions (takes 1 minute)"):
            for new_entry in new_entries:
                emos = get_activities_emotions(new_entry["what_happened"])
                for emo in emos:
                    activity_row = {
                        "Reviewed": False,
                        "Delete": False,
                        "Dive": False,
                        "Activity": emo.activity,
                        "Emotions": emo.emotion,
                        "Activity Raw": emo.activity_raw,
                        "Date": new_entry["date"],
                    }
                    activity_rows.append(activity_row)
                    activity = db_manager.add_activity(
                        emo, new_entry["id"], new_entry["user_id"]
                    )
                    id = activity["id"]
                    if id:
                        activities_from_db[id] = activity
                        activities_not_reviewed_from_db[id] = activity

            st.rerun()
        print("New activity added successfully.")
    else:
        st.write("No new activities to review. Head to create a New Entry!")
        yesno = st.button("Create a New Entry!")
        if yesno:
            switch_page("new entry")

    ## RENDERING
    st.markdown("## Review")
    if len(activity_rows) > 0:
        st.write(
            "Please review the following activities and select the ones you want to dive deeper into."
        )
        edited_df = st.data_editor(
            pd.DataFrame(activity_rows),
            column_config={
                "Reviewed": st.column_config.CheckboxColumn(
                    "Reviewed",
                    help="Reviewed",
                    disabled=False,
                    width=None,
                    required=True,
                ),
                "Delete": st.column_config.CheckboxColumn(
                    "Delete",
                    help="Delete",
                    disabled=False,
                    width=None,
                    required=True,
                ),
                "Dive": st.column_config.CheckboxColumn(
                    "Dive",
                    help="Click to dive deeper",
                    disabled=False,
                    width="small",
                    required=True,
                ),
                "Activity Raw": st.column_config.Column(
                    "Activity Raw",
                    help="Events in your own words",
                    disabled=True,
                    width=None,
                    required=True,
                ),
                "Activity": st.column_config.Column(
                    "Activity",
                    help="summary",
                    width=None,
                    required=True,
                ),
                "Date": st.column_config.Column(
                    "Date",
                    help="Date",
                    disabled=True,
                    width="small",
                    required=True,
                ),
            },
            key="ACTIVITIES_table",
            hide_index=True,
            num_rows="fixed",
        )

    if "ACTIVITIES_table" in st.session_state:
        edited = st.session_state["ACTIVITIES_table"]
        if any(
            any(k != "Dive" and row[k] for k in row.keys())
            for row in edited["edited_rows"].values()
        ):
            if st.button(label="Save changes"):
                activities_from_db_array = list(
                    activities_not_reviewed_from_db.values()
                )
                for i, row in edited["edited_rows"].items():
                    update_payload = {}
                    if "Emotions" in row:
                        update_payload["emotions"] = row["Emotions"].lower()

                    if "Activity" in row:
                        update_payload["activity"] = row["Activity"]

                    if "Reviewed" in row and row["Reviewed"]:
                        data = activities_from_db_array[i]["data"]
                        data.update({"reviewed": True})
                        update_payload["data"] = data

                    if update_payload:
                        response = db_manager.edit_activity(
                            activities_from_db_array[i]["id"], update_payload
                        )

                    if "Delete" in row and row["Delete"]:
                        db_manager.delete_activity(activities_from_db_array[i]["id"])

                st.session_state["ACTIVITIES_table"]["edited_rows"].clear()
                st.write("Changes saved!")
                st.rerun()

        if any(row["Dive"] for row in edited["edited_rows"].values() if "Dive" in row):
            for i, row in edited["edited_rows"].items():
                if "Dive" in row and row["Dive"]:
                    actual_row = activity_rows[i]
                    render_switch_page_component(
                        i, actual_row["Activity"], actual_row["Emotions"]
                    )

    reviewed_entries = dict(
        sorted(reviewed_entries.items(), key=lambda item: item[0], reverse=True)
    )
    for reviewed_entry_date, activities in reviewed_entries.items():
        st.write(f"Reviewed: {reviewed_entry_date}")
        st.data_editor(
            pd.DataFrame(activities).drop(
                columns=["Date", "Reviewed", "Delete", "Dive"]
            ),
            column_config={
                "Activity Raw": st.column_config.Column(
                    "Activity Raw",
                    help="Events in your own words",
                    disabled=True,
                    width="large",
                    required=True,
                ),
                "Activity": st.column_config.Column(
                    "Activity",
                    help="summary",
                    disabled=True,
                    width=None,
                    required=True,
                ),
                "Emotions": st.column_config.Column(
                    "Emotions",
                    help="Emotions",
                    disabled=True,
                    width="medium",
                    required=True,
                ),
            },
            key=f"ACTIVITIES_table_reviewed_{reviewed_entry_date}",
            hide_index=True,
            num_rows="fixed",
        )
    return reviewed_entries


def _reformat_data(reviewed_entries):
    df_able_count = collections.defaultdict(int)
    meta = emotions_metadata()
    emotion_meta = {k.lower(): v for k, v in meta.items()}
    num_dates = 0
    for reviewed_entry_date, activities in reviewed_entries.items():
        num_dates += 1
        for activity in activities:
            emotion_name = activity["Emotions"].lower()
            if emotion_name not in emotion_meta:
                print(f"{emotion_name} not counted")
                break

            df_able_count[(reviewed_entry_date, emotion_name)] += 1

    df_able = []
    date_set = set()
    for (date, emotion), pop in df_able_count.items():
        adate = datetime.strptime(date, "%Y-%m-%d").date()
        date_set.add(adate)
        df_able.append(
            {
                "date": date,
                "x": emotion_meta[emotion]["x"],
                "y": emotion_meta[emotion]["y"],
                "emotion": emotion,
                "pop": pop,
            }
        )

    print(date_set)
    return df_able, list(date_set)


def plot_emotions_for_date(df, date):
    # Use plotly like the working test
    
    df_date = df[df["date"] == date]
    
    if df_date.empty:
        st.write("No data found for the selected date.")
        return
    
    # Create plotly scatter plot with different colors for each emotion
    fig = go.Figure()
    
    # Define colors for different emotions
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
    
    # Add a separate trace for each unique emotion
    for i, emotion in enumerate(df_date['emotion'].unique()):
        emotion_data = df_date[df_date['emotion'] == emotion]
        
        # Calculate marker sizes based on pop values (scale them up for visibility)
        marker_sizes = (emotion_data['pop'] * 15 + 10).tolist()  # min size 10, scales by 15x
        
        fig.add_trace(go.Scatter(
            x=emotion_data['x'].tolist(),
            y=emotion_data['y'].tolist(),
            mode='markers',
            marker=dict(
                size=marker_sizes, 
                color=colors[i % len(colors)],
                sizemode='diameter'
            ),
            name=emotion,
            text=[f"{em} (pop: {pop})" for em, pop in zip(emotion_data['emotion'], emotion_data['pop'])],
            textposition="top center",
            hovertemplate='%{text}<br>X: %{x}<br>Y: %{y}<extra></extra>'
        ))
    
    fig.update_layout(
        title="Emotions Scatter Plot",
        xaxis_title="Valence",
        yaxis_title="Arousal",
        xaxis=dict(range=[-6, 6]),
        yaxis=dict(range=[-6, 6]),
        width=800,
        height=600,
        showlegend=False
    )
    
    # Add center lines
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    fig.add_vline(x=0, line_dash="dash", line_color="gray")
    
    st.plotly_chart(fig, use_container_width=True)


def view_emotions(reviewed_entries):
    st.markdown("## Past Emotions")
    df, dates = _reformat_data(reviewed_entries)
    df = pd.DataFrame(df)

    dates.sort()
    date = st.select_slider("Date", options=dates, value=max(dates))
    st.write("Date:", date)
    plot_emotions_for_date(df, str(date))


user_valid, user_email = is_user_valid(st)
current_date = datetime.now().strftime("%Y-%m-%d")

if not user_valid:
    show_login(st)
elif is_user_subscriber(st, user_email):
    if not os.path.exists(f"analytics/{user_email}"):
        os.makedirs(f"analytics/{user_email}")

    reviewed_entries = full_app()
    if len(reviewed_entries) > 0:
        view_emotions(reviewed_entries)

# DEBUG
# st.write(reviewed_entries)
# if "ACTIVITIES_table" in st.session_state:
#     st.write(st.session_state["ACTIVITIES_table"])
