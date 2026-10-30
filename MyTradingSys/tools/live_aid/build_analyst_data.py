"""Write analyst_data.js for live_aid.html: every analyst in the CBP roster (analysts.json) with its newest CBP row,
rows the gates rejected, when ingestion last ran, and the BTC price levels from scripts/dev/analyst_levels.py.

live_aid.html is opened from disk, so the data comes in as a script file (browsers block fetch() of local files).
CBP rows live outside the public repo: analyst_data.js is gitignored and rebuilt on each run.
Rebuild after CBP ingestion or before a chart read:
  python MyTradingSys/tools/live_aid/build_analyst_data.py            # with live price + hit/open per level
  python MyTradingSys/tools/live_aid/build_analyst_data.py --offline  # no network
"""
import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in (ROOT / "MyTradingSys", ROOT / "scripts" / "dev"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import cbp  # noqa: E402
import analyst_levels as al  # noqa: E402

OUT = HERE / "analyst_data.js"
VAR = "LIVE_AID_ANALYSTS"


def read_json(p, default):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def build(store=None, roster_file=None, stamp_file=None, days=10, offline=False, now=None):
    """The data block for the page. Every roster analyst is listed, ingested or not; an analyst that has rows
    but is missing from the roster is added with in_roster false, so nobody drops out of view."""
    now = now or datetime.now(timezone.utc)
    home = cbp.default_cbp_home()
    cfg = read_json(roster_file or home / "cbp_v2" / "analysts.json", {})
    data = cbp.load(store)
    rows = [r for r in data["rows"] if not cbp.validate_row(r)]
    roster = [dict(short=a.get("short", ""), channel=a.get("channel", ""), tier=a.get("tier", ""), pillar=a.get("pillar", ""),
                   enabled=bool(a.get("enabled")), ingested=bool(a.get("enabled")) and a.get("profile") == "actionable", in_roster=True)
              for a in cfg.get("analysts", [])]
    names = {a["short"] for a in roster}
    for r in rows:
        if r["analyst"] not in names:
            names.add(r["analyst"])
            roster.append(dict(short=r["analyst"], channel="", tier="", pillar="", enabled=True, ingested=True, in_roster=False))
    cutoff = (now - timedelta(days=days)).date().isoformat()
    lv = al.ladder([r for r in rows if r["published"] >= cutoff])
    price = None
    if lv and not offline:
        try:
            since = min(datetime.fromisoformat(x["published"]) for x in lv).replace(tzinfo=timezone.utc)
            price = al.mark(lv, al.spot_1h(since), now)
        except Exception:  # network down: levels still shown, distances come from the live page
            price = None
    for x in lv:
        x.setdefault("hit", None)
        x["expired"] = bool(x["expires_at"]) and cbp.parse_expiry(x["expires_at"]) <= now
    stamp = read_json(stamp_file or home / "cbp_store" / "stamp.json", {})
    return dict(asof=now.isoformat(timespec="seconds"), window_days=cbp.WINDOW_DAYS, last_ingest=stamp.get("last_run", ""),
                price=price, roster=roster,
                rows=[dict(analyst=r["analyst"], published=r["published"], bias=r.get("bias", ""), video_id=r.get("video_id", "")) for r in rows],
                rejected=[dict(analyst=x[1], video_id=x[0], why=str(x[2])[:160]) for x in data["rejected"] if len(x) >= 3],
                levels=lv)


def write(block, out=OUT):
    out.write_text("window." + VAR + " = " + json.dumps(block, indent=1) + ";\n", encoding="utf-8", newline="\n")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--days", type=int, default=10)
    ap.add_argument("--store")
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args(argv)
    b = build(a.store, days=a.days, offline=a.offline)
    write(b, Path(a.out))
    print("analyst_data.js: %d analysts, %d rows, %d rejected, %d levels -> %s" % (len(b["roster"]), len(b["rows"]), len(b["rejected"]), len(b["levels"]), a.out))


if __name__ == "__main__":
    main()
