import streamlit as st
from utils.storage import get_records

st.markdown(
    """
    <style>
    .big-title { font-size: 2.8rem; font-weight: 800; margin-bottom: 0; }
    .subtitle { font-size: 1.1rem; opacity: 0.85; margin-top: 0.3rem; margin-bottom: 1.5rem; }
    .feature-card {
        background-color: #132A4E;
        border-radius: 16px;
        padding: 1.3rem 1.4rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(233, 180, 76, 0.25);
        height: 100%;
    }
    .feature-card:hover { border: 1px solid #E9B44C; }
    .feature-icon { font-size: 2.2rem; }
    .feature-card h4 { margin: 0.4rem 0 0.4rem 0; }
    .feature-card p { margin: 0 0 0.8rem 0; opacity: 0.85; font-size: 0.92rem; min-height: 65px; }
    .stat-box {
        background-color: #132A4E;
        border-radius: 14px;
        padding: 1rem;
        text-align: center;
        border-top: 3px solid #E9B44C;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<p class="big-title">🌉 LinguaBridge</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Your bridge from home to study abroad — '
    "master IELTS, and the language of the country you're moving to.</p>",
    unsafe_allow_html=True,
)

if "student_name" not in st.session_state:
    st.session_state.student_name = ""

name = st.text_input("👋 What's your name?", value=st.session_state.student_name, placeholder="e.g. Hafsa")
st.session_state.student_name = name

if name:
    st.success(f"Welcome back, **{name}**! Ready to practice today?")

st.write("")
st.subheader("Choose where to start")

sections = [
    ("📖", "Reading", "Fresh IELTS passages every time, with real question types and detailed explanations.", "reading"),
    ("🎧", "Listening", "AI-generated audio clips with comprehension questions — just like the real test.", "listening"),
    ("✍️", "Writing", "Real Task 1 & 2 prompts, scored against the 4 official IELTS band criteria.", "writing"),
    ("🗣️", "Speaking", "A full mock interview with an AI examiner, plus a real band-score breakdown.", "speaking"),
    ("🌍", "Language Coach", "Practice real conversations for life abroad — renting, ordering food, and more.", "language_coach"),
    ("📊", "Progress", "See every band score you've earned, charted over time.", "progress"),
]

cols = st.columns(2)
for i, (icon, title, desc, page_file) in enumerate(sections):
    with cols[i % 2]:
        st.markdown(
            f"""
            <div class="feature-card">
                <div class="feature-icon">{icon}</div>
                <h4>{title}</h4>
                <p>{desc}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(f"views/{page_file}.py", label=f"Go to {title} →", icon=icon)

records = get_records()
if records:
    st.write("")
    st.divider()
    st.subheader("📈 Your stats so far")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="stat-box"><h2>{len(records)}</h2>Practice attempts</div>', unsafe_allow_html=True)
    with c2:
        avg = round(sum(r["band_score"] for r in records) / len(records), 1)
        st.markdown(f'<div class="stat-box"><h2>{avg}</h2>Average band score</div>', unsafe_allow_html=True)
