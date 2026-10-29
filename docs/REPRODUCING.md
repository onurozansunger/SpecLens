# Reproduce the frozen candidate

The saved reports were measured on an Apple M4 Pro with 48 GiB unified memory, native macOS and Python 3.12. The application uses MLX for Qwen inference. Development corpus embeddings were built on MPS; the small held-out index was built on CPU. Both use the same pinned multilingual E5 model. Do not run bulk embedding or training concurrently with latency measurements.

## Source snapshots

Source URLs and hashes are in `configs/corpus.json` and `configs/test_corpus.json`. Upstream PDF URLs can change. The prepared release asset preserves exactly the 14 PDFs and 14 Markdown sources, two source manifests and attribution:

- Filename: `speclens-corpus-2026-10-29.zip`
- Size: 18,248,062 bytes
- SHA-256: `d62487d13ee4cdf43ecec86b4a6fa3ae006f91f4b8cf5b3b731a09b4aa599d3f`
- Local location: `dist/` (excluded from Git; attach separately when publishing a release)

The archive contains no model weights, environments or personal files. Verification checks an exact member allowlist, every PDF/Markdown hash and manifest paths. Restore refuses to overwrite different existing files. A clean temporary-directory restore and a repeated identical restore were tested.

From a new checkout, with `uv` installed:

```bash
make setup
export PYTHONPATH="$PWD/src"
uv run --locked python scripts/corpus_snapshot.py restore \
  --file /path/to/speclens-corpus-2026-10-29.zip
make data
make models
make test-data
make check
make check-release
make run
```

If the original source URLs still match, `make bootstrap` followed by `make test-data` can acquire everything directly. A hash mismatch requires the archived source or a deliberately new dataset version; do not replace expected hashes just to continue.

The model and embedding revisions are pinned in `configs/models.json`. The first download needs internet access. Inference uses local cached models; no paid API credentials are required.

## Run the sealed test

With the worker active, in another terminal:

```bash
make benchmark
```

This writes `reports/test-reproduction.json`. The evaluator refuses an existing output file. For another reproduction, choose a different filename explicitly; never replace the first-run reports.

```bash
export PYTHONPATH="$PWD/src"
HF_HUB_OFFLINE=1 uv run --locked speclens evaluate quality \
  --tasks data/evaluation/test.jsonl --corpus-root data/heldout \
  --freeze configs/release_freeze.json --prompt-version v3 \
  --output reports/my-test-reproduction.json
```

The same command with `--prompt-version v2` runs the frozen baseline. The sealed test checks the implementation freeze, prompt allowance, task hash and source-chunk hash. Repeat runs check reproducibility; they must not be used to choose a favorable result. Hardware/library nondeterminism and runtime load can alter outputs or timing even with deterministic decoding.

## CPU-only checks

A clean CPU environment without PyTorch passed the 61-test suite, lint and release metadata verification. The GitHub workflow uses this path:

```bash
uv sync --locked --no-default-groups --group dev
uv run --no-sync pytest -q
uv run --no-sync ruff check src scripts tests
PYTHONPATH=src uv run --no-sync python scripts/check_release.py
```

CPU checks do not exercise MLX. Run `uv sync --locked` to restore the main ML dependency group before model inference. One dependency deprecation warning from Starlette's TestClient/httpx integration was observed; tests passed.

The checkout launcher and Makefile set `PYTHONPATH` explicitly. On the measured Mac, Python sometimes skipped editable-install `.pth` files carrying the macOS hidden flag. Explicit source paths avoid depending on those files; the origin of that flag was not established. Use the shown `PYTHONPATH` export for direct CLI commands.

## Audit artifacts

Primary results are `reports/quality_v2_development_release.json`, `quality_v3_development_release.json`, `quality_v2_test.json` and `quality_v3_test.json`. Each stores questions, retrieved evidence, model output, checks and timings. The development v2 report replays previously saved outputs against the final field-level references; the held-out reports are fresh model runs.

`configs/release_freeze.json` freezes prediction and scoring files. `data/evaluation/test_manifest.json` seals that manifest and the test data. `python scripts/check_release.py --local` verifies the seal and literal source excerpts. Human review is still pending; reproducibility checks do not supply semantic validation.
