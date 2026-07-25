import streamlit as st
from utils.ai_client import ask_ai, ask_ai_json
from utils.prompts import (
    LANGUAGE_LESSON_PROMPT,
    LANGUAGE_LESSON_FEEDBACK_PROMPT,
    LANGUAGE_COACH_SYSTEM_PROMPT,
)
from utils.storage import add_record

st.title("🌍 Language Coach")
st.caption("Learn a language from scratch, or practice real conversations for life abroad.")

LEARNABLE_LANGUAGES = [
    "Arabic", "German", "Urdu", "English", "Hindi", "French",
    "Spanish", "Chinese (Mandarin)", "Turkish", "Japanese", "Korean", "Italian",
]

LEVELS = [
    ("Level 1", "Alphabet & Pronunciation", "Learning the letters/script and how they sound"),
    ("Level 2", "Greetings & Basic Phrases", "Hello, goodbye, please, thank you, introducing yourself"),
    ("Level 3", "Numbers, Colors & Common Words", "Counting, colors, everyday objects"),
    ("Level 4", "Simple Sentences & Grammar Basics", "Building basic sentences, simple present tense"),
    ("Level 5", "Everyday Conversations", "Ordering food, asking directions, shopping"),
    ("Level 6", "Advanced Fluency & Idioms", "Natural expressions, idioms, more complex grammar"),
]

tab_learn, tab_practice = st.tabs(["📘 Learn a Language", "💬 Practice Conversation"])

# ---------------------------------------------------------------------
# TAB 1: Structured learning curriculum
# ---------------------------------------------------------------------
with tab_learn:
    st.subheader("Choose a language to learn")
    col1, col2 = st.columns(2)
    with col1:
        learn_language = st.selectbox("Which language?", LEARNABLE_LANGUAGES, key="learn_lang")
    with col2:
        level_labels = [f"{code} — {name}" for code, name, desc in LEVELS]
        level_choice = st.selectbox("Which level?", level_labels, key="learn_level")

    level_index = level_labels.index(level_choice)
    level_code, level_name, level_desc = LEVELS[level_index]

    if "lesson_data" not in st.session_state:
        st.session_state.lesson_data = None
    if "lesson_submitted" not in st.session_state:
        st.session_state.lesson_submitted = False

    if st.button("📖 Generate today's lesson", type="primary"):
        with st.spinner(f"Preparing your {learn_language} lesson..."):
            prompt = LANGUAGE_LESSON_PROMPT.format(
                language=learn_language, level_name=level_name, level_description=level_desc
            )
            st.session_state.lesson_data = ask_ai_json(prompt, f"Generate the {level_name} lesson now.")
            st.session_state.lesson_submitted = False

    data = st.session_state.lesson_data

    if data and "lesson_title" in data:
        st.divider()
        st.subheader(f"📝 {data['lesson_title']}")
        st.write(data.get("explanation", ""))

        if data.get("vocabulary"):
            st.write("**Vocabulary:**")
            for v in data["vocabulary"]:
                st.markdown(f"- **{v.get('word','')}** _(pronounced: {v.get('pronunciation','')})_ — {v.get('meaning','')}")

        if data.get("example_sentences"):
            st.write("**Example sentences:**")
            for s in data["example_sentences"]:
                st.markdown(f"- *{s.get('sentence','')}* — {s.get('translation','')}")

        st.divider()
        st.subheader("Practice")

        answers = {}
        for q in data.get("practice_questions", []):
            st.write(f"**{q['id']}. {q['question']}**")
            if q["type"] == "multiple_choice":
                answers[q["id"]] = st.radio("Choose one:", q["options"], key=f"lesson_{q['id']}", label_visibility="collapsed")
            else:
                answers[q["id"]] = st.text_input("Your answer:", key=f"lesson_{q['id']}", label_visibility="collapsed")
            st.write("")

        if st.button("✅ Check my answers"):
            with st.spinner("Checking..."):
                correct_count = 0
                summary_lines = []
                for q in data.get("practice_questions", []):
                    given = answers.get(q["id"], "")
                    summary_lines.append(f"Q{q['id']}: {q['question']} | Correct: {q['answer']} | Student: {given}")
                    if str(given).strip().lower() == str(q["answer"]).strip().lower():
                        correct_count += 1

                feedback_prompt = LANGUAGE_LESSON_FEEDBACK_PROMPT.format(language=learn_language)
                feedback = ask_ai(feedback_prompt, "\n".join(summary_lines))

                total = len(data.get("practice_questions", []))
                st.session_state.lesson_submitted = True
                st.session_state.lesson_score_text = f"{correct_count}/{total}"
                st.session_state.lesson_feedback = feedback

                approx_score = round(min(9, 4 + (correct_count / max(total, 1)) * 5), 1)
                add_record("Language Learning", approx_score, f"{learn_language} — {level_name}: {correct_count}/{total}")

        if st.session_state.lesson_submitted:
            st.success(f"Score: {st.session_state.lesson_score_text}")
            st.write(st.session_state.lesson_feedback)
    else:
        st.info("Pick a language and level above, then click **Generate today's lesson**.")

# ---------------------------------------------------------------------
# TAB 2: Free conversation practice (destination-focused)
# ---------------------------------------------------------------------
with tab_practice:
    DEST_LANGUAGES = {
        "United Kingdom": "English (British)",
        "Canada": "English (Canadian) / French",
        "Germany": "German",
        "France": "French",
        "Italy": "Italian",
        "Spain": "Spanish",
        "China": "Mandarin Chinese",
        "Turkey": "Turkish",
        "Japan": "Japanese",
        "South Korea": "Korean",
    }

    SCENARIOS = [
        "Renting a flat / talking to a landlord",
        "Ordering food at a restaurant",
        "Meeting classmates on your first day",
        "Opening a bank account",
        "Asking for directions",
        "Talking to a doctor about feeling unwell",
        "Small talk at a part-time job",
    ]

    st.subheader("Practice a real-life conversation")
    col1, col2 = st.columns(2)
    with col1:
        country = st.selectbox("Where are you moving to?", list(DEST_LANGUAGES.keys()), key="coach_country")
    with col2:
        scenario = st.selectbox("Pick a scenario to practice:", SCENARIOS, key="coach_scenario")

    language = DEST_LANGUAGES[country]

    if "coach_history" not in st.session_state:
        st.session_state.coach_history = []

    if st.button("🎬 Start conversation", type="primary", key="coach_start"):
        st.session_state.coach_history = []
        system_prompt = LANGUAGE_COACH_SYSTEM_PROMPT.format(language=language, country=country, scenario=scenario)
        with st.spinner("Getting into character..."):
            opener = ask_ai(system_prompt, "Start the conversation naturally with your opening line.")
        st.session_state.coach_history.append({"role": "coach", "text": opener})
        st.session_state.coach_system_prompt = system_prompt

    st.divider()

    for h in st.session_state.coach_history:
        if h["role"] == "coach":
            st.markdown(f"🌍 **Coach:** {h['text']}")
        else:
            st.markdown(f"🗣️ **You:** {h['text']}")
        st.write("")

    if st.session_state.coach_history:
        user_msg = st.text_input("Type your reply (try it in the target language!):", key="coach_input")
        if st.button("Send", key="coach_send"):
            if user_msg.strip():
                st.session_state.coach_history.append({"role": "student", "text": user_msg})
                transcript = "\n".join(
                    f"{'Coach' if h['role'] == 'coach' else 'Student'}: {h['text']}"
                    for h in st.session_state.coach_history
                )
                with st.spinner("..."):
                    reply = ask_ai(st.session_state.coach_system_prompt, transcript + "\n\nContinue naturally with your next line.")
                st.session_state.coach_history.append({"role": "coach", "text": reply})
                st.rerun()
    else:
        st.info("Pick a country and scenario, then click **Start conversation**.")
