"""
Provider abstractions for the LLM extraction stage and web search/fetch.

The pipeline is provider-agnostic. Concrete providers are selected from env:
  - LLM:     OPENAI_API_KEY  -> OpenAIProvider
             ANTHROPIC_API_KEY -> AnthropicProvider
  - Search:  TAVILY_API_KEY  -> TavilySearch   (or SERPER_API_KEY)
  - Composio: COMPOSIO_API_KEY -> ComposioCorroborator (optional corroboration)

No keys are hardcoded. If a required key is missing, the provider raises a clear
error so the operator knows exactly what to configure. This keeps the LLM stage
runnable by any reviewer with their own key, without changing pipeline code.
"""
from __future__ import annotations

import json
import os
import urllib.request
from typing import Any


class ProviderError(RuntimeError):
    pass


# --------------------------------------------------------------------------- #
# LLM providers
# --------------------------------------------------------------------------- #
class BaseLLM:
    def complete_json(self, system: str, user: str) -> dict[str, Any]:
        raise NotImplementedError


class OpenAIProvider(BaseLLM):
    def __init__(self, model: str = "gpt-4.1") -> None:
        self.key = os.environ.get("OPENAI_API_KEY")
        if not self.key:
            raise ProviderError("OPENAI_API_KEY not set")
        self.model = os.environ.get("OPENAI_MODEL", model)

    def complete_json(self, system: str, user: str) -> dict[str, Any]:
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0,
        }
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(body).encode(),
            headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=90) as r:
            data = json.loads(r.read())
        return json.loads(data["choices"][0]["message"]["content"])


class AnthropicProvider(BaseLLM):
    def __init__(self, model: str = "claude-3-7-sonnet-latest") -> None:
        self.key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.key:
            raise ProviderError("ANTHROPIC_API_KEY not set")
        self.model = os.environ.get("ANTHROPIC_MODEL", model)

    def complete_json(self, system: str, user: str) -> dict[str, Any]:
        body = {
            "model": self.model,
            "max_tokens": 4096,
            "system": system,
            "messages": [{"role": "user", "content": user + "\n\nReturn ONLY valid JSON."}],
            "temperature": 0,
        }
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=json.dumps(body).encode(),
            headers={
                "x-api-key": self.key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=90) as r:
            data = json.loads(r.read())
        text = "".join(blk.get("text", "") for blk in data.get("content", []))
        start, end = text.find("{"), text.rfind("}")
        return json.loads(text[start : end + 1])


def get_llm() -> BaseLLM:
    if os.environ.get("ANTHROPIC_API_KEY"):
        return AnthropicProvider()
    if os.environ.get("OPENAI_API_KEY"):
        return OpenAIProvider()
    raise ProviderError(
        "No LLM key configured. Set ANTHROPIC_API_KEY or OPENAI_API_KEY. "
        "(The dataset in data/final/ was produced by the Kiro research agent; "
        "this stage reproduces that workflow programmatically.)"
    )


# --------------------------------------------------------------------------- #
# Web search
# --------------------------------------------------------------------------- #
class BaseSearch:
    def search(self, query: str, k: int = 6) -> list[dict[str, str]]:
        raise NotImplementedError


class TavilySearch(BaseSearch):
    def __init__(self) -> None:
        self.key = os.environ.get("TAVILY_API_KEY")
        if not self.key:
            raise ProviderError("TAVILY_API_KEY not set")

    def search(self, query: str, k: int = 6) -> list[dict[str, str]]:
        body = {"api_key": self.key, "query": query, "max_results": k}
        req = urllib.request.Request(
            "https://api.tavily.com/search",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=45) as r:
            data = json.loads(r.read())
        return [
            {"title": x.get("title", ""), "url": x.get("url", ""), "snippet": x.get("content", "")}
            for x in data.get("results", [])
        ]


def get_search() -> BaseSearch:
    if os.environ.get("TAVILY_API_KEY"):
        return TavilySearch()
    raise ProviderError("No search key configured. Set TAVILY_API_KEY.")


def fetch_url(url: str, timeout: int = 30) -> str:
    """Best-effort HTML/text fetch with graceful failure."""
    req = urllib.request.Request(url, headers={"User-Agent": "composio-research-agent/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read(400_000)
    try:
        return raw.decode("utf-8", errors="ignore")
    except Exception:
        return ""
