import streamlit as st
def render_sidebar():
    # Inject external CSS
    with open("Style/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    st.sidebar.write("hello")
    