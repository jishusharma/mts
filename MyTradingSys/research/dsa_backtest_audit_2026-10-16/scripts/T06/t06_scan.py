"""T06 cost-constant scanner (shared by t06_inventory.py and test_cost_inventory.py).

Finds every line under MyTradingSys/backtest and MyTradingSys/research (tracked .py files,
excluding dsa_backtest_audit_* and test files) that binds a cost-like name to a numeric
literal, or carries a typical fee literal on a line that talks about fees/slippage/funding.
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
NUM = r"-?\d+(?:\.\d+)?(?:e-?\d+)?"
NAME = r"[A-Za-z_0-9]*(?:fee|slip|spread|cost|fund|taker|maker|bps|_bp|commission|c_pct)[A-Za-z_0-9]*"
BIND = re.compile(r"(?P<name>" + NAME + r")['\"]?\s*[:=]\s*(?:float\()?\s*(?P<val>" + NUM + r")(?![\w.])", re.I)
LITS = re.compile(r"(?<![\d.])(0\.0005|0\.0002|0\.0007|0\.0012|0\.0014|0\.0010|0\.001|0\.002|0\.0006|0\.0004)(?![\d])")
KEYLINE = re.compile(r"fee|slip|cost|spread|fund|taker|maker|commission|bps|_bp", re.I)


def tracked_py():
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "MyTradingSys/backtest", "MyTradingSys/research"],
                         capture_output=True, text=True, check=True).stdout.split("\n")
    res = []
    for p in out:
        if not p.endswith(".py") or "dsa_backtest_audit_" in p:
            continue
        if Path(p).name.startswith("test_") or "/tests/" in p:
            continue
        res.append(p)
    return res


def scan():
    """Return list of (file, lineno, name, value, text)."""
    hits = []
    for p in tracked_py():
        try:
            lines = (ROOT / p).read_text(encoding="utf-8", errors="replace").split("\n")
        except OSError:
            continue
        for i, ln in enumerate(lines, 1):
            s = ln.strip()
            if not s or s.startswith("#"):
                continue
            code = ln.split("#", 1)[0]
            seen = set()
            for m in BIND.finditer(code):
                key = (m.group("name"), m.group("val"))
                if key in seen:
                    continue
                seen.add(key)
                hits.append((p, i, m.group("name"), m.group("val"), s[:160]))
            if not seen and LITS.search(code) and KEYLINE.search(code):
                hits.append((p, i, "(literal)", LITS.search(code).group(1), s[:160]))
    return hits


if __name__ == "__main__":
    h = scan()
    print(len(h), "hits in", len({x[0] for x in h}), "files")
