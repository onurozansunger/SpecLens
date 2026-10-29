import json

from speclens.pipeline import Pipeline


class CharacterTokenizer:
    def apply_chat_template(self, messages, **kwargs):
        return list(messages[1]["content"])


def test_budget_packing_keeps_whole_chunks_and_reports_omissions():
    pipeline = Pipeline(retriever=object(), prompt_version="v2")
    pipeline.tokenizer = CharacterTokenizer()
    chunks = [
        {"id": f"a:{i}", "document_id": "a", "page": i + 1, "text": str(i) * 1700} for i in range(4)
    ]
    selected, user, context, count, omitted = pipeline._pack("What is VIN?", ["a"], chunks)
    assert count <= 4096
    assert len(selected) == 2
    assert omitted == ["a:2", "a:3"]
    assert context[0]["text"] == chunks[0]["text"]
    assert json.loads(user)["question"] == "What is VIN?"
