"""Verify a local corpus without downloading or overwriting anything."""

import json

from speclens.common import ROOT, digest, read_json, write_json


def main():
    manifest = read_json(ROOT / "data/raw/manifest.json")
    checks = []
    for source in manifest["documents"]:
        checks.append(
            {
                "document_id": source["id"],
                "pdf_matches": digest(ROOT / source["pdf_path"]) == source["pdf_sha256"],
                "markdown_matches": digest(ROOT / source["source_path_local"])
                == source["source_sha256"],
            }
        )
    embedding = read_json(ROOT / "data/processed/embedding_manifest.json")
    result = {
        "sources": checks,
        "chunk_snapshot_matches": digest(ROOT / "data/processed/chunks.jsonl")
        == embedding["chunks_sha256"],
        "vector_snapshot_matches": digest(ROOT / "data/processed/embeddings.npy")
        == embedding["vectors_sha256"],
    }
    result["valid"] = (
        all(c["pdf_matches"] and c["markdown_matches"] for c in checks)
        and result["chunk_snapshot_matches"]
        and result["vector_snapshot_matches"]
    )
    write_json(ROOT / "reports/snapshot_check.json", result)
    print(json.dumps(result, indent=2))
    if not result["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
