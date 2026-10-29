"""Versioned field-level references for the already-used development tasks.

References are checked against source text; human semantic review remains pending.
"""

from speclens.common import ROOT, normalize, read_jsonl, write_jsonl

# Each alternative is a physical page and a short sufficient reference substring.
SPECS = {
    "uno-vin": (
        "vin_voltage",
        [r"(?<!\d)6\b", r"\b24\s*V(?:DC)?\b"],
        [
            (2, "Recommended input voltage (VIN) is 6-24 V"),
            (6, "V IN Input voltage from VIN pad / DC Jack 6 7.0 24 V"),
            (5, "supports input voltages from 6-24 V"),
        ],
    ),
    "nano-vin": (
        "vin_voltage",
        [r"(?<!\d)6\b", r"\b21\s*V\b"],
        [
            (13, "The recommended input voltage range is 6-21 V."),
            (2, "VIN range is 6-21 V"),
            (5, "V IN Input voltage from VIN pad 6 7.0 21 V"),
        ],
    ),
    "nano-gpio": (
        "gpio_voltage",
        [r"\b3[.,]3\s*V\b"],
        [(13, "All digital & analog pins on the Nano ESP32 are 3.3 V.")],
    ),
    "uno-wifi-sram": (
        "sram_capacity",
        [r"\b32\s*(?-i:kB|KB)\b"],
        [
            (2, "32 kB SRAM"),
            (9, "256 kB flash / 32 kB SRAM / 8 kB data flash (EEPROM)"),
            (1, "32 kB SRAM"),
        ],
    ),
    "ble-flash": ("flash_capacity", [r"\b1\s*(?-i:MB)\b"], [(3, "1 MB Flash + 256 kB RAM")]),
    "sense-humidity": (
        "humidity_sensor",
        [r"\bHS3003\b"],
        [
            (4, "HS3003 Temperature & humidity sensor"),
            (10, "HS3003 (U8) Relative Humidity and Temperature Sensor"),
            (
                10,
                "The HS3003 (U8) is a MEMS sensors, designed to provide accurate readings of relative humidity and temperature in a small package.",
            ),
        ],
    ),
    "rp2040-sram": ("sram_capacity", [r"\b264\s*(?-i:kB|KB)\b"], [(2, "264 kB on-chip SRAM")]),
    "mkr-clock": (
        "clock_frequency",
        [r"\b48\s*MHz\b"],
        [
            (2, "Arm® Cortex®-M0+ at up to 48 MHz"),
            (7, "Arm® Cortex®-M0+ running at up to 48 MHz"),
        ],
    ),
    "mega-pins": (
        "digital_io_count",
        [r"\b54\b"],
        [(2, "54 Digital"), (1, "54 digital input/output pins")],
    ),
    "portenta-flash": (
        "flash_capacity",
        [r"\b16\s*(?-i:MB)\b"],
        [(5, "16 MB QSPI Flash memory (MX25L12833F)")],
    ),
    "opta-supply": (
        "nominal_supply",
        [r"\b12\b", r"\b24\s*V(?:DC)?\b"],
        [(8, "Supply voltage 12 - 24 V")],
    ),
    "opta-temperature": (
        "operating_temperature",
        [r"-20", r"\b50\s*°?\s*C\b"],
        [(8, "Temperature Operating Range -20...50 °C")],
    ),
    "opta-price": ("retail_price", [], []),
}


def build():
    pages = {
        (p["document_id"], p["page"]): p for p in read_jsonl(ROOT / "data/processed/pages.jsonl")
    }

    def reference(document, page, quote):
        source = pages[(document, page)]
        assert normalize(quote) in normalize(source["text"]), (document, page, quote)
        return {"document_id": document, "page": page, "quote": quote, "pdf_sha256": source["sha256"]}

    tasks = read_jsonl(ROOT / "data/evaluation/pilot.jsonl")
    for task in tasks:
        base, document = task["base_task"], task["documents"][0]
        if base == "opta-variant":
            groups = [
                [
                    (4, "SKU AFX00003 AFX00001 AFX00002"),
                    (13, "Wi-Fi® and Bluetooth® Low Energy (AFX00002 Only)"),
                    (
                        5,
                        "Wi-Fi® 2.4 GHz and Bluetooth® LE 4.2 supported by firmware, 5.1 supported by hardware (AFX00002)",
                    ),
                ],
                [
                    (4, "Wi-Fi® N/A N/A 802.11 b/g/n"),
                    (13, "Wi-Fi® and Bluetooth® Low Energy (AFX00002 Only)"),
                    (
                        5,
                        "Wi-Fi® 2.4 GHz and Bluetooth® LE 4.2 supported by firmware, 5.1 supported by hardware (AFX00002)",
                    ),
                ],
            ]
            fields = [
                {
                    "document_id": document,
                    "field": "wifi_sku",
                    "status": "stated",
                    "value_patterns": [r"\bAFX00002\b"],
                    "evidence_groups": [[reference(document, p, q) for p, q in g] for g in groups],
                }
            ]
        elif base == "nano-temperature-review":
            fields = []
            for field, pattern, page, quote in [
                (
                    "ambient_temperature",
                    r"\b105\s*°?\s*C\b",
                    5,
                    "T ambient Ambient Temperature -40 25 105 °C",
                ),
                (
                    "eut_temperature",
                    r"\b85\s*°?\s*C\b",
                    21,
                    "The operating temperature of the EUT can’t exceed 85°C",
                ),
            ]:
                fields.append(
                    {
                        "document_id": document,
                        "field": field,
                        "status": "stated",
                        "value_patterns": [pattern],
                        "evidence_groups": [[reference(document, page, quote)]],
                    }
                )
        else:
            field, patterns, alternatives = SPECS[base]
            fields = [
                {
                    "document_id": document,
                    "field": field,
                    "status": "stated" if alternatives else "not_stated",
                    "value_patterns": patterns,
                    "evidence_groups": [[reference(document, p, q) for p, q in alternatives]]
                    if alternatives
                    else [],
                }
            ]
        task["expected_findings"] = fields
        task["canonical_evidence"] = [
            ref for f in fields for group in f["evidence_groups"] for ref in group
        ]
        task["annotation_version"] = "development-fields-v1"
        task["notes"] = (
            "Already used for tuning. Agent-authored reference checks, human review pending."
        )
    write_jsonl(ROOT / "data/evaluation/development.jsonl", tasks)
    print("Wrote", len(tasks), "development prompts with per-field value and evidence references.")


if __name__ == "__main__":
    build()
