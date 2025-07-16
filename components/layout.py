import streamlit as st

def render_app():
    # Inject external CSS
    with open("Style/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Main UI structure and core components    
    st.set_page_config(page_title="Law System", layout="wide")
    st.title("Hello to My Law Swstem")
    st.markdown("---")
def render_form():
    with st.form("respon.form"):
        user_name = st.text_input("Enter your name", max_chars=32)
        user_question=st.text_input("Enter Your Question", max_chars=1000)
        submit=st.form_submit_button("Generate Respone")
        if submit :
            if user_name.strip() == ""  or user_question.strip() == ""  :
                st.warning("Please Fill all the fields")
            else:
                st.success("Question sent succesfuly")
                return user_name, user_question
    return None, None

def render_final_answer(response: str):
    if response:
        st.subheader("📜 الإجابة النهائية:")
        st.markdown("---")
        with st.chat_message("ai"):
            st.markdown(response)
        st.markdown("---")

    # def file_aleart():
    #     if havefile:
    #         st.text(st.session_state.fileuse)
    #     else:
    #         st.text(st.session_state.fileuse)
    # havefile = st.checkbox("checkbox", value=True , on_change=file_aleart, key="fileuse")
    # field = st.selectbox(" choose the field you want", options=("Labor and Employment","E-Commerce","Traffic Regulations","Other"))
    # st.text_area("Please Enter Your Question", max_chars=1000)
    # attechments = st.file_uploader("Please Upload the Knowlage Bace", type=["pdf","jpg","png"], accept_multiple_files=True)
    # responButton = st.button("I'm cute button")

    


