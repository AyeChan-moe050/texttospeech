import requests


def generate_minutes(
    transcript: str,
    model: str = "llama3.2",
    ollama_url: str = "http://localhost:11434",
) -> str:
    """Generate structured Myanmar meeting minutes from a transcript via Ollama."""
    prompt = (
        "Read the following meeting transcript and write structured meeting minutes "
        "entirely in the Myanmar (Burmese) language using Unicode.\n"
        "Include these sections:\n"
        "- Meeting Summary\n"
        "- Key Discussion Points\n"
        "- Decisions Made\n"
        "- Action Items (Owner, Task, Deadline)\n\n"
        f"Transcript:\n{transcript}"
    )

    response = requests.post(
        f"{ollama_url}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
        },
        timeout=300,
    )
    response.raise_for_status()
    return response.json()["response"].strip()
