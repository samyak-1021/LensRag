"""Answer generation providers (the LLM / VLM layer).

* ``MockProvider`` — deterministic, offline. Extracts the sentence from the
  retrieved context that best matches the question. No network, no key, stable
  output — so the full pipeline, tests and CI run anywhere.
* ``GeminiProvider`` — real multimodal generation via the Google AI Studio REST
  API (free tier). For visual-RAG it sends the actual page *images*, so it can
  read charts and tables. Enable with ``LENSRAG_LLM_PROVIDER=gemini`` + a key.

Both share one async interface: ``answer(question, contexts, image_paths)``.
"""

from __future__ import annotations

import base64
import re
from functools import lru_cache
from pathlib import Path
from typing import Protocol

import httpx

from app.config import get_settings
from app.services.embeddings import tokenize
from app.services.guard import INSUFFICIENT_MESSAGE

_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")

_SYSTEM_PROMPT = (
    "You are LensRAG, a careful document assistant. Answer the question using ONLY "
    "the provided page excerpts and images, which may include charts and tables. "
    "Read values directly off charts/tables when needed. Be concise and cite page "
    "numbers like (p.3). If the answer is not present, reply exactly: "
    "'Insufficient information.'"
)


class LLMProvider(Protocol):
    name: str

    async def answer(
        self, question: str, contexts: list[str], image_paths: list[str] | None = None
    ) -> str: ...


class MockProvider:
    """Extractive, deterministic answerer for offline/dev/CI."""

    name = "mock"

    async def answer(
        self, question: str, contexts: list[str], image_paths: list[str] | None = None
    ) -> str:
        if not contexts:
            return INSUFFICIENT_MESSAGE
        q_tokens = set(tokenize(question))
        best_sentence, best_overlap = "", 0.0
        for ctx in contexts:
            for sentence in _SENTENCE_RE.split(ctx):
                s_tokens = set(tokenize(sentence))
                if not s_tokens:
                    continue
                overlap = len(q_tokens & s_tokens) / max(1, len(q_tokens))
                if overlap > best_overlap:
                    best_sentence, best_overlap = sentence.strip(), overlap
        if best_overlap == 0.0:
            return INSUFFICIENT_MESSAGE
        return best_sentence


class GeminiProvider:
    """Real multimodal generation via Google AI Studio (Gemini)."""

    name = "gemini"
    _ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def __init__(self, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model

    async def answer(
        self, question: str, contexts: list[str], image_paths: list[str] | None = None
    ) -> str:
        parts: list[dict] = [{"text": self._build_prompt(question, contexts)}]
        for path in image_paths or []:
            data = Path(path).read_bytes()
            parts.append(
                {
                    "inline_data": {
                        "mime_type": "image/png",
                        "data": base64.b64encode(data).decode(),
                    }
                }
            )
        payload = {
            "contents": [{"role": "user", "parts": parts}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 512},
        }
        url = self._ENDPOINT.format(model=self._model)
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    url, params={"key": self._api_key}, json=payload
                )
                resp.raise_for_status()
                data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (httpx.HTTPError, KeyError, IndexError):
            # Fail safe: never crash a request on a provider hiccup — abstain instead.
            return INSUFFICIENT_MESSAGE

    @staticmethod
    def _build_prompt(question: str, contexts: list[str]) -> str:
        joined = "\n\n".join(f"[excerpt {i + 1}] {c}" for i, c in enumerate(contexts))
        return f"{_SYSTEM_PROMPT}\n\nPage excerpts:\n{joined}\n\nQuestion: {question}"


@lru_cache
def get_provider() -> LLMProvider:
    settings = get_settings()
    if settings.llm_provider == "gemini" and settings.gemini_api_key:
        return GeminiProvider(settings.gemini_api_key, settings.gemini_model)
    return MockProvider()
