import os
import requests


def _build_prompt(transcript: str) -> str:
    return (
        "Read the following meeting transcript and write structured meeting minutes "
        "in the Myanmar (Burmese) language using clean Unicode.\n"
        "Include these sections:\n"
        "- Meeting Summary\n"
        "- Key Discussion Points\n"
        "- Decisions Made\n"
        "- Action Items (Owner, Task, Deadline)\n\n"
        f"Transcript:\n{transcript}"
    )


def generate_minutes_gemini(
    transcript: str,
    api_key: str,
    model: str = "gemini-3.5-flash-lite",
) -> str:
    """Generate Myanmar meeting minutes using the Gemini REST API."""
    if not api_key:
        raise ValueError(
            "Missing GEMINI_API_KEY. Add it to Streamlit Secrets or enter it in the sidebar."
        )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": _build_prompt(transcript)},
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload, timeout=180)
    response.raise_for_status()
    data = response.json()

    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError("Gemini API returned no candidates.")

    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join(part.get("text", "") for part in parts).strip()
    if not text:
        raise RuntimeError("Gemini API returned an empty response.")
    return text


def generate_minutes_ollama(
    transcript: str,
    model: str = "llama3.2",
    ollama_url: str = "http://localhost:11434",
) -> str:
    """Generate Myanmar meeting minutes using a local/remote Ollama instance."""
    response = requests.post(
        f"{ollama_url.rstrip('/')}/api/generate",
        json={
            "model": model,
            "prompt": _build_prompt(transcript),
            "stream": False,
        },
        timeout=300,
    )
    response.raise_for_status()
    return response.json().get("response", "").strip()


def generate_minutes(
    transcript: str,
    provider: str = "gemini",
    model: str = "gemini-3.5-flash-lite",
    api_key: str | None = None,
    ollama_url: str = "http://localhost:11434",
) -> str:
    """Generate structured Myanmar meeting minutes using Gemini (default) or Ollama."""
    if provider == "ollama":
        return generate_minutes_ollama(transcript, model=model, ollama_url=ollama_url)

    resolved_key = api_key or os.getenv("GEMINI_API_KEY", "")
    return generate_minutes_gemini(transcript, api_key=resolved_key, model=model)
