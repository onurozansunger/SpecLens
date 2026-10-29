import pytest

from speclens.common import write_json, write_jsonl
from speclens.corpus import split_lines
from speclens.retrieval import Retriever


def corpus(tmp_path):
    rows = [
        {"id": "a:1", "document_id": "a", "text": "VIN input voltage 6-24 V"},
        {"id": "b:1", "document_id": "b", "text": "VIN input voltage 6-21 V"},
        {"id": "b:2", "document_id": "b", "text": "WiFi network Bluetooth antenna"},
    ]
    write_jsonl(tmp_path / "data/processed/chunks.jsonl", rows)
    return Retriever(tmp_path)


def test_document_filter_prevents_cross_product_retrieval(tmp_path):
    hits = corpus(tmp_path).search("input voltage", "bm25", 3, ["b"])
    assert {h["document_id"] for h in hits} == {"b"}
    assert hits[0]["id"] == "b:1"


def test_unknown_document_is_not_silently_ignored(tmp_path):
    with pytest.raises(ValueError, match="Unknown document"):
        corpus(tmp_path).search("voltage", "bm25", documents=["wrong"])


def test_changed_chunks_reject_stale_vector_index(tmp_path):
    retriever = corpus(tmp_path)
    write_json(tmp_path / "data/processed/embedding_manifest.json", {"chunks_sha256": "stale"})
    with pytest.raises(ValueError, match="rebuild"):
        retriever.search("voltage", "dense")


def test_chunking_does_not_lose_source_lines_or_numbers():
    text = "\n".join(f"Parameter {i}: minimum -40 maximum {i + 10}.5 °C" for i in range(40))
    blocks = split_lines(text, max_chars=200)
    assert all(len(block) <= 200 for block in blocks)
    assert all(line in "\n".join(blocks) for line in text.splitlines())
