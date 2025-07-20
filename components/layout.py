# components/layout.py

import streamlit as st
from streamlit.components.v1 import html

def render_app():
    st.set_page_config(page_title="Legal AI Chatbot", layout="centered", initial_sidebar_state="auto")

    # Custom CSS for better look
    st.markdown("""
        <style>
        .stChatMessage { padding: 0.5rem 1rem; border-radius: 1rem; margin-bottom: 1rem; }
        .stChatMessage.user { background-color: #f0f0f5; text-align: right; }
        .stChatMessage.assistant { background-color: #e7f3ec; text-align: left; }
        .stTextInput>div>div>input {
            border-radius: 0.5rem;
            padding: 0.8rem;
            font-size: 1rem;
        }
        .stButton>button {
            background-color: #007B83;
            color: white;
            border-radius: 0.5rem;
            padding: 0.6rem 1.2rem;
            font-size: 0.95rem;
        }
        .css-18e3th9 { padding-top: 1rem !important; }
        </style>
    """, unsafe_allow_html=True)

    st.sidebar.title("📚 Legal Support AI")
    st.sidebar.info("هذا المساعد القانوني يساعدك في فهم الأنظمة السعودية بطريقة واضحة.")


def chat_message(role, content):
    css_class = "user" if role == "user" else "assistant"
    st.markdown(f'<div class="stChatMessage {css_class}">{content}</div>', unsafe_allow_html=True)