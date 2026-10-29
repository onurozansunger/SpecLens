from __future__ import annotations

import re
import statistics
from datetime import UTC, datetime

from .common import ROOT, digest, normalize, read_jsonl, write_json
from .retrieval import Retriever


def evidence_recall(task: dict, hits: list[dict]) -> float | None:
    required = task["canonical_evidence"]
    if not required:
        return None
    matched = sum(
        any(
            c["document_id"] == gold["document_id"]
            and c["sha256"] == gold["pdf_sha256"]
            and c["page"] == gold["page"]
            and normalize(gold["quote"]) in normalize(c["text"])
            for c in hits
        )
        for gold in required
    )
    return matched / len(required)


def evaluate_retrieval(methods=("bm25", "dense", "hybrid"), output=None):
    tasks_path = ROOT / "data/evaluation/pilot.jsonl"
    tasks = read_jsonl(tasks_path)
    retriever = Retriever()
    rows = []
    for method in methods:
        for task in tasks:
            hits = retriever.search(task["question"], method, 10, task["documents"])
            rows.append(
                {
                    "task_id": task["id"],
                    "language": task["language"],
                    "method": method,
                    "recall_at_3": evidence_recall(task, hits[:3]),
                    "recall_at_5": evidence_recall(task, hits[:5]),
                    "recall_at_10": evidence_recall(task, hits),
                    "retrieved_ids": [h["id"] for h in hits],
                }
            )
    summary = []
    for method in methods:
        for language in ("en", "tr"):
            selected = [
                r
                for r in rows
                if r["method"] == method
                and r["language"] == language
                and r["recall_at_5"] is not None
            ]
            summary.append(
                {
                    "method": method,
                    "language": language,
                    "tasks": len(selected),
                    **{
                        f"canonical_quote_recall_at_{k}": statistics.mean(
                            r[f"recall_at_{k}"] for r in selected
                        )
                        for k in (3, 5, 10)
                    },
                }
            )
    result = {
        "created_at": datetime.now(UTC).isoformat(),
        "split": "development",
        "human_validated": False,
        "document_filter": "given_by_task",
        "warning": "Canonical-quote recall may miss valid alternate evidence. Paired prompts are correlated.",
        "tasks_sha256": digest(tasks_path),
        "chunks_sha256": digest(ROOT / "data/processed/chunks.jsonl"),
        "summary": summary,
        "rows": rows,
    }
    write_json(output or ROOT / "reports/retrieval_pilot.json", result)
    return summary


def evaluate_generation(method="hybrid", limit=30, output=None, per_document=8):
    from .pipeline import Pipeline

    pipeline = Pipeline()
    tasks_path = ROOT / "data/evaluation/pilot.jsonl"
    tasks = read_jsonl(tasks_path)[:limit]
    rows = []
    for task in tasks:
        result = pipeline.answer(task["question"], task["documents"], method, per_document)
        values = " ".join(f["value"] or "" for f in result["findings"])
        pattern_match = all(
            re.search(p, values, re.IGNORECASE) for p in task["expected_value_patterns"]
        )
        if not task["answerable"]:
            pattern_match = bool(result["findings"]) and all(
                f["status"] == "not_stated" for f in result["findings"]
            )
        rows.append(
            {
                "task_id": task["id"],
                "language": task["language"],
                "expected_pattern_match": pattern_match,
                "provenance_pass": result["status"] == "provenance_checked",
                "result": result,
            }
        )
        # Incremental checkpoints keep completed measurements if interrupted.
        write_json(
            output or ROOT / "reports/generation_pilot.json",
            {
                "created_at": datetime.now(UTC).isoformat(),
                "split": "development",
                "human_validated": False,
                "method": method,
                "per_document": per_document,
                "warning": "Pattern match is a diagnostic, NOT semantic correctness or benchmark accuracy.",
                "tasks_sha256": digest(tasks_path),
                "completed": len(rows),
                "requested": len(tasks),
                "pattern_matches": sum(r["expected_pattern_match"] for r in rows),
                "provenance_passes": sum(r["provenance_pass"] for r in rows),
                "rows": rows,
            },
        )
        print(
            f"{task['id']}: provenance={rows[-1]['provenance_pass']} patterns={pattern_match}",
            flush=True,
        )
    return {
        "completed": len(rows),
        "pattern_matches": sum(r["expected_pattern_match"] for r in rows),
        "provenance_passes": sum(r["provenance_pass"] for r in rows),
    }
