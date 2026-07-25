import streamlit as st
from utils.ai_client import ask_ai_json
from utils.prompts import WRITING_TASK1_PROMPT, WRITING_TASK2_PROMPT, WRITING_SCORING_PROMPT
from utils.storage import add_record

st.title("✍️ IELTS Writing Practice")

task_choice = st.radio("Which task do you want to practice?", ["Task 1 (Report/Chart)", "Task 2 (Essay)"], horizontal=True)

if "writing_prompt" not in st.session_state:
    st.session_state.writing_prompt = None
if "writing_result" not in st.session_state:
    st.session_state.writing_result = None

if st.button("🎲 Generate a new prompt", type="primary"):
    with st.spinner("Writing your prompt..."):
        if task_choice.startswith("Task 1"):
            data = ask_ai_json(WRITING_TASK1_PROMPT, "Generate a new Task 1 prompt now.")
        else:
            data = ask_ai_json(WRITING_TASK2_PROMPT, "Generate a new Task 2 prompt now.")
        st.session_state.writing_prompt = data.get("prompt", "")
        st.session_state.writing_result = None

if st.session_state.writing_prompt:
    st.subheader("Your Prompt")
    st.info(st.session_state.writing_prompt)

    min_words = 150 if task_choice.startswith("Task 1") else 250
    essay = st.text_area(
        f"Write your response here (aim for at least {min_words} words):",
        height=300,
        key="writing_essay",
    )
    word_count = len(essay.split())
    st.caption(f"Word count: {word_count}")

    if st.button("✅ Submit for scoring"):
        if word_count < 30:
            st.warning("Please write a fuller response before submitting.")
        else:
            with st.spinner("Your examiner is reading your response..."):
                scoring_input = f"Task prompt:\n{st.session_state.writing_prompt}\n\nStudent's response:\n{essay}"
                result = ask_ai_json(WRITING_SCORING_PROMPT, scoring_input)
                st.session_state.writing_result = result
                if result.get("overall_band"):
                    add_record("Writing", result["overall_band"], task_choice)

if st.session_state.writing_result:
    r = st.session_state.writing_result
    st.divider()
    st.subheader(f"🎯 Overall Band: {r.get('overall_band', '—')}")
    st.write(r.get("summary", ""))

    st.write("")
    cols = st.columns(2)
    criteria = [
        ("Task Achievement", "task_achievement"),
        ("Coherence & Cohesion", "coherence_cohesion"),
        ("Lexical Resource", "lexical_resource"),
        ("Grammar", "grammar"),
    ]
    for i, (label, key) in enumerate(criteria):
        c = r.get(key, {})
        with cols[i % 2]:
            st.metric(label, c.get("score", "—"))
            st.caption(c.get("feedback", ""))
