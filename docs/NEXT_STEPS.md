# Next engineering steps

The repository now contains a frozen, locally exercised extraction candidate, a separate family-held-out test and a reproducible source archive. The remaining work is narrower than the original plan.

1. **Complete human review.** Review the 15 development and 24 test base tasks, including accepted alternative pages and model interpretation. Use `ANNOTATION_REVIEW.md`; do not mark records reviewed without an actual reviewer/date.
2. **Version the evaluation corrections.** Preserve the original 40/48 result. Numeric formatting and incomplete reference alternatives need a reviewed annotation/scoring revision, not a silent update to the sealed test.
3. **Develop the next candidate with a new holdout.** The observed `x54` rejection, Due table/narrative scope error and Nicla comparison abstentions are now known development cases. See `FAILURE_ANALYSIS.md`. Any tuning on them consumes this test's independence for the new candidate.
4. **Broaden source diversity.** Four held-out families from Arduino do not establish performance on new vendors, scanned PDFs, diagrams or unrelated layouts. Add licensed sources and explicit conflict tasks before making broader claims.
5. **Test training only if it addresses measured failures.** The app uses the base 4-bit model. The synthetic LoRA adapter is not a quality result. A real experiment needs reviewed training families and a distinct validation split.
6. **Present the published project.** The [GitHub repository](https://github.com/onurozansunger/SpecLens) and [source release](https://github.com/onurozansunger/SpecLens/releases/tag/v0.1.0) provide code, reports and the pinned corpus. Add the project to the portfolio using the prepared wording. Record a short demo showing a correct answer, its PDF source and one abstention/review case.

Current measurements are sequential local requests, not a concurrency SLA or a production reliability claim. OCR, arbitrary uploads, hosted access and page-region highlighting remain outside this release.
