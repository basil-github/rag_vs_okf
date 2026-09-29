"""
One tiny function, chat(system, user), used by BOTH pipelines.

Switch provider with the LLM_PROVIDER env var ("ollama" or "anthropic").
Whichever provider is active, RAG and OKF get the exact same model and settings.
"""
import os

import requests

import config

_anthropic_client = None


def chat(system: str, user: str) -> str:
    """Send one system + user message, return the model's text reply."""
    if config.LLM_PROVIDER == "anthropic":
        return _chat_anthropic(system, user)
    return _chat_ollama(system, user)


def _chat_ollama(system: str, user: str) -> str:
    try:
        resp = requests.post(
            f"{config.OLLAMA_URL}/api/chat",
            json={
                "model": config.OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "stream": False,
                "options": {
                    "temperature": config.TEMPERATURE,
                    "seed": config.SEED,
                    "num_ctx": config.NUM_CTX,
                    "num_predict": config.MAX_TOKENS,
                },
            },
            timeout=300,
        )
    except requests.ConnectionError:
        raise RuntimeError(
            f"Can't reach Ollama at {config.OLLAMA_URL}. Start it with: ollama serve"
        )
    if resp.status_code == 404:
        raise RuntimeError(
            f"Model '{config.OLLAMA_MODEL}' not found. Run: ollama pull {config.OLLAMA_MODEL}"
        )
    if resp.status_code == 500 and "runner" in resp.text:
        raise RuntimeError(
            "Ollama ran out of memory. Close other apps or lower the context window, e.g. NUM_CTX=2048."
        )
    resp.raise_for_status()
    return resp.json()["message"]["content"].strip()


def _chat_anthropic(system: str, user: str) -> str:
    global _anthropic_client
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError("LLM_PROVIDER=anthropic but ANTHROPIC_API_KEY is not set.")
    if _anthropic_client is None:
        import anthropic  # imported lazily so Ollama users don't need a key

        _anthropic_client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
    msg = _anthropic_client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=config.MAX_TOKENS,
        temperature=config.TEMPERATURE,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(block.text for block in msg.content if block.type == "text").strip()


def warm_up() -> None:
    """
    Load the model before timing anything. The first Ollama call has to load
    the model into memory (several seconds), which would unfairly slow
    down whichever pipeline happened to run first.
    """
    chat("Reply with the single word OK.", "Ready?")
