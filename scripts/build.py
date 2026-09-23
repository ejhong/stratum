#!/usr/bin/env python3
"""One command for everything: validate → database → analysis → site.

  python3 scripts/build.py
  python3 -m http.server -d _site 8000     # then open http://localhost:8000

Stops (exit 1) if any record is invalid, so a broken record can never reach the site.
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for step in ("validate.py", "build_db.py", "analyze.py", "build_site.py"):
    if subprocess.run([sys.executable, str(HERE / step)]).returncode != 0:
        sys.exit(f"build stopped at {step}")
print("\nDone. Preview: python3 -m http.server -d _site 8000")
