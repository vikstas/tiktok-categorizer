from datetime import date, timedelta

import pytest

from credit_repair.case import Case, Item, Letter, Profile
from credit_repair.letters import SPECS, track_for

TODAY = date(2026, 12, 1)


@pytest.fixture
def case():
    return Case(profile=Profile(full_name="Jane Sample", address="1 Main St\nAustin, TX 78701",
                                ssn_last4="1234", state="TX", skip_personal_info=True))


def add_item(case, kind="collection", **kw):
    item = Item(id=case.new_item_id(), kind=kind, furnisher=kw.pop("furnisher", "Midland"),
                furnisher_address=kw.pop("furnisher_address", "PO Box 1\nSan Diego, CA 92193"),
                bureaus=kw.pop("bureaus", ["EX", "TU"]), **kw)
    case.items.append(item)
    return item


def add_letter(case, code, items, *, bureau="", sent=TODAY, outcome="", marked=None, results=None):
    """A letter mailed on `sent`, signed for 3 days later, with an optional outcome."""
    if not isinstance(items, list):
        items = [items]
    spec = SPECS[code]
    lt = Letter(id=case.new_letter_id(), code=code, item_ids=[i.id for i in items],
                track=track_for(spec, bureau), recipient_name="X", recipient_address="Y",
                created_on=sent.isoformat(), bureau=bureau, mailed_on=sent.isoformat(),
                delivered_on=(sent + timedelta(days=3)).isoformat(), outcome=outcome,
                marked_disputed=marked, item_results=results or {})
    case.letters.append(lt)
    return lt


def day_after_deadline(sent=TODAY, wait=31):
    return sent + timedelta(days=3 + wait)
