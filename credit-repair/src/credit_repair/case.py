"""Your case file: profile, credit reports, negative items, letters and their outcomes.

Everything is stored in one JSON file (``case.json``) inside your case folder.
Your full Social Security number is never stored - letters that need it leave a
blank for you to write in by hand.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass, field, fields
from datetime import date
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1

ITEM_KINDS = {
    "collection": "Collection account (debt collector / debt buyer)",
    "charge_off": "Charged-off account reported by the original creditor",
    "late_payment": "Late payment(s) on an account",
    "public_record": "Bankruptcy, judgment, tax lien or other court record",
    "inquiry": "Hard inquiry",
    "repossession": "Vehicle repossession",
    "student_loan_federal": "Federal student loan",
    "student_loan_private": "Private student loan",
    "medical": "Medical collection",
    "chexsystems": "ChexSystems entry (bank account history)",
    "foreclosure": "Foreclosure",
    "identity_theft": "Account you never had and have no knowledge of",
    "other": "Other derogatory item",
}

# Outcomes you can record for a letter.
OUTCOMES = {
    "deleted": "Item removed / deleted",
    "verified": "They say it's verified / sent an itemized bill or printout / 'blah blah' stall reply",
    "updated": "Bureau 'updated' the item but kept it",
    "proof_with_signature": "They sent a contract with your signature",
    "no_response": "No reply within the deadline",
    "original_creditor_responded": "You disputed a collector but the original creditor answered instead",
    "returned_mail": "Your letter came back undeliverable",
    "credit_repair_accusation": "Bureau says your letter came from a third party / credit repair company",
    "not_updated": "Personal info letter: changes were not made",
}


def _filter(cls, data: dict[str, Any]) -> dict[str, Any]:
    names = {f.name for f in fields(cls)}
    return {k: v for k, v in data.items() if k in names}


@dataclass
class Profile:
    full_name: str = ""
    address: str = ""  # multi-line mailing address
    ssn_last4: str = ""
    dob: str = ""
    phone: str = ""
    employer: str = ""
    state: str = ""  # two-letter state you live in (SOL chart, licensing checks)
    skip_personal_info: bool = False
    notes: str = ""


@dataclass
class Report:
    id: str
    bureau: str
    source: str
    pulled_on: str
    file: str = ""
    notes: str = ""


@dataclass
class Item:
    id: str
    kind: str
    furnisher: str = ""
    furnisher_address: str = ""
    original_creditor: str = ""
    original_creditor_address: str = ""
    account_number: str = ""
    bureaus: list[str] = field(default_factory=list)
    derogatory_condition: str = ""  # e.g. "I owe $200.00" / "my account was charged off $800"
    month_year: str = ""  # month/year the entry shows, for Part 2 letters
    balance: str = ""
    late_payment_dates: str = ""
    inquiry_date: str = ""
    credit_granted: bool | None = None  # inquiries: was credit granted (open account)?
    recognized: str = ""  # "yes" / "no" / "unsure" - do you recognize this account?
    errors: list[str] = field(default_factory=list)
    estimated_removal: dict[str, str] = field(default_factory=dict)  # bureau -> YYYY-MM
    status: dict[str, str] = field(default_factory=dict)  # bureau -> reporting/deleted/reinserted
    deleted_on: dict[str, str] = field(default_factory=dict)
    reinserted_on: dict[str, str] = field(default_factory=dict)
    strategy: str = ""  # "" (book default for the kind), "goodwill", "dispute"
    flags: dict[str, str] = field(default_factory=dict)  # e.g. cfpb_complaint -> date
    extra: dict[str, str] = field(default_factory=dict)  # extra letter fields (vin, patient_name...)
    notes: str = ""

    def bureau_status(self, bureau: str) -> str:
        return self.status.get(bureau, "reporting")

    def active_bureaus(self) -> list[str]:
        return [b for b in self.bureaus if self.bureau_status(b) != "deleted"]

    def label(self) -> str:
        acct = f" #{self.account_number}" if self.account_number else ""
        return f"{self.id} {self.furnisher or self.kind}{acct}"


@dataclass
class Letter:
    id: str
    code: str
    item_ids: list[str]
    track: str
    recipient_name: str
    recipient_address: str
    created_on: str
    bureau: str = ""
    mailed_on: str = ""
    tracking: str = ""
    delivered_on: str = ""  # the day they signed for it: the 30-day clock starts here
    outcome: str = ""
    outcome_on: str = ""
    item_results: dict[str, str] = field(default_factory=dict)
    marked_disputed: bool | None = None  # seen on the day-31 reports (Part 1 letters)
    files: list[str] = field(default_factory=list)
    notes: str = ""

    def result_for(self, item_id: str) -> str:
        return self.item_results.get(item_id, self.outcome)


@dataclass
class Event:
    on: str
    kind: str
    note: str
    item_id: str = ""


@dataclass
class Case:
    profile: Profile = field(default_factory=Profile)
    reports: list[Report] = field(default_factory=list)
    items: list[Item] = field(default_factory=list)
    letters: list[Letter] = field(default_factory=list)
    events: list[Event] = field(default_factory=list)
    schema_version: int = SCHEMA_VERSION

    # ---- lookups -------------------------------------------------------
    def item(self, item_id: str) -> Item:
        for it in self.items:
            if it.id.lower() == item_id.lower():
                return it
        raise KeyError(f"No item {item_id!r}. Run 'item list' to see your items.")

    def letter(self, letter_id: str) -> Letter:
        for lt in self.letters:
            if lt.id.lower() == letter_id.lower():
                return lt
        raise KeyError(f"No letter {letter_id!r}. Run 'letter list' to see your letters.")

    def letters_for(self, item_id: str, track: str | None = None) -> list[Letter]:
        return [
            lt
            for lt in self.letters
            if item_id in lt.item_ids and (track is None or lt.track == track)
        ]

    def next_id(self, prefix: str, existing: list[str]) -> str:
        n = 0
        for value in existing:
            if value.startswith(prefix) and value[len(prefix):].isdigit():
                n = max(n, int(value[len(prefix):]))
        return f"{prefix}{n + 1}"

    def new_item_id(self) -> str:
        return self.next_id("I", [i.id for i in self.items])

    def new_letter_id(self) -> str:
        return self.next_id("L", [lt.id for lt in self.letters])

    def new_report_id(self) -> str:
        return self.next_id("R", [r.id for r in self.reports])

    def log(self, kind: str, note: str, on: date, item_id: str = "") -> None:
        self.events.append(Event(on=on.isoformat(), kind=kind, note=note, item_id=item_id))

    # ---- serialization -------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Case":
        return cls(
            profile=Profile(**_filter(Profile, data.get("profile", {}))),
            reports=[Report(**_filter(Report, r)) for r in data.get("reports", [])],
            items=[Item(**_filter(Item, i)) for i in data.get("items", [])],
            letters=[Letter(**_filter(Letter, lt)) for lt in data.get("letters", [])],
            events=[Event(**_filter(Event, e)) for e in data.get("events", [])],
            schema_version=data.get("schema_version", SCHEMA_VERSION),
        )


class CaseStore:
    """Reads and writes the case folder."""

    def __init__(self, root: Path):
        self.root = Path(root)

    @property
    def case_file(self) -> Path:
        return self.root / "case.json"

    @property
    def letters_dir(self) -> Path:
        return self.root / "letters"

    def exists(self) -> bool:
        return self.case_file.exists()

    def init(self) -> None:
        for sub in ("reports", "letters", "responses", "evidence"):
            (self.root / sub).mkdir(parents=True, exist_ok=True)
        gitignore = self.root / ".gitignore"
        if not gitignore.exists():
            # Belt and braces: this folder holds your personal information.
            gitignore.write_text("*\n", encoding="utf-8")

    def load(self) -> Case:
        if not self.exists():
            raise FileNotFoundError(
                f"No case file at {self.case_file}. Start with: init --name ... --address ..."
            )
        with self.case_file.open(encoding="utf-8") as fh:
            return Case.from_dict(json.load(fh))

    def save(self, case: Case) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=self.root, prefix=".case-", suffix=".json")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(case.to_dict(), fh, indent=2, ensure_ascii=False)
                fh.write("\n")
            os.replace(tmp, self.case_file)
        except BaseException:
            Path(tmp).unlink(missing_ok=True)
            raise
