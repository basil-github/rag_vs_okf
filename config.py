"""
Shared settings for BOTH pipelines.

Everything that could make the comparison unfair (model, temperature,
output length, answer instructions) lives here and is used by RAG and OKF alike.
"""
import os
from pathlib import Path

# --- Paths -------------------------------------------------------------------
ROOT = Path(__file__).parent
OKF_DIR = ROOT / "okf"          # curated OKF bundle
RAW_DIR = ROOT / "raw"          # messy unstructured corpus
CHROMA_DIR = ROOT / "chroma_db" # vector store for RAG (created on first run)

# --- LLM provider ------------------------------------------------------------
# "ollama" (default, fully local) or "anthropic" (needs ANTHROPIC_API_KEY).
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")

# Same generation settings for both pipelines.
TEMPERATURE = 0.0
MAX_TOKENS = 500
SEED = 42          # Ollama only: makes local runs repeatable
# Ollama only: context window in tokens. 4096 fits 4 chunks or 3 OKF files (~2k tokens)
# and runs on an 8 GB Mac. Raise it (e.g. NUM_CTX=8192) if you have more memory.
NUM_CTX = int(os.getenv("NUM_CTX", "4096"))

# --- RAG settings ------------------------------------------------------------
RAG_TOP_K = 4
CHUNK_SIZE = 1000     # characters
CHUNK_OVERLAP = 150   # characters

# --- OKF settings ------------------------------------------------------------
OKF_MAX_FILES = 3     # max files the agent may open per question

# --- The answer prompt: IDENTICAL for both pipelines -------------------------
ANSWER_SYSTEM_PROMPT = """You are an internal assistant for Northwind Analytics employees.
Answer the question using ONLY the context provided below.
If the context does not contain the answer, say "I don't have enough information to answer that." Do not guess.
Be concise (under 150 words). Use short bullet points when listing several items.
Mention the file name(s) you relied on."""


def active_model() -> str:
    """Human-readable 'provider / model' string for the UI and CSV."""
    model = ANTHROPIC_MODEL if LLM_PROVIDER == "anthropic" else OLLAMA_MODEL
    return f"{LLM_PROVIDER} / {model}"
