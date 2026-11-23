#!/usr/bin/env python3
"""Run the credit repair case tool without installing it: python credit-repair/cr.py --help"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from credit_repair.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
