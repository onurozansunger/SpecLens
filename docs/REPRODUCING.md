# Reproduce the frozen candidate

The saved reports were measured on an Apple M4 Pro with 48 GiB unified memory, native macOS and Python 3.12. The application uses MLX for Qwen inference. Development corpus embeddings were built on MPS; the small held-out index was built on CPU. Both use the same pinned multilingual E5 model. Do not run bulk embedding or training concurrently with latency measurements.

## Source snapshots

Source URLs and hashes are pinned in `configs/corpus.json` and `configs/test_corpus.json`. PDF and Markdown snapshots are checked separately. Upstream PDF URLs can change; a mismatch stops acquisition rather than changing the benchmark sources.

```bash
make bootstrap
make test-data
make check
make check-release
make run
```

No corpus archive is published. An installation can create a local archive of its verified source files with:

```bash
export PYTHONPATH="$PWD/src"
uv run --locked python scripts/corpus_snapshot.py create
```

The archive contains 14 PDFs, 14 Markdown sources, two manifests and attribution. It is written to `dist/` and excluded from Git. The script checks an exact member allowlist, source hashes and manifest paths. To restore an existing archive before running `make data`:

```bash
make setup
export PYTHONPATH="$PWD/src"
uv run --locked python scripts/corpus_snapshot.py restore --file /path/to/corpus.zip
make data
make models
make test-data
```

The locally verified snapshot has SHA-256 `d62487d13ee4cdf43ecec86b4a6fa3ae006f91f4b8cf5b3b731a09b4aa599d3f` and is 18,248,062 bytes. Archive hashes can differ with ZIP metadata; source-file hashes remain authoritative. If a pinned upstream source is unavailable and no matching archive is available, that snapshot cannot be reproduced. Do not replace expected hashes to bypass the check.

Model and embedding revisions are pinned in `configs/models.json`. Initial setup requires internet access; inference uses the local cache.

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
