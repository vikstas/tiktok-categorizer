from datetime import date, timedelta

from conftest import TODAY, add_item, add_letter, day_after_deadline
from credit_repair import workflow


def codes(case, today, item=None, kind="make_letter"):
    acts = workflow.plan(case, today).actions
    return [(a.code, a.bureau) for a in acts if a.kind == kind and (item is None or item.id in a.item_ids)]


def kinds(case, today, item):
    return [a.kind for a in workflow.plan(case, today).actions if item.id in a.item_ids]


def test_new_collection_starts_with_license_check_and_p1l1(case):
    item = add_item(case)
    assert codes(case, TODAY, item) == [("P1L1", "")]
    acts = workflow.plan(case, TODAY).due_now(TODAY)
    assert "license" in acts[0].message.lower()


def test_public_records_start_at_part2_for_each_bureau(case):
    item = add_item(case, "public_record", bureaus=["EQ", "TU"])
    assert codes(case, TODAY, item) == [("P2L1", "EQ"), ("P2L1", "TU")]


def test_must_wait_full_30_days_even_after_a_reply(case):
    item = add_item(case)
    add_letter(case, "P1L1", item, outcome="verified", marked=False)
    early = TODAY + timedelta(days=10)
    assert codes(case, early, item) == []
    assert "wait" in kinds(case, early, item)
    assert codes(case, day_after_deadline(), item) == [("P1L2A", "")]


def test_day31_without_reply_asks_for_outcome(case):
    item = add_item(case)
    add_letter(case, "P1L1", item)
    assert kinds(case, day_after_deadline(), item) == ["record_outcome"]


def test_unmailed_and_untracked_letters(case):
    item = add_item(case)
    lt = add_letter(case, "P1L1", item)
    lt.delivered_on = ""
    assert kinds(case, TODAY, item) == ["confirm_delivery"]
    lt.mailed_on = ""
    assert kinds(case, TODAY, item) == ["mail"]


def test_part1_branches(case):
    expectations = {
        "verified": "P1L2A",
        "no_response": "P1L2B",
        "original_creditor_responded": "P1L2C",
    }
    for result, expected in expectations.items():
        item = add_item(case)
        add_letter(case, "P1L1", item, outcome=result, marked=True)
        assert codes(case, day_after_deadline(), item) == [(expected, "")], result


def test_not_marked_disputed_leads_to_p1l3_then_part2(case):
    item = add_item(case)
    add_letter(case, "P1L1", item, outcome="verified", marked=False)
    second = TODAY + timedelta(days=40)
    add_letter(case, "P1L2A", item, sent=second, outcome="verified")
    assert codes(case, day_after_deadline(second), item) == [("P1L3", "")]
    third = second + timedelta(days=40)
    add_letter(case, "P1L3", item, sent=third, outcome="no_response")
    assert codes(case, day_after_deadline(third), item) == [("P2L1", "EX"), ("P2L1", "TU")]


def test_marked_disputed_skips_p1l3(case):
    item = add_item(case)
    add_letter(case, "P1L1", item, outcome="no_response", marked=True)
    second = TODAY + timedelta(days=40)
    add_letter(case, "P1L2B", item, sent=second, outcome="no_response")
    assert codes(case, day_after_deadline(second), item) == [("P2L1", "EX"), ("P2L1", "TU")]


def test_unknown_disputed_flag_is_asked_for(case):
    item = add_item(case)
    add_letter(case, "P1L1", item, outcome="verified")
    second = TODAY + timedelta(days=40)
    add_letter(case, "P1L2A", item, sent=second, outcome="verified")
    acts = workflow.plan(case, day_after_deadline(second)).actions
    assert any(a.kind == "record_outcome" and "--marked-disputed" in a.command for a in acts)


def test_proof_with_signature_and_marked_disputed_goes_to_part2(case):
    item = add_item(case, bureaus=["EQ"])
    add_letter(case, "P1L1", item, outcome="proof_with_signature", marked=True)
    assert codes(case, day_after_deadline(), item) == [("P2L1", "EQ")]


def test_returned_mail_goes_straight_to_returned_mail_letter(case):
    item = add_item(case, bureaus=["EX"])
    add_letter(case, "P1L1", item, outcome="returned_mail")
    assert codes(case, TODAY + timedelta(days=5), item) == [("RETURNED", "EX")]


def test_deleted_means_monitor(case):
    item = add_item(case, bureaus=["EX"])
    add_letter(case, "P1L1", item, outcome="deleted")
    item.status["EX"] = "deleted"
    assert kinds(case, day_after_deadline(), item) == ["monitor"]


def test_part2_sequence_to_escalation(case):
    item = add_item(case, "public_record", bureaus=["EQ"], errors=["an incorrect date"])
    d = TODAY
    for code, result, expected in [
        ("P2L1", "verified", "P2L2A"),
        ("P2L2A", "verified", "P2L3"),
        ("P2L3", "no_response", "INCOMPLETE"),
        ("INCOMPLETE", "verified", "BIZARRE"),
    ]:
        add_letter(case, code, item, bureau="EQ", sent=d, outcome=result)
        assert codes(case, day_after_deadline(d), item) == [(expected, "EQ")], code
        d += timedelta(days=40)
    add_letter(case, "BIZARRE", item, bureau="EQ", sent=d, outcome="verified")
    acts = workflow.plan(case, day_after_deadline(d)).actions
    commands = " ".join(a.command for a in acts)
    for flag in ("cfpb_complaint", "ag_complaint", "bbb_complaint", "small_claims", "data_miners"):
        assert flag in commands
    assert "letter make COURT_CLERK" in commands


def test_no_response_from_bureau_gets_p2l2b(case):
    item = add_item(case, bureaus=["TU"], kind="public_record")
    add_letter(case, "P2L1", item, bureau="TU", outcome="no_response")
    assert codes(case, day_after_deadline(), item) == [("P2L2B", "TU")]


def test_credit_repair_accusation_gets_stall_letter_now(case):
    item = add_item(case, "public_record", bureaus=["EX"])
    add_letter(case, "P2L1", item, bureau="EX", outcome="credit_repair_accusation")
    assert codes(case, TODAY + timedelta(days=10), item) == [("STALL", "EX")]
    later = TODAY + timedelta(days=12)
    add_letter(case, "STALL", item, bureau="EX", sent=later, outcome="verified")
    assert codes(case, day_after_deadline(later, 15), item) == [("P2L2A", "EX")]


def test_late_payments_and_goodwill(case):
    late = add_item(case, "late_payment", bureaus=["EX"])
    assert codes(case, TODAY, late) == [("LP1", "")]
    add_letter(case, "LP1", late, outcome="verified")
    assert codes(case, day_after_deadline(), late) == [("LP2", "")]

    gw = add_item(case, "late_payment", bureaus=["EX"], strategy="goodwill")
    assert codes(case, TODAY, gw) == [("GW", "")]
    add_letter(case, "GW", gw, outcome="verified")
    assert codes(case, day_after_deadline(), gw) == [("GW", "")]
    second = TODAY + timedelta(days=40)
    add_letter(case, "GW", gw, sent=second, outcome="verified")
    assert codes(case, day_after_deadline(second), gw) == [("P1L1", "")]


def test_repossession_letter2_after_15_days(case):
    repo = add_item(case, "repossession", bureaus=["EQ"])
    assert codes(case, TODAY, repo) == [("REPO1", "")]
    add_letter(case, "REPO1", repo, outcome="no_response")
    assert codes(case, day_after_deadline(TODAY, 15), repo) == [("REPO2", "EQ")]


def test_medical_and_chexsystems_entry_letters(case):
    med = add_item(case, "medical")
    assert codes(case, TODAY, med) == [("HIPAA_CA", "")]
    chex = add_item(case, "chexsystems", bureaus=["CX"])
    add_letter(case, "P1L1", chex, outcome="no_response", marked=True)
    second = TODAY + timedelta(days=40)
    add_letter(case, "P1L2B", chex, sent=second, outcome="no_response")
    assert codes(case, day_after_deadline(second), chex) == [("CHEX", "CX")]


def test_identity_theft_items_go_to_fraud_departments(case):
    item = add_item(case, "identity_theft", bureaus=["EQ", "TU"], recognized="no")
    assert codes(case, TODAY, item) == [("IDT", "EQ"), ("IDT", "TU")]


def test_inquiries(case):
    case.profile.skip_personal_info = False
    inq = add_item(case, "inquiry", bureaus=["EQ"], credit_granted=False)
    granted = add_item(case, "inquiry", bureaus=["EQ"], credit_granted=True)
    acts = workflow.plan(case, TODAY).actions
    assert any(a.code == "INQ1" and inq.id in a.item_ids for a in acts)
    assert any(a.kind == "blocked" and a.code == "INQ2" for a in acts)  # PI letter not done yet
    assert not any(a.kind == "make_letter" and granted.id in a.item_ids for a in acts)

    pi = add_letter(case, "PI", [], bureau="EQ", outcome="updated")
    assert pi.track == "PI:EQ"
    assert ("INQ2", "EQ") in codes(case, TODAY, inq)

    add_letter(case, "INQ1", inq, outcome="no_response")
    add_letter(case, "INQ2", inq, bureau="EQ", outcome="verified")
    assert ("INQ3", "EQ") in codes(case, day_after_deadline(), inq)


def test_personal_info_letters_come_first(case):
    case.profile.skip_personal_info = False
    add_item(case)
    first = workflow.plan(case, TODAY).due_now(TODAY)[:3]
    assert [(a.code, a.bureau) for a in first] == [("PI", "EX"), ("PI", "EQ"), ("PI", "TU")]


def test_early_exclusion_window(case):
    item = add_item(case, "late_payment", bureaus=["TU", "EX"],
                    estimated_removal={"TU": "2027-05", "EX": "2027-05"})
    assert ("EARLY", "TU") in codes(case, date(2026, 11, 1), item)   # TU: 6 months early
    assert ("EARLY", "EX") not in codes(case, date(2026, 11, 1), item)  # EX: only 3 months
    assert ("EARLY", "EX") in codes(case, date(2027, 2, 1), item)


def test_reinsertion_gets_the_5_day_letter(case):
    item = add_item(case, bureaus=["EX"])
    add_letter(case, "P1L1", item, outcome="deleted")
    item.status["EX"] = "reinserted"
    item.reinserted_on["EX"] = (TODAY + timedelta(days=90)).isoformat()
    later = TODAY + timedelta(days=95)
    assert ("REINSERT", "EX") in codes(case, later, item)
