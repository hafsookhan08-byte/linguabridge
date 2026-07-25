import streamlit as st

st.set_page_config(
    page_title="LinguaBridge — IELTS & Language Prep",
    page_icon="🌉",
    layout="centered",
)

home = st.Page("views/home.py", title="Home", icon="🏠", default=True)
reading = st.Page("views/reading.py", title="Reading", icon="📖")
listening = st.Page("views/listening.py", title="Listening", icon="🎧")
writing = st.Page("views/writing.py", title="Writing", icon="✍️")
speaking = st.Page("views/speaking.py", title="Speaking", icon="🗣️")
coach = st.Page("views/language_coach.py", title="Language Coach", icon="🌍")
progress = st.Page("views/progress.py", title="Progress", icon="📊")

pg = st.navigation([home, reading, listening, writing, speaking, coach, progress])
pg.run()
