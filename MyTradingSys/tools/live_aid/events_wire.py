"""Build the Upcoming-events strip data (card cbp-events-to-watch-wire-1108).

  python MyTradingSys/tools/live_aid/events_wire.py [--asof YYYY-MM-DD]

Writes research/cbp/events_to_watch.json (analyst-named events, public analyst context, no account data) from
research/news_effects_2026-11/analyst_events.md, and events_strip_data.js (schedule + last same-class move + analyst counts)
for the live aid page. Context only: nothing here gates or sizes anything.
Re-extraction from F:/CryptoScrapper (extract_prompt.md events_to_watch) is outside this repo; this reads the existing extractions.
"""
import argparse
import csv
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent.parent / "research"
NEWS = RESEARCH / "news_effects_2026-11"
OUT_JSON = RESEARCH / "cbp" / "events_to_watch.json"
OUT_JS = HERE / "events_strip_data.js"
ET = ZoneInfo("America/New_York")
MIN = 60_000
DIRS = {"up": "L", "down": "S", "none": "H"}
# BLS prints delayed by the 2025 shutdown (research/news_effects_2026-11/news_events.csv ts notes)
STALE_IDS = {"cpi-2025-10-24", "nfp-2025-11-20", "ppi-2025-11-25"}
CSV_CLASS = {"MACRO_CPI": "CPI", "MACRO_NFP": "NFP", "MACRO_PPI": "PPI", "FOMC": "FOMC"}


def export_events(md: str) -> dict:
    """Analyst-named events, one per event id (= event + date), with analyst count and LONG/SHORT/HOLD split."""
    seen = {}
    for blk in re.split(r"(?m)^### ", md)[1:]:
        head, _, rest = blk.partition("\n")
        f = {k: v.strip() for k, v in re.findall(r"(?m)^(event|expected_btc_dir|timing|evidence): ?(.*)$", rest)}
        if "event" not in f:
            continue
        analyst = head.split("|")[0].strip()
        quote = f.get("evidence", "").strip().strip('"')
        e = seen.setdefault(f["event"], {"event": f["event"], "quote": quote, "per": {}})
        dirs = e["per"].setdefault(analyst, set())
        if f.get("timing") == "before":
            dirs.add(DIRS.get(f.get("expected_btc_dir"), "H"))
    events = []
    for e in seen.values():
        c = {"L": 0, "S": 0, "H": 0}
        for dirs in e["per"].values():       # one vote per analyst; split LONG and SHORT = HOLD
            d = dirs - {"H"}
            c["H" if len(d) != 1 else next(iter(d))] += 1
        m = re.search(r"(\d{4})-?(\d\d)-?(\d\d)$", e["event"])
        events.append({"event": e["event"], "date": "-".join(m.groups()) if m else "", "analysts": len(e["per"]),
                       "long": c["L"], "short": c["S"], "hold": c["H"], "quote": e["quote"][:240]})
    events.sort(key=lambda x: (x["date"], x["event"]))
    return {"note": "Analyst context only (CBP transcripts); never a signal. long/short/hold = one vote per analyst, split = hold.",
            "events": events}


def _ms(day: str, hh: int, mm: int) -> int:
    y, mo, d = map(int, day.split("-"))
    return int(datetime(y, mo, d, hh, mm, tzinfo=ET).astimezone(timezone.utc).timestamp() * 1000)


def schedule(cal: dict, asof: str, days: int = 400) -> list:
    """Release rows from the BLS and Fed schedule (08:30 ET prints, FOMC statement 14:00 ET, presser +30 min)."""
    end = (date.fromisoformat(asof) + timedelta(days=days)).isoformat()
    cor = cal.get("corrections", {})
    rows = []
    for cls in ("CPI", "NFP", "PPI"):
        tbl = {k: v for k, v in cal["bls"].get(cls, {}).items() if not (cls == "PPI" and k in cor.get("drop", []))}
        if cls == "PPI":
            tbl.update(cor.get("set", {}))
        for day, tm in tbl.values():
            if asof <= day <= end:
                hh, mm = map(int, re.match(r"(\d+):(\d+)", tm).groups())
                hh = hh % 12 + (12 if "PM" in tm.upper() else 0)
                rows.append({"id": "%s-%s" % (cls.lower(), day), "cls": cls, "t0": _ms(day, hh, mm), "stale": False})
    for day in cal.get("fomc", []):
        if asof <= day <= end:
            t0 = _ms(day, 14, 0)
            rows.append({"id": "fomc-" + day, "cls": "FOMC", "t0": t0, "stale": False})
            rows.append({"id": "fomc-pc-" + day, "cls": "FOMC_PRESSER", "t0": t0 + 30 * MIN, "stale": False})
    rows.sort(key=lambda r: (r["t0"], r["id"]))
    return rows


def last_moves(csv_path: Path) -> dict:
    """Latest verified same-class row: date, r15, z15d, vr5 (BTC) from news_events.csv."""
    out = {}
    with open(csv_path, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            cls = CSV_CLASS.get(r["class"])
            if not cls or r["verified"] != "Y" or not r["btc_z15d"]:
                continue
            if cls not in out or r["t0_utc"] > out[cls]["t0"]:
                out[cls] = {"t0": r["t0_utc"], "date": r["t0_utc"][:10], "r15": float(r["btc_r15"]),
                            "z15d": float(r["btc_z15d"]), "vr5": float(r["btc_vr5"])}
    for v in out.values():
        del v["t0"]
    return out


def strip_data(asof: str) -> dict:
    cal = json.loads((NEWS / "calendar_cache.json").read_text(encoding="utf-8"))
    ev = json.loads(OUT_JSON.read_text(encoding="utf-8"))["events"]
    sch = schedule(cal, asof)
    for r in sch:
        r["stale"] = r["id"] in STALE_IDS
    ids = {r["id"] for r in sch}
    analysts = {e["event"]: {"n": e["analysts"], "L": e["long"], "S": e["short"], "H": e["hold"]} for e in ev}
    named = []  # analyst-named events that are not on the schedule and still ahead: shown by day (no time known)
    for e in ev:
        if e["event"] not in ids and e["date"] >= asof and not re.match(r"(cpi|nfp|ppi|fomc)-", e["event"]):
            named.append({"id": e["event"], "label": e["event"], "weekOf": _ms(e["date"], 0, 0)})
    return {"schedule": sch, "last": last_moves(NEWS / "news_events.csv"), "analysts": analysts, "named": named}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--asof", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    a = ap.parse_args(argv)
    md = (NEWS / "analyst_events.md").read_text(encoding="utf-8")
    OUT_JSON.write_text(json.dumps(export_events(md), indent=1) + "\n", encoding="utf-8", newline="\n")
    d = strip_data(a.asof)
    OUT_JS.write_text("// generated by events_wire.py; do not edit\nwindow.EVENTS_STRIP_DATA = " + json.dumps(d, separators=(",", ":")) + ";\n",
                      encoding="utf-8", newline="\n")
    print(OUT_JSON, len(json.loads(OUT_JSON.read_text(encoding="utf-8"))["events"]), "analyst events;", len(d["schedule"]), "schedule rows")


if __name__ == "__main__":
    sys.exit(main())
