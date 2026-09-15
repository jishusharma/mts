# State-code emitter prototype - reads stored snapshots
# Purpose: validate 5 v1 signals + transition table before Java build
import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path

SNAP_DIR = Path(__file__).resolve().parents[3] / "data" / "snapshots"


def load():
    files = sorted(SNAP_DIR.glob("BTCUSDT*.json"))
    out = []
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                d = json.load(fh)
            d["_file"] = f.name
            out.append(d)
        except Exception as e:
            print(f"SKIP {f.name}: {e}")
    out.sort(key=lambda s: s.get("timestamp_utc", ""))
    return out


def s_net_delta(s):
    v = (s.get("trade_flow") or {}).get("net_delta_1m")
    if v is None: return None
    return "bearish" if v < 0 else ("bullish" if v > 0 else "neutral")


def s_last3(s):
    v = (s.get("cvd") or {}).get("last_3_delta")
    if not isinstance(v, list) or len(v) != 3: return None
    if all(x == "negative" for x in v): return "bearish"
    if all(x == "positive" for x in v): return "bullish"
    return "neutral"


def s_vol_ratio(s):
    v = (s.get("order_flow") or {}).get("volume_ratio")
    if v is None: return None
    if v <= 2.0: return "neutral"
    nd = (s.get("trade_flow") or {}).get("net_delta_1m")
    if nd is None: return "neutral"
    return "bearish" if nd < 0 else ("bullish" if nd > 0 else "neutral")


def s_cvd_slope(s):
    v = (s.get("cvd") or {}).get("slope")
    if not v: return None
    if v == "falling": return "bearish"
    if v == "rising": return "bullish"
    if v == "flat": return "neutral"
    return None


def s_price_vs_vwap(s):
    p = s.get("current_price")
    w = (s.get("vwap") or {}).get("price")
    if p is None or w is None or w == 0: return None
    d = (p - w) / w * 100.0
    if abs(d) <= 0.05: return "neutral"
    return "bullish" if d > 0 else "bearish"


SIGS = [
    ("net_delta_1m", s_net_delta),
    ("last_3_delta", s_last3),
    ("volume_ratio", s_vol_ratio),
    ("cvd_slope", s_cvd_slope),
    ("price_vs_vwap", s_price_vs_vwap),
]


def evaluate(s):
    out = {}
    for name, fn in SIGS:
        try:
            out[name] = fn(s)
        except Exception:
            out[name] = None
    b = sum(1 for v in out.values() if v == "bearish")
    bl = sum(1 for v in out.values() if v == "bullish")
    av = sum(1 for v in out.values() if v is not None)
    return out, b, bl, av


def next_target(state, b, bl):
    if state == "A":
        if b >= 2 and bl <= 1: return "A>S"
        if bl >= 2 and b <= 1: return "A>L"
    elif state == "A>S":
        if b >= 3: return "S"
    elif state == "A>L":
        if bl >= 3: return "L"
    elif state == "S":
        if bl >= 3: return "S>L"
    elif state == "L":
        if b >= 3: return "L>S"
    elif state == "S>L":
        if bl >= 3: return "L"
        if b >= 3: return "S"
    elif state == "L>S":
        if b >= 3: return "S"
        if bl >= 3: return "L"
    return state


def run(snaps):
    state = "A"
    pending = None
    pc = 0
    quiet = 0
    rows = []
    trans = []
    raw = 0

    for s in snaps:
        ts = s.get("timestamp_utc", "?")
        sig, b, bl, av = evaluate(s)
        tgt = next_target(state, b, bl)

        if tgt != state:
            raw += 1
            if pending == tgt:
                pc += 1
            else:
                pending = tgt
                pc = 1
            if pc >= 2:
                trans.append((ts, state, tgt, b, bl, av, s["_file"], "target"))
                state = tgt
                pending = None
                pc = 0
                quiet = 0
        else:
            pending = None
            pc = 0

        if b < 3 and bl < 3:
            quiet += 1
        else:
            quiet = 0

        if quiet >= 2 and state in ("A>S", "A>L", "S", "L"):
            trans.append((ts, state, "A", b, bl, av, s["_file"], "quiet-decay"))
            state = "A"
            quiet = 0
            pending = None
            pc = 0

        rows.append({"ts": ts, "file": s["_file"], "b": b, "bl": bl,
                     "av": av, "state": state, "sig": sig})
    return rows, trans, raw


def main():
    snaps = load()
    print(f"Loaded {len(snaps)} BTCUSDT snapshots")
    print()
    if not snaps:
        return
    rows, trans, raw = run(snaps)

    print("=== PER-SNAPSHOT ===")
    hdr = f"{'file':<48} {'av':>3} {'B':>3} {'Bl':>3}  {'state':<5}  signals"
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        sigstr = " ".join(f"{k}={v or 'NA'}" for k, v in r["sig"].items())
        print(f"{r['file']:<48} {r['av']:>3} {r['b']:>3} {r['bl']:>3}  {r['state']:<5}  {sigstr}")

    print()
    print("=== AVAILABILITY TALLY ===")
    n = len(rows)
    for name, _ in SIGS:
        ok = sum(1 for r in rows if r["sig"][name] is not None)
        print(f"  {name:<20} {ok}/{n} ({100*ok//n}%)")
    for thresh in (3, 4, 5):
        c = sum(1 for r in rows if r["av"] >= thresh)
        print(f"  snapshots with >={thresh} signals: {c}/{n}")

    print()
    print("=== TRANSITIONS ===")
    print(f"  raw condition hits: {raw}")
    print(f"  fired transitions:  {len(trans)}")
    for ts, fr, to, b, bl, av, f, why in trans:
        print(f"  {ts}  {fr} -> {to}  B={b} Bl={bl} av={av}  [{why}]  {f}")
    if not trans:
        print("  (none fired)")


if __name__ == "__main__":
    main()
