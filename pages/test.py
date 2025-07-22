import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.openSdk import load_database, find_matching_cases, generate_final_judgment, agent_phase1, agent_phase2

# ----------------------------
#  Initialize Phase 1 & Phase 2 Models
# ----------------------------
def init_model():
    return {
        "phase1": {"system": agent_phase1},
        "phase2": {"system": agent_phase2}
    }

# ----------------------------
#  Custom CSS for Dark Mode and Gradients
# ----------------------------
def custom_css():
    st.markdown(
        """
        <style>
        body {
            background-color: #0F1117;  /* Dark Background */
            color: #E3E3E3;
            font-family: 'Cairo', sans-serif;
            text-align: center;  /* Center align the text */
            margin: 0;
            padding: 0;
        }

        h1, h2, h3, h4, h5, h6 {
            text-align: center;
            font-size: 3em;
            font-weight: bold;
            color: #00A7A9;
            text-shadow: 0 0 10px rgba(0, 167, 169, 1), 0 0 30px rgba(0, 167, 169, 0.7);
        }

        .stButton button {
            background-color: #00A7A9;
            color: white;
            font-weight: bold;
            border-radius: 12px;
            padding: 12px 25px;
            border: none;
            transition: all 0.3s ease;
        }

        .stButton button:hover {
            background-color: #007C7D;
        }

        .stTextArea textarea {
            background-color: #1E222B;
            color: #E3E3E3;
            border: 2px solid #00A7A9;
            border-radius: 12px;
            padding: 15px;
            font-size: 1.1em;
        }

        
        /* Spinner Customization */
        .stSpinner {
            color: #00A7A9;
        }

        /* Markdown Box Styling */
        .stMarkdown {
            background-color: #1E222B;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }

        .stSubtitle, .stSubheader {
            color: #00A7A9;
        }
        </style>
        """, unsafe_allow_html=True)

# ----------------------------
#  Virtual Ruling Page UI
# ----------------------------
def app():
    # Apply Custom CSS
    custom_css()

    st.title("🧠 القاضي الافتراضي")

    case_input_text = st.text_area("الرجاء ادخال وصف القضية", height=450)

    if st.button("تحليل القضية"):
        if not case_input_text.strip():
            st.warning("الرجاء ادخال وصف القضية اولا.")
        else:
            model = init_model()
            database = load_database()

            # ----------------------------
            #  Search for Similar Cases
            # ----------------------------
            with st.spinner("🔄 البحث عن قضايا مشابهة..."):
                matched_cases = find_matching_cases(model["phase1"], database, case_input_text)

            with st.expander("🔍 القضايا المتشابهة"):
                if matched_cases:
                    for case in matched_cases:
                        st.markdown(f"- 🆔 **الرقم التسلسلي:** {case.get('case_id', 'N/A')}")
                        st.markdown(f"  - 🔹 اوجة التشابه: {case.get('PointOfSimilarity', 'N/A')}")
                else:
                    st.info("لا توجد قضايا مشابهة.")

            # ----------------------------
            #  Generate Final Judgment based on Similar Cases
            # ----------------------------
            with st.spinner("⏳ انشاء الحكم النهائي..."):
                case_input = {"description": case_input_text.strip()}
                judgment = generate_final_judgment(model["phase2"], case_input, matched_cases)

            if judgment:
                with st.expander("📚 نظرة عامة"):
                    for scase in judgment.get("similar_cases", []):
                        st.markdown(f"- 🆔 **الرقم التسلسلي:** {scase.get('case_id', 'N/A')}")
                        st.markdown(f"  - 📝 نبذة: {scase.get('summary', '')}")

                with st.expander("🧠 أساس الحكم"):
                    st.markdown(judgment.get("Source", "No explanation available."))

                with st.expander("📖 الحكم النهائي"):
                    judgment_text = judgment.get("predicted_judgment", "No judgment generated.")
                    st.markdown(
                        f"<div style='direction: rtl; font-size: 16px; line-height: 1.5; text-align: justify; margin-top: 1em;'>{judgment_text}</div>",
                        unsafe_allow_html=True
                    )

            else:
                st.error("❌ Failed to generate judgment. Please check your internet connection and API key.")

# ----------------------------
#  Run app only if this is the main file
# ----------------------------
if __name__ == "__main__":
    app()



