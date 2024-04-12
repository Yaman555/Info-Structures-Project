import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai
from PyPDF2 import PdfReader
import requests
from collections import deque  
from langchain.text_splitter import RecursiveCharacterTextSplitter
import io

load_dotenv()

st.set_page_config(
    page_title="Chat with Gemini-Pro!",
    page_icon="🤖",  
    layout="centered",  
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

gen_ai.configure(api_key=GOOGLE_API_KEY)
model = gen_ai.GenerativeModel('gemini-pro')

chat_history = deque(maxlen=100)  

def translate_role_for_streamlit(user_role):
    if user_role == "model":
        return "assistant"
    else:
        return user_role


def extract_text_from_pdf(uploaded_file):
    text = ""
    if uploaded_file is not None:
        file_content = uploaded_file.read() 
        reader = PdfReader(io.BytesIO(file_content))
        for page in reader.pages:
            text += page.extract_text()
    return text.strip()


def chunk_text(text, chunk_size=10000):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i+chunk_size])
    return chunks


def download_and_extract_pdf_text(url):
    response = requests.get(url)
    if response.status_code == 200:
        with io.BytesIO(response.content) as f:
            reader = PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text.strip()
    else:
        st.error(f"Failed to download PDF from URL: {url}")
        return None

background_color = "#abdbe3" 


container_style = f"background-color: {background_color}; padding: 1rem; border-radius: 10px;"

st.title("🤖 Gemini Pro - ChatBot")
st.markdown(
    f"""
    <div style="{container_style}">
    """,
    unsafe_allow_html=True
)


if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

try:
    for message in st.session_state.chat_session.history:
        with st.chat_message(translate_role_for_streamlit(message.role)):
            st.markdown(message.parts[0].text)
except gen_ai.exceptions.StopCandidateException as e:
   
    st.session_state.chat_session = model.start_chat(history=[])


user_prompt = st.chat_input("Ask Gemini-Pro...")


uploaded_file = st.file_uploader("Upload PDF file", type=["pdf"])

pdf_url = st.text_input("Paste URL of a PDF file")

if user_prompt:
    
    st.chat_message("user").markdown(user_prompt)
    chat_history.append({'role': 'user', 'text': user_prompt})
    
    
    gemini_response = st.session_state.chat_session.send_message(user_prompt)

    with st.chat_message("assistant"):
        st.markdown(gemini_response.text)
        chat_history.append({'role': 'model', 'text': gemini_response.text})

elif uploaded_file:
   
    uploaded_text = extract_text_from_pdf(uploaded_file)
    if uploaded_text:

        text_chunks = chunk_text(uploaded_text)

        for chunk in text_chunks:
            gemini_response = st.session_state.chat_session.send_message(chunk)

            
            with st.chat_message("assistant"):
                st.markdown(gemini_response.text)
                chat_history.append({'role': 'model', 'text': gemini_response.text})

elif pdf_url:
    
    uploaded_text_from_url = download_and_extract_pdf_text(pdf_url)
    if uploaded_text_from_url:
        text_chunks = chunk_text(uploaded_text_from_url)

        for chunk in text_chunks:
            gemini_response = st.session_state.chat_session.send_message(chunk)

            with st.chat_message("assistant"):
                st.markdown(gemini_response.text)
                chat_history.append({'role': 'model', 'text': gemini_response.text})

st.markdown("</div>", unsafe_allow_html=True)


