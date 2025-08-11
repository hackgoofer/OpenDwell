import os
from data_model import ActivityEmotions, ValuesComparisons
from database import DatabaseManager
import json
from auth import AuthManager
from ai_service import ai_service
from dotenv import load_dotenv

load_dotenv()

# Initialize managers
auth_manager = AuthManager()
db_manager = DatabaseManager()


def retry_on_error(x):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for i in range(1, x + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Attempt {i} of {x} failed: {e}")
                    if i == x:
                        raise  # Re-raise the exception on the final attempt
            # This line is no longer needed as the exception will be re-raised

        return wrapper

    return decorator


def is_user_valid(st):
    return auth_manager.is_user_valid(st)


def is_user_subscriber(st, user_email):
    """Check if user is subscribed and handle restriction if not."""
    if auth_manager.should_restrict_content(st, user_email):
        auth_manager.show_access_restriction(st, user_email)
        return False

    # Set session state for backward compatibility
    st.session_state["session_data"]["user_subscribed"] = True
    return True


def set_wide_page(st):
    is_valid, _ = is_user_valid(st)
    try:
        st.set_page_config(
            page_title="Dwell - Your AI Journal",
            page_icon="🧊",
            layout="wide",
            initial_sidebar_state="collapsed" if not is_valid else "expanded",
        )
        st.markdown(
            f"""
        <style>
            .reportview-container .main .block-container{{
                max-width: 1000px;
                padding-top: 0rem;
                padding-right: 0rem;
                padding-left: 0rem;
                padding-bottom: 0rem;
            }}

        </style>
        """,
            unsafe_allow_html=True,
        )
    except:
        pass


def show_login(st):
    """Show login UI or handle auto-login for vanilla auth."""
    # For vanilla auth, session should already be created by is_user_valid()
    if auth_manager.provider.provider_name == "vanilla":
        # This shouldn't happen with vanilla since auto-login occurs in is_user_valid()
        # But just in case, show a simple message
        st.info("Loading...")
        st.rerun()
        return

    print("not logged in")
    session_data = auth_manager.show_login(st)
    if session_data:
        st.session_state["session_data"] = session_data
        st.rerun()


def date_from_timestamp(iso_date_string):
    from datetime import datetime

    # Convert ISO 8601 string to datetime object
    datetime_object = datetime.fromisoformat(iso_date_string)

    # Extract just the date part
    date_object = datetime_object.date()
    return str(date_object)


def add_chat_message(st, user_id, thread_id, role, message, history):
    print(f"{role}: {message}")
    if role == "user":
        with st.chat_message("user"):
            st.markdown(message)
    else:
        with st.chat_message("assistant"):
            st.markdown(message)
    history.append({"role": role, "content": message})
    db_manager.add_chat_message_DB(user_id, thread_id, role, message)


@ai_service.retry_on_error(3)  # Retry up to 3 times
def get_activities_emotions(content, type="journal entry"):
    # Get user profile from auth manager
    if hasattr(auth_manager.provider, "get_user_bio"):
        user_bio = auth_manager.provider.get_user_bio()
    else:
        user_bio = "I am a user interested in personal development."

    return ai_service.extract_activities_emotions(content, user_bio, type)


@ai_service.retry_on_error(3)  # Retry up to 3 times
def get_value_comparisons(content, type="journal entry"):
    return ai_service.extract_value_comparisons(content, type)
