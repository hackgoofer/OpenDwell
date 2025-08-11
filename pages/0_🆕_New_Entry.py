import instructor
import streamlit as st
from database import DatabaseManager
from ai_service import ai_service
from datetime import date
from random import sample
from streamlit_extras.switch_page_button import switch_page
import os
import streamlit_analytics
from dotenv import load_dotenv
from utils import set_wide_page, is_user_valid, show_login
from datetime import datetime
set_wide_page(st)
load_dotenv()

# Initialize database manager
db_manager = DatabaseManager()

def full_app():
    st.markdown("# New Entry")
    st.sidebar.markdown("# New Entry")

    # Default to "Add New Entry"
    st.subheader("New Journal Entry")
    # sidebarstate()

    # Logic to add a new journal entry
    # Sample logic here; actual logic may involve database operations
    new_date = st.date_input("Date", value=date.today())
    new_what_happened = st.text_area("What happened and what is on your mind?")
    # st.button("Dig Deeper") # unused for now

    # uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])
    # if uploaded_file:
    #     file_path = os.path.join("uploads", f"{new_date}_{uploaded_file.name}")
    #     with open(file_path, "wb") as f:
    #         f.write(uploaded_file.read())

    if st.button("Complete Entry"):
        db_manager.add_entry(new_what_happened, st.session_state["session_data"]["user"]["id"], new_date.isoformat())

        # Notify the user
        st.success("New journal entry added successfully.")
                
    if st.button("See all entries!"):
        switch_page("Dwell")
        pass

user_valid, user_email  = is_user_valid(st)
current_date = datetime.now().strftime('%Y-%m-%d')

if not user_valid:
    show_login(st)
else:
    if not os.path.exists(f"analytics/{user_email}"):
        os.makedirs(f"analytics/{user_email}")
    
    full_app()