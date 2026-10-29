"""Author and seal held-out references from PDFs, before any test-model run.

Never overwrite a sealed test set. Annotation is by the coding agent, not a human.
"""

import re
from copy import deepcopy
from datetime import UTC, datetime

from speclens.benchmark import check_freeze
from speclens.common import ROOT, digest, normalize, read_json, read_jsonl, write_json, write_jsonl
from speclens.dataset import validate_dataset


def main():
    target = ROOT / "data/evaluation/test.jsonl"
    seal = ROOT / "data/evaluation/test_manifest.json"
    if target.exists() or seal.exists():
        raise SystemExit("Test set already sealed. Create a new version instead of overwriting it.")
    check_freeze(ROOT / "configs/release_freeze.json")
    pages = read_jsonl(ROOT / "data/heldout/data/processed/pages.jsonl")
    lookup = {(p["document_id"], p["page"]): p for p in pages}
    cases = []
    refs = {}

    def ref(doc, page, quote):
        source = lookup[(doc, page)]
        if normalize(quote) not in normalize(source["text"]):
            raise ValueError(f"Reference not in source: {doc} p{page}: {quote}")
        return {"document_id": doc, "page": page, "pdf_sha256": source["sha256"], "quote": quote}

    def add(key, doc, en, tr, field, patterns, alternatives, forbidden=None):
        finding = {
            "document_id": doc,
            "field": field,
            "status": "stated" if alternatives else "not_stated",
            "value_patterns": patterns,
            "forbidden_patterns": forbidden or [],
            "evidence_groups": [[ref(doc, page, quote) for page, quote in alternatives]]
            if alternatives
            else [],
        }
        refs[key] = finding
        cases.append((key, [doc], en, tr, [finding]))

    add(
        "due-sram",
        "due",
        "How much total SRAM does the SAM3X8E have, before dividing it into banks?",
        "Bankalara ayırmadan önce SAM3X8E toplam SRAM kapasitesi nedir?",
        "sram_capacity",
        [r"\b96\s*(?-i:KB|kB)\b"],
        [(6, "96 KB SRAM")],
    )
    add(
        "due-flash",
        "due",
        "What is the SAM3X8E flash memory capacity?",
        "SAM3X8E flash bellek kapasitesi nedir?",
        "flash_capacity",
        [r"\b512\s*(?-i:KB|kB)\b"],
        [(6, "Flash Memory 512 KB"), (6, "SAM3X 512 KB Flash")],
    )
    add(
        "due-vin-table",
        "due",
        "In the Recommended Operating Conditions table, what are the minimum and maximum VIN input voltages? Exclude the typical value.",
        "Recommended Operating Conditions tablosundaki minimum ve maksimum VIN giriş gerilimi nedir? Tipik değeri hariç tut.",
        "vin_voltage",
        [r"(?<!\d)6(?:[.,]0)?\b", r"\b16\s*V\b"],
        [(7, "V IN Input voltage from VIN pad 6.0 7.0 16 V")],
        [r"\b12\b"],
    )
    add(
        "due-digital",
        "due",
        "How many digital input pins are listed for the board?",
        "Kart için kaç dijital giriş pini listeleniyor?",
        "digital_io_count",
        [r"\b54\b"],
        [
            (7, "54x digital inputs"),
            (1, "54x digital input/output"),
            (6, "Digital Inputs not 5 V compatible (x54)"),
        ],
    )

    add(
        "giga-sram",
        "giga-r1-wifi",
        "What is the on-chip SRAM capacity of the STM32H747, excluding external SDRAM?",
        "Harici SDRAM hariç STM32H747 dahili SRAM kapasitesi nedir?",
        "sram_capacity",
        [r"\b1\s*(?-i:MB)\b"],
        [(11, "1 MB SRAM on the STM32H747"), (2, "STM32H747XI 2 MB Flash 1 MB RAM")],
        [r"\b8\s*MB\b"],
    )
    add(
        "giga-external-flash",
        "giga-r1-wifi",
        "What is the external NOR flash memory capacity, excluding the MCU internal flash?",
        "MCU dahili flash hariç harici NOR flash bellek kapasitesi nedir?",
        "flash_capacity",
        [r"\b16\s*(?-i:MB)\b"],
        [(2, "16 MB NOR Flash"), (11, "16 MB of NOR Flash")],
        [r"\b2\s*MB\b"],
    )
    add(
        "giga-m7-clock",
        "giga-r1-wifi",
        "What is the maximum clock frequency of the Cortex-M7 core only?",
        "Yalnızca Cortex-M7 çekirdeğinin maksimum saat frekansı nedir?",
        "clock_frequency",
        [r"\b480\s*MHz\b"],
        [
            (2, "Cortex®-M7 core with double-precision FPU and L1 cache up to 480 MHz"),
            (10, "Cortex®-M7 running at 480 MHz"),
        ],
        [r"\b240\b"],
    )
    add(
        "giga-vin-table",
        "giga-r1-wifi",
        "What minimum-to-maximum VIN range is stated in the Recommended Operating Conditions table?",
        "Recommended Operating Conditions tablosunda belirtilen minimum-maksimum VIN aralığı nedir?",
        "vin_voltage",
        [r"(?<!\d)6\b", r"\b32\s*V\b"],
        [(7, "V IN Input voltage from VIN pad 6 7.0 32 V")],
        [r"\b24\b"],
    )

    add(
        "nicla-sram",
        "nicla-sense-me",
        "How much internal SRAM is available in the nRF52832?",
        "nRF52832 içinde ne kadar dahili SRAM var?",
        "sram_capacity",
        [r"\b64\s*(?-i:KB|kB)\b"],
        [(4, "Internal SRAM Memory 64 KB"), (11, "64 KB SRAM is available to the user.")],
    )
    add(
        "nicla-internal-flash",
        "nicla-sense-me",
        "What is the internal flash memory capacity of the nRF52832, excluding external flash?",
        "Harici flash hariç nRF52832 dahili flash bellek kapasitesi nedir?",
        "flash_capacity",
        [r"\b512\s*(?-i:KB|kB)\b"],
        [(4, "Internal Flash Memory 512 KB"), (11, "nRF52832 internal 512 KB FLASH")],
        [r"\b2\s*MB\b"],
    )
    add(
        "nicla-humidity",
        "nicla-sense-me",
        "Which environmental sensor measures humidity?",
        "Nemi ölçen çevresel sensörün modeli nedir?",
        "humidity_sensor",
        [r"\bBME688\b"],
        [(5, "Model Bosch® BME688"), (11, "via the Bosch® BME688 sensor (U6).")],
    )
    refs["nicla-humidity"]["evidence_groups"].append(
        [
            ref("nicla-sense-me", 5, "Humidity: 0-100%"),
            ref(
                "nicla-sense-me",
                11,
                "This provides capabilities for pressure, humidity, temperature",
            ),
        ]
    )
    add(
        "nicla-vin-table",
        "nicla-sense-me",
        "What is the minimum-to-maximum VIN input range? Do not use the logic-level voltage.",
        "Minimum-maksimum VIN giriş aralığı nedir? Mantık seviyesi gerilimini kullanma.",
        "vin_voltage",
        [r"\b3[.,]5\b", r"\b5[.,]5\s*V\b"],
        [(7, "V IN Input voltage from VIN pad 3.5 5.0 5.5 V")],
        [r"\b3[.,]3\b"],
    )

    add(
        "edge-sram",
        "edge-control",
        "How much RAM is listed for the Nina B306 module?",
        "Nina B306 modülü için ne kadar RAM listeleniyor?",
        "sram_capacity",
        [r"\b256\s*(?-i:KB|kB)\b"],
        [(2, "1 MB Flash + 256 KB RAM")],
    )
    add(
        "edge-storage-flash",
        "edge-control",
        "What is the additional external flash memory capacity for data storage?",
        "Veri depolama için ek harici flash bellek kapasitesi nedir?",
        "flash_capacity",
        [r"\b2\s*(?-i:MB)\b"],
        [(15, "additional 2MB flash memory for data storage"), (2, "Memory 2MB onboard QSPI")],
    )
    add(
        "edge-clock",
        "edge-control",
        "What is the maximum clock frequency of the main processor?",
        "Ana işlemcinin maksimum saat frekansı nedir?",
        "clock_frequency",
        [r"\b64\s*MHz\b"],
        [
            (11, "The Main Processor is a Cortex M4F running at up to 64MHz."),
            (2, "64 MHz Arm® Cortex®-M4F (with FPU)"),
        ],
    )
    add(
        "edge-recommended-temperature",
        "edge-control",
        "What is the recommended operating temperature range, excluding absolute maximum ratings?",
        "Mutlak maksimum değerler hariç önerilen çalışma sıcaklığı aralığı nedir?",
        "operating_temperature",
        [r"-15", r"\b60\s*°?\s*C\b"],
        [(8, "T Conservative thermal limits -15 20 60 °C")],
        [r"\b85\b", r"-40"],
    )

    absence_scan = []
    for doc in ("due", "giga-r1-wifi", "nicla-sense-me", "edge-control"):
        add(
            doc + "-missing-price",
            doc,
            "What retail price in Turkish lira is stated in this datasheet?",
            "Bu datasheet içinde Türk lirası cinsinden hangi perakende satış fiyatı belirtiliyor?",
            "retail_price",
            [],
            [],
        )
        hits = []
        for page in pages:
            if page["document_id"] == doc:
                for line in page["text"].splitlines():
                    if re.search(
                        r"\bprice\b|\bretail\b|\blira\b|₺|\bTRY\s*\d", line, re.IGNORECASE
                    ):
                        hits.append({"page": page["page"], "text": line})
        absence_scan.append({"document_id": doc, "full_text_keyword_hits": hits})
        if hits:
            raise ValueError("Review possible price evidence before sealing: " + doc)

    combinations = [
        (
            "due-memory-pair",
            ["due"],
            "Give the SAM3X8E SRAM and flash capacities separately.",
            "SAM3X8E SRAM ve flash kapasitelerini ayrı ayrı ver.",
            ["due-sram", "due-flash"],
        ),
        (
            "nicla-memory-pair",
            ["nicla-sense-me"],
            "Give the nRF52832 internal SRAM and internal flash capacities separately.",
            "nRF52832 dahili SRAM ve dahili flash kapasitelerini ayrı ayrı ver.",
            ["nicla-sram", "nicla-internal-flash"],
        ),
        (
            "compare-sram",
            ["due", "nicla-sense-me"],
            "Compare the main processor SRAM capacity in the two selected boards. Give one value per document.",
            "Seçilen iki kartın ana işlemci SRAM kapasitesini karşılaştır. Her belge için ayrı değer ver.",
            ["due-sram", "nicla-sram"],
        ),
        (
            "compare-vin",
            ["giga-r1-wifi", "nicla-sense-me"],
            "Compare the minimum-to-maximum VIN ranges in the Recommended Operating Conditions tables. Give one range per document.",
            "Recommended Operating Conditions tablolarındaki minimum-maksimum VIN aralıklarını karşılaştır. Her belge için ayrı aralık ver.",
            ["giga-vin-table", "nicla-vin-table"],
        ),
    ]
    for key, docs, en, tr, keys in combinations:
        cases.append((key, docs, en, tr, [deepcopy(refs[k]) for k in keys]))
    tasks = []
    for key, docs, en, tr, findings in cases:
        for language, question in [("en", en), ("tr", tr)]:
            tasks.append(
                {
                    "id": "test-" + key + "-" + language,
                    "base_task": "test-" + key,
                    "language": language,
                    "question": question,
                    "documents": docs,
                    "split": "test",
                    "review_status": "agent_checked_human_review_pending",
                    "annotation_version": "test-v1",
                    "answerable": any(f["status"] == "stated" for f in findings),
                    "expected_findings": findings,
                    "expected_value_patterns": [p for f in findings for p in f["value_patterns"]],
                    "canonical_evidence": [
                        r for f in findings for g in f["evidence_groups"] for r in g
                    ],
                    "notes": "Product-family-held-out, same publisher/domain. Physical PDF pages and source hashes checked. Paired languages and combined tasks are correlated.",
                }
            )
    all_docs = (
        read_json(ROOT / "configs/corpus.json")["documents"]
        + read_json(ROOT / "configs/test_corpus.json")["documents"]
    )
    checks = validate_dataset(
        read_jsonl(ROOT / "data/evaluation/development.jsonl") + tasks,
        all_docs,
        read_jsonl(ROOT / "data/processed/pages.jsonl") + pages,
    )
    if not checks["valid"]:
        raise ValueError(checks)
    write_jsonl(target, tasks)
    write_json(
        seal,
        {
            "sealed_at": datetime.now(UTC).isoformat(),
            "tasks_sha256": digest(target),
            "prediction_freeze_sha256": digest(ROOT / "configs/release_freeze.json"),
            "corpus_config_sha256": digest(ROOT / "configs/test_corpus.json"),
            "test_families": sorted(
                {d["family"] for d in read_json(ROOT / "configs/test_corpus.json")["documents"]}
            ),
            "prompts": len(tasks),
            "base_tasks": len(cases),
            "human_validated": False,
            "review_status": "agent-authored; independent human review pending",
            "source_visual_review": [
                "due:p6",
                "due:p7",
                "giga-r1-wifi:p7",
                "nicla-sense-me:p4",
                "nicla-sense-me:p7",
                "edge-control:p8",
            ],
            "absence_scan": absence_scan,
            "combined_split_validation": checks,
            "protocol": "No test-model responses viewed before sealing; do not tune this release on these results. Any future tuning retires v1 as an independent test.",
        },
    )
    print(
        {
            "prompts": len(tasks),
            "base_tasks": len(cases),
            "expected_fields": sum(len(t["expected_findings"]) for t in tasks),
            "split_validation": checks,
        }
    )


if __name__ == "__main__":
    main()
