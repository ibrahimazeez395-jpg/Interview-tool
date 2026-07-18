import streamlit as st
from openai import OpenAI
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="Streamlit Chat", page_icon="🤖")
st.title("Chatbot")

if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False

if "user_message_count" not in st.session_state:
    st.session_state.user_message_count = 0
if "feedback_shown" not in st.session_state:
    st.session_state.feedback_shown = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_completed" not in st.session_state:
    st.session_state.chat_completed = False

# function that toggles the completion of the setup process
def complete_setup():
    st.session_state.setup_complete = True

# function that toggles the feedback display
def show_feedback():
    st.session_state.feedback_shown = True
if not st.session_state.setup_complete: 

    st.subheader('Personal Information', divider='rainbow') 

    if "name" not in st.session_state:
        st.session_state["name"] = ""
    if "experience" not in st.session_state:
        st.session_state["experience"] = ""
    if "skills" not in st.session_state:
        st.session_state["skills"] = ""

    st.session_state["name"] = st.text_input(label= "Name", max_chars= 40, value = st.session_state["name"], placeholder= "Enter your name:")

    st.session_state["experience"] = st.text_area(label = "Experience", value = st.session_state["experience"], height = None, max_chars = 200, placeholder = "Describe your experience:")

    st.session_state["skills"] = st.text_area(label = "Skills", value = st.session_state["skills"], height = None, max_chars = 200, placeholder = "List your skills:") 

# These are not needed again since we are already storing the values in the session state, 
# but if you want to display them, you can uncomment these lines.

    #st.write(f"**Your Name**: {st.session_state['name']}")
    #st.write(f"**Your Experience**: {st.session_state['experience']}")
    #st.write(f"**Your Skills**: {st.session_state['skills']}")

    st.subheader('Company and Position', divider='rainbow')

    if "level" not in st.session_state:
        st.session_state["level"] = "Junior"
    if "position" not in st.session_state:
        st.session_state["position"] = "Data Engineer"
    if "company" not in st.session_state:
        st.session_state["company"] = "Amazon"

    col1, col2 = st.columns(2)
    with col1:
        st.radio(
        "Choose level",
        key="level",
        options=["Junior", "Mid-level", "Senior"])

    with col2:
        st.selectbox("Choose position", 
                     key="position", 
                     options=["Data Engineer", "ML Engineer", "Data Scientist", "BI Analyst", "Financial Analyst"])

    st.selectbox("Choose a Company", 
                 options=["Amazon", "Google", "Microsoft", "Meta", "Apple", "Netflix", "Tesla", "Udemy"],
                key="company")

    st.write(f"**Your Information**: {st.session_state['level']} {st.session_state['position']} at {st.session_state['company']}")

    if st.button("Start Interview"):
        complete_setup()
        st.write("Setup complete. Starting interview...")
    
# by combining these 3 conditions using the logical AND operator, 
# we are determining if the application should proceed to the interview phase.
if st.session_state.setup_complete and not st.session_state.feedback_shown and not st.session_state.chat_completed:

    st.info(
        """
        Start by introducing yourself.
        """,
        icon="💡"
    )

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o"
# The 'if not' statement checks if the 'messages' list in the session state is empty.
# If it is, it initializes the list with a system message that sets the context for the chatbot.
# This message includes details about the interviewee (name, experience, skills) and the position they are interviewing for (level, position, company).
# This ensures that the chatbot has the necessary context to conduct the interview effectively.

    if not st.session_state.messages:
        st.session_state["messages"] = [{
        "role": "system",
        "content": f"""
    You are an experienced HR interviewer.

    You are interviewing a candidate named {st.session_state['name']}.

    Candidate's experience:
    {st.session_state['experience']}

    Candidate's skills:
    {st.session_state['skills']}

    The role is:
    {st.session_state['level']} {st.session_state['position']} at {st.session_state['company']}.

    Rules:
    - Do NOT introduce yourself.
    - Do NOT say "My name is..." or use placeholders like "[Your Name]".
    - Ask one interview question at a time.
    - Keep your responses professional and concise.
    - Base your questions on the candidate's previous answers.
    - After greeting the candidate, immediately begin the interview.
    """
    }]

    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

# Before the code accepts the user input, we check if the user has sent fewer than five messages.
    if st.session_state.user_message_count < 5:
        if prompt := st.chat_input("What do you want to ask?", max_chars=1000):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

        # If the statement is true, the assistance response will be generated and displayed if there are more than 4,
        # the assistant won't respond, ensuring the limit interaction to a maximum of 5.   
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
        st.session_state.chat_completed = True

# This section checks if the chat has been completed and if feedback has not yet been shown. 
# If both conditions are met, it displays a button labeled "Get Feedback". 
# When the button is clicked, it triggers the show_feedback function,
# which sets the feedback_shown state to True and displays a message indicating that feedback is being fetched.

if st.session_state.chat_completed and not st.session_state.feedback_shown:
    if st.button("Get Feedback", on_click = show_feedback):
        st.write("Fetching feedback...")

if st.session_state.feedback_shown:
    st.subheader("Feedback")

    conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])

    feedback_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    feedback_completion = feedback_client.chat.completions.create(
        model = "gpt-4o",
            messages = [
                {"role": "system", "content": """You are a helpful tool that provides feedback on an interviewee performance.
                 Before the Feedback give a score of 1 to 10.
                 Follow this format:
                 Overall Score: // Your Score
                 Feedback:// Here you put your feedback
                 Give only the feedback do not ask any additional questions.
                 """},
                 {"role": "user", "content": f"This is the interview you need to evaluate. Keep in mind that you are only a tool and shouldn't engage in conversation: {conversation_history}"}
            ]
        )
    st.write(feedback_completion.choices[0].message.content)

    if st.button("Restart Interview", type = "primary"):
            streamlit_js_eval(js_expressions = "parent.window.location.reload()")
       