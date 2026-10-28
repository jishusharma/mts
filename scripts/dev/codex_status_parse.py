"""Parse the `codex_run.py status` allowance line (standalone; usage_log.py may import this later).

Real format (codex_run.budget_line, sample in LAYER_LAB.md):
  Codex allowance (plus): 5-hour window 6% used (resets 10-19 08:32Z); week 27% used (resets 10-24 20:41Z)
Over the NUC gate: ssh -i ~/.ssh/nuc_gate e-ngineers@192.168.29.110 <verb> prints this line among others.
"""
import re
import sys

_LINE = re.compile(
    r"Codex allowance \((?P<plan>[^)]*)\):\s*"
    r"5-hour window (?P<win>\d+(?:\.\d+)?)% used(?: \(resets (?P<wr>\d\d-\d\d \d\d:\d\dZ)\))?;\s*"
    r"week (?P<wk>\d+(?:\.\d+)?)% used(?: \(resets (?P<kr>\d\d-\d\d \d\d:\d\dZ)\))?"
)


def parse_status(text):
    """Return {'plan','window_pct','window_resets','week_pct','week_resets'} or None (no reading: caller writes NOT_IN_DATA)."""
    m = _LINE.search(text or "")
    if not m:
        return None
    return {"plan": m["plan"], "window_pct": float(m["win"]), "window_resets": m["wr"],
            "week_pct": float(m["wk"]), "week_resets": m["kr"]}


if __name__ == "__main__":
    print(parse_status(sys.stdin.read()))
