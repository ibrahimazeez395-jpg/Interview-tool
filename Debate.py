import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Debate Chat", page_icon="🤖")
st.title("Debate Chatbot")

if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False

if "user_message_count" not in st.session_state:
    st.session_state.user_message_count = 0
if "evaluation_shown" not in st.session_state:
    st.session_state.evaluation_shown = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "debate_completed" not in st.session_state:
    st.session_state.debate_completed = False
if "user_side" not in st.session_state:
    st.session_state.user_side = "For"

def complete_setup():
    st.session_state.setup_complete = True

def show_evaluation():
    st.session_state.evaluation_shown = True
if not st.session_state.setup_complete:

    st.subheader("Personal Information", divider="rainbow")
    if "user_name" not in st.session_state:
        st.session_state["user_name"] = ""
    if "debate_topic" not in st.session_state:
        st.session_state["debate_topic"] = ""
    if "user_side" not in st.session_state:
        st.session_state["user_side"] = ""
    if "level" not in st.session_state:
        st.session_state["level"] = ""
    
    st.session_state["user_name"] = st.text_input(label="Name", 
                                                    max_chars=40, 
                                                    value=st.session_state["user_name"], 
                                                    placeholder="Enter your name:")
    st.session_state["debate_topic"] = st.text_area(label="Debate Topic",
                                                    value=st.session_state["debate_topic"], 
                                                    height=None, 
                                                    max_chars=100, 
                                                    placeholder="Enter the debate topic:")
    col1, col2 = st.columns(2)
    with col1:
        st.radio(label="Your Side", 
                 options=["for", "against"], 
                 key="user_side")
    with col2:
        st.radio(label="Difficulty Level", 
                 options=["Beginner", "Intermediate", "Advanced"], 
                 key="level"
    )
    st.write(f"**Name:** {st.session_state['user_name']}")
    st.write(f"**Debate Topic:** {st.session_state['debate_topic']}")
    st.write(f"**Level:** {st.session_state['level']}")
    st.write(f"**Your Position:** {st.session_state['user_side']}")

    if st.button("Start Debate"):
        complete_setup()
        st.write("Setup complete! You can now start the debate.")

if st.session_state.setup_complete and not st.session_state.evaluation_shown and not st.session_state.debate_completed:

    st.info(
        """
        Start by introducing yourself and your topic.
        """,
        icon="💡"
    )

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o"

    if not st.session_state.messages:
        st.session_state["messages"] = [{
        "role": "system",
        "content": f"""
    You are an expert debater.

    You are debating against the user.

    Topic:
    Socialism is the best form of government.

    The user supports:
    FOR

    You must argue AGAINST.

    Rules:
    - Never switch sides.
    - Give logical arguments.
    - Challenge weak reasoning.
    - Ask follow-up questions.
    - Be respectful.
    - Limit each response to about 80 words.
    - One response per turn.
        """
        }]

    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if st.session_state.user_message_count < 5:
        if prompt := st.chat_input("What do you want to ask?", max_chars=1000):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            if st.session_state.user_message_count < 4:  
                with st.chat_message("assistant"):
                    stream = client.chat.completions.create(
                        model=st.session_state["openai_model"],
                        messages= [
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages  
                        ],
                        stream=True,
                    )
                    response = st.write_stream(stream)
                st.session_state.messages.append({"role": "assistant", "content": response})    
            st.session_state.user_message_count += 1
    if st.session_state.user_message_count >= 5:
        st.session_state.debate_completed = True

if st.session_state.debate_completed and not st.session_state.evaluation_shown:
    if st.button("Evaluate Debate", on_click=show_evaluation):
        st.write("Evaluating debate...")

def show_evaluation():
    st.session_state.evaluation_shown = True

# The second model

if st.session_state.evaluation_shown:
    st.subheader("Debate Result")

    conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])
    judge_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    judge_response = judge_client.chat.completions.create(
        model = "gpt-4o",
            messages = [
                {"role": "system", "content":  """
        You are an impartial debate judge.

        Evaluate the debate between the user and the AI.

        Judge both sides using:
        - logical reasoning
        - relevance
        - clarity
        - evidence
        - rebuttals
        - persuasiveness

        Do not automatically favor the AI.

        Return the result using this exact format:

        Winner: User, AI, or Draw

        User Score: /50
        AI Score: /50

        Reason:
        Explain clearly why the winner won.

        User Strengths:
        - ...

        User Weaknesses:
        - ...

        AI Strengths:
        - ...

        AI Weaknesses:
        - ...
        """
                    },
                    {"role": "user",
                    "content": f"""
                    Debate topic:
                    {st.session_state['debate_topic']}

                    The user's side:
                    {st.session_state['user_side']}

                    Debate transcript:
                    {conversation_history}
                    """
                    }])
    result = judge_response.choices[0].message.content
    st.write(result)