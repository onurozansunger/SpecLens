# Experiments and measured results

Measured on 29 October 2026, Apple M4 Pro / 48 GiB, native macOS. The served model is the pinned 4-bit `Qwen3-4B-Instruct-2507` MLX conversion. The app does not use a fine-tuned adapter.

## Primary comparison

| Split / pipeline | Complete-task checks | Value checks | Reference-evidence checks | Extra-field responses | Provenance passes | Median | p95 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Development / v2 | 16/30 | 26/32 | 22/32 | 8/30 | 24/30 | 6.66 s | 17.86 s |
| Development / v3 | 28/30 | 32/32 | 30/32 | 0/30 | 30/30 | 4.72 s | 7.49 s |
| Held-out / v2 | 25/48 | 38/56 | 33/56 | 3/48 | 41/48 | 5.16 s | 6.90 s |
| Held-out / v3 | 40/48 | 51/56 | 50/56 | 0/48 | 47/48 | 4.69 s | 9.37 s |

Held-out complete-task checks rose from **52.1% to 83.3%**, a 31.25 percentage-point difference. Both versions use expanded hybrid retrieval, at most eight chunks per requested document and the same base model. V3 changes the field contract, excerpt-ID output, context reserve, JSON stopping, repair behavior and literal-capacity fallback. This comparison measures the combined pipeline change; it does not isolate the effect of each component.

Complete-task checks require all expected fields, permitted value patterns and source references, no extra fields and no outstanding provenance failure. Value/evidence denominators are expected fields; other denominators are prompts. These are **automated reference checks, not human semantic accuracy**. Post-run inspection found numeric-format and alternate-page limitations in the sealed scorer. The original counts are retained; [failure analysis](FAILURE_ANALYSIS.md) explains every failed v3 test prompt.

| Held-out detail | v2 | v3 |
|---|---:|---:|
| English complete-task checks | 14/24 | 20/24 |
| Turkish complete-task checks | 11/24 | 20/24 |
| Absent-price prompt checks | 2/8 | 8/8 |
| Repair attempts | 0 | 3 |
| Literal-capacity recoveries | 0 | 2 |
| Maximum recorded MLX allocation | 3.75 GB | 3.64 GB |

Failed absent-price checks may mean missing fields or invalid abstention formatting, not necessarily invented prices. This narrow absence category does not measure general unsupported-question behavior. V3 attempted two repairs and made two literal-capacity recoveries on development; these are visible in the corresponding raw records.

## Evaluation protocol

Development comprises 15 base tasks / 30 bilingual prompts over ten documents in eight product-family groups. Test comprises 24 base tasks / 48 bilingual prompts over four different product families and different PDF hashes. The test has 16 single-field answerable base tasks, four price-absence tasks, two memory-pair tasks and two cross-document comparisons.

The implementation, scorer, prompts, dependency locks and model/source configurations were frozen before the first held-out model response. Test tasks and source chunks were sealed separately. Both frozen pipelines ran once. Test results were inspected only after the candidate run finished; no changes were then made to the frozen implementation or labels. Current UI/documentation/release scripts are outside that prediction freeze.

Labels were authored from source PDFs by the coding agent; human review is pending. Literal quotes and source hashes were programmatically verified, and six held-out table pages were visually inspected. All documents are Arduino publications and may share components/templates. Product-family separation is not vendor, architecture or pretraining-data independence. Language pairs and combined tasks are correlated, so no independence-based significance claim is made.

The task supplies document filters. The test therefore does not measure routing from an arbitrary document collection. The test retrieval index contains its source PDF text, but no questions or answer labels.

Primary raw artifacts:

- [Development v2](../reports/quality_v2_development_release.json): saved v2 generation outputs replayed through the final field-level references; no new inference.
- [Development v3](../reports/quality_v3_development_release.json): final development inference run before freezing.
- [Held-out v2](../reports/quality_v2_test.json): first frozen baseline test run.
- [Held-out v3](../reports/quality_v3_test.json): first frozen candidate test run.

Each retains question, retrieved text, accepted/rejected fields, model output, provenance, timings and attempt history. Earlier `quality_v2_development.json` and `quality_v3_intermediate.json` used intermediate development references; they are diagnostic history, not the primary comparison.

## Timing limits

Times are sequential, variable-length requests including retrieval, context packing and any repair. Worker/model state is warm across a run; initial encoder/model activity can affect early requests. V3 has a lower median but a higher held-out p95 because some requests take a second attempt. These are not fixed-token throughput, cold-start or concurrency benchmarks. MLX allocation is not total system memory or process RSS. The main API/retriever has separate allocations.

The native worker enforces a 4,096-input-token limit. V3 initially targets 3,584 tokens to reserve room for repair feedback. Outputs are capped at 512 tokens for a single field or 1,024 for multiple requested fields/documents. The report records planned and actual token counts.

## Earlier retrieval and generation diagnostics

These use development data only. Canonical-quote recall requires the reference page, PDF hash and text; equivalent evidence elsewhere can count as a miss. Each language has 14 answerable base tasks for recall; price absence is excluded.

| Retrieval method | EN recall@5 | TR recall@5 |
|---|---:|---:|
| BM25 | 92.9% | 82.1% |
| E5 dense | 89.3% | 60.7% |
| Hybrid RRF | 89.3% | 82.1% |
| Hybrid with query expansion | 89.3% | 92.9% |

Early generation v1 passed 24/30 weak expected-pattern checks with either plain or expanded hybrid search. Prompt v2 with larger context passed 28/30 such checks, but only 24/30 provenance checks. Pattern presence anywhere in an answer concealed extra/missing fields; the new field-level evaluation replaces it as the primary measure. The original artifacts are preserved.

`generation_v2_context8.json` contains a historical planned-token counting bug, annotated in that file. The worker still enforced its input cap. The corrected `generation_final.json` agrees on application/worker token counts and supplies the replayed development v2 outputs.

## Runtime and robustness checks

PyTorch MPS executed a real matrix operation. E5 embedded the 257 development chunks in 1.82 seconds after loading, at batch size 16 with maximum 481 input tokens. The 132 held-out chunks were embedded on CPU, maximum 500 tokens. These small-corpus measurements do not predict bulk throughput.

The synthetic LoRA compatibility test completed 80 micro-steps / 20 optimizer updates in 39.49 seconds, with 3.11 GB peak MLX allocation. It used rank 8 on the final eight layers, accumulation 4, prompt masking and gradient checkpointing; sequences were at most 178 tokens. Adapter reload produced an unwanted prefix before JSON. This is a negative quality result for that fixture, and the adapter is not served.

The historical four synthetic prompt probes passed 3/4 under v1. The updated v3 pipeline passed 6/6 synthetic probes: document instructions, a counterfactual voltage, GPIO/VIN scope, absent price, bits/bytes and temperature scope. Its separate report is `reports/robustness_v3.json`. These hand-written development probes do not establish prompt-injection security or general robustness.

## Verification status

The 61 CPU tests passed locally and in a clean CPU environment without PyTorch. Lint, source/vector checks, sealed-test integrity and a corpus-archive restore round trip passed. The published [GitHub Actions workflow](https://github.com/onurozansunger/SpecLens/actions/workflows/tests.yml) runs the CPU checks; its latest result is recorded on GitHub. Local Metal behavior was exercised with real model calls; CPU CI does not certify it.

See [REPRODUCING.md](REPRODUCING.md) for exact commands, source archive hash and environmental limits. The [review worksheet](ANNOTATION_REVIEW.md) records the outstanding human annotation step.
