"""Unified LLM wrapper supporting Anthropic Claude and OpenAI.

Usage:
    llm = LLMProvider()
    result = await llm.generate_json(system_prompt, user_prompt)
"""

from __future__ import annotations

import asyncio
import json
import os

from dotenv import load_dotenv

load_dotenv()


class LLMProvider:
    """Generates structured JSON from an LLM. Provider selected via LLM_PROVIDER env var."""

    def __init__(self) -> None:
        self.provider = os.getenv("LLM_PROVIDER", "anthropic").lower()

        if self.provider == "anthropic":
            from anthropic import Anthropic

            self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            self.model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
        elif self.provider == "openai":
            from openai import OpenAI

            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        else:
            raise ValueError(
                f"Unknown LLM_PROVIDER: {self.provider!r}. Use 'anthropic' or 'openai'."
            )

    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> dict:
        """Call the LLM and return parsed JSON."""
        if self.provider == "anthropic":
            return await self._generate_anthropic(system_prompt, user_prompt)
        return await self._generate_openai(system_prompt, user_prompt)

    async def _generate_anthropic(
        self, system_prompt: str, user_prompt: str,
    ) -> dict:
        response = await asyncio.to_thread(
            self.client.messages.create,
            model=self.model,
            max_tokens=4096,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt},
                {"role": "assistant", "content": "{"},
            ],
        )
        text = "{" + response.content[0].text
        return json.loads(text)

    async def _generate_openai(
        self, system_prompt: str, user_prompt: str,
    ) -> dict:
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
