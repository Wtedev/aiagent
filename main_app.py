import streamlit as st
st.set_page_config(page_title="قانونيد - المنصة الذكية", layout="wide")
st.markdown("""
    <style>
    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
    }
    </style>
""", unsafe_allow_html=True)
if "page" not in st.session_state:
    st.session_state.page = "main"

# ----------------------------
# ✅ Top Header + Style
# ----------------------------
st.markdown("""
<style>
.navbar {
    background-color: #27DDDF;
    padding: 1rem 2rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    color: white;
    text-align: center;
    font-size: 24px;
    font-weight: bold;
}
.stButton>button {
    width: 100%;
    background-color: #27DDDF;
    color: white;
    font-size: 20px;
    padding: 0.75rem;
    border: none;
    border-radius: 0.5rem;
}
.divider {
    border-top: 1px solid #ccc;
    margin: 1.2rem 0;
}
.feature-box {
    background-color: #f9f9f9;
    border: 1px solid #eee;
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
}
</style>
<div class="navbar">⚖️ قانونيد - المنصة الذكية للاستشارات القانونية</div>
""", unsafe_allow_html=True)

# ----------------------------
# ✅ Main Page Content
# ----------------------------
if st.session_state.page == "main":

    # لماذا قانونيد؟
    st.subheader("✨ لماذا قانونيد؟")
    st.markdown("""
    - 🤖 يعتمد على الذكاء الاصطناعي لتحليل القضايا بدقة.
    - 📚 مستند إلى الأنظمة السعودية الرسمية والمصادر القضائية.
    - 🧠 يقدم إجابات موثوقة ويولد قوالب قانونية قابلة للتخصيص.
    - 🛠️ أدوات ذكية مثل التحقق من المستندات وإصدار أحكام افتراضية.
    """)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.subheader("🔹 اختر خدمة:")

    # --- Service: Legal Q&A ---
    st.markdown("""
    <div class="feature-box">
    <strong>🧾 إجابة عن الأسئلة القانونية</strong><br>
    اطرح أي سؤال قانوني واحصل على إجابة دقيقة مبنية على الأنظمة الرسمية السعودية.
    </div>
    """, unsafe_allow_html=True)
    if st.button("استخدم الميزة", key="chat"):
        st.session_state.page = "chat"
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # --- Service: Virtual Ruling ---
    st.markdown("""
    <div class="feature-box">
    <strong>🧠 إصدار حكم افتراضي لقضيتك</strong><br>
    أدخل ملخص قضيتك، وسينشئ النظام حكمًا افتراضيًا مشابهًا للأحكام القضائية الحقيقية.
    </div>
    """, unsafe_allow_html=True)
    if st.button("استخدم الميزة", key="virtual"):
        st.session_state.page = "virtual"
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # --- Service: Smart Contracts ---
    st.markdown("""
    <div class="feature-box">
    <strong>📄 قوالب عقود ذكية</strong><br>
    أنشئ عقدك القانوني بسهولة من خلال قوالب جاهزة قابلة للتخصيص حسب حاجتك.
    </div>
    """, unsafe_allow_html=True)
    if st.button("استخدم الميزة", key="contracts"):
        st.session_state.page = "contracts"
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # --- Service: Document Check ---
    st.markdown("""
    <div class="feature-box">
    <strong>🕵️‍♂️ التحقق من صحة المستندات</strong><br>
    حمّل مستنداتك وتحقق من مطابقتها للأنظمة السعودية من خلال الذكاء الاصطناعي.
    </div>
    """, unsafe_allow_html=True)
    if st.button("استخدم الميزة", key="verify"):
        st.session_state.page = "doc_verification"

# ----------------------------
# ✅ Routing Logic
# ----------------------------
def show_placeholder(title):
    st.title(title)
    st.warning("🚧 هذه الصفحة قيد التطوير.")
    st.button("🔙 العودة للرئيسية", on_click=lambda: st.session_state.update({"page": "main"}))

if st.session_state.page == "chat":
    show_placeholder("🧠 الاجابه")

    
elif st.session_state.page == "virtual":
    show_placeholder("🧠 إصدار حكم افتراضي")

elif st.session_state.page == "contracts":
    show_placeholder("📄 قوالب عقود ذكية")

elif st.session_state.page == "doc_verification":
    show_placeholder("🕵️‍♂️ التحقق من صحة المستندات")


# ----------------- 🔒 Disclaimer -----------------
st.markdown("""---""")
st.markdown("""
<div class='disclaimer'>
🔒 هذا الرد مقدم من نظام ذكي ولا يغني عن استشارة محامٍ مرخص.
</div>
""", unsafe_allow_html=True)