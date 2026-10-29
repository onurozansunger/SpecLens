import pytest

from speclens.common import digest, write_json
from speclens.documents import document_file


def test_preview_refuses_changed_source_snapshot(tmp_path):
    path = tmp_path / "document.pdf"
    path.write_bytes(b"original PDF fixture")
    write_json(
        tmp_path / "data/raw/manifest.json",
        {"documents": [{"id": "fixture", "pdf_path": "document.pdf", "pdf_sha256": digest(path)}]},
    )
    assert document_file("fixture", tmp_path)[0] == path
    path.write_bytes(b"changed PDF fixture")
    with pytest.raises(ValueError, match="snapshot changed"):
        document_file("fixture", tmp_path)


def test_preview_document_id_is_not_a_filesystem_path(tmp_path):
    write_json(tmp_path / "data/raw/manifest.json", {"documents": []})
    with pytest.raises(ValueError, match="Unknown document"):
        document_file("../../etc/passwd", tmp_path)
