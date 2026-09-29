"""
OKF pipeline: no embeddings, no vector search.

1. Build an index of the OKF bundle (path + type + title + description),
   taken from each file's YAML frontmatter.
2. Ask the LLM which file(s) answer the question (or NONE).
3. Read those files in full and answer from them.
4. If no file covers the question, say so and don't guess.
"""
import time

import yaml

import config
import llm

RESERVED_FILES = {"index.md", "log.md"}  # OKF v0.2 reserved file names

NOT_COVERED = (
    "The OKF knowledge bundle has no file that covers this question, "
    "so I can't answer it without guessing."
)

SELECT_SYSTEM_PROMPT = f"""You route questions to files in a company knowledge bundle.
You get an INDEX (one file per line: path | type | title | description) and a QUESTION.
Reply with the path(s) of the file(s) needed to answer the question, one per line, at most {config.OKF_MAX_FILES}.
Copy paths exactly as written in the index. Output nothing else.
If no file in the index is relevant to the question, reply with exactly: NONE"""


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split '---\\nyaml\\n---\\nbody' into (metadata dict, body)."""
    if text.startswith("---"):
        _, fm, body = text.split("---", 2)
        return yaml.safe_load(fm) or {}, body.strip()
    return {}, text


def load_index() -> list[dict]:
    """One entry per OKF concept file, built from its frontmatter."""
    entries = []
    for path in sorted(config.OKF_DIR.rglob("*.md")):
        if path.name in RESERVED_FILES:
            continue
        meta, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        entries.append({
            "path": path.relative_to(config.OKF_DIR).as_posix(),  # e.g. metrics/monthly-active-users.md
            "type": meta.get("type", ""),
            "title": meta.get("title", path.stem),
            "description": meta.get("description", ""),
        })
    return entries


def index_as_text(entries: list[dict]) -> str:
    return "\n".join(f"{e['path']} | {e['type']} | {e['title']} | {e['description']}" for e in entries)


def pick_files(question: str, entries: list[dict]) -> tuple[list[str], str]:
    """Ask the LLM which files to open. Returns (valid paths, raw reply)."""
    reply = llm.chat(SELECT_SYSTEM_PROMPT, f"INDEX:\n{index_as_text(entries)}\n\nQUESTION: {question}")
    # Keep only real paths from the index (ignores anything the model invents),
    # in the order the model mentioned them.
    found = [(reply.find(e["path"]), e["path"]) for e in entries if e["path"] in reply]
    picked = [p for _, p in sorted(found)][: config.OKF_MAX_FILES]
    return picked, reply


def answer(question: str) -> dict:
    """Pick files from the index, read them, answer. Returns answer, sources and timing."""
    start = time.perf_counter()
    entries = load_index()
    picked, router_reply = pick_files(question, entries)

    if not picked:
        reply = NOT_COVERED
    else:
        context = "\n\n".join(
            f"### File: okf/{p}\n{(config.OKF_DIR / p).read_text(encoding='utf-8')}" for p in picked
        )
        reply = llm.chat(config.ANSWER_SYSTEM_PROMPT, f"CONTEXT:\n{context}\n\nQUESTION: {question}")

    return {
        "answer": reply,
        "seconds": time.perf_counter() - start,
        "sources": [{"file": f"okf/{p}", "text": (config.OKF_DIR / p).read_text(encoding="utf-8")} for p in picked],
        "router_reply": router_reply,
    }


if __name__ == "__main__":
    print(index_as_text(load_index()))
