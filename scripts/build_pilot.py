"""Create development fixtures from exact quotes in the downloaded PDF snapshot.

Labels are agent-reviewed candidates, NOT a human-validated or held-out benchmark.
"""

from speclens.common import ROOT, normalize, read_jsonl, write_jsonl

# Quotes were inspected in the extracted pages. Each pair represents one base task.
CASES = [
    (
        "uno-vin",
        "uno-r4-minima",
        "What is the recommended VIN input voltage range?",
        "Önerilen VIN giriş gerilimi aralığı nedir?",
        [(2, "Recommended input voltage (VIN) is 6-24 V")],
        [r"6", r"24", r"V"],
    ),
    (
        "nano-vin",
        "nano-esp32",
        "What is the recommended VIN voltage range?",
        "Önerilen VIN gerilim aralığı nedir?",
        [(13, "The recommended input voltage range is 6-21 V.")],
        [r"6", r"21", r"V"],
    ),
    (
        "nano-gpio",
        "nano-esp32",
        "What voltage do the digital and analog pins use?",
        "Dijital ve analog pinlerin gerilimi kaç volt?",
        [(13, "All digital & analog pins on the Nano ESP32 are 3.3 V.")],
        [r"3[.,]3", r"V"],
    ),
    (
        "uno-wifi-sram",
        "uno-r4-wifi",
        "How much SRAM does the main RA4M1 MCU have?",
        "Ana RA4M1 mikrodenetleyicisinde ne kadar SRAM var?",
        [(2, "32 kB SRAM")],
        [r"32", r"kB|KB|kilobyte"],
    ),
    (
        "ble-flash",
        "nano-33-ble-rev2",
        "How much flash memory does the NINA B306 processor have?",
        "NINA B306 işlemcisinin flash belleği ne kadar?",
        [(3, "1 MB Flash + 256 kB RAM")],
        [r"1", r"MB"],
    ),
    (
        "sense-humidity",
        "nano-33-ble-sense-rev2",
        "Which sensor measures relative humidity?",
        "Bağıl nemi hangi sensör ölçüyor?",
        [(4, "HS3003 Temperature & humidity sensor")],
        [r"HS3003"],
    ),
    (
        "rp2040-sram",
        "nano-rp2040-connect",
        "How much on-chip SRAM does the RP2040 have?",
        "RP2040 işlemcisinde ne kadar dahili SRAM var?",
        [(2, "264 kB on-chip SRAM")],
        [r"264", r"kB|KB|kilobyte"],
    ),
    (
        "mkr-clock",
        "mkr-wifi-1010",
        "What is the maximum SAMD21 processor clock frequency?",
        "SAMD21 işlemcisinin en yüksek saat frekansı kaç?",
        [(2, "Arm® Cortex®-M0+ at up to 48 MHz")],
        [r"48", r"MHz"],
    ),
    (
        "mega-pins",
        "mega-2560",
        "How many digital I/O pins are listed for the board?",
        "Kart için kaç dijital I/O pini listeleniyor?",
        [(2, "54 Digital")],
        [r"54"],
    ),
    (
        "portenta-flash",
        "portenta-c33",
        "What is the external QSPI flash memory capacity?",
        "Harici QSPI flash bellek kapasitesi nedir?",
        [(5, "16 MB QSPI Flash memory (MX25L12833F)")],
        [r"16", r"MB"],
    ),
    (
        "opta-supply",
        "opta",
        "What is the nominal supply voltage range, excluding the permissible range?",
        "İzin verilen tolerans aralığından ayrı olarak nominal besleme gerilimi aralığı nedir?",
        [(8, "Supply voltage 12 - 24 V")],
        [r"12", r"24", r"V"],
    ),
    (
        "opta-variant",
        "opta",
        "Which Opta SKU provides Wi-Fi connectivity?",
        "Hangi Opta SKU kodu Wi-Fi bağlantısı sunuyor?",
        [(4, "SKU AFX00003 AFX00001 AFX00002"), (4, "Wi-Fi® N/A N/A 802.11 b/g/n")],
        [r"AFX00002"],
    ),
    (
        "opta-temperature",
        "opta",
        "What is the recommended operating temperature range?",
        "Önerilen çalışma sıcaklığı aralığı nedir?",
        [(8, "Temperature Operating Range -20...50 °C")],
        [r"-20", r"50", r"°C|Celsius"],
    ),
    (
        "nano-temperature-review",
        "nano-esp32",
        "Report both upper temperature limits: the recommended ambient table and the EUT compliance statement. Preserve their different scopes.",
        "Önerilen ortam sıcaklığı tablosu ile EUT uygunluk ifadesindeki iki üst sıcaklık sınırını da ayrı kapsamlarıyla bildir.",
        [
            (5, "T ambient Ambient Temperature -40 25 105 °C"),
            (21, "The operating temperature of the EUT can’t exceed 85°C"),
        ],
        [r"105", r"85"],
    ),
    (
        "opta-price",
        "opta",
        "What is the retail price in Turkish lira stated in this datasheet?",
        "Bu datasheet'te Türk lirası cinsinden belirtilen perakende satış fiyatı nedir?",
        [],
        [],
    ),
]


def main():
    pages = {
        (p["document_id"], p["page"]): p for p in read_jsonl(ROOT / "data/processed/pages.jsonl")
    }
    tasks = []
    for task_id, document, english, turkish, quotes, patterns in CASES:
        evidence = []
        for number, quote in quotes:
            page = pages[(document, number)]
            if normalize(quote) not in normalize(page["text"]):
                raise ValueError(f"Reference quote changed: {task_id}:p{number}")
            evidence.append(
                {
                    "document_id": document,
                    "page": number,
                    "quote": quote,
                    "pdf_sha256": page["sha256"],
                }
            )
        for language, question in [("en", english), ("tr", turkish)]:
            tasks.append(
                {
                    "id": task_id + "-" + language,
                    "base_task": task_id,
                    "language": language,
                    "question": question,
                    "documents": [document],
                    "split": "development",
                    "review_status": "agent_checked_human_review_pending",
                    "answerable": bool(quotes),
                    "expected_value_patterns": patterns,
                    "canonical_evidence": evidence,
                    "notes": "Language pairs are not independent tasks. Not held out.",
                }
            )
    write_jsonl(ROOT / "data/evaluation/pilot.jsonl", tasks)
    print(f"Wrote {len(tasks)} prompts / {len(CASES)} base tasks; human review pending.")


if __name__ == "__main__":
    main()
