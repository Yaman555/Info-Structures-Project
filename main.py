import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai
from PyPDF2 import PdfReader
from collections import deque  
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

# Configure Streamlit page settings
st.set_page_config(
    page_title="Chat with Gemini-Pro!",
    page_icon="🤖",  
    layout="centered",  
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Set up Google Gemini-Pro AI model
gen_ai.configure(api_key=GOOGLE_API_KEY)
model = gen_ai.GenerativeModel('gemini-pro')

# Initialize deque for chat history
chat_history = deque(maxlen=100)  # Set a maximum length to avoid unbounded growth

# Function to translate roles between Gemini-Pro and Streamlit terminology
def translate_role_for_streamlit(user_role):
    if user_role == "model":
        return "assistant"
    else:
        return user_role


# Function to extract text from uploaded PDF file
def extract_text_from_pdf(uploaded_file):
    text = ""
    if uploaded_file is not None:
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            text += page.extract_text()
    return text.strip()

# Set the background color
background_color = "#abdbe3" 

# Define CSS styles for the container
container_style = f"background-color: {background_color}; padding: 1rem; border-radius: 10px;"

st.title("🤖 Gemini Pro - ChatBot")
st.markdown(
    f"""
    <div style="{container_style}">
    """,
    unsafe_allow_html=True
)

# Initialize chat session in Streamlit if not already present
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Display the chat history
try:
    for message in st.session_state.chat_session.history:
        with st.chat_message(translate_role_for_streamlit(message.role)):
            st.markdown(message.parts[0].text)
except gen_ai.exceptions.StopCandidateException as e:
    # Reset the chat session if it reaches a stopping point
    st.session_state.chat_session = model.start_chat(history=[])

# Input field for user's message
user_prompt = st.chat_input("Ask Gemini-Pro...")

# Check if the user has uploaded a PDF file
uploaded_file = st.file_uploader("Upload PDF file", type=["pdf"])

if user_prompt or uploaded_file:
    if user_prompt:
        # Add user's message to chat and display it
        st.chat_message("user").markdown(user_prompt)
        chat_history.append({'role': 'user', 'text': user_prompt})
    else:
        # Extract text from the uploaded PDF file
        uploaded_text = extract_text_from_pdf(uploaded_file)
        if uploaded_text:
            # Add user's uploaded text to chat and display it
            st.chat_message("user").markdown(uploaded_text)
            chat_history.append({'role': 'user', 'text': uploaded_text})

    # Send user's message to Gemini-Pro and get the response
    gemini_response = st.session_state.chat_session.send_message(user_prompt if user_prompt else uploaded_text)

    # Display Gemini-Pro's response
    with st.chat_message("assistant"):
        st.markdown(gemini_response.text)
        chat_history.append({'role': 'model', 'text': gemini_response.text})

# Close the container
st.markdown("</div>", unsafe_allow_html=True)
