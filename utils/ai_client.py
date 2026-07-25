"""
Central AI client for LinguaBridge.
Every page (Reading, Listening, Writing, Speaking, Language Coach)
calls into this file so the API logic lives in exactly one place.

Uses Groq (https://console.groq.com) — genuinely free tier, no credit
card required, no billing-linked quota issues like some other providers.
"""

import json
import streamlit as st
from groq import Groq

MODEL_NAME = "llama-3.3-70b-versatile"


def _get_api_key():
    """Reads the Groq API key from Streamlit secrets."""
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return None


def _get_client():
    api_key = _get_api_key()
    if not api_key:
        st.error(
            "⚠️ No Groq API key found. Add GROQ_API_KEY to your "
            "`.streamlit/secrets.toml` file (locally) or to your app's "
            "Secrets in Streamlit Cloud settings (when deployed)."
        )
        st.stop()
    return Groq(api_key=api_key)


def ask_ai(system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
    """
    Sends a system prompt + user prompt to the model and returns plain text.
    Used for free-form responses (feedback, conversation replies, etc).
    """
    client = _get_client()
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Something went wrong talking to the AI: {e}"


def ask_ai_json(system_prompt: str, user_prompt: str, temperature: float = 0.7) -> dict:
    """
    Same as ask_ai, but instructs the model to return ONLY valid JSON,
    and parses it into a Python dict. Used for structured things like
    quiz questions and band-score breakdowns.
    """
    client = _get_client()
    strict_instruction = (
        "\n\nIMPORTANT: Respond with ONLY valid JSON. No markdown code "
        "fences, no preamble, no explanation outside the JSON. "
        "The JSON must be directly parseable by json.loads()."
    )
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=temperature,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt + strict_instruction},
                {"role": "user", "content": user_prompt},
            ],
        )
        text = response.choices[0].message.content.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception as e:
        st.error(f"⚠️ The AI returned something unexpected. Please try again. ({e})")
        return {}
