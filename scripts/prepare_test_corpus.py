"""Prepare the isolated test corpus; never add its labels to the retrieval index."""

import argparse
import shutil

from speclens.common import ROOT, read_json, write_json
from speclens.corpus import extract_corpus, fetch_corpus


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pin", action="store_true", help="Authoring only: pin newly acquired snapshots"
    )
    parser.add_argument("--embed", action="store_true")
    args = parser.parse_args()
    root = ROOT / "data/heldout"
    (root / "configs").mkdir(parents=True, exist_ok=True)
    config_path = ROOT / "configs/test_corpus.json"
    config = read_json(config_path)
    if not args.pin and any("expected_pdf_sha256" not in d for d in config["documents"]):
        raise SystemExit("Unpinned test corpus: complete snapshot authoring first.")
    shutil.copyfile(config_path, root / "configs/corpus.json")
    shutil.copyfile(ROOT / "configs/models.json", root / "configs/models.json")
    print(fetch_corpus(root), flush=True)
    if args.pin:
        manifest = read_json(root / "data/raw/manifest.json")
        acquired = {d["id"]: d for d in manifest["documents"]}
        for document in config["documents"]:
            source = acquired[document["id"]]
            document.update(
                expected_pdf_sha256=source["pdf_sha256"],
                expected_source_sha256=source["source_sha256"],
                expected_pages=source["pages"],
            )
        write_json(config_path, config)
        shutil.copyfile(config_path, root / "configs/corpus.json")
    print(extract_corpus(root), flush=True)
    if args.embed:
        from speclens.retrieval import build_embeddings

        print(build_embeddings(root, device="cpu", offline=True), flush=True)


if __name__ == "__main__":
    main()
