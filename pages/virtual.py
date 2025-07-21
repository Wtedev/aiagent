import streamlit as st
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
#  Virtual Ruling Page UI
# ----------------------------
def app():
    st.title("🧠 القاضي الافتراضي")

    case_input_text = st.text_area("الرجاء ادخال وصف القضية", height=200)

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

            st.subheader("🔍 القضايا المتشابهة")
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
                # Display similar cases from judgment response if present
                similar_cases = judgment.get("similar_cases", [])
                if similar_cases:
                    st.markdown("### 📚 نظرة عامة")
                    for scase in similar_cases:
                        st.markdown(f"- 🆔 **الرقم التسلسلي:** {scase.get('case_id', 'N/A')}")
                        st.markdown(f"  - 📝 نبذة: {scase.get('summary', '')}")
                    

                # Display explanation/source text
                st.markdown("### 🧠 اساس الحكم")
                st.markdown(judgment.get("Source", "No explanation available."))
                    

                # Display predicted judgment text 
                st.subheader("📖 الحكم النهائي")
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
