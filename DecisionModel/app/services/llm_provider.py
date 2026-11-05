from __future__ import annotations

import os


class LLMProvider:
    """Thin adapter for OpenAI or other providers; defaults to a safe mock mode."""

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def generate(self, prompt: str) -> str:
        if not self.api_key:
            return ""

        try:
            import openai

            response = openai.OpenAI(api_key=self.api_key).chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )
            return response.choices[0].message.content or ""
        except Exception:
            return ""
