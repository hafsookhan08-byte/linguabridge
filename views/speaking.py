import streamlit as st
from utils.ai_client import ask_ai, ask_ai_json
from utils.prompts import SPEAKING_EXAMINER_PROMPT, SPEAKING_FEEDBACK_PROMPT
from utils.storage import add_record

st.title("🗣️ IELTS Speaking Mock Interview")
st.caption("A full 3-part interview with an AI examiner. Type your answers just like you'd speak them.")

if "speaking_history" not in st.session_state:
    st.session_state.speaking_history = []
if "speaking_finished" not in st.session_state:
    st.session_state.speaking_finished = False
if "speaking_feedback" not in st.session_state:
    st.session_state.speaking_feedback = None


def start_interview():
    st.session_state.speaking_history = []
    st.session_state.speaking_finished = False
    st.session_state.speaking_feedback = None
    reply = ask_ai(SPEAKING_EXAMINER_PROMPT, "Begin the interview with Part 1, question 1.")
    st.session_state.speaking_history.append({"role": "examiner", "text": reply})


col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🎬 Start new interview", type="primary"):
        with st.spinner("Your examiner is getting ready..."):
            start_interview()
with col2:
    if st.session_state.speaking_history and not st.session_state.speaking_finished:
        if st.button("🏁 End interview & get feedback"):
            with st.spinner("Scoring your interview..."):
                transcript = "\n".join(
                    f"{'Examiner' if h['role'] == 'examiner' else 'Student'}: {h['text']}"
                    for h in st.session_state.speaking_history
                )
                feedback = ask_ai_json(SPEAKING_FEEDBACK_PROMPT, transcript)
                st.session_state.speaking_feedback = feedback
                st.session_state.speaking_finished = True
                if feedback.get("overall_band"):
                    add_record("Speaking", feedback["overall_band"], "Mock interview")

st.divider()

for h in st.session_state.speaking_history:
    if h["role"] == "examiner":
        st.markdown(f"🧑‍🏫 **Examiner:** {h['text']}")
    else:
        st.markdown(f"🗣️ **You:** {h['text']}")
    st.write("")

if st.session_state.speaking_history and not st.session_state.speaking_finished:
    user_reply = st.text_area("Your answer:", key="speaking_input", height=100)
    if st.button("Send answer"):
        if user_reply.strip():
            st.session_state.speaking_history.append({"role": "student", "text": user_reply})
            transcript_so_far = "\n".join(
                f"{'Examiner' if h['role'] == 'examiner' else 'Student'}: {h['text']}"
                for h in st.session_state.speaking_history
            )
            with st.spinner("Examiner is thinking..."):
                reply = ask_ai(SPEAKING_EXAMINER_PROMPT, transcript_so_far + "\n\nContinue the interview with your next line.")
            st.session_state.speaking_history.append({"role": "examiner", "text": reply})
            st.rerun()

if st.session_state.speaking_feedback:
    f = st.session_state.speaking_feedback
    st.divider()
    st.subheader(f"🎯 Overall Band: {f.get('overall_band', '—')}")

    cols = st.columns(3)
    parts = [
        ("Fluency & Coherence", "fluency_coherence"),
        ("Lexical Resource", "lexical_resource"),
        ("Grammar", "grammar"),
    ]
    for i, (label, key) in enumerate(parts):
        c = f.get(key, {})
        with cols[i]:
            st.metric(label, c.get("score", "—"))
            st.caption(c.get("feedback", ""))

    if f.get("pronunciation_note"):
        st.caption(f"🔊 {f['pronunciation_note']}")

    if f.get("common_mistakes"):
        st.subheader("Common Mistakes to Fix")
        for m in f["common_mistakes"]:
            st.markdown(f"❌ *{m.get('mistake', '')}* → ✅ **{m.get('correction', '')}**")
            st.caption(m.get("explanation", ""))
            st.write("")

if not st.session_state.speaking_history:
    st.info("Click **Start new interview** to begin your mock IELTS Speaking test.")
