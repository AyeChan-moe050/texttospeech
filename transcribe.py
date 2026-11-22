import gc
import streamlit as st
import whisper


@st.cache_resource(show_spinner=False)
def _load_whisper_model(model_size: str):
    """Load and cache Whisper model once per model size to save memory."""
    return whisper.load_model(model_size)


def transcribe_audio(
    audio_path: str,
    model_size: str = "base",
    language: str = "my",
) -> str:
    """Transcribe an audio/video meeting file using a cached Whisper model."""
    model = _load_whisper_model(model_size)
    result = model.transcribe(
        audio_path,
        language=language,
        task="transcribe",
        fp16=False,
    )
    gc.collect()
    return result.get("text", "").strip()
