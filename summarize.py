import requests

MYANMAR_MINUTES_PROMPT = """အောက်ပါ အစည်းအဝေး အသံဖိုင်မှ စာသားမှတ်တမ်းကို ဖတ်ရှုပြီး စနစ်တကျ အစည်းအဝေး မှတ်တမ်း (Meeting Minutes) အဖြစ် မြန်မာဘာသာဖြင့် ပြန်လည်ရေးသားပေးပါ။

အောက်ပါ ကဏ္ဍများ ပါဝင်ပါစေ-
- အစည်းအဝေး အကျဉ်းချုပ် (Meeting Summary)
- အဓိက ဆွေးနွေးချက်များ (Key Discussion Points)
- ဆုံးဖြတ်ချက်များ (Decisions Made)
- ဆက်လက်ဆောင်ရွက်ရမည့် လုပ်ငန်းတာဝန်များ (Action Items - တာဝန်ခံ၊ လုပ်ငန်း၊ ပြီးစီးရမည့်ရက်)

စာသားမှတ်တမ်း-
{transcript}
"""


def generate_minutes(
    transcript: str,
    model: str = "llama3.2",
    ollama_url: str = "http://localhost:11434",
) -> str:
    """Generate structured Myanmar meeting minutes from a transcript via Ollama."""
    response = requests.post(
        f"{ollama_url}/api/generate",
        json={
            "model": model,
            "prompt": MYANMAR_MINUTES_PROMPT.format(transcript=transcript),
            "stream": False,
        },
        timeout=300,
    )
    response.raise_for_status()
    return response.json()["response"].strip()
