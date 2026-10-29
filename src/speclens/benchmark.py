"""Field-level reference checks. These metrics are not human semantic accuracy."""

from __future__ import annotations

import re
import statistics
from datetime import UTC, datetime
from pathlib import Path

import httpx

from .common import ROOT, digest, normalize, read_json, read_jsonl, write_json
from .intent import fold, requested_fields


def canonical_field(field: str) -> str:
    label = fold(field.replace("_", " "))
    if label in {"sensor", "sensor type", "humidity sensor"}:
        return "humidity_sensor"
    if "humidity" in label and "range" in label:
        return field
    if "ambient" in label and ("temperature" in label or "limit" in label):
        return "ambient_temperature"
    if "eut" in label:
        return "eut_temperature"
    if "dijital" in label and "pin" in label:
        return "digital_io_count"
    if "qspi" in label and "bellek" in label:
        return "flash_capacity"
    candidates = requested_fields(field.replace("_", " "))
    if len(candidates) == 1:
        return candidates[0]
    if re.search(r"digital.*pin|I/O.*pin", field, re.IGNORECASE):
        return "digital_io_count"
    return field


def score_result(task: dict, result: dict) -> dict:
    expected = task["expected_findings"]
    actual = result.get("findings", [])
    required = {(f["document_id"], f["field"]) for f in expected}
    extras = [f for f in actual if (f["document_id"], canonical_field(f["field"])) not in required]
    rows = []
    for gold in expected:
        matches = [
            f
            for f in actual
            if f["document_id"] == gold["document_id"]
            and canonical_field(f["field"]) == gold["field"]
        ]
        value_ok, evidence_ok = False, False
        if len(matches) == 1:
            finding = matches[0]
            value = normalize(finding["value"] or "")
            value_ok = (
                finding["status"] == gold["status"]
                and all(
                    re.search(pattern, value, re.IGNORECASE) is not None
                    for pattern in gold.get("value_patterns", [])
                )
                and not any(
                    re.search(pattern, value, re.IGNORECASE)
                    for pattern in gold.get("forbidden_patterns", [])
                )
            )
            if gold["status"] == "not_stated":
                value_ok = value_ok and finding["value"] is None and not finding["citations"]
                evidence_ok = value_ok
            else:
                # Every evidence group must match at least one accepted source alternative.
                evidence_ok = bool(gold.get("evidence_groups")) and all(
                    any(
                        c["document_id"] == ref["document_id"]
                        and c["page"] == ref["page"]
                        and c["pdf_sha256"] == ref["pdf_sha256"]
                        and normalize(ref["quote"]) in normalize(c["quote"])
                        for ref in group
                        for c in finding["citations"]
                    )
                    for group in gold.get("evidence_groups", [])
                )
        rows.append(
            {
                "document_id": gold["document_id"],
                "field": gold["field"],
                "unique_field_present": len(matches) == 1,
                "value_check": bool(value_ok),
                "reference_evidence_check": bool(evidence_ok),
            }
        )
    return {
        "fields": rows,
        "extra_fields": len(extras),
        "all_checks_passed": bool(rows)
        and not extras
        and result.get("status") == "provenance_checked"
        and all(
            r["unique_field_present"] and r["value_check"] and r["reference_evidence_check"]
            for r in rows
        ),
    }


def summarize(rows: list[dict]) -> dict:
    fields = [f for row in rows for f in row["checks"]["fields"]]
    times = [r["result"]["metrics"]["total_seconds"] for r in rows if "metrics" in r["result"]]
    return {
        "prompts": len(rows),
        "base_tasks": len({r["base_task"] for r in rows}),
        "expected_fields": len(fields),
        "unique_fields_present": sum(f["unique_field_present"] for f in fields),
        "value_checks_passed": sum(f["value_check"] for f in fields),
        "reference_evidence_checks_passed": sum(f["reference_evidence_check"] for f in fields),
        "all_checks_passed": sum(r["checks"]["all_checks_passed"] for r in rows),
        "responses_with_extra_fields": sum(r["checks"]["extra_fields"] > 0 for r in rows),
        "provenance_passes": sum(r["result"].get("status") == "provenance_checked" for r in rows),
        "repairs_attempted": sum(len(r["result"].get("attempts", [])) > 1 for r in rows),
        "rule_recoveries": sum(len(r["result"].get("rule_recoveries", [])) for r in rows),
        "median_seconds": statistics.median(times) if times else None,
        "p95_seconds": sorted(times)[max(0, __import__("math").ceil(len(times) * 0.95) - 1)]
        if times
        else None,
    }


def check_freeze(path: Path) -> dict:
    freeze = read_json(path)
    changed = [name for name, sha in freeze["files"].items() if digest(ROOT / name) != sha]
    if changed:
        raise ValueError(f"Frozen configuration changed: {changed}")
    return freeze


def evaluate_quality(
    tasks_path: Path,
    output: Path,
    corpus_root: Path = ROOT,
    prompt_version: str = "v3",
    freeze_path: Path | None = None,
    replay_path: Path | None = None,
) -> dict:
    if output.exists():
        raise ValueError("Report already exists; choose a new output path to preserve run history")
    tasks = read_jsonl(tasks_path)
    split = {t["split"] for t in tasks}
    if len(split) != 1 or not tasks:
        raise ValueError("Evaluate one nonempty split at a time")
    if "test" in split:
        if freeze_path is None:
            raise ValueError("Held-out evaluation requires a frozen configuration")
        frozen = check_freeze(freeze_path)
        lock = read_json(ROOT / "data/evaluation/test_manifest.json")
        if digest(freeze_path) != lock["prediction_freeze_sha256"]:
            raise ValueError("Test seal refers to a different prediction freeze")
        if prompt_version not in frozen.get("allowed_prompt_versions", [frozen["prompt_version"]]):
            raise ValueError("Prompt version is outside the frozen comparison")
        if digest(corpus_root / "data/processed/chunks.jsonl") != lock["chunks_sha256"]:
            raise ValueError("Test index differs from the sealed source snapshot")
        if digest(tasks_path) != lock["tasks_sha256"]:
            raise ValueError("Test labels changed after sealing")
    replay = (
        {r["task_id"]: r["result"] for r in read_json(replay_path)["rows"]} if replay_path else None
    )
    if replay is None:
        from .pipeline import Pipeline
        from .retrieval import Retriever

        pipeline = Pipeline(Retriever(corpus_root), prompt_version=prompt_version)
    rows = []
    for task in tasks:
        try:
            result = (
                replay[task["id"]]
                if replay is not None
                else pipeline.answer(task["question"], task["documents"], "hybrid_expanded", 8)
            )
        except (httpx.HTTPError, ValueError, OSError, KeyError) as exc:
            # Preserve failed requests in the denominator and make partial runs inspectable.
            result = {
                "status": "request_failed",
                "findings": [],
                "error": f"{type(exc).__name__}: {exc}",
            }
        checks = score_result(task, result)
        rows.append(
            {
                "task_id": task["id"],
                "base_task": task["base_task"],
                "language": task["language"],
                "checks": checks,
                "result": result,
            }
        )
        report = {
            "created_at": datetime.now(UTC).isoformat(),
            "split": next(iter(split)),
            "human_validated": False,
            "prompt_version": prompt_version if replay is None else "from_replay",
            "labels": "agent-authored; human review pending",
            "metric_warning": "Field/value/reference checks, not human semantic accuracy. Language pairs are correlated.",
            "document_filter": "given_by_task",
            "requested": len(tasks),
            "completed": len(rows),
            "complete": len(rows) == len(tasks),
            "tasks_sha256": digest(tasks_path),
            "chunks_sha256": digest(corpus_root / "data/processed/chunks.jsonl"),
            "freeze_sha256": digest(freeze_path) if freeze_path else None,
            "replayed_from": str(replay_path.relative_to(ROOT)) if replay_path else None,
            "summary": summarize(rows),
            "by_language": {
                lang: summarize([r for r in rows if r["language"] == lang]) for lang in ("en", "tr")
            },
            "rows": rows,
        }
        write_json(output, report)
        print(f"{task['id']}: all_reference_checks={checks['all_checks_passed']}", flush=True)
    return report["summary"]
