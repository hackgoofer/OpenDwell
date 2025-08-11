import streamlit as st
import os
from database import DatabaseManager
from utils import set_wide_page, is_user_valid, show_login, add_chat_message, is_user_subscriber
from ai_service import ai_service
from datetime import datetime
import streamlit_analytics
import os
set_wide_page(st)

# Initialize database manager
db_manager = DatabaseManager()


def how_this_works(expanded=False):
    ### How this works
    activity = st.session_state["HOWTOFEEL_activity"] if "HOWTOFEEL_activity" in st.session_state else ""
    emotions = st.session_state["HOWTOFEEL_emotions"] if "HOWTOFEEL_emotions" in st.session_state else ""
    goal = st.session_state["HOWTOFEEL_goal"] if "HOWTOFEEL_goal" in st.session_state else ""

    with st.expander("How this works", expanded=expanded):
        st.session_state["HOWTOFEEL_goal"] = st.text_input(label="We will help to you achieve the goal: ", value=goal if len(goal) != 0 else "")
        st.session_state["HOWTOFEEL_emotions"] = st.text_input(label="Related to this feeling: ", value=emotions if len(emotions) != 0 else "")
        st.session_state["HOWTOFEEL_activity"] = st.text_input(label="The activity of interest is: ", value=activity if len(activity) != 0 else "")

        st.markdown(f"""
        > **_NOTE:_**  Before starting the session, please make sure to fill out contents above.
                    
        > **_NOTE:_**  Please do not close this thread until you feel like you have achieved your goal.""")



def chat(thread_id, user_id):
    # # Display chat messages from history on app rerun
    for message in st.session_state.HOWTOFEEL_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # first LLM call
    activity = st.session_state["HOWTOFEEL_activity"] if "HOWTOFEEL_activity" in st.session_state else ""
    emotions = st.session_state["HOWTOFEEL_emotions"] if "HOWTOFEEL_emotions" in st.session_state else ""
    goal = st.session_state["HOWTOFEEL_goal"] if "HOWTOFEEL_goal" in st.session_state else ""
    system_prompt = f"""You are a trusted therapist in the user's life. The user is feeling: {emotions} during the event: {activity}. User's goal is: {goal}. Help user achieve the goal by crafting a message. Message histories: """
    
    if len(st.session_state["HOWTOFEEL_messages"]) == 0:
        response = ai_service.chat_thread(
            messages=[{"role": "system", "content": system_prompt}]
            + st.session_state.HOWTOFEEL_messages
        )
        add_chat_message(st, user_id=user_id, thread_id=thread_id, role="assistant", message=response, history=st.session_state.HOWTOFEEL_messages)

    def end_session():
        pass

    # React to user input
    if prompt := st.chat_input(
        "Please respond... type 'done' to end the session."
    ):
        if prompt == "done":
            end_session()
        
        # Display user message in chat message container
        add_chat_message(st, user_id=user_id, thread_id=thread_id, role="user", message=prompt, history=st.session_state.HOWTOFEEL_messages)
        
        gpt_response = ai_service.chat_thread(
            messages=[{"role": "system", "content": system_prompt}]
            + st.session_state.HOWTOFEEL_messages
        )
        add_chat_message(st, user_id=user_id, thread_id=thread_id, role="assistant", message=gpt_response, history=st.session_state.HOWTOFEEL_messages)
    
    if st.button("Restart"):
        st.session_state["HOWTOFEEL_messages"] = False
        st.session_state.HOWTOFEEL_messages = []
        st.rerun()


def full_app():
    st.title("How to Feel", "how_to_feel")

    user_id = st.session_state["session_data"]["user"]["id"]
    values = db_manager.get_pairwise_user_values(user_id)
    
    # Get user profile from auth manager
    from auth import AuthManager
    import json
    import os
    
    auth_manager = AuthManager()
    if hasattr(auth_manager.provider, 'get_user_profile'):
        profile = auth_manager.provider.get_user_profile()
    else:
        try:
            # Load user_profile_path from config
            config_file = "user_config.json"
            user_profile_path = "user_profile.txt"  # default
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    user_profile_path = config.get("user_profile_path", "user_profile.txt")
            
            profile = open(user_profile_path, "r").read()
        except FileNotFoundError:
            profile = "A user interested in personal development and emotional wellbeing."

    if "ACTIVITIES_HOWTOFEEL"  in st.session_state:
        page_data = st.session_state["ACTIVITIES_HOWTOFEEL"]
        st.session_state["HOWTOFEEL_activity"] = page_data["activity"]
        st.session_state["HOWTOFEEL_emotions"] = page_data["emotions"]
        st.session_state["HOWTOFEEL_goal"] = page_data["goal"]


    if "HOWTOFEEL_messages" not in st.session_state:
        st.session_state.HOWTOFEEL_messages = []


    if "state_dict" not in st.session_state:
        st.session_state["state_dict"] = {}


    if "HOWTOFEEL_chat_threadID" in st.session_state and st.session_state["HOWTOFEEL_chat_threadID"]:
        how_this_works()
        chat(st.session_state["HOWTOFEEL_chat_threadID"], user_id)
    else:
        how_this_works(expanded=True)
        activity = st.session_state["HOWTOFEEL_activity"] if "HOWTOFEEL_activity" in st.session_state else ""
        emotions = st.session_state["HOWTOFEEL_emotions"] if "HOWTOFEEL_emotions" in st.session_state else ""
        goal = st.session_state["HOWTOFEEL_goal"] if "HOWTOFEEL_goal" in st.session_state else ""
        
        if st.button("Start Chat", disabled= (len(activity) == 0 or len(emotions) == 0 or len(goal) == 0)):
            st.session_state["HOWTOFEEL_chat_threadID"] = db_manager.add_thread_DB(user_id, "howtofeel", {"activity": activity, "emotions": emotions, "goal": goal})
            st.rerun()

        # # Add a button to add another entry
        # if st.button("Lucky Perspectives"):
        #     gpt_response = ai_service.chat_thread(
        #         messages=[{"role": "system", "content": system_prompt}]
        #         + st.session_state.HOWTOFEEL_messages
        #         + [
        #             {
        #                 "role": "user",
        #                 "content": "Can you display the story, fact, new perspectives 1, new perspectives 2, new perspectives 3 in a markdownt able",
        #             }
        #         ]
        #     )
        #     st.session_state.HOWTOFEEL_messages.append({"role": "assistant", "content": gpt_response})
        #     with st.chat_message("assistant"):
        #         st.markdown(gpt_response)


user_valid, user_email  = is_user_valid(st)
current_date = datetime.now().strftime('%Y-%m-%d')

if not user_valid:
    show_login(st)
elif is_user_subscriber(st, user_email):
    if not os.path.exists(f"analytics/{user_email}"):
        os.makedirs(f"analytics/{user_email}")
    
    full_app()
