
import streamlit as st
import google.generativeai as genai 
#VERIFICATION CODE STARTS
import hmac

def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        st.markdown("<h1 style='text-align: center; font-size: 48px;'>Welcome to 📊Insightify</h1>", unsafe_allow_html=True)
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("enter the username and password")
    return False


if not check_password():
    st.stop()
    
    
def logout():
    """Resets the session state to log out the user."""
    st.session_state["password_correct"] = False

# Add a logout button to the sidebar
st.sidebar.button("Logout", on_click=logout)
#VERIFICATION CODE ENDS

import google.generativeai as genai
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import sklearn
import plotly.express as px
import plotly.graph_objects as go
import sklearn

if 'messages' not in st.session_state:
    st.session_state.messages = []


if 'first_run' not in st.session_state:
    st.session_state.first_run = False


def prepend_prompt_format(prompt, data):
    return f"""
    Your task is to generate Python code that exclusively uses Streamlit and Plotly for visualization.
    - The answer should be in two sections:
      1. First section starts with `#ANSWER#` and contains a short insight about the dataset.
      2. Second section starts with `#CODE#` and contains Streamlit-compatible Python code.
    - The generated code should:
      - Use `st.write()` to describe insights.
      - Use `st.plotly_chart()` for interactive plots.
      - Ensure the data is available in the `data` variable.
      - Not modify the `data` variable.
      - Use Plotly for all visualizations to enable pan/zoom functionality.

    Generate Streamlit Python code for visualizing this dataset: {data.head().to_string()}.\n
    Query: {prompt}
    """

def show_user_message(message):
    st.chat_message("user").write(message['parts'][0])


def exec_chart_code(code, data):
    if not code:
        return None

    try:
        exec_locals = {}
        exec(code, {"plt": plt, "sns": sns, "pd": pd, 'sklearn': sklearn, "data": data}, exec_locals)
        plot_buffer = io.BytesIO()
        plt.savefig(plot_buffer, format='png')
        plt.close()
        return plot_buffer
    except Exception as e:
        st.error(f"Error in executing the generated code: {str(e)}")
        return None



def show_assistant_message(message):
    answer = message.parts[0].text.split("#ANSWER#")[1].split("#CODE#")[0].strip()
    code = message.parts[0].text.split("#CODE#")[1].strip()
    if code.startswith('```python'):
        code = code[9:-3]
    if code.startswith('nocode'):
        code = ''

    st.chat_message("assistant").write(answer)
    if code:
        exec_chart_code(code, data)
        

genai.configure(api_key="AIzaSyDRlwiOh459hntINFtVRz_tWSTQDOmRkxs")
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

st.markdown("<h1 style='text-align: left; font-size: 48px;'>📊 Insightify</h1>", unsafe_allow_html=True)


uploaded_file = st.file_uploader("Upload your dataset (CSV format)", type=["csv"])

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    print(data.head().to_string())
    st.write("Here's a preview of your dataset:", data.head())

    st.write("### Chat Section")

    
    # history
    for message in st.session_state.messages:
        if hasattr(message, 'role') and message.role == 'model':
            show_assistant_message(message)
        elif message['role'] == 'user':
            show_user_message(message)

    if not st.session_state.first_run:
        st.session_state.first_run = True
        first_message = [
            {
                'role': 'user',
                'parts': [prepend_prompt_format("Tell me few lines about the dataset and then Show 4 visualization in a single plot that will be the most relevant for this dataset (let them all be of different chart type like scatterplot, histogram, boxplot, etc)", data)]
            }]
        
        response = model.generate_content(
            first_message
        )
        st.session_state.messages.append(response.candidates[0].content)    
        show_assistant_message(st.session_state.messages[-1])
        

    prompt = st.chat_input("Describe the visualization you want (e.g., 'scatter plot of age vs. income')")

  
    if prompt:

        st.session_state.messages.append(
            {
                'role': "user",
                'parts': [prompt]
            }
        )

        show_user_message(st.session_state.messages[-1])

        conversation = []

        for message in st.session_state.messages:
            if hasattr(message, 'role') and message.role == 'model':
                conversation.append(message)
            elif message['role'] == 'user':
                conversation.append({
                    'role': 'user',
                    'parts': [prepend_prompt_format(message['parts'][0], data)]
                })


        response = model.generate_content(
            conversation
        )

        
        st.session_state.messages.append(response.candidates[0].content)

        show_assistant_message(st.session_state.messages[-1])
        
