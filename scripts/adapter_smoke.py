"""Verify that the synthetic compatibility adapter reloads; not a model-quality test."""

import json
import os
import time
from pathlib import Path

os.environ["HF_HUB_OFFLINE"] = "1"

import mlx.core as mx
from huggingface_hub import snapshot_download
from mlx_lm import generate, load
from mlx_lm.sample_utils import make_sampler

ROOT = Path(__file__).resolve().parents[1]
spec = json.loads((ROOT / "configs/models.json").read_text())["models"]["llm"]
path = snapshot_download(
    spec["repo_id"],
    revision=spec["revision"],
    local_files_only=True,
    allow_patterns=["*.json", "*.safetensors", "*.model", "*.txt", "*.jinja"],
)
fixture = json.loads(
    (ROOT / "data/training/synthetic-smoke/valid.jsonl").read_text().splitlines()[0]
)
started = time.perf_counter()
model, tokenizer = load(
    path, adapter_path=str(ROOT / "models/adapters/synthetic-smoke"), trust_remote_code=False
)
prompt = tokenizer.apply_chat_template(
    fixture["messages"][:-1], tokenize=True, add_generation_prompt=True, return_dict=False
)
text = generate(model, tokenizer, prompt=prompt, max_tokens=512, sampler=make_sampler(temp=0))
mx.synchronize()
try:
    matches_fixture = json.loads(text) == json.loads(fixture["messages"][-1]["content"])
except ValueError:
    matches_fixture = False
result = {
    "purpose": "synthetic_adapter_reload_only",
    "quality_claim": False,
    "reloaded": True,
    "matches_synthetic_fixture": matches_fixture,
    "output": text,
    "seconds": time.perf_counter() - started,
    "mlx_peak_allocation_bytes": mx.get_peak_memory(),
}
(ROOT / "reports/adapter_reload.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
