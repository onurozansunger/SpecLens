.PHONY: setup data models bootstrap run test check evaluate test-data check-release benchmark
export PYTHONPATH := $(CURDIR)/src

setup:
	uv sync --locked
	uv sync --locked --project environments/llm

data:
	uv run --locked speclens fetch
	uv run --locked speclens extract

models:
	uv run --locked --project environments/llm python scripts/llm_worker.py download
	uv run --locked speclens embed

bootstrap: setup
	$(MAKE) data
	$(MAKE) models

run:
	uv run --locked python scripts/run_local.py

test:
	uv run --locked pytest -q

check:
	uv run --locked ruff check src scripts tests
	uv run --locked pytest -q
	uv run --locked speclens check-data
	uv run --locked python scripts/check_snapshot.py

evaluate:
	uv run --locked speclens evaluate retrieval

test-data:
	uv run --locked python scripts/prepare_test_corpus.py --embed

check-release:
	uv run --locked python scripts/check_release.py --local

benchmark:
	uv run --locked speclens evaluate quality --tasks data/evaluation/test.jsonl --corpus-root data/heldout --freeze configs/release_freeze.json --prompt-version v3 --output reports/test-reproduction.json
