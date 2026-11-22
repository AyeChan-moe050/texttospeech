import argparse
from datetime import datetime
from pathlib import Path

from export_doc import save_docx, save_markdown
from summarize import generate_minutes
from transcribe import transcribe_audio


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Myanmar meeting minutes from an audio file."
    )
    parser.add_argument(
        "audio_file", help="Path to meeting recording (.mp3, .wav, .m4a, .mp4)"
    )
    parser.add_argument(
        "--whisper-model",
        default="small",
        help="Whisper model (tiny, base, small, medium, large)",
    )
    parser.add_argument(
        "--language",
        default="my",
        help="Audio language code (default: my for Myanmar)",
    )
    parser.add_argument(
        "--llm-model",
        default="llama3.2",
        help="Ollama model name for minutes formatting",
    )
    parser.add_argument(
        "--ollama-url",
        default="http://localhost:11434",
        help="Ollama base URL",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Directory to save generated record files",
    )
    args = parser.parse_args()

    print("1/3 Transcribing audio...")
    transcript = transcribe_audio(
        args.audio_file,
        model_size=args.whisper_model,
        language=args.language,
    )

    print("2/3 Generating meeting minutes...")
    minutes_text = generate_minutes(
        transcript,
        model=args.llm_model,
        ollama_url=args.ollama_url,
    )

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(args.output_dir)
    transcript_path = save_markdown(transcript, out_dir / f"transcript_{stamp}.txt")
    md_path = save_markdown(minutes_text, out_dir / f"meeting_minutes_{stamp}.md")
    docx_path = save_docx(minutes_text, out_dir / f"meeting_minutes_{stamp}.docx")

    print("3/3 Done! Saved files:")
    print(f" - Transcript: {transcript_path}")
    print(f" - Markdown:   {md_path}")
    print(f" - Word Doc:   {docx_path}")


if __name__ == "__main__":
    main()
