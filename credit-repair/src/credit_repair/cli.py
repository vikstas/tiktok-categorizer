"""Command line for the Credit Secrets agent's case file.

Run ``python credit-repair/cr.py --help`` (or ``credit-repair --help`` once installed).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import fields as dc_fields
from datetime import date, timedelta
from pathlib import Path

from . import rules, workflow
from .case import ITEM_KINDS, OUTCOMES, Case, CaseStore, Item, Letter, Profile, Report
from .letters import SPECS, Recipient, build_fields, fmt_date, recipient_for, render, track_for, write_files


class UserError(Exception):
    pass


# ---------------------------------------------------------------------------
# setup


def default_case_dir() -> Path:
    env = os.environ.get("CREDIT_CASE_DIR")
    if env:
        return Path(env).expanduser()
    project = Path(__file__).resolve().parents[2]
    if (project / "cr.py").exists():
        return project / "my-case"
    return Path.cwd() / "credit-repair-case"


def get_today(args: argparse.Namespace) -> date:
    value = args.today or os.environ.get("CR_TODAY")
    return date.fromisoformat(value) if value else date.today()


def parse_date(value: str | None, today: date) -> date:
    if not value:
        return today
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise UserError(f"Dates look like 2026-11-23 (got {value!r})") from exc


def yes_no(value: str) -> bool:
    v = value.strip().lower()
    if v in ("y", "yes", "true", "1"):
        return True
    if v in ("n", "no", "false", "0"):
        return False
    raise UserError(f"Expected yes or no, got {value!r}")


def multiline(value: str) -> str:
    """Addresses can be passed with '|' or '\\n' between lines."""
    return "\n".join(part.strip() for part in re.split(r"\||\\n|\n", value) if part.strip())


# ---------------------------------------------------------------------------
# item fields from key=value pairs

LIST_FIELDS = {"bureaus", "errors"}
DICT_FIELDS = {"estimated_removal", "status", "deleted_on", "reinserted_on", "flags", "extra"}
ADDRESS_FIELDS = {"furnisher_address", "original_creditor_address"}


def apply_pairs(item: Item, pairs: list[str]) -> None:
    names = {f.name for f in dc_fields(Item)} - {"id"}
    for pair in pairs:
        if "=" not in pair:
            raise UserError(f"Use key=value (got {pair!r})")
        key, value = pair.split("=", 1)
        key = key.strip()
        base, _, sub = key.partition(".")
        if base not in names:
            raise UserError(f"Unknown item field {base!r}. Fields: {', '.join(sorted(names))}")
        if base in DICT_FIELDS:
            if not sub:
                raise UserError(f"Use {base}.<key>=value, e.g. extra.vin=1HGCM82633A004352")
            target = getattr(item, base)
            if value == "":
                target.pop(sub.upper() if base != "extra" and base != "flags" else sub, None)
            else:
                k = sub if base in ("extra", "flags") else sub.upper()
                target[k] = value
        elif base in LIST_FIELDS:
            sep = "," if base == "bureaus" else "|"
            values = [v.strip() for v in value.split(sep) if v.strip()]
            if base == "bureaus":
                values = [v.upper() for v in values]
                bad = [v for v in values if v not in rules.BUREAUS]
                if bad:
                    raise UserError(f"Unknown bureau code(s) {bad}. Use: {', '.join(rules.BUREAUS)}")
            setattr(item, base, values)
        elif base == "credit_granted":
            item.credit_granted = None if value == "" else yes_no(value)
        elif base == "kind":
            if value not in ITEM_KINDS:
                raise UserError(f"Unknown kind {value!r}. Kinds: {', '.join(ITEM_KINDS)}")
            item.kind = value
        elif base in ADDRESS_FIELDS:
            setattr(item, base, multiline(value))
        else:
            setattr(item, base, value)


def item_from_dict(case: Case, data: dict) -> Item:
    kind = data.get("kind", "")
    if kind not in ITEM_KINDS:
        raise UserError(f"Unknown kind {kind!r}. Kinds: {', '.join(ITEM_KINDS)}")
    item = Item(id=case.new_item_id(), kind=kind)
    for key, value in data.items():
        if key in ("id", "kind"):
            continue
        if key in DICT_FIELDS:
            if not isinstance(value, dict):
                raise UserError(f"{key} must be an object")
            for k, v in value.items():
                apply_pairs(item, [f"{key}.{k}={v}"])
        elif key in LIST_FIELDS:
            if isinstance(value, str):
                joined = value
            else:
                joined = (",".join if key == "bureaus" else "|".join)(str(v) for v in value)
            apply_pairs(item, [f"{key}={joined}"])
        elif key == "credit_granted":
            item.credit_granted = value if isinstance(value, bool) or value is None else yes_no(str(value))
        else:
            apply_pairs(item, [f"{key}={value}"])
    return item


# ---------------------------------------------------------------------------
# commands


def cmd_init(store: CaseStore, args, today: date) -> None:
    if store.exists() and not args.force:
        raise UserError(f"A case already exists at {store.case_file}. Use --force to start over.")
    last4 = re.sub(r"\D", "", args.ssn_last4 or "")
    if args.ssn_last4 and len(last4) != 4:
        raise UserError("Only the LAST 4 digits of your SSN are stored. Letters that need the full "
                        "number leave a blank for you to write in by hand.")
    store.init()
    case = Case(
        profile=Profile(
            full_name=args.name, address=multiline(args.address), ssn_last4=last4,
            dob=args.dob or "", phone=args.phone or "", employer=args.employer or "",
            state=(args.state or "").upper(),
        )
    )
    case.log("init", "Case started", today)
    store.save(case)
    print(f"Case created at {store.root}")
    print("Next: get all 3 credit reports (not from AnnualCreditReport.com), save them in "
          f"{store.root / 'reports'}, and record them with 'report add'.")


def cmd_profile(case: Case, args) -> bool:
    if args.pairs:
        names = {f.name for f in dc_fields(Profile)}
        for pair in args.pairs:
            key, _, value = pair.partition("=")
            if key not in names:
                raise UserError(f"Unknown profile field {key!r}. Fields: {', '.join(sorted(names))}")
            if key == "ssn_last4":
                value = re.sub(r"\D", "", value)
                if len(value) != 4:
                    raise UserError("Only the last 4 digits of your SSN are stored.")
            if key == "skip_personal_info":
                setattr(case.profile, key, yes_no(value))
            elif key == "address":
                case.profile.address = multiline(value)
            elif key == "state":
                case.profile.state = value.upper()
            else:
                setattr(case.profile, key, value)
        print("Profile updated.")
        return True
    for f in dc_fields(Profile):
        print(f"{f.name}: {getattr(case.profile, f.name)}")
    return False


def cmd_report(case: Case, args, today: date, store: CaseStore) -> bool:
    if args.report_cmd == "add":
        bureau = args.bureau.upper()
        if bureau not in rules.BUREAUS:
            raise UserError(f"Unknown bureau {bureau}. Use: {', '.join(rules.BUREAUS)}")
        report = Report(
            id=case.new_report_id(), bureau=bureau, source=args.source,
            pulled_on=parse_date(args.date, today).isoformat(), file=args.file or "",
            notes=args.notes or "",
        )
        case.reports.append(report)
        case.log("report", f"{bureau} report from {args.source} ({report.pulled_on})", today)
        print(f"Recorded {report.id}: {rules.BUREAU_NAMES[bureau]} report pulled {report.pulled_on}.")
        if "annual" in args.source.lower():
            print("WARNING: " + rules.ANNUAL_REPORT_WARNING)
        return True
    if not case.reports:
        print("No reports recorded yet.")
    for r in case.reports:
        print(f"{r.id}  {r.pulled_on}  {r.bureau:<3} {r.source}  {r.file}")
    return False


def cmd_item(case: Case, args, today: date) -> bool:
    sub = args.item_cmd
    if sub == "add":
        if args.kind not in ITEM_KINDS:
            raise UserError(f"Unknown kind {args.kind!r}. Kinds: {', '.join(ITEM_KINDS)}")
        item = Item(id=case.new_item_id(), kind=args.kind)
        apply_pairs(item, args.pairs)
        case.items.append(item)
        case.log("item", f"Added {item.label()}", today, item.id)
        print(f"Added {item.label()}")
        return True
    if sub == "import":
        data = json.loads(Path(args.file).read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data = data.get("items", [])
        added = []
        for entry in data:
            item = item_from_dict(case, entry)
            case.items.append(item)
            added.append(item)
        case.log("item", f"Imported {len(added)} items", today)
        for item in added:
            print(f"Added {item.label()} [{item.kind}] bureaus={','.join(item.bureaus)}")
        return True
    if sub == "set":
        item = case.item(args.item_id)
        apply_pairs(item, args.pairs)
        print(f"Updated {item.label()}")
        return True
    if sub == "flag":
        item = case.item(args.item_id)
        value = args.value or today.isoformat()
        item.flags[args.flag] = value
        case.log("flag", f"{args.flag}: {value}", today, item.id)
        print(f"{item.label()}: {args.flag} = {value}")
        return True
    if sub == "reinserted":
        item = case.item(args.item_id)
        bureau = args.bureau.upper()
        item.status[bureau] = "reinserted"
        item.reinserted_on[bureau] = parse_date(args.date, today).isoformat()
        case.log("reinserted", f"Reinserted on {rules.BUREAU_NAMES.get(bureau, bureau)}", today, item.id)
        print(f"{item.label()} marked reinserted on {bureau}. Run 'next' for the 5 Day Reinsertion letter.")
        return True
    if sub == "show":
        item = case.item(args.item_id)
        for f in dc_fields(Item):
            value = getattr(item, f.name)
            if value not in ("", [], {}, None):
                print(f"{f.name}: {value}")
        return False
    if not case.items:
        print("No items yet. Add them with 'item add' or 'item import'.")
    for item in case.items:
        statuses = " ".join(f"{b}:{item.bureau_status(b)}" for b in item.bureaus) or "-"
        print(f"{item.id:<4} {item.kind:<20} {item.furnisher[:34]:<34} {statuses}")
    return False


def _resolve_items(case: Case, args) -> list[Item]:
    ids: list[str] = []
    if args.item:
        ids.append(args.item)
    if args.items:
        ids += [i.strip() for i in args.items.split(",") if i.strip()]
    return [case.item(i) for i in ids]


def cmd_letter(case: Case, args, today: date, store: CaseStore) -> bool:
    sub = args.letter_cmd
    if sub == "templates":
        for spec in SPECS.values():
            src = f"p.{spec.page}" + ("" if spec.from_book else ", written from the book's instructions")
            print(f"{spec.code:<15} {spec.title} ({src})\n{'':<15} {spec.when}\n")
        return False
    if sub == "make":
        return _make_letter(case, args, today, store)
    if sub == "list":
        if not case.letters:
            print("No letters yet.")
        for lt in case.letters:
            state = lt.outcome or ("signed " + lt.delivered_on if lt.delivered_on else
                                   "mailed " + lt.mailed_on if lt.mailed_on else "not mailed")
            print(f"{lt.id:<4} {lt.code:<14} {','.join(lt.item_ids):<10} {lt.recipient_name[:30]:<30} {state}")
        return False
    letter = case.letter(args.letter_id)
    if sub == "show":
        for path in letter.files:
            if path.endswith(".txt") and Path(path).exists():
                print(Path(path).read_text(encoding="utf-8"))
        print(json.dumps({k: v for k, v in letter.__dict__.items() if v not in ("", [], {}, None)},
                         indent=2))
        return False
    if sub == "mailed":
        letter.mailed_on = parse_date(args.date, today).isoformat()
        if args.tracking:
            letter.tracking = args.tracking
        case.log("mailed", f"{letter.id} {letter.code} mailed to {letter.recipient_name}"
                 + (f" (tracking {letter.tracking})" if letter.tracking else ""), today,
                 letter.item_ids[0] if letter.item_ids else "")
        spec = SPECS[letter.code]
        msg = f"{letter.id} marked mailed {letter.mailed_on}."
        if spec.certified:
            msg += " When tracking shows it was signed for, run: letter delivered " + letter.id
        print(msg)
        return True
    if sub == "delivered":
        when = parse_date(args.date, today)
        letter.delivered_on = when.isoformat()
        wait = SPECS[letter.code].wait_days
        case.log("delivered", f"{letter.id} signed for by {letter.recipient_name}", today,
                 letter.item_ids[0] if letter.item_ids else "")
        print(f"{letter.id} signed for {when.isoformat()}. Day {wait} is {(when + timedelta(days=wait)).isoformat()}.")
        return True
    if sub == "outcome":
        return _record_outcome(case, letter, args, today)
    raise UserError(f"Unknown letter command {sub}")


def _make_letter(case: Case, args, today: date, store: CaseStore) -> bool:
    code = args.code.upper()
    if code not in SPECS:
        raise UserError(f"Unknown letter {code}. Run 'letter templates' for the list.")
    spec = SPECS[code]
    items = _resolve_items(case, args)
    if spec.group != "personal_info" and spec.send_to != "court_clerk" and not items:
        raise UserError(f"{code} needs --item (or --items for grouped inquiry letters).")
    bureau = (args.bureau or "").upper()
    if spec.needs_bureau and not bureau:
        actives = items[0].active_bureaus() if len(items) == 1 else []
        if len(actives) == 1:
            bureau = actives[0]
        else:
            raise UserError(f"{code} goes to a bureau: add --bureau (EX, EQ, TU, ...).")
    if spec.send_to == "bureau" and bureau and bureau not in rules.BUREAUS:
        raise UserError(f"Unknown bureau {bureau}. Use: {', '.join(rules.BUREAUS)}")
    if spec.send_to == "bureau_fraud" and bureau not in rules.FRAUD_ADDRESSES:
        raise UserError("Identity theft letters go to EX, EQ or TU fraud departments.")

    problems = _check_rules(case, spec, items, bureau, today)
    if problems and not args.force:
        raise UserError("\n".join(problems) + "\n(Add --force to make it anyway.)")

    overrides = {}
    for pair in args.set or []:
        key, _, value = pair.partition("=")
        overrides[key.strip()] = multiline(value) if "address" in key or "block" in key else value
    rec = recipient_for(spec, items, bureau)
    if args.to_name:
        rec = Recipient(args.to_name, rec.address)
    if args.to_address:
        rec = Recipient(rec.name, multiline(args.to_address))
    values = build_fields(case, spec, items, bureau, today, overrides, rec)
    rendered = render(spec, values)

    letter = Letter(
        id=case.new_letter_id(), code=code, item_ids=[i.id for i in items],
        track=track_for(spec, bureau), recipient_name=rec.name or values.get("recipient_name", ""),
        recipient_address=rec.address, created_on=today.isoformat(), bureau=bureau,
    )
    paths = write_files(store.letters_dir, letter.id, spec, letter.recipient_name or code, rendered.text)
    letter.files = [str(p) for p in paths]
    case.letters.append(letter)
    case.log("letter", f"{letter.id} {code} created for {letter.recipient_name}", today,
             items[0].id if items else "")

    print(f"Created {letter.id}: {spec.title} -> {letter.recipient_name or '(recipient missing)'}")
    for p in paths:
        print(f"  {p}")
    if rendered.missing:
        print("Still blank (fill in before mailing, or re-make with --set field=value): "
              + ", ".join(rendered.missing))
    how = "certified mail, return receipt requested" if spec.certified else "regular mail"
    if code == "CHEX":
        how = "registered mail (sign this one)"
    print(f"Mail it {how}. Then: letter mailed {letter.id} --tracking <number>")
    for problem in problems:
        print(f"NOTE: {problem}")
    return True


def _check_rules(case: Case, spec, items: list[Item], bureau: str, today: date) -> list[str]:
    """The book's do's and don'ts that apply before a letter goes out."""
    problems = []
    if spec.code in ("INQ1", "INQ2", "INQ3"):
        for item in items:
            if item.kind != "inquiry":
                problems.append(f"{item.id} is not an inquiry.")
            if item.credit_granted:
                problems.append(f"{item.label()}: credit was granted - the book says do NOT dispute "
                                "an inquiry tied to an open account (they can close it).")
    if spec.code in ("INQ2", "INQ3") and workflow._pi_pending(case, bureau):
        problems.append("The book says not to send Inquiry Letter 2 at the same time as your "
                        "personal information update letter to that bureau - send the PI letter "
                        "and record its outcome first (or: profile skip_personal_info=yes).")
    if spec.code == "CHEX" and bureau != "CX":
        problems.append("The ChexSystems letter goes to ChexSystems: use --bureau CX.")
    if spec.code == "IDT":
        for item in items:
            if item.recognized != "no":
                problems.append(f"{item.label()}: the identity theft letter is for accounts you "
                                "have never had and have no knowledge of (set recognized=no). "
                                "You also need an FTC Identity Theft Report.")
    if spec.code == "GW":
        for item in items:
            n = len([d for d in re.split(r"[,;]| and ", item.late_payment_dates) if d.strip()])
            if n > 2:
                problems.append(f"{item.label()}: the book's goodwill letter is for one or two late "
                                "pays (and it's an admission they're yours).")
    track = track_for(spec, bureau)
    for item in items:
        prior = case.letters_for(item.id, track)
        if prior:
            last = prior[-1]
            if not last.mailed_on:
                problems.append(f"{last.id} ({last.code}) in this conversation hasn't been mailed yet.")
            else:
                due = workflow.next_step_date(last)
                if due and today < due and last.result_for(item.id) not in ("returned_mail", "credit_repair_accusation"):
                    problems.append(f"The book says always wait the full 30 days: {last.id} was "
                                    f"signed for {last.delivered_on}; next letter not before {due.isoformat()}.")
    return problems


def _record_outcome(case: Case, letter: Letter, args, today: date) -> bool:
    when = parse_date(args.date, today)
    if args.result:
        if args.result not in OUTCOMES:
            raise UserError(f"Unknown result {args.result!r}. Use one of: {', '.join(OUTCOMES)}")
        targets = [case.item(args.item).id] if args.item else list(letter.item_ids)
        if args.item:
            letter.item_results[targets[0]] = args.result
            if not letter.outcome:
                letter.outcome = args.result
        else:
            letter.outcome = args.result
        letter.outcome_on = when.isoformat()
        for item_id in targets:
            if args.result == "deleted":
                item = case.item(item_id)
                bureaus = [letter.bureau] if letter.bureau else list(item.bureaus)
                for b in bureaus:
                    item.status[b] = "deleted"
                    item.deleted_on[b] = when.isoformat()
            case.log("outcome", f"{letter.id} {letter.code}: {OUTCOMES[args.result]}", when, item_id)
        if letter.code == "PI" and args.result == "updated":
            case.log("outcome", f"Personal info updated by {letter.recipient_name}", when)
    if args.marked_disputed is not None:
        letter.marked_disputed = yes_no(args.marked_disputed)
        case.log("disputed_check",
                 f"Day-31 reports: {'marked' if letter.marked_disputed else 'NOT marked'} disputed "
                 f"after {letter.id}", when, letter.item_ids[0] if letter.item_ids else "")
    if args.note:
        letter.notes = (letter.notes + "\n" + args.note).strip()
    if not (args.result or args.marked_disputed is not None or args.note):
        raise UserError("Give --result, --marked-disputed and/or --note.")
    print(f"{letter.id} updated: outcome={letter.outcome or '-'} marked_disputed="
          f"{'-' if letter.marked_disputed is None else letter.marked_disputed}")
    return True


def print_actions(actions: list[workflow.Action], case: Case) -> None:
    for n, a in enumerate(actions, 1):
        due = f" (due {a.due.isoformat()})" if a.due else ""
        tag = {"make_letter": "LETTER", "mail": "MAIL", "confirm_delivery": "TRACK",
               "record_outcome": "CHECK", "task": "TODO", "blocked": "BLOCKED",
               "wait": "WAIT", "monitor": "WATCH", "info": "INFO"}.get(a.kind, a.kind.upper())
        print(f"{n}. [{tag}]{due} {a.message}")
        if a.command:
            print(f"     -> {a.command}")


def cmd_next(case: Case, args, today: date) -> None:
    plan = workflow.plan(case, today)
    due = plan.due_now(today)
    print(f"Today is {today.isoformat()}.")
    if not case.items and not case.letters:
        print("No items yet: get your 3 reports, then add the negative items ('item add' / 'item import').")
    if due:
        print(f"\nTo do now ({len(due)}):")
        print_actions(due, case)
    else:
        print("\nNothing due today.")
    later = [a for a in plan.upcoming(today) if args.all or a.kind not in ("monitor", "info")]
    if later:
        print("\nComing up:")
        print_actions(later, case)


def cmd_status(case: Case, today: date) -> None:
    p = case.profile
    print(f"{p.full_name} - {len(case.items)} items, {len(case.letters)} letters, "
          f"{len(case.reports)} reports")
    plan = workflow.plan(case, today)
    for item in case.items:
        acts = [a for a in plan.actions if item.id in a.item_ids]
        statuses = " ".join(f"{b}:{item.bureau_status(b)}" for b in item.bureaus) or "bureaus?"
        print(f"\n{item.label()} [{item.kind}] {statuses}")
        for lt in case.letters_for(item.id):
            bits = [f"{lt.id} {lt.code}"]
            if lt.mailed_on:
                bits.append(f"mailed {lt.mailed_on}")
            if lt.delivered_on:
                bits.append(f"signed {lt.delivered_on}")
            if lt.outcome:
                bits.append(f"-> {lt.result_for(item.id)}")
            if lt.marked_disputed is not None:
                bits.append("disputed-flag " + ("yes" if lt.marked_disputed else "NO"))
            print("   " + ", ".join(bits))
        for a in acts[:3]:
            due = f" by {a.due.isoformat()}" if a.due else ""
            print(f"   next{due}: {a.message[:150]}")


def cmd_calendar(case: Case, args, today: date, store: CaseStore) -> None:
    plan = workflow.plan(case, today)
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//credit-secrets-agent//EN"]
    count = 0
    for n, a in enumerate(plan.actions):
        if not a.due or a.kind == "monitor":
            continue
        day = max(a.due, today)
        text = a.message.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;")
        summary = f"Credit repair: {a.code or a.kind} {','.join(a.item_ids)}".strip()
        lines += [
            "BEGIN:VEVENT",
            f"UID:cr-{n}-{day.isoformat()}-{a.kind}-{'-'.join(a.item_ids)}@credit-secrets-agent",
            f"DTSTAMP:{today.strftime('%Y%m%d')}T000000Z",
            f"DTSTART;VALUE=DATE:{day.strftime('%Y%m%d')}",
            f"DTEND;VALUE=DATE:{(day + timedelta(days=1)).strftime('%Y%m%d')}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{text}",
            "END:VEVENT",
        ]
        count += 1
    lines.append("END:VCALENDAR")
    out = Path(args.out) if args.out else store.root / "credit-repair-deadlines.ics"
    out.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8")
    print(f"Wrote {count} reminders to {out} - import it into your phone's calendar.")


def cmd_timeline(case: Case, args) -> None:
    item = case.item(args.item_id)
    print(f"Evidence timeline - {item.label()} [{ITEM_KINDS[item.kind]}]")
    print(f"Reported by: {item.furnisher} {('(original creditor: ' + item.original_creditor + ')') if item.original_creditor else ''}")
    print(f"Bureaus: {', '.join(rules.BUREAU_NAMES.get(b, b) + ' - ' + item.bureau_status(b) for b in item.bureaus)}")
    rows: list[tuple[str, str]] = []
    for e in case.events:
        if e.item_id == item.id and e.kind not in ("mailed", "delivered"):
            rows.append((e.on, e.note))
    for lt in case.letters_for(item.id):
        if lt.mailed_on:
            rows.append((lt.mailed_on, f"Mailed {lt.id} {SPECS[lt.code].title} to {lt.recipient_name}"
                         + (f", certified tracking {lt.tracking}" if lt.tracking else "")))
        if lt.delivered_on:
            rows.append((lt.delivered_on, f"{lt.recipient_name} signed for {lt.id}"))
            due = workflow.next_step_date(lt)
            if due:
                rows.append((due.isoformat(), f"Deadline for {lt.id} (day {SPECS[lt.code].wait_days})"))
    for r in case.reports:
        if r.bureau in item.bureaus:
            rows.append((r.pulled_on, f"Pulled {rules.BUREAU_NAMES.get(r.bureau, r.bureau)} report ({r.source}) {r.file}"))
    seen = set()
    for on, note in sorted(rows):
        if (on, note) in seen:
            continue
        seen.add((on, note))
        print(f"{on}  {note}")
    print("\nFor CFPB/AG/BBB complaints and your small-claims binder, attach the letters, certified "
          "mail receipts, their replies and the dated reports listed above.")


def cmd_info(args, case: Case | None) -> None:
    topic = args.topic
    if topic == "bureaus":
        for code, info in rules.BUREAUS.items():
            print(f"{code:<4} {info['name']}\n     {info['address'].replace(chr(10), ', ')}")
    elif topic == "fraud":
        for code, info in rules.FRAUD_ADDRESSES.items():
            print(f"{code:<4} {info['name']}, {info['address'].replace(chr(10), ', ')}")
    elif topic == "data-miners":
        for dm in rules.DATA_MINERS:
            print(f"{dm['name']}\n  freeze/opt-out: {dm['freeze_optout']}\n  your file: {dm['get_report']}")
            if "suppress" in dm:
                print(f"  suppress: {dm['suppress']}")
        print("\nID they ask for (two of): " + "; ".join(rules.DATA_MINER_ID_DOCS))
    elif topic == "sol":
        state = (args.arg or (case.profile.state if case else "") or "").upper()
        print("Years: written contracts / oral contracts / promissory notes / open accounts (credit cards)")
        for st, row in rules.SOL.items():
            if not state or st == state:
                print(f"{st}: {' / '.join(row)}")
        print(rules.SOL_NOTES)
    elif topic == "early-exclusion":
        print(rules.EARLY_EXCLUSION_NOTE)
    elif topic == "lawsuits":
        for who, why, law in rules.LAWSUIT_TABLE:
            print(f"- {who}: {why} [{law}]")
        print("\nLegal contacts to copy when suing a bureau (2024 edition):")
        for c in rules.LEGAL_CONTACTS:
            print(f"- {c}")
    elif topic == "checklist":
        for line in rules.ERROR_CHECKLIST:
            print(f"- {line}")
        print("\nMedical debt:")
        for line in rules.MEDICAL_RULES:
            print(f"- {line}")
        print("\nPublic records:")
        for line in rules.PUBLIC_RECORD_RULES:
            print(f"- {line}")
    elif topic == "sources":
        for line in rules.REPORT_SOURCES:
            print(f"- {line}")
        print(rules.ANNUAL_REPORT_WARNING)
    elif topic == "kinds":
        for k, v in ITEM_KINDS.items():
            print(f"{k:<22} {v}")
    elif topic == "outcomes":
        for k, v in OUTCOMES.items():
            print(f"{k:<28} {v}")


# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="credit-repair", description="Credit Secrets case file & letters")
    p.add_argument("--case-dir", help="Case folder (default: credit-repair/my-case or $CREDIT_CASE_DIR)")
    p.add_argument("--today", help="Pretend today is YYYY-MM-DD (for planning)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help="Start your case")
    s.add_argument("--name", required=True)
    s.add_argument("--address", required=True, help="Mailing address; separate lines with |")
    s.add_argument("--ssn-last4")
    s.add_argument("--dob")
    s.add_argument("--phone")
    s.add_argument("--employer")
    s.add_argument("--state", help="Two-letter state")
    s.add_argument("--force", action="store_true")

    s = sub.add_parser("profile", help="Show or set profile fields (key=value)")
    s.add_argument("pairs", nargs="*")

    s = sub.add_parser("report", help="Credit reports you pulled")
    rs = s.add_subparsers(dest="report_cmd", required=True)
    a = rs.add_parser("add")
    a.add_argument("--bureau", required=True)
    a.add_argument("--source", required=True)
    a.add_argument("--date")
    a.add_argument("--file")
    a.add_argument("--notes")
    rs.add_parser("list")

    s = sub.add_parser("item", help="Negative items on your reports")
    is_ = s.add_subparsers(dest="item_cmd", required=True)
    a = is_.add_parser("add")
    a.add_argument("--kind", required=True, help="Run 'info kinds'")
    a.add_argument("pairs", nargs="*", help="field=value, e.g. furnisher='Midland Credit' bureaus=EX,TU")
    a = is_.add_parser("import")
    a.add_argument("file")
    a = is_.add_parser("set")
    a.add_argument("item_id")
    a.add_argument("pairs", nargs="+")
    a = is_.add_parser("flag")
    a.add_argument("item_id")
    a.add_argument("flag", help="e.g. license_checked, cfpb_complaint, ag_complaint, bbb_complaint, "
                   "small_claims, court_letter, data_miners")
    a.add_argument("value", nargs="?")
    a = is_.add_parser("reinserted")
    a.add_argument("item_id")
    a.add_argument("--bureau", required=True)
    a.add_argument("--date")
    a = is_.add_parser("show")
    a.add_argument("item_id")
    is_.add_parser("list")

    s = sub.add_parser("letter", help="Make and track letters")
    ls = s.add_subparsers(dest="letter_cmd", required=True)
    ls.add_parser("templates")
    ls.add_parser("list")
    a = ls.add_parser("make")
    a.add_argument("code")
    a.add_argument("--item")
    a.add_argument("--items", help="Comma-separated item ids (grouped inquiry letters)")
    a.add_argument("--bureau")
    a.add_argument("--to-name")
    a.add_argument("--to-address")
    a.add_argument("--set", action="append", help="field=value for any letter blank")
    a.add_argument("--force", action="store_true")
    for name in ("show", "mailed", "delivered", "outcome"):
        a = ls.add_parser(name)
        a.add_argument("letter_id")
        if name in ("mailed", "delivered", "outcome"):
            a.add_argument("--date")
        if name == "mailed":
            a.add_argument("--tracking")
        if name == "outcome":
            a.add_argument("--result", help="Run 'info outcomes'")
            a.add_argument("--item", help="Result applies to just this item (grouped letters)")
            a.add_argument("--marked-disputed", help="yes/no: was it marked disputed on day 31?")
            a.add_argument("--note")

    s = sub.add_parser("next", help="What to do now, and what's coming up")
    s.add_argument("--all", action="store_true")
    sub.add_parser("status", help="Every item, its letters and next step")
    s = sub.add_parser("calendar", help="Export deadlines as a calendar file (.ics)")
    s.add_argument("--out")
    s = sub.add_parser("timeline", help="Evidence timeline for one item")
    s.add_argument("item_id")
    s = sub.add_parser("info", help="Reference data from the book")
    s.add_argument("topic", choices=["bureaus", "fraud", "data-miners", "sol", "early-exclusion",
                                     "lawsuits", "checklist", "sources", "kinds", "outcomes"])
    s.add_argument("arg", nargs="?")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    store = CaseStore(Path(args.case_dir).expanduser() if args.case_dir else default_case_dir())
    try:
        today = get_today(args)
        if args.cmd == "init":
            cmd_init(store, args, today)
            return 0
        if args.cmd == "info" and not store.exists():
            cmd_info(args, None)
            return 0
        if args.cmd == "letter" and args.letter_cmd == "templates":
            cmd_letter(Case(), args, today, store)
            return 0
        case = store.load()
        changed = False
        if args.cmd == "profile":
            changed = cmd_profile(case, args)
        elif args.cmd == "report":
            changed = cmd_report(case, args, today, store)
        elif args.cmd == "item":
            changed = cmd_item(case, args, today)
        elif args.cmd == "letter":
            changed = cmd_letter(case, args, today, store)
        elif args.cmd == "next":
            cmd_next(case, args, today)
        elif args.cmd == "status":
            cmd_status(case, today)
        elif args.cmd == "calendar":
            cmd_calendar(case, args, today, store)
        elif args.cmd == "timeline":
            cmd_timeline(case, args)
        elif args.cmd == "info":
            cmd_info(args, case)
        if changed:
            store.save(case)
        return 0
    except (UserError, KeyError, FileNotFoundError) as exc:
        message = exc.args[0] if exc.args else str(exc)
        print(f"Error: {message}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
