# Report index

Primary result files:

| File | Meaning |
|---|---|
| `quality_v2_development_release.json` | Saved v2 development predictions scored against final field references: 16/30 task checks. |
| `quality_v3_development_release.json` | Final v3 development run: 28/30 task checks. |
| `quality_v2_test.json` | First frozen baseline held-out run: 25/48 task checks. |
| `quality_v3_test.json` | First frozen candidate held-out run: 40/48 task checks. |
| `robustness_v3.json` | Six synthetic development probes, 6/6 passed; not a security evaluation. |

The quality reports contain full requests, evidence, attempts, findings, checks and timings. Labels are agent-authored, not human-validated. Language pairs are correlated. Read `docs/EXPERIMENTS.md` and `docs/FAILURE_ANALYSIS.md` before quoting any metric.

Earlier `generation_*`, retrieval and `quality_*` files preserve development history. `final_verification.json`, `readiness_review.json` and `experiment_summary.json` describe earlier checkpoints; current verification is in `release_verification.json`. Weak whole-response pattern checks and intermediate label versions are not comparable to the primary field-level scores. `robustness_probes.json` is the historical v1 diagnostic. Synthetic training/adapter reports are compatibility experiments; their adapter is not used by the application.

`qa/` is excluded from Git. Full PDFs, cached models, training artifacts and the source archive are stored outside this report directory and excluded from Git. Derived source excerpts retain Arduino attribution; see `THIRD_PARTY.md`.
