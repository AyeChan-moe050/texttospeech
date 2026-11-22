import whisper


def transcribe_audio(
    audio_path: str,
    model_size: str = "small",
    language: str = "my",
) -> str:
    """Transcribe an audio/video meeting file using Whisper (defaults to Myanmar)."""
    model = whisper.load_model(model_size)
    result = model.transcribe(
        audio_path,
        language=language,
        task="transcribe",
    )
    return result["text"].strip()
