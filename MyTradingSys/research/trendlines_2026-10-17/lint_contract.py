"""Spec lint for TRENDLINE_CONTRACT.md: every parameter row has a value and a tag."""
import re
import sys
from pathlib import Path

p = Path(__file__).with_name("TRENDLINE_CONTRACT.md")
bad = 0
rows = 0
for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
    m = re.match(r"\| ([A-Z]+\d+) \|", line)
    if not m:
        continue
    rows += 1
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) < 4 or not cells[2] or not re.search(r"SOURCED|OURS", cells[3] if len(cells) > 3 else ""):
        if not re.search(r"SOURCED|OURS", line):
            print(f"line {n}: {m.group(1)} missing tag"); bad += 1
    if re.search(r"\b(TBD|TODO|unset)\b", line):
        print(f"line {n}: {m.group(1)} unset"); bad += 1
if rows < 40:
    print(f"only {rows} parameter rows"); bad += 1
print(f"rows={rows} problems={bad}")
sys.exit(1 if bad else 0)
