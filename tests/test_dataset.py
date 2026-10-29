from speclens.dataset import validate_dataset


def test_related_boards_and_translation_pairs_cannot_cross_splits():
    docs = [{"id": "board-rev1", "family": "board"}, {"id": "board-rev2", "family": "board"}]
    tasks = [
        {
            "id": "question-en",
            "base_task": "question",
            "split": "train",
            "documents": ["board-rev1"],
            "canonical_evidence": [],
        },
        {
            "id": "question-tr",
            "base_task": "question",
            "split": "test",
            "documents": ["board-rev2"],
            "canonical_evidence": [],
        },
    ]
    result = validate_dataset(tasks, docs, [])
    assert not result["valid"]
    assert any("family crosses" in e for e in result["errors"])
    assert any("translations cross" in e for e in result["errors"])
