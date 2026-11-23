"""The letter library: every letter in Credit Secrets, filled in from your case file."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from . import rules
from .case import Case, Item, Letter

TEMPLATE_DIR = Path(__file__).parent / "letters"
FIELD_RE = re.compile(r"{{([a-z0-9_]+)}}")

# Tracks a letter can belong to.
PART1 = "P1"  # letters to the creditor / collection agency
PART2 = "P2"  # letters to a credit bureau (P2:EX, P2:EQ, ...)


@dataclass(frozen=True)
class LetterSpec:
    code: str
    title: str
    page: int
    send_to: str  # furnisher | creditor | bureau | bureau_fraud | provider | court_clerk | repo_parties
    group: str  # personal_info | inquiry_creditor | inquiry_bureau | part1 | part2 | other
    when: str
    certified: bool = True
    wait_days: int = 31  # days after they sign for it before the next step
    defaults: dict[str, str] = field(default_factory=dict)
    from_book: bool = True

    @property
    def template(self) -> str:
        return (TEMPLATE_DIR / f"{self.code}.txt").read_text(encoding="utf-8")

    @property
    def fields(self) -> list[str]:
        seen: list[str] = []
        for name in FIELD_RE.findall(self.template):
            if name not in seen:
                seen.append(name)
        return seen

    @property
    def needs_bureau(self) -> bool:
        return self.send_to in ("bureau", "bureau_fraud")


SPECS: dict[str, LetterSpec] = {
    s.code: s
    for s in [
        LetterSpec(
            "PI", "Change of Address / personal information update", 30, "bureau", "personal_info",
            "#Jumpstart (Chapter 1). Send to each bureau to remove old addresses, name variations, "
            "SSNs, birth dates, employers and phone numbers. Enclose a copy of your driver's "
            "license, SSN card and a recent utility bill (or pay stub, insurance, registration, "
            "phone bill). Update your address on old POSITIVE accounts with those creditors first.",
        ),
        LetterSpec(
            "INQ1", "Inquiry Removal Letter 1 - to the creditor", 34, "creditor", "inquiry_creditor",
            "Send directly to the company that made an inquiry you don't recall authorizing. "
            "Do NOT dispute an inquiry where credit was granted (they can close the account).",
        ),
        LetterSpec(
            "INQ2", "Inquiry Removal Letter 2 - to the credit bureau", 35, "bureau", "inquiry_bureau",
            "Send to the bureau to dispute inquiries without permissible purpose. You can list all "
            "'denial' inquiries in one letter. Do NOT send at the same time as your personal "
            "information update letters.",
        ),
        LetterSpec(
            "INQ3", "Inquiry Removal Letter 3 - follow-up to the credit bureau", 36, "bureau",
            "inquiry_bureau",
            "Send to the bureau if you get no reply or they say the inquiries were 'verified'.",
        ),
        LetterSpec(
            "P1L1", "Part 1, Letter #1 - validation request", 48, "furnisher", "part1",
            "First letter for every negative account that isn't a public record. Send directly to "
            "the bank, creditor or collection agency that reported it (address from your report).",
        ),
        LetterSpec(
            "P1L2A", "Part 1, Letter #2A - they replied 'verified'", 50, "furnisher", "part1",
            "Send only if they replied to Letter #1 saying it's verified/accurate. No matter what "
            "their response says, if it doesn't say they're deleting the account, send this.",
        ),
        LetterSpec(
            "P1L2B", "Part 1, Letter #2B - no reply", 52, "furnisher", "part1",
            "Send ONLY if you did not hear back from Letter #1.",
        ),
        LetterSpec(
            "P1L2C", "Part 1, Letter #2C - original creditor answered for the collector", 54,
            "furnisher", "part1",
            "Send if you disputed a collection account but got a response from the original "
            "creditor instead of the collection agency.",
        ),
        LetterSpec(
            "P1L3", "Part 1, Letter #3 - not marked 'disputed' within 30 days", 56, "furnisher",
            "part1",
            "Wait until day 31 after they signed for Letter #1, check your reports. If the item is "
            "NOT marked 'disputed' in the comments, send this after Letter #2A or #2B.",
        ),
        LetterSpec(
            "P2L1", "Part 2, Letter #1 - original dispute with the credit bureau", 65, "bureau",
            "part2",
            "Send to each bureau reporting the item if Part 1 didn't get it removed. Start here "
            "for public records (and federal student loans).",
        ),
        LetterSpec(
            "P2L2A", "Part 2, Letter #2A - bureau says 'verified': method of verification", 67,
            "bureau", "part2",
            "Send if the bureau says the account was 'verified' as accurate.",
        ),
        LetterSpec(
            "P2L2B", "Part 2, Letter #2B - bureau did not respond", 69, "bureau", "part2",
            "Send if you get no response from the bureau to Letter #1.",
        ),
        LetterSpec(
            "P2L3", "Part 2, Letter #3 - final letter to the bureau", 71, "bureau", "part2",
            "Send if you haven't heard back or they keep 'verifying' without proof and you are "
            "ready to take legal action (or use the Bizarre or Incomplete/Missing Info letter "
            "instead of legal action).",
        ),
        LetterSpec(
            "STALL", "Stall tactic - credit repair accusation", 96, "bureau", "part2",
            "Send if a bureau says your letter appears to come from a third party / credit repair "
            "company. Gives them 15 days, not 30 more.",
            wait_days=15,
        ),
        LetterSpec(
            "IDT", "Identity theft - FCRA 605B block request", 97, "bureau_fraud", "part2",
            "For accounts you never had and have no knowledge of. Create an FTC Identity Theft "
            "Report first. Write to each bureau's FRAUD address, one at a time. Circle the items "
            "on your report and enclose ID + FCRA 605B.",
        ),
        LetterSpec(
            "EARLY", "Early exclusion request (not a dispute)", 100, "bureau", "other",
            "When an item's scheduled removal date is within the bureau's early exclusion window "
            "(TU 6 months, EX 3 months, EQ 1-2 months). If it isn't removed, call and ask for a US "
            "supervisor - say it's not a dispute but an early exclusion request.",
        ),
        LetterSpec(
            "REINSERT", "5 Day Reinsertion letter", 102, "bureau", "other",
            "Send to the bureau if a deleted item is put back without written notice within 5 "
            "business days. Also file a CFPB complaint against the bureau.",
        ),
        LetterSpec(
            "LP1", "Late payments - first letter to the original creditor", 103, "furnisher",
            "part1", "Start here for one or multiple late payments.",
        ),
        LetterSpec(
            "LP2", "Late payments - second letter to the original creditor", 104, "furnisher",
            "part1",
            "If their response to the first letter doesn't say they removed the late payment(s).",
        ),
        LetterSpec(
            "GW", "Goodwill letter", 106, "furnisher", "part1",
            "For one or two late pays, after you've been current for a while. This is an admission "
            "the lates are yours. Regular mail is fine (no need for certified).",
            certified=False,
        ),
        LetterSpec(
            "INCOMPLETE", "Incomplete / missing info letter", 107, "bureau", "part2",
            "For an item you acknowledge is yours: challenge it on a technicality (truncated "
            "account number, wrong high balance, missing status, undated late pay, etc.). Should "
            "not replace Part 1 Letter 1.",
        ),
        LetterSpec(
            "RETURNED", "Returned mail letter", 108, "bureau", "part2",
            "If your letter to the address on your credit report came back undeliverable. Enclose "
            "a photocopy of the returned envelope.",
        ),
        LetterSpec(
            "BIZARRE", "Alternative / Bizarre letter", 109, "bureau", "part2",
            "Can be used for most circumstances, sent to the bureau. The misspellings and grammar "
            "errors are on purpose - meant to get past the bureau's automated system to a real "
            "employee.",
        ),
        LetterSpec(
            "CHEX", "Letter to ChexSystems", 127, "bureau", "part2",
            "Dispute a ChexSystems entry (P1L1 goes to the bank, this goes to ChexSystems). The "
            "book says to sign this one and send it registered mail.",
        ),
        LetterSpec(
            "REPO1", "Repo Letter 1 - collector, original creditor and dealer", 137, "repo_parties",
            "part1",
            "Send to the collection agency, original creditor AND car dealership. If you don't "
            "have the details it needs, send Part 1 Letter 1 first.",
            wait_days=15,
        ),
        LetterSpec(
            "REPO2", "Repo Letter 2 - credit bureaus", 139, "bureau", "part2",
            "Send to the bureaus 15 days after Repo Letter 1.",
        ),
        LetterSpec(
            "HIPAA_PROVIDER", "HIPAA letter to the original health care provider", 141, "provider",
            "other", "Medical collections: send to the provider's HIPAA Compliance Office.",
            wait_days=10,
            defaults={"charitable_hospital_line": ""},
        ),
        LetterSpec(
            "HIPAA_CA", "HIPAA collection agency validation, dispute, cease & desist", 143,
            "furnisher", "part1",
            "Medical collections: send to the collection agency (debt beyond SOL or invalid, and "
            "subject to HIPAA privacy laws).",
        ),
        LetterSpec(
            "COURT_CLERK", "Letter to a clerk of court (public records loophole)", 75, "court_clerk",
            "other",
            "Public records: write to a clerk of court NOT in the district where your record was "
            "filed, asking their procedure for verifying records with the credit bureaus. Enclose "
            "a self-addressed stamped envelope. The book describes this letter but has no "
            "template - this one is written from its instructions.",
            certified=False,
            from_book=False,
        ),
        LetterSpec(
            "WRITTEN_ONLY", "Communicate with me only in writing", 163, "furnisher", "other",
            "Stop a collection agency's phone calls (FAQ). Text taken from the book's FAQ answer.",
            from_book=False,
        ),
    ]
}

GROUP_TRACK_PREFIX = {
    "personal_info": "PI",
    "inquiry_creditor": "INQ1",
    "inquiry_bureau": "INQ",
    "part1": PART1,
    "part2": PART2,
}


def track_for(spec: LetterSpec, bureau: str) -> str:
    """Which conversation a letter belongs to: one per creditor, one per bureau."""
    if spec.group == "part1":
        return PART1
    if spec.group == "inquiry_creditor":
        return "INQ1"
    if spec.group in ("part2", "inquiry_bureau", "personal_info"):
        return f"{GROUP_TRACK_PREFIX[spec.group]}:{bureau}"
    if spec.needs_bureau:
        return f"{spec.code}:{bureau}"
    return spec.code


def fmt_date(value: str | date | None) -> str:
    if not value:
        return ""
    d = value if isinstance(value, date) else date.fromisoformat(value)
    return f"{d:%B} {d.day}, {d.year}"


def _one_line(address: str) -> str:
    return ", ".join(part.strip() for part in address.splitlines() if part.strip())


def _join_phrases(values: list[str]) -> str:
    values = [v for v in values if v]
    if len(values) <= 1:
        return "".join(values)
    return ", ".join(values[:-1]) + " and " + values[-1]


def _first_in_track(case: Case, item: Item, track: str, codes: tuple[str, ...] = ()) -> Letter | None:
    for lt in case.letters_for(item.id, track):
        if not codes or lt.code in codes:
            return lt
    return None


@dataclass
class Recipient:
    name: str
    address: str


def recipient_for(spec: LetterSpec, items: list[Item], bureau: str) -> Recipient:
    item = items[0] if items else None
    if spec.send_to == "bureau":
        info = rules.BUREAUS[bureau]
        return Recipient(info["name"], info["address"])
    if spec.send_to == "bureau_fraud":
        info = rules.FRAUD_ADDRESSES[bureau]
        return Recipient(info["name"], info["address"])
    if item is None:
        return Recipient("", "")
    if spec.send_to in ("furnisher", "creditor"):
        return Recipient(item.furnisher, item.furnisher_address)
    if spec.send_to == "provider":
        return Recipient(
            item.extra.get("provider_name", item.original_creditor),
            item.extra.get("provider_address", item.original_creditor_address),
        )
    if spec.send_to == "court_clerk":
        return Recipient(item.extra.get("court_name", ""), item.extra.get("court_address", ""))
    if spec.send_to == "repo_parties":
        return Recipient(item.furnisher, item.furnisher_address)
    return Recipient("", "")


def build_fields(
    case: Case,
    spec: LetterSpec,
    items: list[Item],
    bureau: str,
    today: date,
    overrides: dict[str, str] | None = None,
    recipient: Recipient | None = None,
) -> dict[str, str]:
    """Collect every value the letter needs from the case file."""
    p = case.profile
    item = items[0] if items else None
    rec = recipient or recipient_for(spec, items, bureau)
    values: dict[str, str] = dict(spec.defaults)
    values.update(
        {
            "date": fmt_date(today),
            "your_name": p.full_name,
            "your_address": p.address,
            "ssn_last4": p.ssn_last4,
            "recipient_name": rec.name,
            "recipient_address": rec.address,
            "current_address": _one_line(p.address),
            "name_on_id": p.full_name,
            "dob": p.dob,
            "employer": p.employer,
            "phone": p.phone,
            "state": p.state,
            "full_ssn": "[WRITE IN BY HAND: your full Social Security number]",
            "proof_of_identity": "[a copy of my driver's license/other government-issued "
            "identification card/other]",
        }
    )
    if item is not None:
        values.update(
            {
                "account_number": item.account_number,
                "derogatory_condition": item.derogatory_condition,
                "month_year": item.month_year,
                "furnisher_name": item.furnisher,
                "company_name": item.furnisher,
                "account_name": item.furnisher,
                "bank_name": item.furnisher,
                "collection_agency_name": item.furnisher,
                "original_creditor_name": item.original_creditor,
                "late_payment_dates": item.late_payment_dates,
                "inquiry_date": item.inquiry_date,
                "returned_address": _one_line(item.furnisher_address),
                "chex_reason_and_date": item.derogatory_condition,
                "chex_reason": item.derogatory_condition,
                "incorrect_info": _join_phrases(item.errors),
                "credit_bureaus": _join_phrases(
                    [rules.BUREAU_NAMES.get(b, b) for b in item.bureaus]
                ),
                "repo_state": p.state,
                "deletion_date": fmt_date(item.deleted_on.get(bureau, "")),
            }
        )
        if spec.send_to == "repo_parties":
            def block(name: str, address: str) -> str:
                return f"{name}\n{address}".strip() if name else ""

            values["collection_agency_block"] = block(item.furnisher, item.furnisher_address)
            values["original_creditor_block"] = block(
                item.original_creditor, item.original_creditor_address
            )
            values["car_dealer_block"] = block(
                item.extra.get("dealer_name", ""), item.extra.get("dealer_address", "")
            )
        values.update(_dates_from_history(case, spec, item, bureau))
        values.update({k: v for k, v in item.extra.items() if v})
    if spec.code in ("INQ2", "INQ3"):
        values["inquiries"] = "\n".join(
            f"{n}. {it.furnisher} - {it.inquiry_date}" for n, it in enumerate(items, 1)
        )
    if spec.code == "IDT":
        values["identity_theft_items"] = "\n".join(
            f"- {it.furnisher}, account {it.account_number or '(number not shown)'}"
            f" ({rules_kind(it)})"
            for it in items
        )
    for key, value in (overrides or {}).items():
        values[key] = value
    return values


def rules_kind(item: Item) -> str:
    return {
        "inquiry": "credit inquiry",
        "collection": "collection account",
        "charge_off": "credit account",
    }.get(item.kind, "credit account")


def _dates_from_history(case: Case, spec: LetterSpec, item: Item, bureau: str) -> dict[str, str]:
    out: dict[str, str] = {}
    track = track_for(spec, bureau)
    first = None
    if spec.code in ("P1L2A", "P1L2B", "P1L2C", "P1L3"):
        first = _first_in_track(case, item, "P1", ("P1L1", "HIPAA_CA"))
    elif spec.code in ("P2L2A", "P2L2B", "P2L3"):
        first = _first_in_track(case, item, track)
    elif spec.code == "INQ3":
        first = _first_in_track(case, item, track, ("INQ2",))
    elif spec.code == "REINSERT":
        first = _first_in_track(case, item, f"P2:{bureau}") or _first_in_track(case, item, "P1")
    if first is not None:
        out["original_letter_date"] = fmt_date(first.mailed_on or first.created_on)
        if first.delivered_on:
            out["received_date"] = fmt_date(first.delivered_on)
            out["p1l1_received_date"] = fmt_date(first.delivered_on)
        if first.outcome == "original_creditor_responded" and first.outcome_on:
            out["original_creditor_letter_date"] = fmt_date(first.outcome_on)
    return out


@dataclass
class Rendered:
    text: str
    missing: list[str]


def render(spec: LetterSpec, values: dict[str, str]) -> Rendered:
    missing: list[str] = []

    def sub(match: re.Match[str]) -> str:
        name = match.group(1)
        if name in values and (values[name] or name in spec.defaults):
            return values[name]
        if name not in missing:
            missing.append(name)
        return f"[FILL IN: {name.replace('_', ' ')}]"

    text = FIELD_RE.sub(sub, spec.template)
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    return Rendered(text=text, missing=missing)


def slug(value: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return s[:40] or "letter"


def write_files(directory: Path, letter_id: str, spec: LetterSpec, recipient: str, text: str) -> list[Path]:
    directory.mkdir(parents=True, exist_ok=True)
    base = directory / f"{letter_id}-{spec.code}-{slug(recipient)}"
    paths = [base.with_suffix(".txt")]
    paths[0].write_text(text, encoding="utf-8")
    docx_path = _write_docx(base.with_suffix(".docx"), text)
    if docx_path:
        paths.append(docx_path)
    return paths


def _write_docx(path: Path, text: str) -> Path | None:
    try:
        from docx import Document
        from docx.shared import Pt
    except ImportError:  # python-docx is optional; the .txt file is always written
        return None
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)
    for block in text.split("\n\n"):
        para = doc.add_paragraph()
        para.paragraph_format.space_after = Pt(10)
        lines = block.split("\n")
        for i, line in enumerate(lines):
            run = para.add_run(line)
            if i < len(lines) - 1:
                run.add_break()
    doc.save(path)
    return path
