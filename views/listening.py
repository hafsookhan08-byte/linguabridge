import io
import streamlit as st
from gtts import gTTS
from utils.ai_client import ask_ai_json, ask_ai
from utils.prompts import LISTENING_GENERATOR_PROMPT, LISTENING_FEEDBACK_PROMPT
from utils.storage import add_record

st.title("🎧 IELTS Listening Practice")
st.caption("A real audio clip generated for you — listen, then answer.")

if "listening_data" not in st.session_state:
    st.session_state.listening_data = None
    st.session_state.listening_audio = None
if "listening_submitted" not in st.session_state:
    st.session_state.listening_submitted = False

if st.button("🎲 Generate a new listening clip", type="primary"):
    with st.spinner("Writing the script..."):
        data = ask_ai_json(LISTENING_GENERATOR_PROMPT, "Generate a new IELTS listening scenario now.")
        st.session_state.listening_data = data
        st.session_state.listening_submitted = False

    if data and "script" in data:
        with st.spinner("Recording the audio..."):
            try:
                tts = gTTS(text=data["script"], lang="en")
                buf = io.BytesIO()
                tts.write_to_fp(buf)
                buf.seek(0)
                st.session_state.listening_audio = buf.read()
            except Exception as e:
                st.session_state.listening_audio = None
                st.warning(f"Couldn't generate audio ({e}). You can still read the transcript below.")

data = st.session_state.listening_data

if data and "script" in data:
    st.subheader(data.get("title", "Listening Clip"))

    if st.session_state.listening_audio:
        st.audio(st.session_state.listening_audio, format="audio/mp3")
    with st.expander("📄 Show transcript (try listening first!)"):
        st.write(data["script"])

    st.divider()
    st.subheader("Questions")

    answers = {}
    for q in data.get("questions", []):
        st.write(f"**{q['id']}. {q['question']}**")
        if q["type"] == "multiple_choice":
            answers[q["id"]] = st.radio("Choose one:", q["options"], key=f"l_{q['id']}", label_visibility="collapsed")
        else:
            answers[q["id"]] = st.text_input("Your answer:", key=f"l_{q['id']}", label_visibility="collapsed")
        st.write("")

    if st.button("✅ Submit answers"):
        with st.spinner("Checking your answers..."):
            correct_count = 0
            summary_lines = []
            for q in data.get("questions", []):
                given = answers.get(q["id"], "")
                summary_lines.append(f"Q{q['id']}: {q['question']} | Correct answer: {q['answer']} | Student answer: {given}")
                if str(given).strip().lower() in str(q["answer"]).strip().lower() or str(q["answer"]).strip().lower() in str(given).strip().lower():
                    correct_count += 1

            feedback_input = f"Script:\n{data['script']}\n\nQuestions and answers:\n" + "\n".join(summary_lines)
            feedback = ask_ai(LISTENING_FEEDBACK_PROMPT, feedback_input)

            score_out_of = len(data.get("questions", []))
            st.session_state.listening_submitted = True
            st.session_state.listening_score_text = f"{correct_count}/{score_out_of}"
            st.session_state.listening_feedback = feedback

            approx_band = round(min(9, 4 + (correct_count / max(score_out_of, 1)) * 5), 1)
            add_record("Listening", approx_band, f"{correct_count}/{score_out_of} correct")

    if st.session_state.listening_submitted:
        st.divider()
        st.success(f"Score: {st.session_state.listening_score_text}")
        st.subheader("Detailed Feedback")
        st.write(st.session_state.listening_feedback)
else:
    st.info("Click **Generate a new listening clip** above to get started.")
