import gc
import mimetypes
import os
from pathlib import Path
import streamlit as st
from google import genai
from google.genai import types
import whisper


@st.cache_resource(show_spinner=False)
def _load_whisper_model(model_size: str):
    return whisper.load_model(model_size)


def transcribe_with_gemini(
    audio_path: str,
    api_key: str,
    model_name: str = "gemini-3.8-flash",
    language: str = "my",
) -> str:
    """Transcribe Myanmar audio directly via Gemini API with low local memory usage."""
    resolved_key = (api_key or os.getenv("GEMINI_API_KEY", "")).strip()
    if not resolved_key:
        raise ValueError(
            "GEMINI_API_KEY မရှိသေးပါ။ Streamlit Secrets မှာ ထည့်ပါ သို့မဟုတ် Sidebar မှာ ထည့်ပါ။"
        )

    path = Path(audio_path)
    mime_type, _ = mimetypes.guess_type(path.name)
    if not mime_type:
        mime_type = "audio/mp4" if path.suffix.lower() == ".m4a" else "audio/mpeg"

    lang_instruction = (
        "အောက်ပါ အသံဖိုင်ထဲမှာ ပြောထားတဲ့ စကားလုံးအားလုံးကို မြန်မာစာ (Unicode) ဖြင့် "
        "အနှစ်ချုပ်မဟုတ်ဘဲ ပြောသမျှအတိုင်း စာသားအပြည့်အစုံ (verbatim transcript) ပြန်ရေးပေးပါ။ "
        "စကားလုံးများကို တတ်နိုင်သမျှ မှန်ကန်တိကျအောင် ရေးပေးပါ။"
        if language == "my"
        else "Transcribe every spoken word in this audio file accurately into plain text without summarizing."
    )

    client = genai.Client(api_key=resolved_key)
    audio_bytes = path.read_bytes()

    response = client.models.generate_content(
        model=model_name,
        contents=[
            types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
            lang_instruction,
        ],
    )
    return (response.text or "").strip()


def transcribe_with_whisper(
    audio_path: str,
    model_size: str = "base",
    language: str = "my",
) -> str:
    """Fallback local/cloud Whisper transcription (use tiny/base on free Streamlit Cloud)."""
    model = _load_whisper_model(model_size)
    result = model.transcribe(
        audio_path,
        language=language,
        task="transcribe",
        fp16=False,
    )
    gc.collect()
    return (result.get("text") or "").strip()


def transcribe_audio(
    audio_path: str,
    engine: str = "gemini",
    model_name: str = "gemini-3.8-flash",
    whisper_model: str = "base",
    language: str = "my",
    api_key: str = "",
) -> str:
    if engine == "whisper":
        return transcribe_with_whisper(
            audio_path=audio_path,
            model_size=whisper_model,
            language=language,
        )
    return transcribe_with_gemini(
        audio_path=audio_path,
        api_key=api_key,
        model_name=model_name,
        language=language,
    )
