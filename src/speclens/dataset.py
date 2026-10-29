from __future__ import annotations

from collections import defaultdict

from .common import ROOT, normalize, read_json, read_jsonl


def validate_dataset(tasks: list[dict], documents: list[dict], pages: list[dict]) -> dict:
    sources = {d["id"]: d for d in documents}
    page_map = {(p["document_id"], p["page"]): p for p in pages}
    family_splits, task_splits, source_splits = defaultdict(set), defaultdict(set), defaultdict(set)
    seen, errors = set(), []
    for task in tasks:
        if task["id"] in seen:
            errors.append(f"Duplicate task id: {task['id']}")
        seen.add(task["id"])
        task_splits[task["base_task"]].add(task["split"])
        for document in task["documents"]:
            if document not in sources:
                errors.append(f"Unknown document: {document}")
                continue
            family_splits[sources[document]["family"]].add(task["split"])
            source = sources[document]
            if source.get("split") and source["split"] != task["split"]:
                errors.append(f"Document split disagrees with task: {task['id']}: {document}")
            if source.get("expected_pdf_sha256"):
                source_splits[source["expected_pdf_sha256"]].add(task["split"])
        expected_keys = [(f["document_id"], f["field"]) for f in task.get("expected_findings", [])]
        if len(expected_keys) != len(set(expected_keys)):
            errors.append(f"Duplicate expected field: {task['id']}")
        if any(d not in task["documents"] for d, _ in expected_keys):
            errors.append(f"Expected finding from a different document: {task['id']}")
        for evidence in task["canonical_evidence"]:
            page = page_map.get((evidence["document_id"], evidence["page"]))
            if not page or page["sha256"] != evidence["pdf_sha256"]:
                errors.append(f"Source snapshot mismatch: {task['id']}")
            elif normalize(evidence["quote"]) not in normalize(page["text"]):
                errors.append(f"Quote missing: {task['id']}")
            if evidence["document_id"] not in task["documents"]:
                errors.append(f"Evidence from a different task document: {task['id']}")
    for name, splits in family_splits.items():
        if len(splits) > 1:
            errors.append(f"Product family crosses splits: {name}: {sorted(splits)}")
    for name, splits in task_splits.items():
        if len(splits) > 1:
            errors.append(f"Task translations cross splits: {name}")
    for sha, splits in source_splits.items():
        if len(splits) > 1:
            errors.append(f"Same PDF snapshot crosses splits under different IDs: {sha}")
    return {
        "valid": not errors,
        "errors": errors,
        "prompts": len(tasks),
        "base_tasks": len(task_splits),
        "families": len(family_splits),
        "human_reviewed": sum(t.get("review_status") == "human_verified" for t in tasks),
    }


def check_pilot():
    return validate_dataset(
        read_jsonl(ROOT / "data/evaluation/pilot.jsonl"),
        read_json(ROOT / "configs/corpus.json")["documents"],
        read_jsonl(ROOT / "data/processed/pages.jsonl"),
    )
