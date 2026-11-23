# Reading the credit reports

How to turn the user's 3 credit reports into case items (Credit Secrets Chapter 1,
Step 2, and the error checklist in Chapter 2).

## 1. Collect

For each bureau report (Experian, Equifax, TransUnion), note the source and the date
it was pulled (`report add`). Read every page, including the personal information
section, the inquiries section and each account's remarks/comments.

## 2. Personal information

List every variation the reports show: names (last name first, middle initial,
middle name, no middle name), addresses, SSNs, birth dates, phone numbers and
employers. Anything that isn't the user's one current, correct value is what the `PI`
letter asks to remove. On the Experian report, note the "Address Identification
Number" on the user's address and on each negative account (a mismatch helps, p.28).

## 3. Negative items

Go section by section in the book's order of damage:

1. **Public records**: bankruptcies, judgments, tax liens -> `public_record`
   (tax liens and civil judgments shouldn't be reporting at all since 2018).
2. **Derogatory accounts**: collections (`collection`, or `medical` if it's a
   medical bill), charge-offs by the original creditor (`charge_off`),
   repossessions (`repossession`), foreclosures (`foreclosure`), student loans
   (`student_loan_federal` / `student_loan_private`).
3. **Unsatisfactory accounts**: accounts with 30/60/90/120+ day lates but not in
   collections -> `late_payment`.
4. **Hard inquiries** -> `inquiry` (one item per inquiry; note the date and whether
   credit was granted).
5. Accounts the user has never had and knows nothing about -> `identity_theft`
   (only on the user's own statement).
6. ChexSystems entries (from their ChexSystems report) -> `chexsystems`, bureau `CX`.

The same account usually appears on several bureaus: make **one item** and list every
bureau that reports it in `bureaus`. If the bureaus show it differently (balance,
dates, status, account number), that difference is itself an error - list it.

## 4. Look for errors (`python credit-repair/cr.py info checklist`)

For each account compare every field across the 3 reports and against the checklist:
wrong/missing balance, credit limit, high balance (or high balance lower than the
balance owed), blank or wrong status, lates after the account closed, account number
with X's/asterisks, wrong account type, invalid furnisher, wrong date of last
activity / last update / date reported, a collection with a credit limit, a charge-off
shown as open or as a collection, the original creditor AND a collector both
reporting a balance on the same debt, dealer financing shown as a direct loan,
missing creditor address. Medical: paid, under $500, or less than a year old ->
shouldn't be reporting. Write each error as a phrase that fits the Incomplete/Missing
Info letter's sentence "...the fact that you are reporting ___", e.g.
`an incorrect high balance`, `an incorrect account number`, `an undated late pay`,
`a missing field of status`, `a collection account with a limit`.

## 5. Ask the user (don't guess)

- Do you recognize this account? (`recognized`: yes / no / unsure) - the book leaves
  the avenue to them: challenge what they don't recognize; challenge the reporting
  errors on what they know is theirs.
- For each inquiry: did you get credit from them (an open account)? If yes, the book
  says don't dispute it.
- Late payments: how many, and would they rather send the goodwill letter (1-2 lates,
  admits them; set `strategy=goodwill`) or dispute (`LP1` -> `LP2`)?
- Repossessions: do they have the VIN, purchase date, lender, sale date and dealer
  details for Repo Letter 1? If not, `strategy=needs_info` (P1L1 first).
- Anything they paid, settled, or that's in a bankruptcy.

## 6. Import

Write the items to a JSON file in the case folder and import them:

```
python credit-repair/cr.py item import credit-repair/my-case/items.json
```

```json
[
  {
    "kind": "collection",
    "furnisher": "Midland Credit Management",
    "furnisher_address": "PO Box 939069|San Diego, CA 92193",
    "original_creditor": "Synchrony Bank",
    "account_number": "8512XXXX",
    "bureaus": ["EX", "TU"],
    "derogatory_condition": "I owe $812.00",
    "month_year": "March 2024",
    "balance": "$812",
    "recognized": "unsure",
    "errors": ["an incorrect account number", "a collection account with a limit"],
    "estimated_removal": {"TU": "2029-04", "EX": "2029-04"},
    "notes": "TU shows balance $812, EX shows $790"
  },
  {
    "kind": "inquiry",
    "furnisher": "Capital One",
    "furnisher_address": "PO Box 30285|Salt Lake City, UT 84130",
    "inquiry_date": "May 3, 2026",
    "bureaus": ["EQ"],
    "credit_granted": false
  },
  {
    "kind": "late_payment",
    "furnisher": "Chase",
    "furnisher_address": "PO Box 15298|Wilmington, DE 19850",
    "account_number": "4147XXXX",
    "late_payment_dates": "August 2025",
    "bureaus": ["EX", "EQ", "TU"],
    "strategy": "goodwill",
    "extra": {"circumstance": "a hospital stay", "upcoming_purpose": "a mortgage"}
  }
]
```

Field notes:
- `derogatory_condition` completes the book's sentence "which you claim ___" (e.g.
  `I owe $200.00`, `my account was charged off $800`); for public records, e.g.
  `a civil judgment of $2,300`.
- `month_year` is the month/year of the entry for Part 2 letters.
- Addresses: separate lines with `|`. Use the creditor/collector address printed on
  the credit report (the book's Returned Mail letter depends on it).
- `estimated_removal`: the "estimated month and year this item will be removed" from
  a report that comes directly from the bureau (for early exclusion).
- `extra`: any other letter blank - e.g. `vin`, `purchase_date`, `financed_by`,
  `sold_by`, `sale_date`, `repo_state`, `dealer_name`, `dealer_address` (repo);
  `patient_name`, `date_of_service`, `provider_name`, `provider_address` (medical);
  `court_name`, `court_address` (clerk letter); `circumstance`, `upcoming_purpose`
  (goodwill).
- Bureau codes: EX, EQ, TU; CX ChexSystems; data miners LN, IN, ARS, LCI, CO.
