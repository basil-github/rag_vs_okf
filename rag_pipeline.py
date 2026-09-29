"""
RAG pipeline: chunk every document in /raw AND /okf, embed with
all-MiniLM-L6-v2 (ChromaDB's built-in local ONNX version), store in ChromaDB,
retrieve the top 4 chunks for a question, and answer from those chunks.

Run `python rag_pipeline.py` to (re)build the vector index.
"""
import time

import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

import config
import llm

COLLECTION = "northwind"


def load_documents() -> list[tuple[str, str]]:
    """Return (relative_path, text) for every .md/.txt file in /raw and /okf."""
    docs = []
    for folder in (config.RAW_DIR, config.OKF_DIR):
        for path in sorted(folder.rglob("*")):
            if path.suffix in (".md", ".txt"):
                rel = path.relative_to(config.ROOT).as_posix()  # e.g. raw/slack/x.txt
                docs.append((rel, path.read_text(encoding="utf-8")))
    return docs


def chunk_text(text: str, size: int = config.CHUNK_SIZE, overlap: int = config.CHUNK_OVERLAP) -> list[str]:
    """Split text into ~size-character chunks with some overlap, preferring to cut at line breaks."""
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            # Try to end the chunk on a line break so chunks stay readable.
            line_break = text.rfind("\n", start + size // 2, end)
            if line_break != -1:
                end = line_break
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return [c for c in chunks if c]


def _client():
    return chromadb.PersistentClient(
        path=str(config.CHROMA_DIR), settings=Settings(anonymized_telemetry=False)
    )


def _collection(client):
    return client.get_or_create_collection(
        COLLECTION,
        embedding_function=DefaultEmbeddingFunction(),  # all-MiniLM-L6-v2, runs locally
        metadata={"hnsw:space": "cosine"},
    )


def build_index() -> int:
    """Rebuild the vector index from scratch. Returns the number of chunks stored."""
    client = _client()
    if COLLECTION in [c.name for c in client.list_collections()]:
        client.delete_collection(COLLECTION)
    col = _collection(client)

    ids, texts, metas = [], [], []
    for rel_path, text in load_documents():
        for i, chunk in enumerate(chunk_text(text)):
            ids.append(f"{rel_path}#{i}")
            texts.append(chunk)
            metas.append({"source": rel_path, "chunk": i})

    col.add(ids=ids, documents=texts, metadatas=metas)
    return len(ids)


def ensure_index() -> None:
    """Build the index only if it doesn't exist yet."""
    if _collection(_client()).count() == 0:
        build_index()


def answer(question: str) -> dict:
    """Retrieve top-k chunks and ask the LLM. Returns answer, sources and timing."""
    start = time.perf_counter()

    results = _collection(_client()).query(query_texts=[question], n_results=config.RAG_TOP_K)
    chunks = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    context = "\n\n".join(
        f"### Chunk {i + 1} (from {m['source']})\n{text}"
        for i, (text, m) in enumerate(zip(chunks, metas))
    )
    reply = llm.chat(config.ANSWER_SYSTEM_PROMPT, f"CONTEXT:\n{context}\n\nQUESTION: {question}")

    return {
        "answer": reply,
        "seconds": time.perf_counter() - start,
        "sources": [
            {"file": m["source"], "chunk": m["chunk"], "distance": d, "text": t}
            for t, m, d in zip(chunks, metas, distances)
        ],
    }


if __name__ == "__main__":
    n = build_index()
    print(f"Indexed {n} chunks from /raw and /okf into {config.CHROMA_DIR}")
