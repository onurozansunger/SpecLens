"""Native macOS MLX worker. Run with environments/llm's locked environment."""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import threading
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from huggingface_hub import snapshot_download
from pydantic import BaseModel, ConfigDict, Field

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from speclens.framing import complete_json_object


class GenerateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    system: str = Field(min_length=1, max_length=16000)
    user: str = Field(min_length=1, max_length=24000)
    max_tokens: int = Field(default=512, ge=1, le=1024)
    stop_at_json_object: bool = False


class Engine:
    def __init__(self, offline: bool = True):
        import mlx.core as mx
        from mlx_lm import load

        if platform.machine() != "arm64" or not mx.metal.is_available():
            raise RuntimeError("This worker requires native arm64 macOS with Metal.")
        self.spec = json.loads((ROOT / "configs/models.json").read_text())["models"]["llm"]
        path = snapshot_download(
            repo_id=self.spec["repo_id"],
            revision=self.spec["revision"],
            local_files_only=offline,
            allow_patterns=["*.json", "*.safetensors", "*.model", "*.txt", "*.jinja"],
        )
        start = time.perf_counter()
        self.model, self.tokenizer = load(path, trust_remote_code=False)
        mx.eval(self.model.parameters())
        self.load_seconds = time.perf_counter() - start
        self.lock = threading.Lock()
        self.requests = 0

    def run(self, request: GenerateRequest) -> dict:
        import mlx.core as mx
        import psutil
        from mlx_lm import stream_generate
        from mlx_lm.sample_utils import make_sampler

        # Concurrent API calls queue here; no simultaneous GPU generation.
        with self.lock:
            prompt = self.tokenizer.apply_chat_template(
                [
                    {"role": "system", "content": request.system},
                    {"role": "user", "content": request.user},
                ],
                tokenize=True,
                add_generation_prompt=True,
                return_dict=False,
            )
            if len(prompt) > 4096:
                raise ValueError(f"Input has {len(prompt)} tokens; worker limit is 4096.")
            mx.reset_peak_memory()
            start = time.perf_counter()
            first_token_seconds = None
            output = []
            last = None
            framed = None
            for response in stream_generate(
                self.model,
                self.tokenizer,
                prompt,
                max_tokens=request.max_tokens,
                sampler=make_sampler(temp=0),
            ):
                if first_token_seconds is None:
                    first_token_seconds = time.perf_counter() - start
                output.append(response.text)
                last = response
                if request.stop_at_json_object:
                    framed = complete_json_object("".join(output))
                    if framed is not None:
                        break
            mx.synchronize()
            elapsed = time.perf_counter() - start
            self.requests += 1
            result = {
                "text": framed if framed is not None else "".join(output),
                "model": self.spec,
                "backend": "mlx-metal",
                "metrics": {
                    "input_tokens": len(prompt),
                    "output_tokens": last.generation_tokens,
                    "generation_tokens_per_second": last.generation_tps,
                    "prompt_tokens_per_second": last.prompt_tps,
                    "first_token_seconds": first_token_seconds,
                    "generation_seconds": elapsed,
                    "model_load_seconds": self.load_seconds,
                    "mlx_peak_allocation_bytes": mx.get_peak_memory(),
                    "process_rss_bytes": psutil.Process().memory_info().rss,
                    "finish_reason": "json_complete" if framed is not None else last.finish_reason,
                    "request_number": self.requests,
                },
            }
            mx.clear_cache()
            return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["download", "smoke", "serve"])
    parser.add_argument("--port", type=int, default=8011)
    args = parser.parse_args()
    if args.command == "download":
        spec = json.loads((ROOT / "configs/models.json").read_text())["models"]["llm"]
        path = snapshot_download(
            repo_id=spec["repo_id"],
            revision=spec["revision"],
            allow_patterns=["*.json", "*.safetensors", "*.model", "*.txt", "*.jinja"],
        )
        print(path)
        return
    os.environ["HF_HUB_OFFLINE"] = "1"
    engine = Engine(offline=True)
    if args.command == "smoke":
        result = engine.run(
            GenerateRequest(
                system="Return only valid JSON. Copy facts only from the supplied evidence.",
                user='Evidence: Recommended input voltage (VIN) is 6-24 V. Return {"min":number,"max":number,"unit":string}.',
                max_tokens=96,
            )
        )
        result["check"] = json.loads(result["text"]) == {"min": 6, "max": 24, "unit": "V"}
        result["python"] = platform.python_version()
        result["architecture"] = platform.machine()
        (ROOT / "reports").mkdir(exist_ok=True)
        (ROOT / "reports/llm_smoke.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
        if not result["check"]:
            raise SystemExit("Model smoke response did not match the supplied evidence.")
        return
    app = FastAPI(title="SpecLens local MLX worker")

    @app.get("/health")
    def health():
        return {"status": "ready", "backend": "mlx-metal", "model": engine.spec}

    @app.post("/generate")
    def generate(request: GenerateRequest):
        try:
            return engine.run(request)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=args.port, workers=1)


if __name__ == "__main__":
    main()
