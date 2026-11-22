import requests

MINUTES_PROMPT = """Convert the following meeting transcript into structured meeting minutes.
Include these sections:
- Meeting Summary
- Key Discussion Points
- Decisions Made
- Action Items (Owner, Task, Deadline if mentioned)

Transcript:
{transcript}
"""


def generate_minutes(transcript: str, model: str = "llama3.2", ollama_url: str = "http://localhost:11434") -> str:
    """Generate structured meeting minutes from a transcript via local Ollama."""
    response = requests.post(
        f"{ollama_url}/api/generate",
        json={
            "model": model,
            "prompt": MINUTES_PROMPT.format(transcript=transcript),
            "stream": False,
        },
        timeout=300,
    )
    response.raise_for_status()
    return response.json()["response"].strip()
