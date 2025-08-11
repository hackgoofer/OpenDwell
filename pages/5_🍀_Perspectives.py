from database import DatabaseManager
import streamlit as st
import os
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
    unbelief = st.session_state["PERSPECTIVES_unbelief"] if "PERSPECTIVES_unbelief" in st.session_state else ""
    with st.expander("How this works", expanded=expanded):
        st.write("We meticulously document a belief that you currently hold, which may no longer be beneficial to your well-being. Subsequently, we conduct a thorough analysis of your convictions, enabling you to discern factual evidence from mere narratives. This process facilitates the development of new, more constructive viewpoints that are conducive to a healthier mindset. We may use your values as a guiding principle to help you develop new perspectives.")
        st.session_state["PERSPECTIVES_unbelief"] = st.text_input(label="A belief that is no longer serving you: ", value=unbelief if len(unbelief) != 0 else "")

        st.markdown("""
            <p align="center">
            Have you ever seen dust dancing in sunbeams?<br>
            How it glitters like flecks of gold?<br>
            Maybe that is the true alchemy.<br>
            Not changing what something is,<br>
            but seeing it in a new light.<br>
            </p>
            """, unsafe_allow_html=True)



def chat(user_id, thread_id):
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
            profile = "A user interested in personal development and changing perspectives."

    system_prompt = f"""
    We have a lot of beliefs about who we are in the world, about what happened, and about what it means that things happened. Each fact can have a million interpretations.
    We should aim to believe in useful stories that aim to help us grow and be happy, rather than believing in stories that make us suffer.

    Here is information about the user {profile}

    Here is the users values: {values}

    Your goals are:
    1. Detect stories vs facts, be explicit. Don't ask questions in the detection. Help people realize that the events they shared are actually stories, and not facts.
    2. Push by asking questions to users for them to give concrete facts on how they arrived at their beliefs.
    3. Help people create useful stories that help them grow and be happy, be concrete action oriented.

    Here is a classification of facts and stories. Fact are concrete what happened. Stories are interpretations of what happened.
    1. I went on two dates (facts)
    2. They both fizzled out (story)
    3. My mom thinks I am fat (story)
    4. I went to bed at 3am last night (fact)

    An example:
    * They say: I am not loved. I am also not brave enough to go out and meet people.
    * What are the facts? Ask questions and detect if it is a story or a fact.
    - user: nodody wants to date me.
    - assistant: This is a story. What is a concrete fact though?
    - user: I went on 2 dates 
    - assistant: This is a fact. Ok, sounds good. So what happened after?
    - user: but both fizzled out.
    - assistant: This is a story. What does "fizzled out" mean? What made you believe that?
    - user: we just did not chat after the date.
    - assistant: This is a fact. Seems like you want to chat with him, so did you reach out? 
    - user: no
    - assistant: Okay, so you just go around your life wanting other people to do what you want them to do?
    - user: no
    - assistant: One concrete action is to reach out to him and say how you feel. You value "Love" and "Courage" right? That's what a person who values "love" and "Courage" would do?
    * You can make it mean (revised more useful story/alternative perspective): 
    - Take actions in the world if I want to make changes. (action orientedness)
    - I need to clarify within myself who I want to date, and date them. (action orientedness)
    - Be very clear about my wants and needs and good to haves. (action orientedness)


    Other common stories:
    * "If I don't do something right, then I won't be liked/loved by my boyfriend."
    * "My manager wants to manage me out because I said things that she disliked."
    * "I will be a failure in starting my own business because I have never done it before."
    * "He can do things faster than me." 
    
    Most things are a story, they will be a fact only if there are specific instances.

    Be spicy and direct, and imply to people that they suck and need to do better. Push on them. Don't proceed to suggest conrete actions until you have converted all of their stories into facts.
    """

    # Display chat messages from history on app rerun
    for message in st.session_state.PERSPECTIVES_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if st.session_state["PERSPECTIVES_messages"][-1]["role"] == "user":
        response = ai_service.chat_thread(
            messages=[{"role": "system", "content": system_prompt}]
            + st.session_state.PERSPECTIVES_messages
        )
        add_chat_message(st, user_id=user_id, thread_id=thread_id, role="assistant", message=response, history=st.session_state.PERSPECTIVES_messages)

    # React to user input
    if prompt := st.chat_input(
        "Write a message."
    ):
        add_chat_message(st, user_id=user_id, thread_id=thread_id, role="user", message=prompt, history=st.session_state.PERSPECTIVES_messages)
        gpt_response = ai_service.chat_thread(
            messages=[{"role": "system", "content": system_prompt}]
            + st.session_state.PERSPECTIVES_messages
        )
        add_chat_message(st, user_id=user_id, thread_id=thread_id, role="assistant", message=gpt_response, history=st.session_state.PERSPECTIVES_messages)

    # Add a button to add another entry
    if len(st.session_state.PERSPECTIVES_messages) >= 5:
        if st.button("Lucky Perspectives"):
            gpt_response = ai_service.chat_thread(
                messages=[{"role": "system", "content": system_prompt}]
                + st.session_state.PERSPECTIVES_messages
                + [
                    {
                        "role": "user",
                        "content": "Can you display the story, fact, new perspectives 1, new perspectives 2, new perspectives 3 in a markdownt able",
                    }
                ]
            )
            add_chat_message(st, user_id=user_id, thread_id=thread_id, role="user", message=gpt_response, history=st.session_state.PERSPECTIVES_messages)

    if st.button("Restart"):
        st.session_state["PERSPECTIVES_chatstarted"] = False
        st.session_state.PERSPECTIVES_messages = []
        st.rerun()

def full_app(user_id):
    st.title("Lucky Perspectives", "Tell me a belief that you think is no longer serving you")
    
    if "PERSPECTIVES_messages" not in st.session_state:
        st.session_state.PERSPECTIVES_messages = []


    if "state_dict" not in st.session_state:
        st.session_state["state_dict"] = {}


    if "PERSPECTIVES_chat_threadID" in st.session_state and st.session_state["PERSPECTIVES_chat_threadID"]:
        how_this_works()
        chat(user_id, st.session_state["PERSPECTIVES_chat_threadID"])
    else:
        how_this_works(expanded=True)
        unbelief = st.session_state["PERSPECTIVES_unbelief"] if "PERSPECTIVES_unbelief" in st.session_state else ""
        
        if st.button("Start Chat", disabled= (len(unbelief) == 0)):
            st.session_state["PERSPECTIVES_chat_threadID"] = db_manager.add_thread_DB(user_id, "perspectives", {"unbelief": unbelief})
            st.session_state.PERSPECTIVES_messages.append({"role": "user", "content": unbelief})
            st.rerun()


user_valid, user_email  = is_user_valid(st)
current_date = datetime.now().strftime('%Y-%m-%d')

if not user_valid:
    show_login(st)
elif is_user_subscriber(st, user_email):
    if not os.path.exists(f"analytics/{user_email}"):
        os.makedirs(f"analytics/{user_email}")

    user_id = st.session_state["session_data"]["user"]["id"]
    full_app(user_id)
