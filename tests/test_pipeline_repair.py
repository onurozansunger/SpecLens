import json

from speclens.pipeline import Pipeline


class Retriever:
    chunks_sha256 = "snapshot"

    def search(self, *args):
        return [
            {
                "id": "a:p1",
                "document_id": "a",
                "page": 1,
                "sha256": "hash",
                "text": "VIN range is 6–24 V.",
            }
        ]


class Tokenizer:
    def apply_chat_template(self, messages, **kwargs):
        return list(range(len(messages[1]["content"]) // 4))


def test_repair_is_bounded_and_retains_rejected_attempt():
    pipeline = Pipeline(Retriever(), prompt_version="v3")
    pipeline.tokenizer = Tokenizer()
    calls = []

    def generate(user, max_tokens):
        calls.append(json.loads(user))
        value = "6–48 V" if len(calls) == 1 else "6–24 V"
        return {
            "model": {"id": "test"},
            "metrics": {"generation_seconds": 0.1},
            "text": json.dumps(
                {
                    "findings": [
                        {
                            "document_id": "a",
                            "field": "vin_voltage",
                            "status": "stated",
                            "value": value,
                            "evidence_ids": ["e0000"],
                        }
                    ]
                }
            ),
        }

    pipeline._generate = generate
    result = pipeline.answer("What is the VIN range?", ["a"])
    assert len(calls) == 2
    assert "value_atoms_missing_from_citations" in calls[1]["validation_feedback"]
    assert result["status"] == "provenance_checked"
    assert result["findings"][0]["value"] == "6–24 V"
    assert result["attempts"][0]["rejected_findings"]
    assert result["metrics"]["total_generation_seconds"] == 0.2


def test_repeated_invalid_output_stops_after_one_repair():
    pipeline = Pipeline(Retriever(), prompt_version="v3")
    pipeline.tokenizer = Tokenizer()
    pipeline._generate = lambda *args: {
        "model": {},
        "metrics": {"generation_seconds": 0.1},
        "text": "bad output",
    }
    result = pipeline.answer("What is VIN?", ["a"])
    assert result["status"] == "invalid_model_output"
    assert len(result["attempts"]) == 2
    assert not result["findings"]
