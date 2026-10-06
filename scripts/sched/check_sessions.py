"""Check 5: MyTradingSys/system/sessions/*.md with `status: open` older than 24 h, or missing header fields.

Required header (common to both existing header styles): status, started, model. Digest check: WARN, never RED.
Hash = check + sorted offending file names with reason kind.
"""
import re
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from _common import REPO, emit, run

REQUIRED = ("status", "started", "model")  # common to both header styles in sessions/
MAX_OPEN = timedelta(hours=24)


def header(text):
    fields = {}
    for line in text.splitlines()[1:40]:
        m = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if m:
            fields.setdefault(m.group(1), m.group(2).strip())
    return fields


def main():
    now = datetime.now(timezone.utc)
    bad = []
    for p in sorted((REPO / "MyTradingSys" / "system" / "sessions").glob("*.md")):
        h = header(p.read_text(encoding="utf-8", errors="replace"))
        missing = [k for k in REQUIRED if not h.get(k)]
        if missing:
            bad.append((p.name, "missing:" + ",".join(missing)))
            continue
        if h["status"].lower() == "open":
            try:
                started = datetime.fromisoformat(h["started"].replace(" ", "T", 1).replace("Z", "+00:00"))
                if started.tzinfo is None:
                    started = started.replace(tzinfo=timezone.utc)
            except ValueError:
                bad.append((p.name, "bad_started"))
                continue
            if now - started > MAX_OPEN:
                bad.append((p.name, "open_over_24h"))
    if bad:
        return emit("sessions", "WARN", f"{len(bad)} session record(s): " + "; ".join(f"{n} {k}" for n, k in bad[:5]),
                    [f"{n}|{k}" for n, k in bad])
    return emit("sessions", "OK", "all session records well-formed, none open >24h", ["ok"])


if __name__ == "__main__":
    run(main)
