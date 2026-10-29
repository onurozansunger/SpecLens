# Frozen v3 failure analysis

The first held-out run passed 40/48 complete-task reference checks. This audit examines the eight failed prompts without changing predictions, labels, scoring code or the frozen implementation. It is an agent review, not independent human adjudication. Counts below describe the eight flagged prompts, not an exhaustive semantic review of the 40 passing prompts.

| Failed prompts | Count | Observed result | Interpretation |
|---|---:|---|---|
| `test-due-vin-table-en` | 1 | Returned 7–12 V despite the question explicitly asking for the 6–16 V recommended-conditions table. Both table and narrative were cited. | Scope conflict was not resolved; a real answer error. Numeric provenance checks cannot catch this because all values occur in the citations. |
| `test-due-digital-tr` | 1 | Model returned 54 with source text containing `x54`; the validator withheld it as a missing numeric atom. | Overly strict token boundary handling. The user receives a review state rather than an accepted answer. |
| `test-compare-vin-en`, `test-compare-vin-tr` | 2 | GIGA VIN was extracted, but Nicla VIN was marked `not_stated` despite being in its source PDF. | False abstention in a multi-document task. Requires analysis of retrieval/packing and extraction coverage. |
| `test-giga-vin-table-en` | 1 | Returned 6.0–32.0 V and cited the correct 6–32 V table. | Equivalent number formatting rejected by the sealed value pattern; a scoring limitation. |
| `test-nicla-sram-tr`, `test-nicla-memory-pair-tr`, `test-compare-sram-en` | 3 | Returned 64 KB with a source quote on page 11 explicitly saying 64 KB SRAM. | The reference set omits this alternate supporting page. The strict citation check fails despite relevant source evidence. |

The last two rows account for four of the eight strict-check failures. This does **not** justify reporting 44/48 as independently verified accuracy: the audit followed the outputs, only failed cases were examined in depth, and no human adjudication has occurred. The published primary metric remains 40/48.

## Development failures

The final development run passed 28/30 task checks. Both remaining failures concern Opta operating-temperature scope: the numbers match, but the selected EUT compliance passage does not satisfy the recommended-operating-table reference. The system can cite genuine text while answering the wrong scope.

The v3 changes were developed on this set: excerpt-ID selection, field contracts, rejection of duplicate fields, complete-JSON stopping, one bounded repair and a narrow literal memory fallback. The fallback's contributions are recorded separately in each raw report.

## Follow-up sequence

1. Have a person inspect the 39 base tasks using the review worksheet, including passing outputs. Record reviewer/date and alternate evidence in a separate versioned review record.
2. Promote this test's observed failures to development regressions for the next candidate. Handle numeric equivalence, `x54`-style counts and alternate evidence without broadening rules to accept unsupported numbers.
3. Compare table-aware context against page-text chunks for scope conflicts and multi-document omissions. Test source selection separately from value extraction.
4. Build a new family-separated holdout before claiming improvements from these changes. Expand vendors/layouts and include conflicts and unsupported questions beyond price absence.

The frozen candidate remains reproducible. These findings are intentionally visible instead of being erased by tuning on the test.
