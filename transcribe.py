import whisper


def transcribe_audio(audio_path: str, model_size: str = "base") -> str:
    """Transcribe an audio/video meeting file into plain text using Whisper."""
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path)
    return result["text"].strip()
