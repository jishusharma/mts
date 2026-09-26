import sys
sys.dont_write_bytecode = True
"""Replays every archived snapshot through verdict.py and writes one row per
snapshot to Dumps/backtest/replay_rows.json (gitignored via Dumps/).
Run: python MyTradingSys/backtest/replay.py   (about 2-3 minutes)"""
import json
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from verdict import compute_verdict, proof_dir_of  # noqa: E402
from snapshots import iter_snapshots, OUT_DIR  # noqa: E402


def main():
    snaps, stats = iter_snapshots()
    rows = []
    for p, s, t in snaps:
        pd = proof_dir_of(s)
        v = compute_verdict(s, pd)
        top = v["top"] or {}
        m = top.get("math") or {}
        rows.append(dict(t=t, ts=str(s["timestamp_utc"])[:19], price=float(s["current_price"]),
                         verdict=v["verdict"], setup=top.get("setup_type"), dir=v["direction"],
                         zone=(top.get("zone") or {}).get("name"), zone_price=(top.get("zone") or {}).get("price"),
                         stop=m.get("stop"), target=m.get("target"), gross=m.get("gross_rr"),
                         net=m.get("net_rr"), proof=v.get("proof"), mode=v["mode"], pd=pd, file=p.name))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "replay_rows.json"
    json.dump(rows, open(out, "w", encoding="utf-8"))
    print("load stats:", stats)
    print("replayed %d snapshots %s -> %s" % (len(rows), rows[0]["ts"], rows[-1]["ts"]))
    c = Counter(r["verdict"] for r in rows)
    for k, n in c.most_common():
        print("  %-14s %5d  %5.1f%%" % (k, n, 100.0 * n / len(rows)))
    cov = sum(rows[i + 1]["t"] - rows[i]["t"] for i in range(len(rows) - 1) if rows[i + 1]["t"] - rows[i]["t"] <= 180) / 3600
    print("covered hours (gaps > 3 min excluded): %.1f" % cov)
    print("wrote", out)


if __name__ == "__main__":
    main()
