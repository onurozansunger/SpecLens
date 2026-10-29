"""Small, versioned question vocabulary. Contains no document answers or product IDs."""

import re
import unicodedata

VERSION = "technical-fields-v1"

CAPACITY_HINTS = {"flash_capacity": r"\bflash\b", "sram_capacity": r"\b(?:sram|ram)\b"}


def possible_capacity_evidence(field: str, text: str) -> bool:
    """A review hint, not proof: a capacity mention may concern another component."""
    return field in CAPACITY_HINTS and bool(
        re.search(CAPACITY_HINTS[field], text, re.IGNORECASE)
        and re.search(r"\b\d+(?:\.\d+)?\s*[kmg]b\b", text, re.IGNORECASE)
    )


def fold(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", text.casefold()) if not unicodedata.combining(c)
    ).replace("ı", "i")


def requested_fields(question: str) -> list[str]:
    q = fold(question)
    fields = []

    def has(pattern):
        return re.search(pattern, q) is not None

    if has(r"\bvin\b"):
        fields.append("vin_voltage")
    if (
        has(r"gpio") or (has(r"digital|dijital|analog") and has(r"voltage|volt|gerilim"))
    ) and not has(r"how many|kac .*pin"):
        fields.append("gpio_voltage")
    if has(r"\bsram\b|\bram\b"):
        fields.append("sram_capacity")
    if has(r"\bflash\b"):
        fields.append("flash_capacity")
    if has(r"humidity|\bnem\w*"):
        fields.append("humidity_sensor")
    if has(r"clock|frekans|frequency|saat"):
        fields.append("clock_frequency")
    if has(
        r"how many.*?pins?|kac\s+(?:adet\s+)?(?:dijital|digital|i/o).*?pin|(?:dijital|digital).*?pin.*?(?:sayisi|adedi)"
    ) and has(r"digital|dijital"):
        fields.append("digital_io_count")
    if has(r"nominal") and has(r"supply|besleme"):
        fields.append("nominal_supply")
    if has(r"sku"):
        fields.append("wifi_sku" if has(r"wi.?fi") else "sku")
    if has(r"temperature|sicak"):
        if has(r"ambient|ortam"):
            fields.append("ambient_temperature")
        if has(r"\beut\b"):
            fields.append("eut_temperature")
        if not any(f.endswith("temperature") for f in fields):
            fields.append("operating_temperature")
    if has(r"retail|price|fiyat|perakende"):
        fields.append("retail_price")
    return fields
