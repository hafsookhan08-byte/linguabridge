import streamlit as st
from utils.ai_client import ask_ai_json, ask_ai
from utils.prompts import READING_GENERATOR_PROMPT, READING_FEEDBACK_PROMPT
from utils.storage import add_record

st.title("📖 IELTS Reading Practice")
st.caption("A fresh passage and question set every time you click Generate.")

if "reading_data" not in st.session_state:
    st.session_state.reading_data = None
if "reading_submitted" not in st.session_state:
    st.session_state.reading_submitted = False

if st.button("🎲 Generate a new passage", type="primary"):
    with st.spinner("Writing your passage..."):
        st.session_state.reading_data = ask_ai_json(READING_GENERATOR_PROMPT, "Generate a new IELTS reading passage now.")
        st.session_state.reading_submitted = False

data = st.session_state.reading_data

if data and "passage" in data:
    st.subheader(data.get("title", "Reading Passage"))
    st.write(data["passage"])
    st.divider()
    st.subheader("Questions")

    answers = {}
    for q in data.get("questions", []):
        st.write(f"**{q['id']}. {q['question']}**")
        if q["type"] == "multiple_choice":
            answers[q["id"]] = st.radio("Choose one:", q["options"], key=f"r_{q['id']}", label_visibility="collapsed")
        elif q["type"] == "true_false_not_given":
            answers[q["id"]] = st.radio("Choose one:", ["True", "False", "Not Given"], key=f"r_{q['id']}", label_visibility="collapsed")
        else:
            answers[q["id"]] = st.text_input("Your answer:", key=f"r_{q['id']}", label_visibility="collapsed")
        st.write("")

    if st.button("✅ Submit answers"):
        with st.spinner("Checking your answers..."):
            correct_count = 0
            summary_lines = []
            for q in data.get("questions", []):
                given = answers.get(q["id"], "")
                summary_lines.append(f"Q{q['id']}: {q['question']} | Correct answer: {q['answer']} | Student answer: {given}")
                if str(given).strip().lower().startswith(str(q["answer"]).strip().lower()[0:3]):
                    correct_count += 1

            feedback_input = (
                f"Passage:\n{data['passage']}\n\n"
                f"Questions and answers:\n" + "\n".join(summary_lines)
            )
            feedback = ask_ai(READING_FEEDBACK_PROMPT, feedback_input)

            score_out_of = len(data.get("questions", []))
            st.session_state.reading_submitted = True
            st.session_state.reading_score_text = f"{correct_count}/{score_out_of}"
            st.session_state.reading_feedback = feedback

            approx_band = round(min(9, 4 + (correct_count / max(score_out_of, 1)) * 5), 1)
            add_record("Reading", approx_band, f"{correct_count}/{score_out_of} correct")

    if st.session_state.reading_submitted:
        st.divider()
        st.success(f"Score: {st.session_state.reading_score_text}")
        st.subheader("Detailed Feedback")
        st.write(st.session_state.reading_feedback)
else:
    st.info("Click **Generate a new passage** above to get started.")
