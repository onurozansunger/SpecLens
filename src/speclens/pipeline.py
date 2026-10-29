from __future__ import annotations

import hashlib
import json
import os
import time

import httpx
from pydantic import ValidationError

from .capacity import VERSION as CAPACITY_VERSION
from .capacity import recover_capacity
from .common import ROOT, read_json
from .evidence import evidence_lines, parse_extraction, parse_span_extraction, validate_evidence
from .intent import VERSION as INTENT_VERSION
from .intent import possible_capacity_evidence, requested_fields
from .retrieval import Retriever

PROMPT_VERSION = os.environ.get("SPECLENS_PROMPT_VERSION", "v3")
if PROMPT_VERSION not in {"v1", "v2", "v3"}:
    raise ValueError("SPECLENS_PROMPT_VERSION must be v1, v2 or v3")
SYSTEM = (ROOT / f"configs/prompts/extraction-{PROMPT_VERSION}.txt").read_text()


class Pipeline:
    def __init__(
        self,
        retriever: Retriever | None = None,
        worker_url: str = "http://127.0.0.1:8011",
        prompt_version: str | None = None,
    ):
        self.retriever = retriever or Retriever()
        self.worker_url = worker_url
        self.tokenizer = None
        self.prompt_version = prompt_version or PROMPT_VERSION
        if self.prompt_version not in {"v1", "v2", "v3"}:
            raise ValueError("Unknown prompt version")
        self.system = (ROOT / f"configs/prompts/extraction-{self.prompt_version}.txt").read_text()

    def _count(self, user: str) -> int:
        return len(
            self.tokenizer.apply_chat_template(
                [{"role": "system", "content": self.system}, {"role": "user", "content": user}],
                tokenize=True,
                add_generation_prompt=True,
                return_dict=False,
            )
        )

    def _pack(self, question: str, documents: list[str], candidates: list[dict]):
        if self.tokenizer is None:
            from transformers import AutoTokenizer

            spec = read_json(ROOT / "configs/models.json")["models"]["llm"]
            self.tokenizer = AutoTokenizer.from_pretrained(
                spec["repo_id"],
                revision=spec["revision"],
                local_files_only=True,
                trust_remote_code=False,
            )

        def serialize(chunks):
            context = [
                {
                    "chunk_id": c["id"],
                    "document_id": c["document_id"],
                    "physical_page": c["page"],
                    "text": c["text"],
                }
                for c in chunks
            ]
            payload = {"question": question, "requested_documents": documents}
            if self.prompt_version == "v3":
                payload["requested_fields"] = requested_fields(question)
                payload["untrusted_evidence"] = evidence_lines(chunks)[0]
            else:
                payload["untrusted_evidence"] = context
            user = json.dumps(payload, ensure_ascii=False)
            count = self._count(user)
            return user, context, count

        selected, omitted = [], []
        # Candidates arrive in round-robin document order to avoid starving a product.
        for candidate in candidates:
            if serialize(selected + [candidate])[2] <= (
                3584 if self.prompt_version == "v3" else 4096
            ):
                selected.append(candidate)
            else:
                omitted.append(candidate["id"])
        user, context, count = serialize(selected)
        if not selected or count > 4096:
            raise ValueError("Question and evidence cannot fit the 4096-token budget")
        return selected, user, context, count, omitted

    def _generate(self, user: str, max_tokens: int) -> dict:
        with httpx.Client(timeout=httpx.Timeout(120, connect=5), trust_env=False) as client:
            response = client.post(
                self.worker_url + "/generate",
                json={
                    "system": self.system,
                    "user": user,
                    "max_tokens": max_tokens,
                    "stop_at_json_object": self.prompt_version == "v3",
                },
            )
            response.raise_for_status()
            return response.json()

    def answer(
        self,
        question: str,
        documents: list[str],
        method: str = "hybrid_expanded",
        per_document: int = 8,
    ) -> dict:
        if not question.strip() or len(question) > 1500:
            raise ValueError("Question must contain between 1 and 1500 characters")
        if not 1 <= len(documents) <= 3 or len(set(documents)) != len(documents):
            raise ValueError("Select between 1 and 3 distinct documents")
        if not 1 <= per_document <= 10:
            raise ValueError("per_document must be between 1 and 10")
        start = time.perf_counter()
        groups = []
        for document in documents:
            groups.append(self.retriever.search(question, method, per_document, [document]))
        candidates = [group[i] for i in range(per_document) for group in groups if i < len(group)]
        chunks, user, context, input_tokens, omitted = self._pack(question, documents, candidates)
        retrieval_seconds = time.perf_counter() - start
        fields = requested_fields(question) if self.prompt_version == "v3" else []
        spans = evidence_lines(chunks)[1] if self.prompt_version == "v3" else {}
        attempts = []
        for attempt in range(2 if self.prompt_version == "v3" else 1):
            supplied_ids = {
                line.split(":", 1)[0]
                for block in json.loads(user).get("untrusted_evidence", [])
                for line in block.get("lines", [])
            }
            active_spans = {sid: spans[sid] for sid in supplied_ids if sid in spans}
            generated = self._generate(
                user, 1024 if len(documents) * max(1, len(fields)) > 1 else 512
            )
            try:
                parsed = (
                    parse_span_extraction(generated["text"], active_spans)
                    if self.prompt_version == "v3"
                    else parse_extraction(generated["text"])
                )
                validated = validate_evidence(
                    parsed,
                    chunks,
                    set(documents),
                    fields,
                    check_claim_atoms=self.prompt_version == "v3",
                )
                covered = {(f["document_id"], f["field"]) for f in validated["findings"]}
                missing_fields = [
                    {"document_id": d, "field": f}
                    for d in documents
                    for f in fields
                    if (d, f) not in covered
                ]
                missing = sorted(set(documents) - {d for d, _ in covered})
                review_hints = []
                chunk_documents = {c["id"]: c["document_id"] for c in chunks}
                for finding in validated["findings"]:
                    if finding["status"] == "not_stated":
                        candidates = [
                            sid
                            for sid, span in spans.items()
                            if chunk_documents[span["chunk_id"]] == finding["document_id"]
                            and possible_capacity_evidence(finding["field"], span["quote"])
                        ]
                        if candidates:
                            review_hints.append(
                                {
                                    "document_id": finding["document_id"],
                                    "field": finding["field"],
                                    "recheck_evidence_ids": candidates[:3],
                                }
                            )
                status = (
                    "review_required"
                    if validated["rejected_findings"] or missing or missing_fields or review_hints
                    else "provenance_checked"
                )
                answer = {
                    **validated,
                    "missing_documents": missing,
                    "missing_fields": missing_fields,
                    "status": status,
                    "review_hints": review_hints,
                }
            except (ValueError, ValidationError) as exc:
                answer = {
                    "status": "invalid_model_output",
                    "findings": [],
                    "error": str(exc),
                    "missing_documents": documents,
                    "rejected_findings": [],
                }
            attempts.append(
                {
                    "number": attempt + 1,
                    "raw_output": generated["text"],
                    "planned_input_tokens": self._count(user),
                    "supplied_evidence_ids": sorted(active_spans),
                    "metrics": generated["metrics"],
                    **answer,
                }
            )
            if answer["status"] == "provenance_checked":
                break
            feedback = json.dumps(
                {
                    "error": answer.get("error", ""),
                    "rejected": [
                        {"field": r["finding"]["field"], "reasons": r["reasons"]}
                        for r in answer.get("rejected_findings", [])
                    ],
                    "missing_fields": answer.get("missing_fields", []),
                    "missing_documents": answer.get("missing_documents", []),
                    "review_hints": answer.get("review_hints", []),
                },
                ensure_ascii=False,
            )[:1200]
            payload = json.loads(user)
            payload["validation_feedback"] = feedback
            if answer.get("review_hints") and len(fields) == 1 and len(documents) == 1:
                # One focused reread for a possible false abstention; no new facts are injected.
                hinted = {
                    sid for hint in answer["review_hints"] for sid in hint["recheck_evidence_ids"]
                }
                focused = []
                for block in payload["untrusted_evidence"]:
                    lines = [line for line in block["lines"] if line.split(":", 1)[0] in hinted]
                    if lines:
                        focused.append({**block, "lines": lines})
                if focused:
                    payload["untrusted_evidence"] = focused
            user = json.dumps(payload, ensure_ascii=False)
            if self._count(user) > 4096:
                break
        # Prefer complete validated output; a failed repair cannot replace better evidence.
        selected_attempt = max(
            attempts,
            key=lambda a: (
                a["status"] == "provenance_checked",
                len(a["findings"]),
                -len(a.get("rejected_findings", [])),
                a["number"],
            ),
        )
        final_answer = {**selected_attempt, "findings": list(selected_attempt["findings"])}
        corrections = []
        if self.prompt_version == "v3":
            for index, finding in enumerate(final_answer["findings"]):
                if finding["status"] != "not_stated":
                    continue
                recovered = recover_capacity(
                    question, finding["field"], finding["document_id"], spans, chunks
                )
                if recovered is None:
                    continue
                checked = validate_evidence(
                    parse_extraction(json.dumps({"findings": [recovered]})),
                    chunks,
                    set(documents),
                    fields,
                    check_claim_atoms=True,
                )
                if checked["findings"] and not checked["rejected_findings"]:
                    final_answer["findings"][index] = {
                        **checked["findings"][0],
                        "extraction_method": CAPACITY_VERSION,
                    }
                    corrections.append(
                        {
                            "document_id": finding["document_id"],
                            "field": finding["field"],
                            "from_status": "not_stated",
                            "method": CAPACITY_VERSION,
                        }
                    )
            corrected = {(c["document_id"], c["field"]) for c in corrections}
            final_answer["review_hints"] = [
                h
                for h in final_answer.get("review_hints", [])
                if (h["document_id"], h["field"]) not in corrected
            ]
            if corrections and not any(
                final_answer.get(k)
                for k in (
                    "rejected_findings",
                    "missing_fields",
                    "missing_documents",
                    "review_hints",
                )
            ):
                final_answer["status"] = "provenance_checked"
        result = {
            "question": question,
            "documents": documents,
            "method": method,
            "evidence": context,
            "model": generated["model"],
            "metrics": {
                **selected_attempt["metrics"],
                "retrieval_seconds": retrieval_seconds,
                "total_seconds": time.perf_counter() - start,
                "attempts": len(attempts),
                "total_generation_seconds": sum(
                    a["metrics"]["generation_seconds"] for a in attempts
                ),
            },
            "chunks_sha256": self.retriever.chunks_sha256,
            "prompt_sha256": hashlib.sha256(self.system.encode()).hexdigest(),
            "prompt_version": self.prompt_version,
            "intent_version": INTENT_VERSION if fields else None,
            "requested_fields": fields,
            "planned_input_tokens": selected_attempt["planned_input_tokens"],
            "initial_input_tokens": input_tokens,
            "omitted_chunk_ids": omitted,
            "per_document_requested": per_document,
            "attempts": attempts,
            "selected_attempt": selected_attempt["number"],
            "evidence_spans": spans,
            "rule_recoveries": corrections,
        }
        return {
            **result,
            **{
                k: v
                for k, v in final_answer.items()
                if k not in {"number", "metrics", "planned_input_tokens"}
            },
        }
