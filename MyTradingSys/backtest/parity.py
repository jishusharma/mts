import sys
sys.dont_write_bytecode = True
"""Parity of verdict.py against verdicts the live loop actually logged in
runtime_data/apparatus_log.txt. Run: python MyTradingSys/backtest/parity.py
Expected 2026-09-26: 541/544, 3 known live-side misses (see verdict.py)."""
import json, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from verdict import compute_verdict, proof_dir_of  # noqa: E402
from snapshots import iter_snapshots, ROOT  # noqa: E402

PAT = re.compile(r"^\S+ \S+ \| (\S+) \| ([\d.]+) \| (\S+) \| (\w+) \((.*?)\) \|.*\| pd=(\w+) \|")


def main():
    snaps, stats = iter_snapshots()
    idx = {str(s.get("timestamp_utc", ""))[:19]: s for _, s, _ in snaps}
    tot = match = nosnap = 0
    miss = []
    log = ROOT / "runtime_data" / "apparatus_log.txt"
    for line in open(log, encoding="utf-8", errors="replace"):
        m = PAT.match(line.strip())
        if not m:
            continue
        ts, _price, _state, verdict, _reason, pd = m.groups()
        s = idx.get(ts)
        if s is None:
            nosnap += 1
            continue
        pdp = proof_dir_of(s)
        v = compute_verdict(s, pdp)
        tot += 1
        if v["verdict"] == verdict and pdp == pd:
            match += 1
        else:
            miss.append((ts, "live=" + verdict, "replay=" + v["verdict"], "live_pd=" + pd, "replay_pd=" + pdp))
    print("snapshot load stats:", stats)
    print("log lines matched to a snapshot: %d | no snapshot file: %d" % (tot, nosnap))
    print("PARITY %d / %d" % (match, tot))
    for x in miss:
        print("  MISS", *x)
    return 0 if tot and match >= tot - 3 else 1


if __name__ == "__main__":
    raise SystemExit(main())
