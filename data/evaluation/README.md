# Evaluation data

| File | Purpose | Product families | Prompts | Base tasks | Expected fields |
|---|---|---:|---:|---:|---:|
| `pilot.jsonl` | Historical development diagnostics | 8 | 30 | 15 | Legacy labels |
| `development.jsonl` | Field-level development checks | 8 | 30 | 15 | 32 |
| `test.jsonl` | Sealed family-held-out comparison | 4 | 48 | 24 | 56 |

All labels are agent-authored; **zero tasks have human review recorded**. Source excerpts were checked against hashed PDF text. Six held-out table pages were also visually inspected by the coding agent.

## Split protocol

The test uses four different product-family groups and PDF hashes from development. Variants and language pairs remain together. The test corpus is isolated under `data/heldout/`; only its PDF text, not its questions or answers, enters the test retrieval index. The application normally serves the development corpus.

Prediction/scoring files and model/source configurations were frozen before any held-out model response was inspected. `test_manifest.json` seals labels, chunks and the freeze manifest. Each of the two frozen pipelines, v2 and v3, ran once on this test. Labels and scoring rules were not revised after seeing their outputs.

This controls development/test reuse at the product-family level. It does not establish unseen vendors, architectures or pretrained-model data. Arduino documents share layouts and components, and base tasks can reuse the same fact. The 48 prompts are 24 bilingual pairs, not 48 independent observations. Correct document filters are supplied; routing is not evaluated.

## Task composition

The 24 base tasks comprise 16 answerable single-field questions, four absent-price questions, two same-document memory questions and two cross-document comparisons. Each has English and Turkish versions. References cover VIN/GPIO scope, internal/external memory, byte units, MCU clock, sensor identity, pin count and recommended/absolute temperature distinctions.

Each expected field specifies document, canonical field ID, status, value patterns, forbidden patterns and groups of accepted source alternatives. Citation checks require source PDF hash, physical page and reference text. All groups must have a match. For `not_stated`, the required output is a null value with no citations. Absence is scoped to this source/evidence, not the entire web or product catalog.

## Metric limits

Complete-task checks require all expected fields exactly once, allowed values and references, no extra fields, and a provenance-checked response. Failed requests remain in the denominator. These checks are stronger than finding a number somewhere in an answer, but they are not semantic entailment or human accuracy.

Post-run inspection found that one numeric pattern rejects an equivalent decimal range and that the Nicla SRAM references omit an alternative supporting page. The original score is preserved. The failure audit distinguishes these reference limitations from actual response failures; do not silently correct labels and present the rescored result as the original held-out result.

## Attribution and changes

Quotes derive from Arduino documentation contributors, under CC BY-SA 4.0. See `THIRD_PARTY.md` and the two corpus configurations for source links, hashes, revisions and licenses. PDF and Markdown revisions are separately hashed, not assumed identical. SpecLens added extraction, normalization, selected excerpts and question/reference annotations.

Builders are retained for provenance, not routine test regeneration. The test-label builder refuses to overwrite the sealed file. Future tuning on these failures retires this test as an independent evaluation for that future candidate.
