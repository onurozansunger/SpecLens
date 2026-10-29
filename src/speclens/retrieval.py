from __future__ import annotations

import re
import time
from pathlib import Path
from threading import Lock

import numpy as np
from rank_bm25 import BM25Okapi

from .common import ROOT, digest, read_json, read_jsonl, write_json
from .query import expand_query


def tokens(text: str) -> list[str]:
    return re.findall(r"[\w]+(?:[.\-][\w]+)*", text.casefold())


def _encoder(root: Path, device: str, offline: bool):
    from sentence_transformers import SentenceTransformer

    model = read_json(root / "configs/models.json")["models"]["embedding"]
    return SentenceTransformer(
        model["repo_id"],
        revision=model["revision"],
        device=device,
        local_files_only=offline,
        trust_remote_code=False,
    )


def build_embeddings(root: Path = ROOT, device: str = "mps", offline: bool = False) -> dict:
    import torch

    if device == "mps" and not torch.backends.mps.is_available():
        raise RuntimeError("MPS is unavailable. Select --device cpu explicitly.")
    chunks_path = root / "data/processed/chunks.jsonl"
    chunks = read_jsonl(chunks_path)
    encoder = _encoder(root, device, offline)
    texts = [f"passage: {c['document_id']}\n{c['text']}" for c in chunks]
    lengths = [len(encoder.tokenizer.encode(t, add_special_tokens=True)) for t in texts]
    oversized = [c["id"] for c, length in zip(chunks, lengths) if length > 512]
    if oversized:
        raise ValueError(
            f"Chunks exceed E5's token budget; rechunk before indexing: {oversized[:8]}"
        )
    start = time.perf_counter()
    vectors = encoder.encode(
        texts,
        batch_size=16,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    ).astype(np.float32)
    if not np.isfinite(vectors).all():
        raise ValueError("Embedding computation produced non-finite values")
    if device == "mps":
        torch.mps.synchronize()
    seconds = time.perf_counter() - start
    np.save(root / "data/processed/embeddings.npy", vectors, allow_pickle=False)
    result = {
        "model": read_json(root / "configs/models.json")["models"]["embedding"],
        "device": device,
        "chunks": len(chunks),
        "dimensions": vectors.shape[1],
        "max_input_tokens": max(lengths),
        "embedding_seconds": seconds,
        "chunks_sha256": digest(chunks_path),
        "vectors_sha256": digest(root / "data/processed/embeddings.npy"),
    }
    write_json(root / "data/processed/embedding_manifest.json", result)
    return result


class Retriever:
    def __init__(self, root: Path = ROOT, device: str = "cpu"):
        self.root, self.device = root, device
        self.chunks = read_jsonl(root / "data/processed/chunks.jsonl")
        if not self.chunks:
            raise ValueError("No chunks available; run extraction first")
        self.chunks_sha256 = digest(root / "data/processed/chunks.jsonl")
        self.bm25 = BM25Okapi([tokens(c["document_id"] + " " + c["text"]) for c in self.chunks])
        self.encoder = None
        self.vectors = None
        self.encoder_lock = Lock()

    def _load_dense(self):
        if self.encoder is not None:
            return
        manifest = read_json(self.root / "data/processed/embedding_manifest.json")
        if manifest["chunks_sha256"] != self.chunks_sha256:
            raise ValueError("Chunk content changed: rebuild the embeddings")
        if manifest["vectors_sha256"] != digest(self.root / "data/processed/embeddings.npy"):
            raise ValueError("Embedding integrity check failed")
        if manifest["model"] != read_json(self.root / "configs/models.json")["models"]["embedding"]:
            raise ValueError("Embedding model changed: rebuild the index")
        self.vectors = np.load(self.root / "data/processed/embeddings.npy", allow_pickle=False)
        if len(self.vectors) != len(self.chunks):
            raise ValueError("Embedding and chunk counts do not match")
        self.encoder = _encoder(self.root, self.device, offline=True)

    def search(
        self, query: str, method: str = "hybrid", limit: int = 6, documents: list[str] | None = None
    ) -> list[dict]:
        if method not in {"bm25", "dense", "hybrid", "hybrid_expanded"}:
            raise ValueError("Unknown retrieval method")
        if not query.strip() or not 1 <= limit <= 20:
            raise ValueError("A nonempty query and limit between 1 and 20 are required")
        known = {c["document_id"] for c in self.chunks}
        if documents and not set(documents).issubset(known):
            raise ValueError("Unknown document filter")
        eligible = np.array(
            [
                i
                for i, c in enumerate(self.chunks)
                if not documents or c["document_id"] in documents
            ],
            dtype=int,
        )
        retrieval_query = expand_query(query) if method == "hybrid_expanded" else query
        lexical = self.bm25.get_scores(tokens(retrieval_query))
        ranks = [eligible[np.argsort(-lexical[eligible], kind="stable")]]
        dense = None
        if method != "bm25":
            with self.encoder_lock:
                self._load_dense()
                prefixed_query = "query: " + retrieval_query
                if (
                    len(self.encoder.tokenizer.encode(prefixed_query, add_special_tokens=True))
                    > 512
                ):
                    raise ValueError("Query exceeds E5's 512-token budget; shorten the question")
                q = self.encoder.encode(
                    [prefixed_query], normalize_embeddings=True, convert_to_numpy=True
                )[0]
            dense = self.vectors @ q
            ranks.append(eligible[np.argsort(-dense[eligible], kind="stable")])
        if method == "bm25":
            scores = lexical
        elif method == "dense":
            scores = dense
        else:
            scores = np.zeros(len(self.chunks), dtype=float)
            for ranking in ranks:
                for rank, idx in enumerate(ranking[:100], start=1):
                    scores[idx] += 1 / (60 + rank)
        ordered = eligible[np.argsort(-scores[eligible], kind="stable")]
        return [
            {
                **self.chunks[int(idx)],
                "score": float(scores[idx]),
                "method": method,
                "retrieval_query": retrieval_query,
            }
            for idx in ordered[:limit]
        ]
