import json

import pytest

from credit_repair.cli import main


@pytest.fixture
def run(tmp_path, capsys):
    def _run(*args, today="2026-12-01"):
        code = main(["--case-dir", str(tmp_path / "case"), "--today", today, *args])
        out = capsys.readouterr()
        return code, out.out + out.err
    return _run


def test_init_refuses_full_ssn(run):
    code, out = run("init", "--name", "Jane", "--address", "1 Main St|Austin, TX", "--ssn-last4", "123456789")
    assert code == 2
    assert "LAST 4" in out


def test_case_folder_is_git_ignored(run, tmp_path):
    run("init", "--name", "Jane", "--address", "1 Main St|Austin, TX", "--ssn-last4", "1234")
    assert (tmp_path / "case" / ".gitignore").read_text() == "*\n"


def test_end_to_end(run, tmp_path):
    run("init", "--name", "Jane Sample", "--address", "1 Main St|Austin, TX 78701",
        "--ssn-last4", "1234", "--state", "TX")
    run("profile", "skip_personal_info=yes")
    items = tmp_path / "items.json"
    items.write_text(json.dumps([{
        "kind": "collection", "furnisher": "Midland Credit", "furnisher_address": "PO Box 1|San Diego, CA",
        "account_number": "8512XXXX", "bureaus": ["EX", "TU"], "derogatory_condition": "I owe $812.00",
    }]))
    code, out = run("item", "import", str(items))
    assert code == 0 and "I1 Midland Credit" in out

    code, out = run("next")
    assert "letter make P1L1 --item I1" in out

    code, out = run("letter", "make", "P1L1", "--item", "I1")
    assert code == 0 and "Created L1" in out
    letter_txt = next((tmp_path / "case" / "letters").glob("L1-P1L1-*.txt")).read_text()
    assert "which you claim I owe $812.00" in letter_txt

    run("letter", "mailed", "L1", "--tracking", "9400111", today="2026-12-02")
    code, out = run("letter", "delivered", "L1", "--date", "2026-12-05")
    assert "Day 31 is 2027-01-05" in out

    code, out = run("letter", "make", "P1L2A", "--item", "I1", today="2026-12-20")
    assert code == 2 and "wait the full 30 days" in out

    code, out = run("next", today="2027-01-05")
    assert "letter outcome L1" in out
    run("letter", "outcome", "L1", "--result", "verified", "--marked-disputed", "no", today="2027-01-05")
    code, out = run("next", today="2027-01-05")
    assert "letter make P1L2A --item I1" in out

    code, out = run("timeline", "I1", today="2027-01-05")
    assert "signed for L1" in out and "NOT marked disputed" in out

    code, out = run("calendar", today="2027-01-05")
    assert code == 0
    assert (tmp_path / "case" / "credit-repair-deadlines.ics").read_text().startswith("BEGIN:VCALENDAR")


def test_outcome_deleted_updates_bureau_status(run, tmp_path):
    run("init", "--name", "Jane", "--address", "1 Main St|Austin, TX", "--ssn-last4", "1234")
    run("profile", "skip_personal_info=yes")
    run("item", "add", "--kind", "public_record", "furnisher=County Court", "bureaus=EQ,TU",
        "derogatory_condition=a judgment of $900", "month_year=June 2021")
    run("letter", "make", "P2L1", "--item", "I1", "--bureau", "EQ")
    run("letter", "outcome", "L1", "--result", "deleted")
    code, out = run("item", "list")
    assert "EQ:deleted" in out and "TU:reporting" in out


def test_identity_theft_letter_requires_unrecognized_account(run):
    run("init", "--name", "Jane", "--address", "1 Main St|Austin, TX", "--ssn-last4", "1234")
    run("item", "add", "--kind", "identity_theft", "furnisher=Unknown Bank", "bureaus=EQ")
    code, out = run("letter", "make", "IDT", "--item", "I1", "--bureau", "EQ")
    assert code == 2 and "never had" in out
    run("item", "set", "I1", "recognized=no")
    code, out = run("letter", "make", "IDT", "--item", "I1", "--bureau", "EQ")
    assert code == 0


def test_info_works_without_a_case(run):
    code, out = run("info", "sol", "TX")
    assert code == 0 and "TX: 4 / 4 / 4 / 4" in out
