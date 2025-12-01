import os
from typing import Optional

class LLMClient:
    def __init__(self, provider: str = "openai"):
        self.provider = provider
        self.enabled = bool(os.getenv("OPENAI_API_KEY"))

    def generate(self, prompt: str) -> Optional[str]:
        if not self.enabled:
            return None

        try:
            if self.provider == "openai":
                from openai import OpenAI
                client = OpenAI()

                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a conservative equity research analyst. "
                                "Do NOT invent numbers. Only explain given facts."
                            ),
                        },
                        {"role": "user", "content": f"Rewrite this analysis in professional tone: {prompt}"},
                    ],
                    temperature=0.2,
                    max_tokens=300,
                )

                return response.choices[0].message.content.strip()
        except Exception:
            return None

        return None
