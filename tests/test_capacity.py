from speclens.capacity import recover_capacity
from speclens.evidence import evidence_lines


def recover(text, question="How much flash memory does the ZX81 module have?"):
    chunks = [{"id": "a:1", "document_id": "a", "page": 1, "text": text}]
    return recover_capacity(question, "flash_capacity", "a", evidence_lines(chunks)[1], chunks)


def test_capacity_recovery_requires_a_literal_value_and_named_component():
    assert recover("ZX81 Processor Features: 8 MB Flash and 96 kB RAM")["value"] == "8 MB"
    assert recover("XY42 Processor Features: 8 MB Flash") is None
    assert recover("ZX81 Processor Features: Flash available") is None
    assert recover("ZX81 Processor Features: 8 Mb Flash") is None


def test_ambiguous_capacity_or_unmatched_scope_stays_unresolved():
    assert recover("ZX81 Processor: 8 MB Flash; radio: 4 MB Flash") is None
    assert recover("ZX81 Processor: 8 MB Flash", "How much external flash does ZX81 have?") is None
    assert (
        recover("ZX81 Processor: 8 MB Flash", "Is ZX81 flash large enough for my application?")
        is None
    )
