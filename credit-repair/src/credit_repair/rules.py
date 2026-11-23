"""Reference data taken from the Credit Secrets book (2024-2025 edition).

Page numbers refer to the PDF page of the book. Addresses and names are as
printed in the book; check them before mailing if anything looks out of date.
"""

from __future__ import annotations

# Credit bureaus: dispute addresses (book p.27). The book says to contact them by
# certified mail only - not online, not by phone - for disputes.
BUREAUS: dict[str, dict[str, str]] = {
    "EX": {"name": "Experian", "address": "P.O. Box 4500\nAllen, TX 75013"},
    "EQ": {
        "name": "Equifax Credit Information Services, Inc.",
        "address": "P.O. Box 740256\nAtlanta, GA 30374",
    },
    "TU": {"name": "TransUnion, LLC", "address": "P.O. Box 2000\nChester, PA 19016"},
    # ChexSystems is treated as "the credit bureau" for bank accounts (p.125-127).
    "CX": {
        "name": "ChexSystems Customer Relations",
        "address": "7805 Hudson Road, Suite 100\nWoodbury, MN 55125",
    },
    # Data miners (p.78-80). They follow the FCRA like the big three; dispute
    # them with Part 2 letters once your personal info is cleaned up.
    "LN": {
        "name": "LexisNexis Risk Solutions Consumer Center",
        "address": "P.O. Box 105108\nAtlanta, GA 30348-5108",
    },
    "IN": {
        "name": "Innovis Consumer Assistance",
        "address": "PO Box 530086\nAtlanta, GA 30353-0086",
    },
    "ARS": {
        "name": "Advanced Resolution Services, Inc.",
        "address": "PO Box 4000\nConway, AR 72033",
    },
    "LCI": {
        "name": "LCI Consumer Center/G2 Risk Solutions",
        "address": "P.O. Box 1582\nBurlingame, CA 94010",
    },
    "CO": {
        "name": "CoreLogic Credco, LLC",
        "address": "P.O. Box 509124\nSan Diego, CA 92150",
    },
}

MAIN_BUREAUS = ("EX", "EQ", "TU")

# Fraud addresses for identity theft letters (p.97) - different from the
# regular dispute addresses.
FRAUD_ADDRESSES: dict[str, dict[str, str]] = {
    "EQ": {"name": "Equifax", "address": "P.O. Box 105069\nAtlanta, GA 30348-5069"},
    "EX": {"name": "Experian", "address": "P.O. Box 9554\nAllen, TX 75013"},
    "TU": {
        "name": "TransUnion Fraud Victim Assistance Department",
        "address": "P.O. Box 2000\nChester, PA 19016",
    },
}

# Early exclusion windows (p.99): how many months before the scheduled
# removal date each bureau may remove a negative account early.
EARLY_EXCLUSION_MONTHS = {"TU": 6, "EX": 3, "EQ": 2}
EARLY_EXCLUSION_NOTE = (
    "TransUnion up to 6 months early, Experian up to 3 months, Equifax 1 or 2 months. "
    "You need the 'estimated month and year this item will be removed' from a report that "
    "comes directly from the bureau (monitoring services don't show it). If this is your "
    "oldest account, removing it early can lower your score."
)

# Data miners: freeze, opt-out/suppress and get your file (p.76-80).
DATA_MINERS = [
    {
        "name": "LexisNexis",
        "freeze_optout": "privacy.information.mgr@lexisnexis.com; opt-out link in the book: "
        "creditsecrets.com/credit-score-hub/lexisnexis",
        "get_report": "Mail the File Disclosure Request Form + ID to LexisNexis Risk Solutions "
        "Consumer Center, Attn: Full File Disclosure, P.O. Box 105108, Atlanta, GA 30348-5108 "
        "(about 15 days)",
        "suppress": "Requires evidence you may be an identity fraud victim: a police report, or a "
        "letter from a creditor (e.g. a data-breach notice such as the 2017 Equifax breach) "
        "identifying you as a potential victim.",
    },
    {
        "name": "Innovis",
        "freeze_optout": "(866) 712-4546; Innovis Consumer Assistance, PO Box 530086, Atlanta, GA "
        "30353-0086",
        "get_report": "Call 800-540-2505 or request online",
    },
    {
        "name": "Advanced Resolution Services (ARS)",
        "freeze_optout": "(800) 392-8911; ARS, PO Box 4000, Conway, AR 72033",
        "get_report": "Call (800) 392-8911, email consumerhelp@ARS-HELP.com, or mail ARS, 5005 "
        "Rockside Road, Suite 600, Independence, OH 44131",
    },
    {
        "name": "LCI Consumer Center / G2 Risk Solutions",
        "freeze_optout": "P.O. Box 1582, Burlingame, CA 94010; consumercenter@lciinc.com",
        "get_report": "Same contact",
    },
    {
        "name": "CoreLogic Credco",
        "freeze_optout": "-",
        "get_report": "Call (800) 637-2422 or mail CoreLogic Credco, LLC, P.O. Box 509124, San "
        "Diego, CA 92150",
    },
]
DATA_MINER_ID_DOCS = [
    "A copy of a state-issued driver's license or state ID card",
    "A recent (no more than 60 days old) cable, utility, or phone statement matching your address",
    "A copy of your SSN card",
    "A copy of your birth certificate",
    "A copy of a U.S. passport (picture page only)",
    "A copy of a voided check with your address",
    "A copy of an Alien Registration Card",
]

# Statute of limitations chart (p.174-175), in years:
# (written contracts, oral contracts, promissory notes, open-ended accounts incl. credit cards)
SOL: dict[str, tuple[str, str, str, str]] = {
    "AL": ("3", "6", "6", "3"), "AK": ("3", "6", "3", "3"), "AZ": ("6", "3", "5", "3"),
    "AR": ("5", "3", "3", "5"), "CA": ("4", "2", "4", "4"), "CO": ("6", "6", "6", "6"),
    "CT": ("6", "3", "6", "6"), "DE": ("3", "3", "3", "3"), "DC": ("3", "3", "3", "3"),
    "FL": ("5", "4", "5", "4"), "GA": ("6", "4", "6", "4 or 6"), "HI": ("6", "6", "6", "6"),
    "ID": ("5", "4", "5", "5"), "IL": ("10", "5", "10", "5 or 10"), "IN": ("10", "6", "10", "6"),
    "IA": ("10", "5", "5", "10"), "KS": ("3", "3", "3", "3"), "KY": ("15", "5", "15", "5 or 15"),
    "LA": ("3", "10", "10", "3"), "ME": ("6", "6", "6", "6"), "MD": ("3", "3", "6", "3"),
    "MA": ("6", "6", "6", "6"), "MI": ("6", "6", "6", "6"), "MN": ("6", "6", "6", "6"),
    "MS": ("3", "3", "3", "3"), "MO": ("5", "5", "5", "5"), "MT": ("8", "5", "8", "8"),
    "NE": ("4", "4", "4", "4"), "NV": ("4", "4", "4", "4"), "NH": ("3", "3", "3", "3"),
    "NJ": ("6", "6", "6", "6"), "NM": ("4", "4", "4", "4"), "NY": ("6", "6", "6", "6"),
    "NC": ("3", "3", "5", "3"), "ND": ("6", "6", "6", "6"), "OH": ("6", "6", "6", "6"),
    "OK": ("5", "3", "5", "3 or 5"), "OR": ("6", "6", "6", "6"), "PA": ("4", "4", "4", "4"),
    "RI": ("10", "10", "10", "10"), "SC": ("10", "10", "3", "3"), "SD": ("6", "3", "6", "6"),
    "TN": ("6", "6", "6", "6"), "TX": ("4", "4", "4", "4"), "UT": ("6", "4", "6", "4"),
    "VT": ("5", "3", "6", "3"), "VA": ("6", "6", "5", "6"), "WA": ("6", "3", "6", "6"),
    "WV": ("10", "10", "10", "10"), "WI": ("6", "6", "10", "6"), "WY": ("10", "8", "10", "8"),
}
SOL_NOTES = (
    "Georgia: Hill v. American Express (2008) - credit cards are 6 years after the amount "
    "becomes due. Illinois: credit card debt without a written contract is 5 years (2009). "
    "Kentucky/Oklahoma: state law doesn't specify open accounts. A collector that sues you on "
    "a debt past the SOL violates the FDCPA (p.174)."
)

# The error checklist (p.45-46). Any of these on a reported account is a reason
# to challenge it, even if the account is yours.
ERROR_CHECKLIST = [
    "Incorrect balance",
    "Missing information",
    "Incorrect credit limit",
    "High balance is lower than owed balance",
    "'Status' or any other field blank",
    "'Status' incorrect",
    "Incorrect high balance",
    "Late pays after an account was closed",
    "Account number inaccurate (X's or asterisks instead of the full number)",
    "Account type inaccurate",
    "Invalid furnisher",
    "Date of last activity incorrect (the 7-year clock starts at the first missed payment "
    "never brought current; no re-aging - even paying a collection doesn't reset it)",
    "Date of last update incorrect",
    "Date reported inaccurate",
    "Collection account listed with a limit (a collection cannot have a limit)",
    "Charge off listed as 'open' or collection",
    "Information differs between the 3 bureaus (challenge every discrepancy)",
    "Duplicate reporting: original creditor AND collector both report a balance on the same "
    "debt (Cook v. Mountain America FCU, 2018)",
    "Dealership (indirect) financing reported as a direct loan (repossessions, p.133)",
    "Experian 'Address Identification Number' on the account doesn't match yours (p.28)",
]

# Medical debt reporting changes the book relies on (p.140).
MEDICAL_RULES = [
    "Since July 1, 2022 paid medical collection debt is no longer included on credit reports.",
    "Unpaid medical collections can't appear until they are 1 year old (was 6 months).",
    "Since April 2023 medical debt with an initial reported balance under $500 must be removed.",
]

PUBLIC_RECORD_RULES = [
    "Since April 2018 tax liens are no longer reported by the big 3 (NCAP settlement).",
    "Civil judgments no longer report either - if one is on your report, send Part 2 letters.",
    "Foreclosures can be removed after 7 years from the original delinquency date, if the "
    "lender is out of business, if the servicer reported inaccurately, or on voluntary dismissal.",
    "Bankruptcy (per the book): Chapter 13 - 7 years, Chapter 7 - 10 years.",
]

# Where members get their 3 reports (p.14). Don't dispute from
# AnnualCreditReport.com reports: that makes the investigation period 45 days.
REPORT_SOURCES = [
    "creditsecrets.com/credit-score-hub/scores (book's top choice - all 3 reports & scores monthly)",
    "Credit Karma (2 reports & scores, free - you still need all 3)",
    "Experian 3 Bureau (all 3 reports & scores)",
    "MyFICO (all 3 reports & scores, expensive)",
    "AnnualCreditReport.com (free reports, no scores) - DO NOT dispute using these reports",
]
ANNUAL_REPORT_WARNING = (
    "The book says not to dispute using AnnualCreditReport.com reports: the FCRA then gives the "
    "bureau 45 days instead of 30, which throws off every 30-day timeline."
)

# What you can sue for in small claims, per the book (p.112-114).
LAWSUIT_TABLE = [
    ("Creditors", "Report your credit history inaccurately", "Defamation, financial injury; FCRA 623"),
    ("Creditors", "You dispute a debt and they fail to report it as disputed", "FCRA 623 - $1,000"),
    ("Creditors", "Pull your credit file without permissible purpose", "FCRA 604(A)(3) - $1,000"),
    ("Credit bureaus", "Refuse to correct information after proof of inaccuracy",
     "Defamation, willful injury; FCRA 623 (Cushman v. Trans Union)"),
    ("Credit bureaus", "Reinsert a deleted item without written notice within 5 business days",
     "FCRA 611(a)(5)(B)(ii) - $1,000"),
    ("Credit bureaus", "Fail to respond to written disputes within 30 days",
     "FCRA 611(a)(1) - $1,000"),
    ("Creditors, collectors, bureaus", "Re-age your account (date of last activity instead of "
     "date of first delinquency)", "FCRA 605(c) - $1,000"),
    ("Collection agency", "Fail to report a disputed debt as disputed", "FDCPA 807(8) - $1,000"),
    ("Collection agency", "Don't validate your debt yet keep collecting by filing for judgment",
     "FDCPA 809(b), FTC opinion letter Cass from LeFevre - $1,000"),
    ("Collection agency", "Keep calling after a cease and desist letter", "FDCPA 805(c) - $1,000"),
    ("Collection agency", "Haven't validated your debt and still report to the bureaus",
     "FDCPA 809(b) - $1,000"),
    ("Collection agency", "Call before 8 AM or after 9 PM", "FDCPA 805(a)(1) - $1,000"),
    ("Collection agency", "Call you at work after you said not to", "FDCPA 805(a)(3) - $1,000"),
    ("Collection agency", "Call third parties (friends, neighbors, relatives) about your debt",
     "FDCPA 805(b) - $1,000"),
    ("Collection agency", "Any harassment or abuse", "FDCPA 806 - $1,000"),
    ("Collection agency", "Claim they will seize property or have you arrested", "FDCPA 807 - $1,000"),
    ("Collection agency", "Sue you outside the county where you signed or now live",
     "FDCPA 811(a)(2) - $1,000"),
]

# People the book suggests copying when you sue a bureau (p.121). As printed in
# the 2024 edition - verify before mailing.
LEGAL_CONTACTS = [
    "Erick Halperin, Assistant Director of Enforcement, Consumer Financial Protection Bureau, "
    "1700 G Street NW, Washington, D.C. 20055",
    "John J. Kelley III, Corporate Vice President, Chief Legal Officer, Office of the General "
    "Counsel, Equifax Corporation, 1550 Peachtree St NE, Atlanta, GA 30309",
    "Heather Russell, Executive VP, Chief Legal Officer, Office of the General Counsel, "
    "TransUnion Corp., 555 W. Adams Street, Chicago, IL 60661",
    "John Migliarini, VP and Head of Legal, Office of the Corporate Counsel, Experian North "
    "America, 475 Anton Blvd., Costa Mesa, CA 92626",
]

COMPLAINTS = {
    "cfpb_complaint": "File a CFPB complaint at consumerfinance.gov/complaint (write it in a doc "
    "first; attach your letters, receipts and reports). Members often see removals in 2 weeks.",
    "ag_complaint": "File a complaint with your State Attorney General (and the collector's state "
    "AG for licensing violations).",
    "bbb_complaint": "File a BBB complaint at bbb.org - no names, phone or account numbers in the "
    "text (it's posted publicly); state the resolution you want; rebut within 10 days.",
}

BUREAU_NAMES = {code: info["name"] for code, info in BUREAUS.items()}
