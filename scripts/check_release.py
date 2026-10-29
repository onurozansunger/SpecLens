"""Check sealed benchmark metadata; --local also checks downloaded source text."""

import argparse
import json

from speclens.benchmark import check_freeze
from speclens.common import ROOT, digest, read_json, read_jsonl
from speclens.dataset import validate_dataset


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true")
    args = parser.parse_args()
    check_freeze(ROOT / "configs/release_freeze.json")
    seal = read_json(ROOT / "data/evaluation/test_manifest.json")
    assert digest(ROOT / "data/evaluation/test.jsonl") == seal["tasks_sha256"]
    assert digest(ROOT / "configs/release_freeze.json") == seal["prediction_freeze_sha256"]
    development = read_jsonl(ROOT / "data/evaluation/development.jsonl")
    test = read_jsonl(ROOT / "data/evaluation/test.jsonl")
    dev_docs = read_json(ROOT / "configs/corpus.json")["documents"]
    test_docs = read_json(ROOT / "configs/test_corpus.json")["documents"]
    assert not ({d["family"] for d in dev_docs} & {d["family"] for d in test_docs})
    assert not (
        {d["expected_pdf_sha256"] for d in dev_docs} & {d["expected_pdf_sha256"] for d in test_docs}
    )
    documents = {d["id"]: d for d in dev_docs + test_docs}
    pairs = {}
    for task in development + test:
        pairs.setdefault(task["base_task"], []).append(task)
        assert all(documents[d]["split"] == task["split"] for d in task["documents"])
        for ref in task["canonical_evidence"]:
            source = documents[ref["document_id"]]
            assert ref["pdf_sha256"] == source["expected_pdf_sha256"]
            assert 1 <= ref["page"] <= source["expected_pages"]
    for pair in pairs.values():
        assert len(pair) == 2 and {t["language"] for t in pair} == {"en", "tr"}
        assert pair[0]["expected_findings"] == pair[1]["expected_findings"]
        assert pair[0]["split"] == pair[1]["split"]
    result = {
        "valid": True,
        "development_prompts": len(development),
        "test_prompts": len(test),
        "test_base_tasks": len({t["base_task"] for t in test}),
        "test_families": len(test_docs),
        "human_reviewed": 0,
        "literal_source_check": "not run (metadata only)",
    }
    if args.local:
        pages = read_jsonl(ROOT / "data/processed/pages.jsonl") + read_jsonl(
            ROOT / "data/heldout/data/processed/pages.jsonl"
        )
        checks = validate_dataset(development + test, dev_docs + test_docs, pages)
        assert checks["valid"], checks
        assert digest(ROOT / "data/heldout/data/processed/chunks.jsonl") == seal["chunks_sha256"]
        result["literal_source_check"] = "passed"
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
