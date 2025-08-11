import streamlit as st
import os
from streamlit_extras.switch_page_button import switch_page
from utils import set_wide_page, is_user_valid, show_login
from dotenv import load_dotenv
from auth import AuthManager
import streamlit_analytics
from database import DatabaseManager
from datetime import datetime

load_dotenv()
set_wide_page(st)

# Initialize managers
auth_manager = AuthManager()
db_manager = DatabaseManager()

is_valid, user_email = is_user_valid(st)
current_date = datetime.now().strftime('%Y-%m-%d')


if is_valid:
    if not os.path.exists(f"analytics/{user_email}"):
        os.makedirs(f"analytics/{user_email}")

    st.markdown("# Settings")
    session_data = st.session_state["session_data"]
    first_name = session_data["user"]["user_metadata"].get("first_name", None)
    email = session_data["user"]["email"]
    st.markdown(f"Logged in as {first_name if first_name else email}")
    
    # Need to better think through this part
    # if st.checkbox("Enable Server Side Encryption?", value=False, key="journal_encrypted"):
    #     if st.button("Confirm? Note the process will take a while... since we need to encrypt all your data."):
    #         progress_text = "Operation in progress... Please wait."
    #         my_bar = st.progress(0, text=progress_text)
    #         user_id = session_data["user"]["id"]
    #         progress = encrypt_journal(user_id)
    #         my_bar.progress(progress, text=progress_text)

    new_session_data = auth_manager.show_logout(st)
    if new_session_data is not None and "loggedOut" in new_session_data and new_session_data["loggedOut"]:
        st.session_state["session_data"] = None
        st.rerun()
else:
    show_login(st)