"""The Credit Secrets process as rules: which letter comes next, and when.

The book's timing rules this follows:
- Send everything certified mail, return receipt (goodwill letters can go regular mail).
- The clock starts the day they sign for your letter.
- ALWAYS wait 30 days before the next letter, even if they answer sooner.
- On day 31, pull fresh reports from all 3 bureaus and check whether the item is
  marked "disputed".
- Part 1 (creditor / collector) first, then Part 2 (each bureau). Public records
  (and federal student loans) start at Part 2.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

from . import rules
from .case import Case, Item, Letter
from .letters import PART1, SPECS, LetterSpec

CERTIFIED = "certified mail, return receipt requested (or electronic delivery confirmation)"
COLLECTOR_KINDS = {"collection", "medical"}
PART2_FIRST_KINDS = {"public_record", "student_loan_federal", "chexsystems_direct"}
NO_PART1_KINDS = {"public_record", "student_loan_federal", "identity_theft"}
PART1_ENTRY_CODES = {"P1L1", "HIPAA_CA"}
PART2_ENTRY_CODES = {"P2L1", "CHEX", "REPO2", "RETURNED", "IDT"}
ALT_CODES = ("INCOMPLETE", "BIZARRE")
NEGATIVE_RESULTS = {"verified", "updated", "proof_with_signature"}
ESCALATE = "ESCALATE"
PART2 = "PART2"
NEED_DISPUTED = "NEED_DISPUTED"


@dataclass
class Action:
    item_ids: list[str]
    kind: str  # make_letter | mail | confirm_delivery | wait | record_outcome | task | monitor | blocked | info
    message: str
    due: date | None = None
    code: str = ""
    bureau: str = ""
    letter_id: str = ""
    command: str = ""
    sort_key: int = 50

    def is_due(self, today: date) -> bool:
        if self.kind in ("wait", "monitor", "info"):
            return False
        return self.due is None or self.due <= today


@dataclass
class Plan:
    actions: list[Action] = field(default_factory=list)

    def due_now(self, today: date) -> list[Action]:
        return [a for a in self.actions if a.is_due(today)]

    def upcoming(self, today: date) -> list[Action]:
        return [a for a in self.actions if not a.is_due(today)]


# ---------------------------------------------------------------------------
# helpers


def parse(value: str) -> date | None:
    return date.fromisoformat(value) if value else None


def clock_start(letter: Letter) -> date | None:
    """The day the 30-day clock started: when they signed for it."""
    if letter.delivered_on:
        return parse(letter.delivered_on)
    spec = SPECS[letter.code]
    if not spec.certified and letter.mailed_on:
        return parse(letter.mailed_on) + timedelta(days=5)
    return None


def next_step_date(letter: Letter) -> date | None:
    start = clock_start(letter)
    if start is None:
        return None
    return start + timedelta(days=SPECS[letter.code].wait_days)


def make_action(code: str, items: list[Item], due: date, why: str, bureau: str = "") -> Action:
    spec = SPECS[code]
    ids = [i.id for i in items]
    target = ""
    if spec.needs_bureau:
        names = rules.FRAUD_ADDRESSES if spec.send_to == "bureau_fraud" else rules.BUREAUS
        target = f" to {names[bureau]['name']}" if bureau in names else f" to {bureau}"
    elif items and spec.send_to in ("furnisher", "creditor", "repo_parties"):
        target = f" to {items[0].furnisher}"
    if len(ids) > 1:
        item_flag = f"--items {','.join(ids)}"
    elif ids:
        item_flag = f"--item {ids[0]}"
    else:
        item_flag = ""
    cmd = f"letter make {code} {item_flag}".strip()
    if spec.needs_bureau or (bureau and code == "PI"):
        cmd += f" --bureau {bureau}"
    return Action(
        item_ids=ids,
        kind="make_letter",
        message=f"Send {spec.title}{target} (p.{spec.page}). {why}".strip(),
        due=due,
        code=code,
        bureau=bureau,
        command=cmd,
        sort_key=20,
    )


def pending_action(letter: Letter, today: date) -> Action | None:
    """What's left to do on a letter that has no outcome yet (or None if it's resolved)."""
    spec = SPECS[letter.code]
    ids = list(letter.item_ids)
    if letter.outcome:
        return None
    if not letter.mailed_on:
        how = CERTIFIED if spec.certified else "regular mail"
        sign = (
            "Sign it (the book says to sign this one) and"
            if letter.code == "CHEX"
            else "Proofread it, keep your typed name (don't sign), make a copy for your file, and"
        )
        return Action(
            ids, "mail",
            f"Print {letter.id} ({spec.title}) for {letter.recipient_name}. {sign} send it {how}.",
            due=today, letter_id=letter.id, sort_key=10,
            command=f"letter mailed {letter.id} --date {today.isoformat()} --tracking <number>",
        )
    start = clock_start(letter)
    if start is None:
        return Action(
            ids, "confirm_delivery",
            f"Check USPS tracking for {letter.id} ({letter.recipient_name}) and record the day they "
            "signed for it - that's when their 30 days start.",
            due=today, letter_id=letter.id, sort_key=15,
            command=f"letter delivered {letter.id} --date <YYYY-MM-DD>",
        )
    due = start + timedelta(days=spec.wait_days)
    check = _day_check_text(letter)
    if today < due:
        return Action(
            ids, "wait",
            f"{letter.id} ({letter.code}) was signed for {start.isoformat()}. Day {spec.wait_days} is "
            f"{due.isoformat()}: {check} If a reply arrives sooner, record it, but still wait.",
            due=due, letter_id=letter.id, sort_key=60,
        )
    return Action(
        ids, "record_outcome",
        f"Day {spec.wait_days} for {letter.id} ({letter.code} to {letter.recipient_name}). {check}",
        due=due, letter_id=letter.id, sort_key=5,
        command=f"letter outcome {letter.id} --result <{'|'.join(_results_for(letter))}>"
        + (" --marked-disputed <yes|no>" if letter.code in PART1_ENTRY_CODES else ""),
    )


def _results_for(letter: Letter) -> list[str]:
    spec = SPECS[letter.code]
    if spec.group == "personal_info":
        return ["updated", "not_updated"]
    if spec.group in ("part2", "inquiry_bureau"):
        return ["deleted", "verified", "updated", "no_response", "credit_repair_accusation"]
    if letter.code in PART1_ENTRY_CODES:
        return [
            "deleted", "verified", "no_response", "original_creditor_responded",
            "proof_with_signature", "returned_mail",
        ]
    return ["deleted", "verified", "no_response", "returned_mail"]


def _day_check_text(letter: Letter) -> str:
    spec = SPECS[letter.code]
    if spec.group == "personal_info":
        return "Check the bureau's USPS reply and your new report: were the old addresses/names removed?"
    if letter.code in PART1_ENTRY_CODES:
        return (
            "Pull fresh, dated copies of all 3 reports that day and check whether the account is "
            "marked 'disputed' in its comments/remarks (they must add it within 30 days), plus "
            "whatever reply you got."
        )
    if spec.group == "part1":
        return "Pull fresh dated reports, check the account and any reply you got."
    if spec.group == "inquiry_creditor":
        return "Check for the creditor's reply and whether the inquiry is gone from your reports."
    return "Check the bureau's reply and a fresh report from that bureau."


def _wait_until(letter: Letter, today: date, then: str) -> Action | None:
    due = next_step_date(letter)
    if due is None or today >= due:
        return None
    return Action(
        list(letter.item_ids), "wait",
        f"Reply to {letter.id} recorded. The book says always wait the full 30 days: on "
        f"{due.isoformat()} {then}",
        due=due, letter_id=letter.id, sort_key=60,
    )


def _monitor(item: Item, where: str) -> Action:
    return Action(
        [item.id], "monitor",
        f"{item.label()} deleted from {where}. Keep checking your reports monthly; if it comes "
        f"back, run: item reinserted {item.id} --bureau <EX|EQ|TU>",
        sort_key=90,
    )


# ---------------------------------------------------------------------------
# accounts


def part1_entry(item: Item) -> str:
    if item.kind == "late_payment":
        return "GW" if item.strategy == "goodwill" else "LP1"
    if item.kind == "medical":
        return "HIPAA_CA"
    if item.kind == "repossession":
        return "P1L1" if item.strategy == "needs_info" else "REPO1"
    return "P1L1"


def part2_entry(item: Item, returned: bool = False) -> str:
    if returned:
        return "RETURNED"
    return {"chexsystems": "CHEX", "repossession": "REPO2", "identity_theft": "IDT"}.get(
        item.kind, "P2L1"
    )


def _part1_rule(item: Item, p1: list[Letter], last: Letter, result: str) -> str:
    code = last.code
    first = next((lt for lt in p1 if lt.code in PART1_ENTRY_CODES), None)
    if code in PART1_ENTRY_CODES:
        if item.kind == "repossession" and code == "P1L1":
            return "REPO1"
        if result == "original_creditor_responded":
            return "P1L2C"
        if result in ("verified", "updated"):
            return "P1L2A"
        if result == "no_response":
            return "P1L2B"
        if result == "proof_with_signature":
            # FAQ p.167: not game over - they still must mark it disputed.
            if last.marked_disputed is None:
                return NEED_DISPUTED
            return "P1L3" if last.marked_disputed is False else PART2
        return "P1L2A"
    if code in ("P1L2A", "P1L2B", "P1L2C"):
        if first is not None:
            if first.marked_disputed is None:
                return NEED_DISPUTED
            if first.marked_disputed is False and not any(lt.code == "P1L3" for lt in p1):
                return "P1L3"
        return PART2
    if code == "LP1":
        return "LP2"
    if code == "GW":
        # FAQ p.172: try again (a different person may help); then dispute with P1L1.
        return "GW" if sum(lt.code == "GW" for lt in p1) < 2 else "P1L1"
    return PART2  # P1L3, LP2, REPO1 and anything else: on to the bureaus


def _eval_part1(case: Case, item: Item, today: date) -> tuple[list[Action], str | None]:
    """Returns (actions, part2_entry). part2_entry is None while Part 1 is still running."""
    p1 = case.letters_for(item.id, PART1)
    if not p1:
        actions = []
        if item.kind in COLLECTOR_KINDS and "license_checked" not in item.flags:
            actions.append(
                Action(
                    [item.id], "task",
                    f"Pre-dispute (p.40): check whether {item.furnisher} is licensed/bonded to "
                    f"collect in {case.profile.state or 'your state'} (book link: "
                    "creditsecrets.com/credit-score-hub/cornerstone). If not, screenshot the proof "
                    "and file complaints with the CFPB, your AG, the collector's AG and the BBB.",
                    due=today, sort_key=19,
                    command=f"item flag {item.id} license_checked",
                )
            )
        code = part1_entry(item)
        why = {
            "P1L1": "Ask them to validate; the clock starts when they sign for it.",
            "HIPAA_CA": "Medical collection: validation, dispute and cease & desist. Also consider "
            "the HIPAA letter to the original provider (HIPAA_PROVIDER).",
            "LP1": "Ask them to validate the late payment(s).",
            "GW": "Ask for a goodwill removal of the late payment(s).",
            "REPO1": "Send to the collector, original creditor AND dealer. If you don't have the "
            "details it needs, send P1L1 first (set strategy=needs_info).",
        }[code]
        actions.append(make_action(code, [item], today, why))
        return actions, None

    last = p1[-1]
    pending = pending_action(last, today)
    if pending:
        return [pending], None
    result = last.result_for(item.id)
    if result == "deleted":
        return [_monitor(item, "your reports (creditor/collector deleted it)")], None
    if result == "returned_mail":
        return [], part2_entry(item, returned=True)

    nxt = _part1_rule(item, p1, last, result)
    check_first = (
        last.code in PART1_ENTRY_CODES and last.marked_disputed is None and nxt != NEED_DISPUTED
    )
    if check_first:
        due = next_step_date(last)
        then_prefix = (
            "pull fresh, dated reports from all 3 bureaus, check whether the account is marked "
            f"'disputed' (record it: letter outcome {last.id} --marked-disputed yes|no), then "
        )
        if due is None or today >= due:
            disputed_prompt = Action(
                [item.id], "record_outcome",
                f"Day 31 check for {last.id}: is {item.label()} marked 'disputed' on your fresh "
                "reports? You'll need this for Part 1 Letter #3.",
                due=due or today, letter_id=last.id, sort_key=6,
                command=f"letter outcome {last.id} --marked-disputed <yes|no>",
            )
        else:
            disputed_prompt = None
    else:
        then_prefix = ""
        disputed_prompt = None
    if nxt == NEED_DISPUTED:
        first = next(lt for lt in p1 if lt.code in PART1_ENTRY_CODES or lt is last)
        return [
            Action(
                [item.id], "record_outcome",
                f"Record whether {item.label()} showed as 'disputed' on your day-31 reports after "
                f"{first.id} - it decides whether you send Part 1 Letter #3.",
                due=today, letter_id=first.id, sort_key=5,
                command=f"letter outcome {first.id} --marked-disputed <yes|no>",
            )
        ], None
    extra = [disputed_prompt] if disputed_prompt else []
    if nxt == PART2:
        entry = "REPO2" if last.code == "REPO1" else part2_entry(item)
        wait = _wait_until(last, today, f"{then_prefix}send {entry} to each bureau reporting it.")
        return ([wait], None) if wait else (extra, entry)
    wait = _wait_until(last, today, f"{then_prefix}send {nxt} ({SPECS[nxt].title}).")
    if wait:
        return [wait], None
    return extra + [make_action(nxt, [item], today, SPECS[nxt].when)], None


def _eval_part2(case: Case, item: Item, bureau: str, entry: str, today: date) -> list[Action]:
    track = f"P2:{bureau}"
    p2 = case.letters_for(item.id, track)
    if not p2:
        if entry == "IDT" and bureau not in rules.FRAUD_ADDRESSES:
            entry = "P2L1"
        return [make_action(entry, [item], today, SPECS[entry].when, bureau=bureau)]
    last = p2[-1]
    pending = pending_action(last, today)
    if pending:
        return [pending]
    result = last.result_for(item.id)
    if result == "deleted":
        return [_monitor(item, rules.BUREAU_NAMES.get(bureau, bureau))]
    if result == "credit_repair_accusation":
        return [make_action("STALL", [item], today, SPECS["STALL"].when, bureau=bureau)]

    effective = last.code
    if effective == "STALL":
        effective = next((lt.code for lt in reversed(p2) if lt.code != "STALL"), "P2L1")
    sent = {lt.code for lt in p2}
    is_entry = effective in PART2_ENTRY_CODES or (effective in ALT_CODES and p2[0].code == effective)
    if is_entry:
        nxt = "P2L2A" if result in NEGATIVE_RESULTS else "P2L2B"
    elif effective in ("P2L2A", "P2L2B"):
        nxt = "P2L3"
    else:  # after P2L3: the Bizarre / Incomplete letters "in lieu of legal action", then escalate
        nxt = ESCALATE
        for alt in ALT_CODES:
            if alt not in sent and (alt != "INCOMPLETE" or item.errors):
                nxt = alt
                break
    if nxt == ESCALATE:
        wait = _wait_until(last, today, "move on to complaints and small claims.")
        return [wait] if wait else _escalation(case, item, today)
    wait = _wait_until(last, today, f"send {nxt} ({SPECS[nxt].title}).")
    if wait:
        return [wait]
    return [make_action(nxt, [item], today, SPECS[nxt].when, bureau=bureau)]


def _escalation(case: Case, item: Item, today: date) -> list[Action]:
    actions: list[Action] = []
    for key, text in rules.COMPLAINTS.items():
        if key not in item.flags:
            actions.append(
                Action([item.id], "task", f"{item.label()}: {text}", due=today, sort_key=25,
                       command=f"item flag {item.id} {key}")
            )
    if item.kind == "public_record":
        if "court_letter" not in item.flags and not case.letters_for(item.id, "COURT_CLERK"):
            actions.append(
                make_action("COURT_CLERK", [item], today,
                            "Public records loophole (p.74-75): get proof the courts don't furnish "
                            "or verify records with the bureaus, then send it to the bureaus.")
            )
        if "data_miners" not in item.flags:
            actions.append(
                Action([item.id], "task",
                       "Public records (p.76-80): freeze and opt-out with the data miners "
                       "(LexisNexis, Innovis, ARS, LCI); request your LexisNexis/CoreLogic/Innovis/"
                       "ARS files and dispute errors there with Part 2 letters (bureau codes LN, "
                       "IN, ARS, LCI, CO). Run 'info data-miners'.",
                       due=today, sort_key=26, command=f"item flag {item.id} data_miners")
            )
    if item.kind == "student_loan_federal" and not case.letters_for(item.id, PART1):
        actions.append(make_action("P1L1", [item], today,
                                   "Federal student loans: after Part 2, move to Part 1 letters."))
    if "small_claims" not in item.flags:
        actions.append(
            Action([item.id], "task",
                   f"{item.label()}: small claims option (Chapter 4). Build your 3-ring binder from "
                   f"'timeline {item.id}', look up the registered agent, and sue for a small amount "
                   "- the goal is removal. Run 'info lawsuits'. Mark done when decided.",
                   due=today, sort_key=40, command=f"item flag {item.id} small_claims")
        )
    if not actions:
        actions.append(
            Action([item.id], "monitor",
                   f"{item.label()}: all letters and escalation steps done. Keep monitoring.",
                   sort_key=90)
        )
    return actions


def _reinsertion(case: Case, item: Item, bureau: str, today: date) -> list[Action]:
    since = item.reinserted_on.get(bureau, "")
    letters = [
        lt for lt in case.letters_for(item.id, f"REINSERT:{bureau}")
        if not since or lt.created_on >= since
    ]
    if not letters:
        return [
            make_action("REINSERT", [item], today,
                        "A deleted item came back without the required 5-business-day written "
                        "notice. Also file a CFPB complaint against the bureau.", bureau=bureau)
        ]
    last = letters[-1]
    pending = pending_action(last, today)
    if pending:
        return [pending]
    if last.result_for(item.id) == "deleted":
        return [_monitor(item, rules.BUREAU_NAMES.get(bureau, bureau))]
    return _escalation(case, item, today)


def _early_exclusion(case: Case, item: Item, today: date) -> list[Action]:
    actions = []
    for bureau, ym in item.estimated_removal.items():
        months = rules.EARLY_EXCLUSION_MONTHS.get(bureau)
        if not months or not ym or item.bureau_status(bureau) == "deleted":
            continue
        year, month = (int(x) for x in ym.split("-")[:2])
        month -= months
        while month < 1:
            month += 12
            year -= 1
        opens = date(year, month, 1)
        early = case.letters_for(item.id, f"EARLY:{bureau}")
        if early:
            last = early[-1]
            if last.outcome and last.result_for(item.id) != "deleted":
                actions.append(
                    Action([item.id], "info",
                           f"{item.label()}: early exclusion not granted by "
                           f"{rules.BUREAU_NAMES[bureau]}. The book says call and ask for a "
                           "representative in the United States / a supervisor, and explain you're "
                           "not disputing - you're asking for early exclusion.",
                           sort_key=85)
                )
            continue
        if today >= opens:
            actions.append(
                make_action("EARLY", [item], today,
                            f"Scheduled removal {ym} is inside the {months}-month early exclusion "
                            "window. Attach the page showing the removal date.", bureau=bureau)
            )
        else:
            actions.append(
                Action([item.id], "info",
                       f"{item.label()}: early exclusion window with "
                       f"{rules.BUREAU_NAMES[bureau]} opens {opens.isoformat()} (removal {ym}).",
                       due=opens, code="EARLY", bureau=bureau, sort_key=80)
            )
    return actions


def item_actions(case: Case, item: Item, today: date) -> list[Action]:
    actions: list[Action] = []
    actions += _early_exclusion(case, item, today)
    for bureau in item.bureaus:
        if item.bureau_status(bureau) == "reinserted":
            actions += _reinsertion(case, item, bureau, today)
    if item.bureaus and not item.active_bureaus():
        has_monitor = any(a.kind == "monitor" for a in actions)
        return actions if has_monitor else actions + [_monitor(item, "all bureaus")]

    if item.kind in NO_PART1_KINDS:
        entry: str | None = part2_entry(item)
    else:
        p1_actions, entry = _eval_part1(case, item, today)
        actions += p1_actions
    if entry is None:
        return actions
    if not item.bureaus:
        actions.append(
            Action([item.id], "task",
                   f"{item.label()}: Part 2 goes to each bureau reporting this item - record which "
                   "ones (EX, EQ, TU; CX for ChexSystems).",
                   due=today, sort_key=20, command=f"item set {item.id} bureaus=EX,EQ,TU")
        )
    for bureau in item.active_bureaus():
        if item.bureau_status(bureau) == "reinserted":
            continue
        actions += _eval_part2(case, item, bureau, entry, today)
    return _dedupe(actions)


# ---------------------------------------------------------------------------
# inquiries and personal information


def _pi_pending(case: Case, bureau: str) -> bool:
    """True while the personal info letter to this bureau is planned or still open."""
    if case.profile.skip_personal_info or bureau not in rules.MAIN_BUREAUS:
        return False
    sent = [lt for lt in case.letters if lt.track == f"PI:{bureau}"]
    return not sent or not sent[-1].outcome


def inquiry_actions(case: Case, today: date) -> list[Action]:
    actions: list[Action] = []
    inquiries = [i for i in case.items if i.kind == "inquiry"]
    eligible = []
    for item in inquiries:
        if item.credit_granted:
            actions.append(
                Action([item.id], "info",
                       f"{item.label()}: credit was granted - the book says do NOT dispute it "
                       "(they could close the account).", sort_key=95)
            )
            continue
        if item.bureaus and not item.active_bureaus():
            actions.append(_monitor(item, "all bureaus"))
            continue
        eligible.append(item)

    # Inquiry Letter 1: to each creditor.
    creditor_done: dict[str, Letter | None] = {}
    for item in eligible:
        sent = case.letters_for(item.id, "INQ1")
        if not sent:
            actions.append(make_action("INQ1", [item], today, "Certified mail; keep a copy."))
            creditor_done[item.id] = None
            continue
        last = sent[-1]
        pending = pending_action(last, today)
        if pending:
            actions.append(pending)
            creditor_done[item.id] = None
        else:
            creditor_done[item.id] = last

    # Inquiry Letters 2 and 3: to each bureau, grouped.
    for bureau in rules.MAIN_BUREAUS:
        on_bureau = [i for i in eligible if bureau in i.active_bureaus()]
        fresh: list[Item] = []
        follow_up: list[Item] = []
        for item in on_bureau:
            letters = case.letters_for(item.id, f"INQ:{bureau}")
            if not letters:
                fresh.append(item)
                continue
            last = letters[-1]
            pending = pending_action(last, today)
            if pending:
                if not any(a.letter_id == last.id and a.kind == pending.kind for a in actions):
                    actions.append(pending)
                continue
            result = last.result_for(item.id)
            if result == "deleted":
                continue
            if last.code == "INQ2":
                inq1 = creditor_done.get(item.id)
                if inq1 is None:
                    continue  # wait for the creditor letter to play out too
                if inq1.result_for(item.id) == "deleted":
                    continue
                wait = _wait_until(last, today, "send Inquiry Letter 3.")
                if wait:
                    actions.append(wait)
                else:
                    follow_up.append(item)
            else:
                wait = _wait_until(last, today, "escalate.")
                actions += [wait] if wait else _escalation(case, item, today)
        for code, group in (("INQ2", fresh), ("INQ3", follow_up)):
            if not group:
                continue
            if _pi_pending(case, bureau):
                actions.append(
                    Action([i.id for i in group], "blocked",
                           f"{code} to {rules.BUREAU_NAMES[bureau]} is waiting: the book says not "
                           "to send it at the same time as your personal information letter to "
                           "that bureau. It unlocks once the PI letter's outcome is recorded (or "
                           "run: profile skip_personal_info=yes).",
                           code=code, bureau=bureau, sort_key=70)
                )
            else:
                actions.append(make_action(code, group, today, SPECS[code].when, bureau=bureau))
    return _dedupe(actions)


def personal_info_actions(case: Case, today: date) -> list[Action]:
    if case.profile.skip_personal_info:
        return []
    actions: list[Action] = []
    for bureau in rules.MAIN_BUREAUS:
        sent = [lt for lt in case.letters if lt.track == f"PI:{bureau}"]
        if not sent:
            act = make_action(
                "PI", [], today,
                "#Jumpstart: first update your address on old POSITIVE accounts with those "
                "creditors (portal/phone/letter) so you don't lose them. Enclose copies of your "
                "driver's license, SSN card and a recent utility bill.",
                bureau=bureau,
            )
            act.sort_key = 12
            actions.append(act)
            continue
        last = sent[-1]
        pending = pending_action(last, today)
        if pending:
            actions.append(pending)
        elif last.outcome == "not_updated" and len(sent) < 2:
            actions.append(
                Action([], "task",
                       f"{rules.BUREAU_NAMES[bureau]} didn't update your personal info. Options "
                       "(p.29): call them about personal info only (don't start any disputes or "
                       "give an email); or get your ID + a bill notarized (UPS store) and resend "
                       "(letter make PI --bureau " + bureau + "); Experian also takes uploads at "
                       "experian.com/upload. If they say it's linked to accounts, move on to "
                       "disputes and come back later.",
                       due=today, bureau=bureau, sort_key=35)
            )
    return actions


# ---------------------------------------------------------------------------


def _dedupe(actions: list[Action]) -> list[Action]:
    seen: set[tuple] = set()
    out = []
    for a in actions:
        key = (a.kind, a.command or a.message, a.bureau, a.letter_id)
        if key in seen:
            continue
        seen.add(key)
        out.append(a)
    return out


def side_letter_actions(case: Case, today: date) -> list[Action]:
    """Letters outside the main tracks (early exclusion, HIPAA provider, court clerk...)."""
    actions = []
    for lt in case.letters:
        if lt.track == PART1 or lt.track.startswith(("P2:", "INQ", "PI:", "REINSERT:")):
            continue
        pending = pending_action(lt, today)
        if pending:
            actions.append(pending)
    return actions


def plan(case: Case, today: date) -> Plan:
    actions: list[Action] = []
    actions += personal_info_actions(case, today)
    actions += inquiry_actions(case, today)
    for item in case.items:
        if item.kind == "inquiry":
            continue
        actions += item_actions(case, item, today)
    actions += side_letter_actions(case, today)
    actions = _dedupe(actions)
    actions.sort(key=lambda a: (a.due or date.max, a.sort_key))
    return Plan(actions)
