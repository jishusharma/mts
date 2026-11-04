"""Mirror runtime_data/liq_events/*.jsonl to F:/MTS/liq_events (idempotent) and count the flush-before-reversal base rate. Descriptive only.
Event line (BinanceLiquidationAccumulator): {symbol, side, price, qty, eventTime, tradeTime}; SELL = a long was liquidated, BUY = a short.
DECISION (OURS): flush = >= MIN_EVENTS same-side events with gaps <= GAP_MS; reversal = after the flush's last event, the event-stream price
reaches ref*(1 +/- MOVE_PCT) the opposite way within HOLD_MS before it extends MOVE_PCT further the flush way. The ledger price path is the
liq event stream itself (no candle ledger is on the mirror host); a flush with no later event in HOLD_MS counts as unresolved, not reversed.
Usage: python liq_mirror.py [--src runtime_data/liq_events] [--dst F:/MTS/liq_events]
"""
import glob, json, os, sys
from datetime import datetime, timezone

MIN_EVENTS, GAP_MS, HOLD_MS, MOVE_PCT = 3, 5 * 60_000, 60 * 60_000, 0.5  # OURS


def mirror(src, dst):
    """Append only the lines the mirror lacks; returns {symbol: new lines copied}."""
    os.makedirs(dst, exist_ok=True)
    out = {}
    for p in sorted(glob.glob(os.path.join(src, "*.jsonl"))):
        name = os.path.basename(p)
        q = os.path.join(dst, name)
        have = 0
        if os.path.exists(q):
            with open(q, encoding="utf-8") as f:
                have = sum(1 for _ in f)
        with open(p, encoding="utf-8") as f:
            lines = [l for l in f.read().split("\n") if l.strip()]
        new = lines[have:]
        if new:
            with open(q, "a", encoding="utf-8", newline="\n") as f:
                f.write("\n".join(new) + "\n")
        out[name[:-6]] = len(new)
    return out


def load(dst):
    """{file name: [events sorted by eventTime]}; malformed lines are skipped."""
    data = {}
    for p in sorted(glob.glob(os.path.join(dst, "*.jsonl"))):
        evs = []
        with open(p, encoding="utf-8") as f:
            for l in f:
                try:
                    e = json.loads(l)
                    evs.append({"side": e["side"], "price": float(e["price"]), "t": int(e["eventTime"])})
                except (ValueError, KeyError, TypeError):
                    continue
        data[os.path.basename(p)] = sorted(evs, key=lambda e: e["t"])
    return data


def _day(ms):
    return datetime.fromtimestamp(ms / 1000, timezone.utc).strftime("%Y-%m-%d")


def base_rate(data, min_events=MIN_EVENTS, gap_ms=GAP_MS, hold_ms=HOLD_MS, move_pct=MOVE_PCT):
    n = rev = unresolved = 0
    sources = []
    for name, evs in data.items():
        if not evs:
            continue
        sources.append("%s %s..%s" % (name, _day(evs[0]["t"]), _day(evs[-1]["t"])))
        i = 0
        while i < len(evs):
            j = i
            while j + 1 < len(evs) and evs[j + 1]["side"] == evs[i]["side"] and evs[j + 1]["t"] - evs[j]["t"] <= gap_ms:
                j += 1
            if j - i + 1 >= min_events:
                n += 1
                sign = -1 if evs[i]["side"] == "SELL" else 1  # SELL flush pushes price down
                ref, t0 = evs[j]["price"], evs[j]["t"]
                verdict = None
                for e in evs[j + 1:]:
                    if e["t"] - t0 > hold_ms:
                        break
                    mv = (e["price"] / ref - 1) * 100 * sign
                    if mv <= -move_pct:
                        verdict = True
                        break
                    if mv >= move_pct:
                        verdict = False
                        break
                if verdict is None:
                    unresolved += 1
                rev += verdict is True
            i = j + 1
    res = n - unresolved
    return {"n": res, "reversed": rev, "unresolved": unresolved, "rate": (rev / res) if res else None, "sources": sources}


def main():
    a = sys.argv
    src = a[a.index("--src") + 1] if "--src" in a else os.path.join("runtime_data", "liq_events")
    dst = a[a.index("--dst") + 1] if "--dst" in a else "F:/MTS/liq_events"
    print("mirrored:", mirror(src, dst))
    r = base_rate(load(dst))
    print("| n resolved flushes | reversed | unresolved | base rate | sources |\n|---|---|---|---|---|")
    print("| %d | %d | %d | %s | %s |" % (r["n"], r["reversed"], r["unresolved"],
          "n/a" if r["rate"] is None else "%.1f %%" % (100 * r["rate"]), "; ".join(r["sources"]) or "none"))


if __name__ == "__main__":
    main()