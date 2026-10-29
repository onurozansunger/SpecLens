"""Versioned, inspectable Turkish technical query expansion; no generated facts."""

import unicodedata

RULES = (
    (("gerilim", "voltaj"), "voltage"),
    (("besleme",), "power supply voltage"),
    (("giris",), "input"),
    (("oneril",), "recommended"),
    (("aralig", "aralik"), "range"),
    (("calisma",), "operating"),
    (("sicak",), "temperature"),
    (("ortam",), "ambient"),
    (("ust", "yuksek"), "maximum upper"),
    (("alt", "dusuk"), "minimum lower"),
    (("dijital",), "digital I/O pins"),
    (("analog",), "analog pins"),
    (("belle",), "memory capacity"),
    (("dahili",), "internal on-chip"),
    (("harici",), "external"),
    (("nem",), "relative humidity sensor"),
    (("sensor",), "sensor"),
    (("islemci", "mikrodenetleyici"), "processor microcontroller"),
    (("frekans", "saat"), "clock frequency"),
    (("baglanti",), "connectivity"),
    (("fiyat", "perakende"), "retail price"),
)
VERSION = "tr-technical-v1"


def expand_query(query: str) -> str:
    folded = "".join(
        c for c in unicodedata.normalize("NFKD", query.casefold()) if not unicodedata.combining(c)
    ).replace("ı", "i")
    words = folded.split()
    additions = [
        english
        for roots, english in RULES
        if any(word.startswith(root) for word in words for root in roots)
    ]
    return query + (" " + " ".join(dict.fromkeys(additions)) if additions else "")
