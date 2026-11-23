# Credit Repair Agent (Credit Secrets method)

A personal credit repair agent that runs the method in the **Credit Secrets** book
(2024-2025 edition) for you, step by step, as the book describes it.

It reads your three credit reports, finds the items to challenge, writes the book's
letters, tracks the certified-mail dates and the 30-day clock, reads the replies you
get back, and tells you which letter comes next. You review, print and mail each
letter yourself.

It has two parts:

- **The agent**: a Claude Code skill (`.claude/skills/credit-repair/`). It holds the
  book's whole method, chapter by chapter, and the step-by-step procedure the agent
  follows with you.
- **The case tool** (`credit-repair/cr.py`): a small Python program that keeps your
  case file. It stores your items, letters, mailing dates and outcomes, fills in the
  letters and works out the next step and its due date from the book's rules.

## How to use it

Open this repository in Claude Code and say something like *"let's work on my
credit"* (or type `/credit-repair`). The agent will:

1. Set up your case. It asks for your name, address, the **last 4** digits of your
   SSN, your date of birth, phone, employer and state.
2. Ask you for all 3 credit reports (PDFs or screenshots). Don't use reports from
   AnnualCreditReport.com for disputing. The book says that stretches the bureau's
   30 days to 45.
3. Go through every public record, collection, charge-off, late payment and inquiry
   with you, and check each one against the book's error checklist.
4. Run the book's order:
   1. personal-info cleanup (#Jumpstart)
   2. inquiries
   3. the collector license check
   4. Part 1 letters to the creditors and collectors
   5. the day-31 "disputed" check
   6. Part 2 letters to the bureaus
   7. method of verification, then the final letters
   8. complaints to the CFPB, your State Attorney General and the BBB
   9. small claims court, if you choose it

   Along the way it also covers public records, data miners, early exclusion,
   reinsertion, goodwill, ChexSystems, repossessions, medical debt and student
   loans, then credit building.
5. Each time you come back, it asks what came in the mail and records it. It then
   gives you the next letters and puts the deadlines in a calendar file for your phone.

Each letter is saved as a `.txt` and a Word `.docx` file in
`credit-repair/my-case/letters/`.

## The letters

All 28 letters in the book are included, with the book's wording. To see the list,
run `python credit-repair/cr.py letter templates`:

- **Personal info and inquiries:** change of address (`PI`) and the 3 inquiry
  letters (`INQ1`-`INQ3`)
- **Part 1** (to the creditor or collector): `P1L1`, `P1L2A`, `P1L2B`, `P1L2C`, `P1L3`
- **Part 2** (to the bureau): `P2L1`, `P2L2A`, `P2L2B`, `P2L3`
- **Other bureau letters:**
  - credit repair accusation (`STALL`)
  - identity theft (`IDT`)
  - early exclusion (`EARLY`)
  - 5-day reinsertion (`REINSERT`)
  - incomplete/missing info (`INCOMPLETE`)
  - returned mail (`RETURNED`)
  - the alternative/bizarre letter (`BIZARRE`, misspellings intact)
- **Late payments:** two dispute letters (`LP1`, `LP2`) and the goodwill letter (`GW`)
- **Special situations:** ChexSystems (`CHEX`), two repossession letters (`REPO1`,
  `REPO2`) and two HIPAA medical letters (`HIPAA_PROVIDER`, `HIPAA_CA`)

The book tells you to write two more letters but doesn't give their text, so they
were written from its instructions and marked that way in the list:

- the clerk-of-court letter for the public records loophole (`COURT_CLERK`)
- the "contact me only in writing" letter for collectors (`WRITTEN_ONLY`)

Only obvious typos were fixed (for example "blantent" → "blatant"). The bizarre
letter keeps its deliberate misspellings.

## The book's rules the tool enforces

- The 30-day clock starts the day they sign for your certified letter. It won't
  make the next letter in a conversation before the 30 days are up. You can override
  this with `--force`.
- On day 31 you pull fresh reports and record whether the item was marked "disputed".
  That decides whether you send Part 1 Letter #3.
- Part 1 comes before Part 2. Public records and federal student loans start at Part 2.
- Inquiry Letter 2 isn't sent at the same time as the personal-info letter to that
  bureau.
- No disputes on inquiries where credit was granted.
- The goodwill letter is for 1-2 late payments.
- The identity theft letter is for accounts you never had.

## Your privacy

- Your case lives in `credit-repair/my-case/`. That folder is git-ignored twice over
  (here and by its own `.gitignore`), so it is never committed. **This repository is
  public.**
- Only the last 4 digits of your SSN are stored. The two letters that need the full
  number (the personal info letter and the ChexSystems letter) leave a blank for you
  to write it in by hand.
- In a Claude Code cloud session, files are deleted when the session ends. The agent
  will zip your case folder for you to download, and ask you to upload it next time.
  Running Claude Code on your own computer keeps it in place.

## Using the case tool directly

```
python credit-repair/cr.py --help
python credit-repair/cr.py next            # what to do today
python credit-repair/cr.py status          # every item and its letters
python credit-repair/cr.py calendar        # deadlines -> .ics for your phone
python credit-repair/cr.py info sol TX     # statute of limitations from the book
```

It needs Python 3.10+. Word output needs `python-docx` (`pip install python-docx`);
without it you get the `.txt` files. Tests: `python -m pytest credit-repair/tests`.

*From the book: "We are not lawyers. The contents of this book should NOT be
considered legal advice in any way."*
