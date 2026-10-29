# Contributing

Use Python 3.12 and the locked environments. Run `make check` before changing the extraction pipeline. CPU tests can also run with `uv sync --locked --no-default-groups --group dev` and `uv run --no-sync pytest -q`.

Develop on `data/evaluation/development.jsonl`. The bilingual prompts are pairs, and related products must remain in the same split. Keep reference annotations separate from retrieval text. A source quote that exists is not sufficient proof that a claim is correct.

`data/evaluation/test.jsonl` is sealed against `configs/release_freeze.json`. If you use its results to change model, prompt, retrieval or extraction behavior, it becomes development data for that new version. Preserve the original report and construct a new holdout; do not overwrite the sealed test or call a tuned rerun independent.

Changing a frozen implementation file intentionally makes the release check fail. Create a new candidate manifest and record the reason after development checks; do not update hashes solely to make a test run green. Human review status may be added only after a person has checked the source, with reviewer/date information in a separate review record.

Keep PDF snapshots, models, adapters, virtual environments, personal files and credentials out of commits. Retain source attribution in derived excerpts and reports; see `THIRD_PARTY.md`.
