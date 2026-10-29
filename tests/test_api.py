from types import SimpleNamespace

from fastapi.testclient import TestClient

from speclens.api import create_app


def test_api_rejects_unbounded_or_missing_document_requests():
    with TestClient(create_app(SimpleNamespace())) as client:
        assert (
            client.post("/answer", json={"question": "voltage", "documents": []}).status_code == 422
        )
        assert (
            client.post("/answer", json={"question": "x" * 1501, "documents": ["a"]}).status_code
            == 422
        )
        assert (
            client.post("/search", json={"question": "voltage", "limit": 1000}).status_code == 422
        )


def test_api_does_not_claim_worker_health_without_checking_it():
    with TestClient(create_app(SimpleNamespace())) as client:
        assert client.get("/health").json()["llm_worker_checked"] is False
