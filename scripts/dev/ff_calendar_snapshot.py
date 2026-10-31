"""Save the ForexFactory weekly calendar next to live_aid.html so the page reads it same-origin.

The feed (nfs.faireconomy.media) sends no CORS header, so a browser page cannot fetch it. This script fetches it
(public market data) and writes MyTradingSys/tools/live_aid/ff_calendar_snapshot.js:
    window.LIVEAID_CAL_SNAP = {"fetched_ms": <epoch ms>, "events": [...]};
A .js file (not .json) so it also loads over file://. The page treats a copy older than 26 h as NO CALENDAR.
Run by hand or from a station loop: python scripts/dev/ff_calendar_snapshot.py
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
OUT = Path(__file__).resolve().parents[2] / "MyTradingSys" / "tools" / "live_aid" / "ff_calendar_snapshot.js"


def render(events, fetched_ms):
    if not isinstance(events, list) or not events:
        raise ValueError("calendar feed is not a non-empty list")
    return "window.LIVEAID_CAL_SNAP = " + json.dumps({"fetched_ms": int(fetched_ms), "events": events}, separators=(",", ":")) + ";\n"


def fetch():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (mts live_aid snapshot)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def main(out=OUT):
    try:
        events = fetch()
        text = render(events, time.time() * 1000)
    except Exception as ex:  # keep the old file: the page ages it out itself after 26 h
        print("ff_calendar_snapshot: FAILED, old file kept: %s" % ex, file=sys.stderr)
        return 1
    Path(out).write_text(text, encoding="utf-8", newline="\n")
    print("ff_calendar_snapshot: %d events -> %s" % (len(events), out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
