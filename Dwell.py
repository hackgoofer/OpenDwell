from database import DatabaseManager
import streamlit as st
import os
from streamlit_extras.switch_page_button import switch_page
from utils import set_wide_page, is_user_valid, show_login
from dotenv import load_dotenv
import random
import time
import streamlit_analytics
from datetime import datetime


load_dotenv()
set_wide_page(st)

# Initialize managers
db_manager = DatabaseManager()

# Import auth manager for subscription check
from auth import AuthManager

auth_manager = AuthManager()


def generate_random_login_info(descriptions):
    random_num = random.randint(0, len(descriptions) - 1)
    st.session_state["login_random_num"] = {
        "random_num": random_num,
        "expiry": time.time() + 180,
    }


# Check if uploads folder exists; if not, create one
if not os.path.exists("uploads"):
    os.makedirs("uploads")
# Main Streamlit App


def full_app(user_email):
    print("logged in")
    st.title("Dwell - Your AI Journal")

    if "DWELL_what_happened" not in st.session_state:
        st.session_state["DWELL_what_happened"] = {}
    if "DWELL_content" not in st.session_state:
        st.session_state["DWELL_content"] = {}

    # Retrieve past entries for sidebar selection
    user_id = st.session_state["session_data"]["user"]["id"]
    entries = db_manager.get_entries(user_id)
    entry_dates = ["All Entries"] + [str(e["date"]) for e in entries]
    if entry_dates:
        selected_entry_date = st.sidebar.selectbox("Past Entries", entry_dates, index=0)

    # Display past entries
    st.markdown("## Past Entries")

    if not entry_dates:
        st.write("No past entries to display. Head to create a New Entry!")
        yesno = st.button("Create a New Entry!")
        if yesno:
            switch_page("new entry")
        return

    if selected_entry_date == "All Entries":
        selected_entries = entries
    else:
        selected_entries = [e for e in entries if str(e["date"]) == selected_entry_date]

    for i, e in enumerate(selected_entries):
        created_at = e["date"]
        st.markdown(
            f"### Entry for {created_at} <a name='{created_at}'></a>",
            unsafe_allow_html=True,
        )

        st.write(e["what_happened"])

        with st.expander("Edit this entry", False):
            with st.form(key=f"form_{i}"):
                what_happened = st.text_area(
                    "What happened:",
                    e["what_happened"],
                )

                if st.form_submit_button(label="Save Changes to"):
                    e["what_happened"] = what_happened
                    st.write("Updated!")

                    db_manager.edit_entry(e["id"], e["what_happened"])
                    st.rerun()

        if auth_manager.is_user_subscriber(st, user_email):
            with st.expander("Review this day with AI", False):
                with st.form(key=f"review_{i}"):
                    default_prompt = "You are an AI smart journaling therapist. Your user is going to tell you about their day, and you should give a short, concise summary of what you hear and offer some feedback and recommendations for them to consider tomorrow."
                    custom_prompt = st.text_area("System prompt", default_prompt)
                    serialized_data = "\n".join(
                        [e["what_happened"]]
                        + [
                            f"Question: {item['question']} \n Answer: {item['answer']}"
                            for i, item in enumerate(e["data"])
                        ]
                    )
                    if st.form_submit_button(label="See response"):
                        from ai_service import ai_service  # must run after set_page_config

                        st.info(
                            ai_service.simple_completion(custom_prompt, serialized_data)
                        )


user_valid, user_email = is_user_valid(st)
date = datetime.now().strftime("%Y-%m-%d")

if not user_valid:
    show_login(st)
else:
    if not os.path.exists(f"analytics/{user_email}"):
        os.makedirs(f"analytics/{user_email}")

    full_app(user_email)
