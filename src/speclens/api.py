from __future__ import annotations

from contextlib import asynccontextmanager
from decimal import Decimal
from pathlib import Path
from typing import Literal

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import Field
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .common import ROOT, read_json
from .evidence import StrictModel
from .pipeline import Pipeline


class SearchRequest(StrictModel):
    question: str = Field(min_length=1, max_length=1500)
    documents: list[str] = Field(default_factory=list, max_length=3)
    method: Literal["bm25", "dense", "hybrid", "hybrid_expanded"] = "hybrid_expanded"
    limit: int = Field(default=6, ge=1, le=20)


class AnswerRequest(StrictModel):
    question: str = Field(min_length=1, max_length=1500)
    documents: list[str] = Field(min_length=1, max_length=3)
    method: Literal["bm25", "dense", "hybrid", "hybrid_expanded"] = "hybrid_expanded"
    per_document: int = Field(default=8, ge=1, le=10)


class CompareRequest(StrictModel):
    documents: list[str] = Field(min_length=1, max_length=3)
    target: Decimal = Field(allow_inf_nan=False)
    unit: Literal["V", "mV", "kV"] = "V"
    method: Literal["bm25", "dense", "hybrid", "hybrid_expanded"] = "hybrid_expanded"


def create_app(pipeline: Pipeline | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app):
        app.state.pipeline = pipeline or Pipeline()
        yield

    app = FastAPI(title="SpecLens", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "testserver"]
    )
    app.mount("/static", StaticFiles(directory=Path(__file__).parent / "web/dist"), name="static")

    @app.get("/", include_in_schema=False)
    def home():
        return FileResponse(Path(__file__).parent / "web/dist/index.html")

    @app.get("/health")
    def health():
        return {"status": "ready", "llm_worker_checked": False}

    @app.get("/documents")
    def documents():
        manifest = read_json(ROOT / "data/raw/manifest.json")
        return [
            {
                "id": d["id"],
                "sku": d["sku"],
                "pages": d["pages"],
                "pdf_sha256": d["pdf_sha256"],
                "source": d["pdf_url"],
                "license": d["license"],
            }
            for d in manifest["documents"]
        ]

    @app.get("/documents/{document_id}/pdf")
    def pdf(document_id: str):
        from .documents import document_file

        try:
            path, _ = document_file(document_id)
            return FileResponse(path, media_type="application/pdf")
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/documents/{document_id}/pages/{page}.png")
    def page_image(document_id: str, page: int):
        from .documents import render_page

        try:
            return FileResponse(render_page(document_id, page), media_type="image/png")
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/compare-vin")
    def compare(request: CompareRequest):
        from .numeric import compare_vin_findings

        result = answer(
            AnswerRequest(
                question="What is the recommended VIN input voltage range? Include VIN in the exact quote.",
                documents=request.documents,
                method=request.method,
            )
        )
        result["comparison"] = compare_vin_findings(result, request.target, request.unit)
        return result

    @app.post("/search")
    def search(request: SearchRequest):
        try:
            return app.state.pipeline.retriever.search(
                request.question,
                request.method,
                request.limit,
                request.documents,
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except (FileNotFoundError, OSError) as exc:
            raise HTTPException(
                status_code=503, detail="Local index/model missing; run setup."
            ) from exc

    @app.post("/answer")
    def answer(request: AnswerRequest):
        try:
            return app.state.pipeline.answer(
                request.question,
                request.documents,
                request.method,
                request.per_document,
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except httpx.HTTPStatusError as exc:
            detail = "MLX worker rejected the request; reduce context size."
            raise HTTPException(status_code=502, detail=detail) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=503, detail="Start the local MLX worker on port 8011."
            ) from exc
        except (FileNotFoundError, OSError) as exc:
            raise HTTPException(
                status_code=503, detail="Local index/model missing; run setup."
            ) from exc

    return app


app = create_app()
