from datetime import date

from conftest import add_item
from credit_repair.letters import SPECS, TEMPLATE_DIR, build_fields, render, write_files


def test_every_letter_has_a_template_and_vice_versa():
    files = {p.stem for p in TEMPLATE_DIR.glob("*.txt")}
    assert files == set(SPECS)


def test_book_letters_are_all_present():
    book = {"PI", "INQ1", "INQ2", "INQ3", "P1L1", "P1L2A", "P1L2B", "P1L2C", "P1L3", "P2L1",
            "P2L2A", "P2L2B", "P2L3", "STALL", "IDT", "EARLY", "REINSERT", "LP1", "LP2", "GW",
            "INCOMPLETE", "RETURNED", "BIZARRE", "CHEX", "REPO1", "REPO2", "HIPAA_PROVIDER",
            "HIPAA_CA"}
    assert book <= set(SPECS)
    assert all(SPECS[c].from_book for c in book)


def test_p1l1_fills_from_case(case):
    item = add_item(case, account_number="8512XXXX", derogatory_condition="I owe $812.00")
    spec = SPECS["P1L1"]
    out = render(spec, build_fields(case, spec, [item], "", date(2026, 12, 1)))
    assert out.missing == []
    assert "which you claim I owe $812.00. This is a formal notice" in out.text
    assert "Re: Acct # 8512XXXX" in out.text
    assert "December 1, 2026" in out.text
    assert "Last 4 of SSN: 1234" in out.text


def test_full_ssn_is_left_for_handwriting(case):
    spec = SPECS["PI"]
    out = render(spec, build_fields(case, spec, [], "EX", date(2026, 12, 1)))
    assert "[WRITE IN BY HAND: your full Social Security number]" in out.text
    assert "P.O. Box 4500" in out.text


def test_missing_fields_are_flagged_not_hidden(case):
    item = add_item(case)
    spec = SPECS["P1L2C"]
    out = render(spec, build_fields(case, spec, [item], "", date(2026, 12, 1)))
    assert "original_creditor_letter_date" in out.missing
    assert "[FILL IN: original creditor letter date]" in out.text


def test_bizarre_letter_keeps_its_deliberate_misspellings():
    text = SPECS["BIZARRE"].template
    for word in ("COMLIANCE", "NECCESSARY", "PROV EN", "426-CHARACTER FORMAT FIELDED P6"):
        assert word in text


def test_grouped_inquiry_letter_lists_each_inquiry(case):
    a = add_item(case, "inquiry", furnisher="Capital One", inquiry_date="May 3, 2026", bureaus=["EQ"])
    b = add_item(case, "inquiry", furnisher="Synchrony", inquiry_date="June 9, 2026", bureaus=["EQ"])
    spec = SPECS["INQ2"]
    out = render(spec, build_fields(case, spec, [a, b], "EQ", date(2026, 12, 1)))
    assert "1. Capital One - May 3, 2026\n2. Synchrony - June 9, 2026" in out.text


def test_identity_theft_goes_to_fraud_address(case):
    item = add_item(case, "identity_theft", recognized="no")
    spec = SPECS["IDT"]
    out = render(spec, build_fields(case, spec, [item], "EQ", date(2026, 12, 1)))
    assert "P.O. Box 105069" in out.text


def test_write_files_creates_txt_and_docx(tmp_path):
    paths = write_files(tmp_path, "L1", SPECS["P1L1"], "Midland Credit", "Hello\n\nWorld\n")
    names = sorted(p.name for p in paths)
    assert names[-1] == "L1-P1L1-midland-credit.txt"
    assert (tmp_path / "L1-P1L1-midland-credit.txt").read_text() == "Hello\n\nWorld\n"
