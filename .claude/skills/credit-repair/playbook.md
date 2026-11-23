# Credit Secrets playbook (2024-2025 edition)

The book's method, chapter by chapter. Page numbers are PDF pages of the book.
Letter codes are the codes in `python credit-repair/cr.py letter templates`.

## Introduction and important notes (p.7-13)

- Under the FCRA an item must be removed if it is **inaccurate** (not yours, wrong
  high balance or account number, closed shown as open, wrong date of last
  activity...), **incomplete** (blank field, truncated number, missing or extra
  characters, data in the wrong field) or **unverifiable** (they can't produce the
  original signed contract or record of it).
- Credit bureaus, creditors and collectors are large and disorganized and often
  miss their legal deadlines; the method turns those misses into leverage.
- Top 5 FDCPA violations: calls before 8am or after 9pm; contacting third parties
  (employer, friends) except for location info; lying about the amount; threatening
  garnishment or sale of property; giving false credit information to a bureau.
- Follow the steps from the beginning, in order. Be organized: folders, reminders for
  cutoff dates, track who got what and when. Goal: become "not worth it" - show them
  you know the law and you're more organized than they are.
- Integrity pledge: don't use the method to defraud a lender, and don't go back to old
  habits once your credit is fixed.

## Chapter 1: Getting started

### Step 1 - get all 3 reports and scores (p.14)
Sources members use: creditsecrets.com/credit-score-hub/scores (top choice), Credit
Karma (2 bureaus), Experian 3 Bureau, MyFICO (expensive), AnnualCreditReport.com
(free, no scores). **Don't dispute from AnnualCreditReport.com reports**: the FCRA
then allows 45 days instead of 30, and a letter on day 31 gets treated as
"additional info", extending the investigation 15 more days.

### Step 2 - look for the bad stuff (p.15-19)
In order of damage: 1) **Public records** (bankruptcies, other court records);
2) **Derogatory accounts** (usually sent to collections); 3) **Unsatisfactory
accounts** (30-180 day late pays, not yet in collections). Accounts may appear on
only one bureau, and bureaus list the same account differently.
- Be careful with collectors promising removal for a payment; many take the money and
  never remove it.
- Case law: Cook v. Mountain America FCU (2018) - original creditor still reporting a
  balance after the debt went to a collector who also reports it = inaccurate and
  duplicative reporting.

### Scores (p.20-25)
FICO: payment history 35%, amounts owed 30%, history length 15%, new credit 10%, mix
10%. VantageScore: payment history 41%, depth 20%, utilization 20%, balances 6%, new
credit 11%, available credit 2%. Keep each card under 30% utilization; 1% overall is
ideal. FICO counts rate-shopping inquiries in 45 days as one (Vantage: 14 days). FICO
ignores collections under $100; newest versions ignore paid collections. Closing old
accounts can lower your score.

### The bureaus (p.26-27)
Experian, P.O. Box 4500, Allen, TX 75013. Equifax Credit Information Services, Inc.,
P.O. Box 740256, Atlanta, GA 30374. TransUnion, LLC, P.O. Box 2000, Chester, PA 19016.
Contact them by **certified mail** - not phone, not online. Print/save every report
as a dated PDF: the dates are leverage.

### #Jumpstart: personal information (p.28-31) - `PI`
Removing old addresses and variations of your name, SSN, birth date, phone and
employers can raise scores and sometimes removes negative accounts tied to old
addresses.
1. Update your contact info directly with creditors: open accounts through their
   portal; old *positive* closed accounts by phone or letter (otherwise removing the
   old address could lose those positive accounts and shorten your history).
2. Experian trick: the "Address Identification Number" on your Experian report
   (from Experian directly, or the online dispute screen - don't complete an online
   dispute). If a negative account's address ID doesn't match yours, removal is more
   likely. Disputes are processed by computer (e-OSCAR, reduced to a 2-digit code),
   so mismatches in address ID or name variations help.
3. Send `PI` to each bureau (certified suggested - it has sensitive info) with a
   recent utility bill (or pay stub, insurance, registration, phone bill), copies of
   driver's license and SSN card (you can cover the signatures). Ask for USPS replies
   only.
4. If not updated: call each bureau about personal info (and inquiries) only - don't
   start any account disputes, don't give an email. Stubborn bureau: get your license
   and a bill notarized (UPS store) and resend. Experian: experian.com/upload. If they
   say it's tied to reporting accounts, move on and come back after the disputes.
5. Goal: hard copies of your reports by mail showing the changes - you'll refer to
   them often.

### Inquiries (p.32-36) - `INQ1`, `INQ2`, `INQ3`
- Hard inquiries cost a few points each (~10% of the score), count half after 6
  months and must drop off at 2 years. Remove inquiries where you were denied credit.
- **Do not dispute an inquiry where credit was granted** / tied to an open positive
  account - the creditor could close it as fraud.
- Members have had success calling the bureaus saying the inquiries had no
  permissible purpose or authorization. Otherwise:
  - `INQ1` to the creditor (certified): no permissible purpose (FCRA 604); asks for
    proof of authorization.
  - `INQ2` to the bureau: FCRA 604(f) certification; all denial inquiries in one
    letter. **Not at the same time as the PI letters.**
  - `INQ3` to the bureau if no reply or "verified".

### The laws (p.38-39)
- FDCPA 807(8) [15 USC 1692e(8)] (collectors): communicating credit information known
  to be false, including failing to communicate that a disputed debt is disputed.
- FCRA 623(a)(3) [15 USC 1681s-2] (creditors/banks): once you dispute with them they
  can't furnish the info without noting it's disputed.
- Fair Credit Billing Act: billing errors (wrong date/amount, math errors, unposted
  payments/credits, bills not sent to a new address given 20+ days before the cycle
  ends, charges you ask to explain).
- Collectors can't call all hours, at work, threaten legal action, use abusive
  language or tell family/friends. Report them to your AG, BBB, CFPB; small claims.

### Pre-dispute: license/bond search (p.40)
Many states require collectors to be licensed and/or bonded. Before any letter:
1. Find your state's rules and lookup links (book link:
   creditsecrets.com/credit-score-hub/cornerstone); note "possible exemptions".
2. Look up every collector on your reports or in your mail; screenshot any
   non-compliance.
3. File complaints with the CFPB, your State AG, the collector's State AG and the BBB,
   in your own words, attaching mail, call records and proof.

### Dunning notices (p.41)
The first letter from a collector. Don't ignore it: answer within 30 days with the
CFPB's "I need more information about this debt" letter (consumerfinance.gov ->
"What should I do when a debt collector contacts me"). That locks them into the
legal requirements, and if they later report it they must report it as disputed.

## Chapter 2: Attack & Conquer (p.42-71)

- Any time you question an item with the company that reported it, they must have it
  marked **disputed** on your report ("Customer has disputed...", "Account disputed",
  "Dispute resolved meets FCRA requirements") **within 30 calendar days**. The book
  says over 90% of the time they don't, or do it late. A report pulled the day they
  sign + a report 31 days later = proof, and leverage (damages "up to $1,000 per
  occurrence" per the book).
- **Part 1** = creditors and collectors directly. **Part 2** = the bureaus. Don't skip
  ahead; exception: public records (bankruptcy, child support...) go straight to Part 2.
- Certified mail, return receipt (or e-delivery confirmation). One dispute per
  envelope. Send all the disputes at once - more chances for their mistakes.
- **Never dispute online/phone** (p.44): FCRA 611(a)(8) lets them skip forwarding,
  written results and the method of verification if deleted in 3 days; it's a
  soft/temporary delete that can be reinserted without the 5-day written notice.
- The clock starts when they sign. **Always wait 30 days**, even if they reply sooner.
  **Day 31**: print new dated reports and check for the "disputed" remark.
- You're allowed to dispute anything - the burden of proof is on them (p.44). The
  book leaves the choice of avenue to you: dispute items you don't recognize, and for
  items you know are yours challenge their errors instead (p.45-46):
  incorrect balance; missing info; incorrect credit limit; high balance lower than
  owed balance; blank or incorrect "status"; incorrect high balance; late pays after
  the account closed; account number with X's/asterisks; wrong account type; invalid
  furnisher; wrong date of last activity (the 7-year clock starts at the first missed
  payment never brought current - no re-aging, even paying doesn't reset it); wrong
  date of last update; wrong date reported; collection listed with a limit; charge
  off listed as open or collection. Differences between bureaus should be challenged.
- Common replies (p.46): "blah blah" stall letters -> next letter; "verified" with an
  itemized printout (FTC opinion: not verification) -> Letter #2 with leverage; no
  reply in 30 days -> violation, leverage; returned mail -> the address they report is
  false, send the returned envelope to the bureaus.
- Don't sign the letters - type your name (p.47).

### Part 1 letters
- `P1L1` (p.48): to the bank/creditor/collector that reported it (address from your
  report). Disputes the claim, demands validation - competent evidence of a
  contractual obligation and the record of how your "signature" was generated.
- `P1L2A` (p.50): they replied "verified" - anything that doesn't say they're
  deleting. Method of verification; FTC LeFevre opinion (a printout isn't
  verification); contract and signature record again.
- `P1L2B` (p.52): no reply to Letter #1.
- `P1L2C` (p.54): you disputed a collector and the original creditor answered
  instead. Quotes the CFPB's 2019 FDCPA report on 809(b): the collector itself must
  obtain and mail verification.
- `P1L3` (p.56): on day 31 after they signed for Letter #1 the item was NOT marked
  disputed -> send after 2A or 2B. Cites FCRA 623(a)(3) and FDCPA 807(8); small claims
  for a minimum of $1,000 per violation (defamation, negligent enablement of identity
  fraud, FDCPA, FCRA), in a court local to you.
- FAQ shortcuts (p.162): papers but no signature -> P1L2; marked disputed but no
  signed contract -> P1L2; responded AND marked disputed -> skip to P2L1.
- FAQ (p.167): signed contract after Letter #1 is not game over - they still had to
  mark it disputed; also check licensing and the statute of limitations.

### The Automator (p.58-63)
The book's paid letter generator; this agent does the same job from your case file.

### Part 2 letters (p.64-71) - the bureaus
- `P2L1`: dispute under FCRA 611(a)(1)(A); 30 days; no consent to e-OSCAR/automated
  verification; USPS replies only. Send if Part 1 didn't work, or first for public
  records.
- `P2L2A`: bureau says verified -> method of verification (FCRA 611(a)(6)-(7), due
  within 15 days), name/address/phone of each person contacted, the contract;
  Wenger v. Trans Union.
- `P2L2B`: no response to Letter #1 -> they violated the law; demand deletion and an
  updated report by USPS.
- `P2L3`: final letter if still no proof / no method of verification (611(a)(7));
  investigate in 30 days, respond within 5 days of finishing; considering complaints
  and legal action. Or skip to the Bizarre or Incomplete/Missing Info letter in lieu
  of legal action.
- If one bureau deletes and another doesn't, or a letter comes back returned, send
  that as evidence to the other bureaus.

## Chapter 3: Advanced tactics

### Public records (p.72-75)
- Tax liens left all 3 bureaus in April 2018 (NCAP); civil judgments no longer report
  either - if one's still there, Part 2 letters.
- Judgments: you can't dispute the court's order itself; satisfy it (they can renew
  every 10 years and garnish/lien) or try to vacate it. A satisfied judgment is easier
  to remove.
- Foreclosure removable when: over 7 years from the original delinquency; the lender
  is out of business; the servicer reported inaccurately; voluntary dismissal.
- **The loophole**: the bureaus list the court ("recorder of deeds", "magistrate",
  "municipal court") as the furnisher, but courts don't furnish data to bureaus -
  data miners like LexisNexis do, and bureaus "verify" through e-OSCAR with the data
  miner, not the court. Reporting a false source = false information. Get proof:
  write (`COURT_CLERK`) to a clerk of court **not in the district where your record
  was filed**, asking for their procedure for verifying records with the bureaus, with
  a self-addressed stamped envelope - or visit a courthouse. Send that to the bureaus.

### Freeze & suppress the data miners (p.76-78)
Since Sept 21, 2018 freezes are free. Freeze LexisNexis (C.L.U.E., Current Carrier,
RiskView reports) and the others so they can't sell your file. LexisNexis
suppression blocks re-reporting but needs evidence you may be an identity fraud
victim: a police report, or a creditor's letter identifying you as a potential victim
(e.g. a data-breach notice like Equifax 2017). Send name, SSN, DOB, phone, address +
two IDs. Contacts: `info data-miners`.

### Data miner reports and disputes (p.79-80)
Get your LexisNexis, CoreLogic Credco, Innovis and ARS files. Dispute personal info
first, then derogatory items with `P2L1` (bureau codes LN, CO, IN, ARS, LCI). They
have 30 days, follow the FCRA like the big 3, and must also get the big-3 entries
marked disputed - watch both.

### CFPB, State AG, BBB (p.83-95)
- CFPB complaint (consumerfinance.gov/complaint): for "stubborn" accounts after the
  letter sequence; minutes to file; members often see removals within 2 weeks. Read
  other consumers' complaints for wording; write yours in a doc first.
- State AG: may not act on every complaint but can open an investigation.
- BBB: no legal authority, but companies respond to protect their rating. They forward
  in 1-5 business days, business has ~14 days, you have 10 days to rebut. The text is
  public: no names, phones or account numbers; professional and brief; state the
  resolution you want; upload your documents.
- Combining all three puts pressure on a collector, creditor or bureau.

### Other letters (p.96-110)
- `STALL`: bureau says your letter came from a third party/credit repair company ->
  you wrote and mailed it; no law bars third parties anyway; 15 days, not 30 more.
- `IDT` (identity theft): for accounts you've never had and have no knowledge of.
  Create an FTC Identity Theft Report; write to each bureau's fraud address one at a
  time; circle the items; enclose the report, ID and FCRA 605B (block within 4
  business days).
- `EARLY` early exclusion (not a dispute): needs the "estimated month and year this
  item will be removed" from a report direct from the bureau. TransUnion up to 6
  months early, Experian 3, Equifax 1-2. If not removed, call, ask for a US
  representative/supervisor, and say it's an early exclusion request, not a dispute.
  Removing your oldest account can lower your score.
- `REINSERT`: a deleted item reinserted without written notice within 5 business days
  (FCRA 611(a)(5)(B)(ii)); also a CFPB complaint against the bureau, or small claims.
  Keep monitoring your reports.
- Late payments: `LP1` (validation of the late dates) -> `LP2` (FCRA 623(a)(7), FTC
  Harris opinion: furnishers aren't required to report negatives and must update and
  correct). A late can drop scores ~100 points; can't be reported until 30+ days late.
- `GW` goodwill: one or two late pays; an admission they're yours; regular mail is
  fine. If it fails, try again (another person may help); then P1L1, then P2L1 (FAQ).
- `INCOMPLETE`: you acknowledge it's yours, challenge a technicality - e.g. a
  truncated account number (FTC Darcy opinion: scrambling/truncating account numbers
  doesn't technically comply with FCRA 609). Doesn't replace P1L1.
- `RETURNED`: your letter to the address on the report came back -> enclose a copy of
  the returned envelope; FCRA 623(a)(1)(A).
- `BIZARRE`: "a bizarre letter that just works many times", from a mathematician who
  sent 45,000+ disputes. Misspellings are deliberate - meant to defeat the automated
  system so a human reviews it. Most circumstances, sent to the bureau.

## Chapter 4: Lawsuits (p.111-123)

- Not legal advice; FCRA/FDCPA attorneys often work on contingency; LegalShield for
  low-cost advice.
- Small claims: cheap to file. Base your claim on **state law** (well-pleaded complaint
  rule, Caterpillar v. Williams) so it stays out of federal court; add the similar
  state statutes, or amend if they try to move it. Sue for a small amount - the goal
  is removal; a judgment is leverage. Most settle or go to mediation; they have to
  come to you and small claims doesn't cover their attorney fees.
- Who/why/law table: `info lawsuits` (p.112-114).
- In court: a 3-ring binder with your letters, their replies, dated reports and
  certified receipts, highlighted; the FCRA/FDCPA sections; a bullet summary; stay
  factual. If they don't show, **ask for a default judgment**. Damages: credit denials,
  higher interest, mental anguish and humiliation count (Bryant v. TRW, Fischl v. GMAC,
  Pinner, Thompson, Collins, Morris, Millstone).
- Objections the book suggests: "no foundation" for a bill; "hearsay" if they weren't
  present when the account was opened; on a signature, say you can't confirm a
  photocopy is authentic.
- Mediation: don't give up because the mediator says you "don't have a case".
- **If YOU are sued: answer it.** No-shows become default judgments and garnishment.
- Registered agent: the address to serve; look it up by business name (e.g.
  registeredagentinfo.com; TransUnion's entity is "TRANS UNION LLC"); certified mail or
  a process server. Copy the CFPB enforcement office and the bureau's chief legal
  officer (`info lawsuits`). FDCPA suits can be filed where you received the letter.
- FAQ: sending the collector a copy of your filed suit and offering to drop it for
  deletion has worked for members.

## Chapter 5: ChexSystems (p.124-127)
The "credit bureau" for checking accounts (~80% of banks). Negative entries generally
stay 5 years. Free report every 12 months or within 60 days of a bank denial
(consumerdebit.com, 800-428-9623, or mail). Same method: `P1L1` to the bank, the
`CHEX` letter to ChexSystems (book: sign it and send registered mail).

## Chapter 6: Student loans, repossessions, HIPAA (p.128-144)
- **Student loans**: no statute of limitations; bankruptcy doesn't erase them.
  Federal loans: start with Part 2 letters, then Part 1 if needed. Private loans: the
  normal Part 1 -> Part 2 process. Each disbursement can show as a separate loan, and
  one missed payment can mark late on all of them. Options: deferment (government
  pays interest on subsidized loans), forbearance (mandatory in some situations;
  interest accrues), consolidation, rehabilitation, forgiveness/discharge (incl.
  closed schools) - studentaid.gov.
- **Repossession**: dealership (indirect) financing reported as a direct loan is a
  common error -> dispute with P2L1, then the repo letters. Keep the contract, all
  dealer/lender documents and envelopes, repair/inspection records, payment records.
  Rules: self-help repo without breach of peace (owner present objecting, entering a
  garage, force/threats); SCRA protects active-duty servicemembers. After repo: a
  redemption notice at least 10 days before sale (amount, date/time, public/private,
  payoff instructions) and a deficiency notice after; bad notice can bar a deficiency;
  a commercially unreasonable sale reduces it; gap insurance/service contracts should
  be credited. Bankruptcy's automatic stay can stop a repo. `REPO1` to the collector,
  original creditor and dealer (send P1L1 first if you lack the details); `REPO2` to
  the bureaus 15 days later.
- **Medical / HIPAA**: paid medical collections stopped reporting July 1, 2022; unpaid
  ones need a year before reporting; under $500 removed since April 2023. Ask the
  collector for verification; if what they send discloses your medical condition or
  treatment, that may breach HIPAA privacy rules - leverage with both. `HIPAA_PROVIDER`
  to the provider's HIPAA compliance office (10 days to respond; add the 501(r)
  charitable-hospital line if it applies: `--set charitable_hospital_line="You may also
  be in violation of the Notice of Proposed Procedures for Charitable Hospitals under
  Section 501(r) of the Affordable Care Act."`), `HIPAA_CA` to the collector (also for
  debts past the SOL).

## Chapter 7: Advanced credit techniques (p.145-159)
- Raise limits to lower utilization (e.g. $4,500 on $5,000 = 90%; on $15,000 = 30%);
  new accounts can help if managed well. No new lines during an open bankruptcy.
- Rent reporting services (landlord verification, fees, check which bureaus).
- Piggybacking: be added as an authorized user on a strong, old card (the user doesn't
  need to use it; depends on the issuer reporting AUs).
- **Shopping cart trick** (soft pull store cards, mostly Comenity/Experian): pop-up
  blocker off; clear history/cookies/cache; create a site account matching your report
  info and subscribe to emails; add ~$100 of items (adjust +/- $50); start checkout,
  type slowly (no autofill); a pre-approval pop-up asking for the last 4 of SSN means
  it worked; only proceed with last 4 (full SSN = likely hard pull, except Overstock);
  no purchase needed. Try 2-3 at a time. List: Abercrombie, Ann Taylor, Bath & Body
  Works, Brylane Home, Buckle, Coldwater Creek, Express, GameStop, HSN, J.Crew, J.Jill,
  Jessica London, King Size, LOFT, NY & Co, One Stop Plus, Overstock, Roamans,
  Sportsman's Guide, Victoria's Secret (reports of hard pulls), Williams-Sonoma,
  Wayfair, Woman Within.
- Credit unions: Navy Federal (military affiliation; Visa Signature for high limits;
  personal loans to consolidate); PenFed (anyone can join: pick an organization, $5
  share deposit). PenFed's Equifax pull is good for 90 days; apply by phone, ask for a
  loan officer if denied.
- Business credit: incorporate, EIN, D-U-N-S number, business bank account and phone,
  trade references, business cards, vendor lines (e.g. OnDeck), monitor scores.
- Secured cards (First Progress, OpenSky, Group One...), unsecured starter cards
  (Indigo, Merit), shopping accounts (NetFirst, Fingerhut), personal loans, nonprofit
  debt consolidation, LendingTree, LendKey.
- After it's fixed: limit increases every 6-12 months; business cards; charge cards;
  rate-shop loans in 14-45 days; don't close accounts (small purchases keep them
  active); monitor reports; diverse mix; stay under 30% (FAQ sweet spot 10-30%);
  budget; be careful with new applications.

## Chapter 8: FAQ highlights (p.160-172)
- Paid collections: don't claim they aren't yours; use reporting errors; old paid
  collections can help your age of credit.
- Start with collections and public records, then late pays.
- Prior disputes from a credit repair firm still showing: call the bureau to remove
  the dispute notations, then start fresh (mortgage lenders require none in dispute).
- Don't dispute an open account just because you're tired of paying - this isn't debt
  elimination.
- Certified mail to a PO Box works. Unclaimed at a PO Box: find their physical address
  and resend certified.
- No address on the report: dispute that as inaccurate/incomplete reporting.
- Collector calls: write that they may only contact you in writing at your address,
  never by phone (`WRITTEN_ONLY`).
- Masked account numbers: write the digits you know and X's for the rest.
- One dispute per envelope. The 30 days start when they sign.
- Removed then reinserted: common - keep watching your reports.
- Pay for delete on old charge-offs: offer to pay only if they notify the bureaus to
  delete; get verbal agreement, then a signed letter from an authorized representative
  agreeing to the deletion **before** you pay.
- Bankruptcy (per the book): Chapter 13 stays 7 years, Chapter 7 10 years; foreclosure
  7 years from the sale.
- Don't close unused cards. Goodwill letters don't need certified mail.

## Chapter 9: Statute of limitations (p.174-175)
`info sol [STATE]`. A collector suing on a debt past the SOL violates the FDCPA.

## Bonus: identity theft protection (p.186-188)
Review reports regularly; protect your SSN; never answer unsolicited requests for
personal info; freeze all 3 bureaus; don't let mail pile up; secure devices; VPN on
public wi-fi; review statements; shred; strong passwords; use credit cards online.
If it happens: fraud alert (one bureau tells the others; extended alert = 7 years),
FTC complaint and police report, check your reports, call affected creditors and log
every call.
