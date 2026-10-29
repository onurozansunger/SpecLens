"""Create, verify or restore a source-only corpus archive against pinned hashes."""

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

from speclens.common import ROOT, digest, read_json


def expected_files():
    files, manifests = {}, {}
    for config, prefix in [
        ("configs/corpus.json", ""),
        ("configs/test_corpus.json", "data/heldout/"),
    ]:
        docs = read_json(ROOT / config)["documents"]
        manifests[prefix + "data/raw/manifest.json"] = (docs, prefix)
        for doc in docs:
            files[prefix + f"data/raw/{doc['id']}/document.pdf"] = doc["expected_pdf_sha256"]
            files[prefix + f"data/raw/{doc['id']}/source.md"] = doc["expected_source_sha256"]
    return files, manifests


def verified_members(archive):
    files, manifests = expected_files()
    expected = set(files) | set(manifests) | {"THIRD_PARTY.md"}
    names = archive.namelist()
    if len(names) != len(set(names)) or set(names) != expected:
        raise ValueError("Archive must contain exactly the allowlisted corpus members")
    payloads = {}
    for name in names:
        info = archive.getinfo(name)
        if info.file_size > 50 * 1024 * 1024:
            raise ValueError("Oversized archive member")
        data = archive.read(name)
        if name in files and hashlib.sha256(data).hexdigest() != files[name]:
            raise ValueError(f"Snapshot hash mismatch: {name}")
        payloads[name] = data
    for name, (documents, _) in manifests.items():
        records = json.loads(payloads[name])["documents"]
        if {r["id"] for r in records} != {d["id"] for d in documents} or len(records) != len(
            documents
        ):
            raise ValueError("Manifest document set differs from pinned corpus")
        by_id = {r["id"]: r for r in records}
        for doc in documents:
            row = by_id[doc["id"]]
            required = {
                "pdf_path": f"data/raw/{doc['id']}/document.pdf",
                "source_path_local": f"data/raw/{doc['id']}/source.md",
                "pdf_sha256": doc["expected_pdf_sha256"],
                "source_sha256": doc["expected_source_sha256"],
                "pages": doc["expected_pages"],
                "status": "downloaded",
            }
            if any(row.get(k) != v for k, v in required.items()):
                raise ValueError("Manifest paths or snapshot metadata differ from pinned corpus")
    return payloads


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["create", "verify", "restore"])
    parser.add_argument("--file", type=Path, default=ROOT / "dist/speclens-corpus-2026-10-29.zip")
    args = parser.parse_args()
    if args.command == "create":
        if args.file.exists():
            raise SystemExit("Archive exists; choose another filename.")
        files, manifests = expected_files()
        for name, sha in files.items():
            if digest(ROOT / name) != sha:
                raise ValueError(f"Local source changed: {name}")
        args.file.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(
            args.file, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6
        ) as archive:
            for name in sorted(set(files) | set(manifests) | {"THIRD_PARTY.md"}):
                archive.write(ROOT / name, name)
    with zipfile.ZipFile(args.file) as archive:
        members = verified_members(archive)
    if args.command == "restore":
        for name, data in members.items():
            if name == "THIRD_PARTY.md":
                continue
            path = ROOT / name
            if path.exists() and path.read_bytes() != data:
                raise ValueError(f"Refusing to overwrite a different existing file: {name}")
        for name, data in members.items():
            if name != "THIRD_PARTY.md":
                path = ROOT / name
                path.parent.mkdir(parents=True, exist_ok=True)
                if not path.exists():
                    path.write_bytes(data)
    print(
        json.dumps(
            {
                "verified": True,
                "members": len(members),
                "archive": args.file.name,
                "sha256": digest(args.file),
                "bytes": args.file.stat().st_size,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
