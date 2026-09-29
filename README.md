# RAG vs OKF: side-by-side demo

This demo asks the same question two ways, using the same model and the same settings:

| | **RAG** | **OKF** |
|---|---|---|
| Knowledge | All docs: messy `/raw` (48 files) + curated `/okf` (11 files) | Only the curated OKF bundle in `/okf` |
| How it finds info | Embeds chunks (all-MiniLM-L6-v2) → ChromaDB → top 4 chunks | LLM reads an index (path, type, title, description) → opens up to 3 files in full |
| When nothing fits | Answers from whatever the top 4 chunks happen to be | Says the bundle doesn't cover the question |

Both pipelines share one answer prompt (`config.ANSWER_SYSTEM_PROMPT`), one model, temperature 0, and the same
output limit. The company "Northwind Analytics" and all of its data are fictional.

The OKF bundle follows the [OKF v0.2 spec](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md):
one concept per Markdown file, YAML frontmatter with the required `type` field plus `title`, `description`,
`tags`, `status`, `verified` and `stale_after`, a root `index.md` with `okf_version: "0.2"`, a `log.md`,
and bundle-relative links (`/metrics/...md`). `owner` and `last_reviewed` are custom keys, which the spec allows.

---

## 1. Setup (once)

```bash
# Python 3.11+ (3.12 recommended)
brew install python@3.12

# Ollama + the model
brew install ollama
brew services start ollama        # or run `ollama serve` in a separate terminal
ollama pull llama3.1:8b

# Project
cd ~/Documents/rak_vs_okf
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Build the vector index (downloads the 80 MB embedding model the first time)
python rag_pipeline.py
```

## 2. Run the app

```bash
cd ~/Documents/rak_vs_okf
source .venv/bin/activate
streamlit run app.py
```

It opens at http://localhost:8501 in dark mode. Click a question in the sidebar, then click **Ask both**.

Recording tips: zoom the browser to about 110–125%, and collapse the sidebar after you click a question.
The first question after startup is slower while the model loads (the app warms it up before timing anything).

## 3. Run all tests → results.csv

```bash
python run_tests.py              # writes results.csv
python run_tests.py -o run2.csv  # another file name
```

Columns: `question, type, rag_answer, okf_answer, rag_sources, okf_sources, rag_time_s, okf_time_s,
rag_correct, okf_correct, reference_notes, model`.

`rag_correct` and `okf_correct` are left **blank** for you to mark right or wrong. `reference_notes` has
the expected answer to help you grade. Nothing is scored automatically.

## 4. Use the Anthropic API instead (optional)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export LLM_PROVIDER=anthropic
# optional, default is claude-haiku-4-5-20251001
export ANTHROPIC_MODEL=claude-haiku-4-5-20251001
streamlit run app.py    # or: python run_tests.py
```

Both pipelines then use that same Claude model at temperature 0. Embeddings stay local.
Switch back with `unset LLM_PROVIDER`.

## Settings you might change (`config.py` or env vars)

| Setting | Default | Notes |
|---|---|---|
| `OLLAMA_MODEL` | `llama3.1:8b` | any Ollama model |
| `NUM_CTX` | `4096` | Ollama context window. 4096 runs on an 8 GB Mac; use 8192 if you have 16 GB+ |
| `RAG_TOP_K` | 4 | chunks retrieved |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | 1000 / 150 chars | then rebuild with `python rag_pipeline.py` |
| `OKF_MAX_FILES` | 3 | files the OKF agent may open |

If you edit anything in `/raw` or `/okf`, re-run `python rag_pipeline.py` so RAG sees the change.
OKF reads the files live, so it needs no rebuild.

## What's in the data (so you can explain the results honestly)

Planted on purpose, as the brief asked:

- **Old MAU definition**: `raw/slack/2026-01-14_data-metrics.txt`, `raw/email/2025-11-20_board-deck-metrics.txt`
  and `raw/meetings/2026-01-20_exec-staff.md` say "logged in during the calendar month". The current
  definition is in `okf/metrics/monthly-active-users.md`.
- **Conflicting refund windows**: `raw/meetings/2026-03-18_billing-sync.md` says 14 days,
  `raw/meetings/2026-03-25_finance-review.md` says 60 days. The official answer (30 days) is in
  `okf/policies/refund-policy.md`, and a support email in `/raw` also cites 30 days.
- **Complaints and feature requests exist only in `/raw`** (tickets, Slack, emails, meeting notes).
  OKF has no file for them, so it should decline those questions.

Kept fair on purpose:

- RAG indexes the OKF files too, so it can find the correct current answers.
- Both pipelines get the same "answer only from context, don't guess" instruction.
- The model is warmed up before timing, and the pipelines run one after the other (never in parallel).
- OKF makes two LLM calls (pick files, then answer); RAG makes one plus a vector search. The times include all of that.

## Files

```
app.py            Streamlit UI
rag_pipeline.py   chunk → embed → ChromaDB → top-4 → answer   (run it to rebuild the index)
okf_pipeline.py   index → pick files → read → answer
llm.py            one chat() used by both (Ollama or Anthropic)
config.py         shared settings + the shared answer prompt
questions.py      the 10 preset questions (+ grading notes)
run_tests.py      runs everything → results.csv
okf/              curated OKF v0.2 bundle (11 concepts + index.md + log.md)
raw/              48 messy docs: slack/, email/, tickets/, meetings/
```

## Troubleshooting

- **"Can't reach Ollama"**: start it with `brew services start ollama` or `ollama serve`.
- **"Ollama ran out of memory"**: close other apps, or run with `NUM_CTX=2048 streamlit run app.py`.
- **Slow answers**: an 8B model on an 8 GB Mac took 8–60 s per pipeline in testing, with occasional outliers of several minutes when memory is tight. For a snappier video, use
  the Anthropic option, or record on a Mac with more RAM.
