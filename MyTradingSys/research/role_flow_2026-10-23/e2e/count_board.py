"""Independent count of stale raw cards from the JSON files (own code, not tasks.py). usage: count_board.py <tasks dir>"""
import json, sys
from datetime import datetime, timezone
from pathlib import Path
now = datetime.now(timezone.utc)
n_raw = stale = parked = fresh = 0
for f in Path(sys.argv[1]).glob("*.json"):
    c = json.loads(f.read_text(encoding="utf-8"))
    if c.get("state") != "raw":
        continue
    n_raw += 1
    if c.get("asks") or int(c.get("refine_tries") or 0) >= 2:
        parked += 1; continue
    s = str(c.get("created") or "")
    try:
        t = datetime.fromisoformat(s.replace("Z", "+00:00")); t = t if t.tzinfo else t.replace(tzinfo=timezone.utc)
        age = (now - t).total_seconds()
    except ValueError:
        age = None
    if age is None or age > 3600: stale += 1
    else: fresh += 1
print(f"INDEPENDENT raw={n_raw} stale={stale} fresh={fresh} parked={parked} at={now:%Y-%m-%dT%H:%MZ}")
