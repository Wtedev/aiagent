import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.markdown("## 🧠 حول المشروع")
        st.markdown("تم تطوير هذا النظام لتقديم استشارات قانونية دقيقة بناءً على النصوص النظامية السعودية.")
        st.markdown("### 📚 مصادر القوانين:")
        st.markdown("- وزارة العدل\n- ديوان المظالم\n- الهيئة العامة للعقار وغيرها")