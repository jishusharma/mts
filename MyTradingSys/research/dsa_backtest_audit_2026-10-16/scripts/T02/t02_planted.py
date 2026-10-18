"""T02 planted look-ahead: the truncation/poison comparator must FAIL a detector that peeks at bar i+1 and PASS a causal one.
Run from the worktree root:  python MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T02/t02_planted.py
Exit 0 only when the causal detector passes AND each planted detector is caught."""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *([".."] * 5))))
import t02_truncation as T  # noqa: E402


def causal(bars):
    """Event at bar i when close[i] > max(close[i-5:i]) (breakout, known at the close of bar i)."""
    return [{"t": bars[i]["t"], "event": "brk"} for i in range(5, len(bars)) if bars[i]["c"] > max(b["c"] for b in bars[i - 5:i])]


def planted_next_close(bars):
    """PLANTED LEAK 1: the same event but only when the NEXT bar closes higher (uses bars[i+1])."""
    return [{"t": bars[i]["t"], "event": "brk"} for i in range(5, len(bars) - 1)
            if bars[i]["c"] > max(b["c"] for b in bars[i - 5:i]) and bars[i + 1]["c"] > bars[i]["c"]]


def planted_centered(bars):
    """PLANTED LEAK 2: centred 5-bar pivot low stamped at the pivot bar (needs 2 future bars)."""
    return [{"t": bars[i]["t"], "event": "piv"} for i in range(2, len(bars) - 2)
            if all(bars[i]["l"] < bars[j]["l"] for j in (i - 2, i - 1, i + 1, i + 2))]


def verdict(fn, bars, cuts):
    full = T.keyed(fn(bars), 10 ** 15)
    late = repaint = pdiff = 0
    for k in cuts:
        Tk = bars[k]["t"]
        At = T.keyed(fn(bars[:k + 1]), Tk)
        Ft = {x: v for x, v in full.items() if x[0] <= Tk}
        late += len(set(Ft) - set(At))
        repaint += len(set(At) - set(Ft))
        for mode in ("nan", "x10"):
            if T.keyed(fn(bars[:k + 1] + T.poison(bars[k + 1:], mode)), Tk) != At:
                pdiff += 1
    return late, repaint, pdiff


if __name__ == "__main__":
    seed = 20261016
    print("seed", seed)
    bars = T.synth(600, 3600000, seed)
    rnd = random.Random(seed)
    cuts = sorted(set(rnd.randrange(50, 599) for _ in range(60)))
    ok = True
    for name, fn, must_fail in (("causal", causal, False), ("planted_next_close", planted_next_close, True),
                                ("planted_centered", planted_centered, True)):
        late, rep, pd_ = verdict(fn, bars, cuts)
        failed = bool(late or rep or pd_)
        print("%-20s late=%d repaint=%d poison_diff=%d -> %s" % (name, late, rep, pd_, "FAIL(look-ahead)" if failed else "PASS"))
        ok &= (failed == must_fail)
    print("HARNESS SELF-TEST", "OK" if ok else "BROKEN")
    sys.exit(0 if ok else 1)
