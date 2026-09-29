"""
Run all 10 preset questions through both pipelines and save results.csv.

Correctness is NOT judged automatically: the rag_correct / okf_correct
columns are left blank for you to fill in by hand.

Usage:  python run_tests.py            (writes results.csv)
        python run_tests.py -o my.csv
"""
import argparse
import csv

import config
import llm
import okf_pipeline
import rag_pipeline
from questions import QUESTIONS


def sources_str(result: dict, kind: str) -> str:
    if kind == "rag":
        return "; ".join(f"{s['file']}#chunk{s['chunk']}" for s in result["sources"])
    return "; ".join(s["file"] for s in result["sources"]) or "(none)"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", default="results.csv")
    args = parser.parse_args()

    print(f"Model: {config.active_model()}")
    print("Preparing vector index and warming up the model…")
    rag_pipeline.ensure_index()
    llm.warm_up()

    rows = []
    for i, q in enumerate(QUESTIONS, 1):
        print(f"[{i}/{len(QUESTIONS)}] {q['question']}")
        rag = rag_pipeline.answer(q["question"])
        okf = okf_pipeline.answer(q["question"])
        print(f"    RAG {rag['seconds']:.1f}s | OKF {okf['seconds']:.1f}s")
        rows.append({
            "question": q["question"],
            "type": q["type"],
            "rag_answer": rag["answer"],
            "okf_answer": okf["answer"],
            "rag_sources": sources_str(rag, "rag"),
            "okf_sources": sources_str(okf, "okf"),
            "rag_time_s": f"{rag['seconds']:.2f}",
            "okf_time_s": f"{okf['seconds']:.2f}",
            "rag_correct": "",   # <- fill in by hand (right / wrong)
            "okf_correct": "",   # <- fill in by hand (right / wrong)
            "reference_notes": q["reference"],
            "model": config.active_model(),
        })

    # utf-8-sig so Excel / Numbers open the file with the right encoding
    with open(args.output, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
