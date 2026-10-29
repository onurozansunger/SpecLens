# Portfolio copy

Prepared for Onur Ozan Sünger. The text below describes the current measured repository; replace repository/demo links with actual published URLs when available. Do not describe the test as human-annotated or the system as production-ready.

## Project card

**SpecLens — technical PDF extraction on Apple Silicon**

A local application for asking English/Turkish questions about technical datasheets and comparing their specifications. It retrieves passages with BM25 and multilingual E5, extracts structured fields with a 4-bit Qwen model through MLX, and displays the original PDF page beside each finding. Source checks, bounded repair and recorded failure cases make the answers inspectable.

**Stack:** Python, FastAPI, MLX/Metal, PyTorch MPS, multilingual E5, BM25, Pydantic, NumPy, PDF processing, pytest, GitHub Actions configuration.

## Case study

### Problem

Technical PDFs contain similar numbers with different meanings: VIN versus GPIO voltage, internal versus external memory, recommended conditions versus absolute limits. A fluent answer or a real quotation can still select the wrong scope. I built SpecLens to return structured findings together with inspectable evidence and an explicit review state when validation fails.

### Engineering work

The pipeline hashes each PDF, extracts page-linked text, combines lexical and dense retrieval, and balances context across selected documents. A native MLX worker runs a pinned 4-bit Qwen3-4B model within a measured token budget. Instead of generating quotes, the model selects excerpt IDs and the application reconstructs citations from source text.

Validation rejects unknown evidence, duplicate or unrequested fields and unsupported numeric tokens. One repair attempt is allowed and retained in the audit record. A narrow literal-capacity rule can recover directly stated memory values when the model abstains; its contributions are reported separately. Explicit VIN comparisons use deterministic unit/range logic.

The implementation and evaluation rules were frozen before testing on four product families excluded from development. Full model responses, source hashes, paired language tasks, failures and timing records are included so readers can inspect the result.

### Measured result

On 48 held-out English/Turkish prompts, the v3 pipeline passed 40 complete-task reference checks versus 25 for the earlier pipeline. The prompts represent 24 base tasks over four Arduino product families. Median local request time was 4.69 seconds on an M4 Pro with 48 GiB unified memory; p95 was 9.37 seconds. The repository has 61 passing CPU tests, also checked in a clean environment without PyTorch.

These are automated field/value/reference checks, not independently human-validated accuracy. The failure audit includes an incorrect table/narrative scope choice, false abstentions, a strict numeric validator and incomplete reference alternatives. The original result is preserved. Human annotation review remains pending, and the app uses the base model rather than the experimental LoRA adapter.

### What I learned

Changing the output contract and validation path improved measured behavior without a larger model or paid inference. However, checking that a quotation exists does not verify its meaning. The next experiment should improve table-aware context and numeric/reference handling, then measure on a new holdout because the current failures are now known development cases.

## CV bullets

- Built SpecLens, a local bilingual technical-PDF extraction system using hybrid BM25/E5 retrieval, Qwen3-4B on MLX/Metal, structured validation, source-page citations and bounded repair.
- Improved complete-task reference-check pass rate from 25/48 to 40/48 on a frozen evaluation of four held-out product families; measured 4.69 s median latency on Apple M4 Pro and added 61 CPU tests plus reproducible source/model manifests.

Keep the linked case study's qualification that labels are agent-authored and await human review. Do not shorten the metric to “83% accuracy.”

## Suggested two-minute demo

1. Select UNO R4 Minima and Nano ESP32. Compare their recommended VIN ranges at a 24 V target.
2. Open the cited page and show the actual source text. Explain the distinction between the claim and the evidence check.
3. Ask for a retail price absent from the selected source. Show the scoped missing-information result.
4. Open the held-out result table and one failure from `FAILURE_ANALYSIS.md`. Explain the frozen split and why later tuning requires another holdout.

The local app is the demo. No public hosted endpoint or published repository is implied by this document.
