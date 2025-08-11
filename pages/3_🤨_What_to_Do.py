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

    with st.expander("How this works", expanded=expanded):
        st.session_state["WHATTODO_rant"] = st.text_area(label="Please rant (provide all details): ")

        st.markdown(f"""
        > **_NOTE:_**  Before starting the session, please make sure to fill out contents above.
                    
        > **_NOTE:_**  Please do not close this thread until you feel like you have achieved your goal.""")



def chat(thread_id, user_id, values=None):
    # # Display chat messages from history on app rerun
    for message in st.session_state.WHATTODO_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # first LLM call
    rant = st.session_state["WHATTODO_rant"] if "WHATTODO_rant" in st.session_state else ""
    value_statement = ""
    if values:
        value_statement = f"Use users' personal values where appropriate: {values}."
    
    system_prompt = f"""You are a trusted therapist in the user's life. Your goal is help user figure out what to do given a particular situation. The user's situation is {rant}. {value_statement} Message histories: """
    
    if len(st.session_state["WHATTODO_messages"]) == 0:
        response = ai_service.chat_thread(
            messages=[{"role": "system", "content": system_prompt}]
            + st.session_state.WHATTODO_messages
        )
        add_chat_message(st, user_id=user_id, thread_id=thread_id, role="assistant", message=response, history=st.session_state.WHATTODO_messages)

    def end_session():
        pass

    # React to user input
    if prompt := st.chat_input(
        "Please respond... type 'done' to end the session."
    ):
        if prompt == "done":
            end_session()
        
        # Display user message in chat message container
        add_chat_message(st, user_id=user_id, thread_id=thread_id, role="user", message=prompt, history=st.session_state.WHATTODO_messages)
        
        gpt_response = ai_service.chat_thread(
            messages=[{"role": "system", "content": system_prompt}]
            + st.session_state.WHATTODO_messages
        )
        add_chat_message(st, user_id=user_id, thread_id=thread_id, role="assistant", message=gpt_response, history=st.session_state.WHATTODO_messages)
    
    if st.button("Restart"):
        st.session_state["WHATTODO_messages"] = False
        st.session_state.WHATTODO_messages = []
        st.rerun()


def full_app():
    st.title("What to do", "what_to_do")

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
            profile = "A user interested in personal development and goal achievement."

    if "WHATTODO_messages" not in st.session_state:
        st.session_state.WHATTODO_messages = []


    if "state_dict" not in st.session_state:
        st.session_state["state_dict"] = {}


    if "WHATTODO_chat_threadID" in st.session_state and st.session_state["WHATTODO_chat_threadID"]:
        how_this_works()
        chat(st.session_state["WHATTODO_chat_threadID"], user_id, values)
    else:
        how_this_works(expanded=True)
        rant = st.session_state["WHATTODO_rant"] if "WHATTODO_rant" in st.session_state else ""
       
        if st.button("Start Chat", disabled= (len(rant) == 0)):
            st.session_state["WHATTODO_chat_threadID"] = db_manager.add_thread_DB(user_id, "whattodo", {"rant": rant})
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
