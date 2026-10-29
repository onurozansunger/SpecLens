"""Synthetic MLX training compatibility test, never a quality/benchmark experiment.

Run in the LLM environment after stopping the inference worker. Artifacts remain local.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import socket
import time
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    destination = ROOT / "models/adapters/synthetic-smoke"
    if destination.exists():
        if args.prepare_only:
            print((ROOT / "reports/lora_smoke.json").read_text())
            return
        raise SystemExit(
            "Synthetic adapter already exists; its report was preserved. Archive this experiment before a new run."
        )
    os.environ["HF_HUB_OFFLINE"] = "1"
    import mlx.core as mx
    import numpy as np
    from huggingface_hub import snapshot_download
    from mlx_lm import load
    from mlx_lm.lora import CONFIG_DEFAULTS, train_model
    from mlx_lm.tuner.callbacks import TrainingCallback
    from mlx_lm.tuner.datasets import ChatDataset, load_dataset
    from mlx_lm.utils import load_tokenizer

    spec = json.loads((ROOT / "configs/models.json").read_text())["models"]["llm"]
    model_path = Path(
        snapshot_download(
            spec["repo_id"],
            revision=spec["revision"],
            local_files_only=True,
            allow_patterns=["*.json", "*.safetensors", "*.model", "*.txt", "*.jinja"],
        )
    )
    tokenizer = load_tokenizer(model_path, tokenizer_config_extra={"trust_remote_code": False})
    folder = ROOT / "data/training/synthetic-smoke"
    folder.mkdir(parents=True, exist_ok=True)
    lengths, offsets, hashes = [], [], {}
    for split, indexes in [("train", range(64)), ("valid", range(100, 108))]:
        records = []
        for index in indexes:
            lower, upper = 3 + index % 11, 19 + index % 13
            quote = f"Synthetic fixture only. VIN range is {lower}-{upper} V."
            output = {
                "findings": [
                    {
                        "document_id": f"fixture-{index}",
                        "field": "VIN",
                        "status": "stated",
                        "value": f"{lower}-{upper} V",
                        "citations": [{"chunk_id": f"fixture-{index}:p1:b0", "quote": quote}],
                    }
                ]
            }
            records.append(
                {
                    "messages": [
                        {
                            "role": "system",
                            "content": "Extract the VIN range from the evidence. Return only a JSON findings object with document_id, field, status, value and citations containing chunk_id and an exact quote.",
                        },
                        {
                            "role": "user",
                            "content": json.dumps(
                                {
                                    "question": "What is the VIN range?",
                                    "document_id": f"fixture-{index}",
                                    "chunk_id": f"fixture-{index}:p1:b0",
                                    "evidence": quote,
                                }
                            ),
                        },
                        {"role": "assistant", "content": json.dumps(output, separators=(",", ":"))},
                    ]
                }
            )
        dataset = ChatDataset(records, tokenizer, mask_prompt=True)
        for record in records:
            tokens, offset = dataset.process(record)
            lengths.append(len(tokens))
            offsets.append(offset)
            if record["messages"][-1]["content"] not in tokenizer.decode(tokens[offset:]):
                raise RuntimeError("Prompt mask removed part of the target assistant response")
            if not 0 < offset < len(tokens):
                raise RuntimeError("Invalid prompt masking offset")
        path = folder / f"{split}.jsonl"
        path.write_text("".join(json.dumps(r) + "\n" for r in records))
        hashes[split] = hashlib.sha256(path.read_bytes()).hexdigest()
    settings = json.loads((ROOT / "configs/lora-smoke.json").read_text())
    if max(lengths) > settings["max_seq_length"]:
        raise RuntimeError("Synthetic fixture would be truncated")
    report = {
        "purpose": "synthetic_runtime_compatibility_only",
        "quality_claim": False,
        "model": spec,
        "train_records": 64,
        "valid_records": 8,
        "max_sequence_tokens": max(lengths),
        "min_prompt_mask_tokens": min(offsets),
        "mask_verified": True,
        "dataset_sha256": hashes,
        "settings": settings,
        "micro_steps": settings["iters"],
        "optimizer_updates": settings["iters"] // settings["grad_accumulation_steps"],
        "train_reports": [],
        "validation_reports": [],
    }
    report_path = ROOT / "reports/lora_smoke.json"
    save(report_path, report)
    if args.prepare_only:
        print(json.dumps(report, indent=2))
        return
    with socket.socket() as sock:
        if sock.connect_ex(("127.0.0.1", 8011)) == 0:
            raise SystemExit("Stop the MLX inference worker before the training smoke test.")
    config = {
        **CONFIG_DEFAULTS,
        **settings,
        "model": str(model_path),
        "data": str(folder),
        "adapter_path": str(destination),
    }

    class Recorder(TrainingCallback):
        def on_train_loss_report(self, info):
            if any(isinstance(v, float) and not math.isfinite(v) for v in info.values()):
                raise RuntimeError("Non-finite training metric")
            report["train_reports"].append(info)
            save(report_path, report)

        def on_val_loss_report(self, info):
            report["validation_reports"].append(info)
            save(report_path, report)

    started = time.perf_counter()
    np.random.seed(settings["seed"])
    mx.random.seed(settings["seed"])
    training_args = SimpleNamespace(**config)
    model, training_tokenizer = load(str(model_path), trust_remote_code=False)
    train_set, valid_set, _ = load_dataset(training_args, training_tokenizer)
    train_model(training_args, model, train_set, valid_set, training_callback=Recorder())
    mx.synchronize()
    report["wall_seconds"] = time.perf_counter() - started
    report["mlx_peak_allocation_bytes"] = mx.get_peak_memory()
    adapter = destination / "adapters.safetensors"
    report["adapter_sha256"] = hashlib.sha256(adapter.read_bytes()).hexdigest()
    report["adapter_bytes"] = adapter.stat().st_size
    report["completed"] = True
    save(report_path, report)
    print(
        json.dumps(
            {k: v for k, v in report.items() if k not in {"train_reports", "validation_reports"}},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
