import os
import json
from datetime import date
# Replace with your LLM provider (OpenAI, etc)


def generate_caption(theme: str, cta: str = "Learn more") -> str:
# TODO: call your LLM here. Below is a deterministic template.
    return f"{theme} — {cta}. #DailyDrop #{date.today().isocalendar().week}"

if __name__ == "__main__":
    print(generate_caption("AI Mind‑Maps in 1 page"))