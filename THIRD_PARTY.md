# Source attribution and licenses

The MIT license applies to original SpecLens code. It does not replace licenses for source documents, derived excerpts, model weights or dependencies.

## Arduino documentation

PDF/Markdown sources, quotations in evaluation labels and reports, and document previews derive from Arduino documentation. Attribution: **Arduino documentation contributors**. The repository's documentation license is **Creative Commons Attribution-ShareAlike 4.0**; retain that attribution and license when sharing these derived document materials.

- [Arduino licensing statement at the pinned revision](https://github.com/arduino/docs-content/blob/3c68978c438b31198e3e33b21477f4513c1e09f4/CONTRIBUTING.md)
- [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
- Development sources, URLs, revisions and hashes: `configs/corpus.json`.
- Held-out sources, URLs, revisions and hashes: `configs/test_corpus.json`.

Changes made by SpecLens: PDF text extraction, whitespace/Unicode normalization, excerpt selection, question/reference annotation and screenshot rendering. Evaluation labels are agent-authored and await human review. Full source PDFs are excluded from Git. A locally prepared corpus archive can accompany a release so readers can reproduce the exact snapshots even if producer URLs change.

PDF snapshots and pinned Markdown sources are separately hashed. Their revisions are not assumed to be identical. External documents linked by Arduino are not included or assumed to share this license. Arduino product names and marks identify the source products; this project is not affiliated with Arduino.

## Models

- [Qwen3-4B-Instruct-2507 MLX 4-bit conversion](https://huggingface.co/mlx-community/Qwen3-4B-Instruct-2507-4bit): Apache-2.0.
- [multilingual-e5-small](https://huggingface.co/intfloat/multilingual-e5-small): MIT.

Exact revisions are recorded in `configs/models.json`. No model weights are redistributed in this repository. Python dependencies retain their own licenses; resolved versions are in the two lockfiles.
