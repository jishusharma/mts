"""Placebo for the 77% acceptance claim (card placebo-for-the-77-acceptance-claim-rand).

accept80.py Event A: two consecutive 30m closes below the prior day's VAL (after being inside) -> price trades a further half VA width below VAL later the same
UTC day (77%, n = 300). Is that 77% special to the acceptance label, or does any day/time touch the same distance below its own close?

Placebo: per real event keep the 30m segment index k and the distance d the real test needed, `d = close_k - (VAL - w/2)`; draw a random UTC day that is not an
Event-A day and test `rest-of-day low <= close_k(that day) - d`. 2000 draws of 300 events, seed 7. Sensitivity row: exact-width variant, d = w/2 from the close.
Descriptive only: no fee, no trade rule, no return.

    python placebo80.py          # needs F:/MTS/data/orderflow_1m (desktop only); writes PLACEBO.md
"""
import datetime as dt
import importlib.util
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
N_DRAWS, SEED, KMAX = 2000, 7, 48


def _acc():
    spec = importlib.util.spec_from_file_location("accept80_for_placebo", HERE / "accept80.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def drop_matrix(days, kmax=KMAX, m30=None):
    """drop[i, k] for the i-th day (sorted by date) and 30m segment k: close of segment k minus the lowest low of the bars AFTER segment k (>= 0 means price fell
    that far below the close at some point). NaN: the day has no segment k. -inf: segment k exists but nothing follows (no later bar, never a hit)."""
    if m30 is None:
        m30 = _acc().m30
    out = np.full((len(days), kmax), np.nan)
    for i, d in enumerate(sorted(days)):
        segs = m30(days[d])
        flat_low = [min(b[3] for b in s) for s in segs]
        for k in range(min(kmax, len(segs))):
            later = flat_low[k + 1:]
            out[i, k] = (segs[k][-1][4] - min(later)) if later else -np.inf
    return out


def placebo_draws(drop, ks, ds, excluded, n_draws=N_DRAWS, seed=SEED):
    """Hit rate of n_draws placebo draws: each event keeps its segment index k and distance d and takes a uniformly random eligible day (segment k exists, not excluded)."""
    rng = np.random.default_rng(seed)
    ks, ds = np.asarray(ks, int), np.asarray(ds, float)
    ok = ~np.isnan(drop)
    ok[list(excluded), :] = False
    cand = {int(k): np.flatnonzero(ok[:, k]) for k in set(ks.tolist())}
    for k, c in cand.items():
        if len(c) == 0:
            raise ValueError("no eligible placebo day for segment %d" % k)
    rates = np.empty(n_draws)
    for r in range(n_draws):
        hit = 0
        for k, d in zip(ks, ds):
            c = cand[int(k)]
            hit += drop[c[rng.integers(len(c))], k] >= d
        rates[r] = hit / len(ks)
    return rates


def events_a(days):
    """Event A of accept80.study(), with the segment index and the two distances kept. -> list of dicts (day index, k, d_needed, w/2, real hit)."""
    acc = _acc()
    keys = sorted(days)
    ev = []
    for pi, (p, d) in enumerate(zip(keys, keys[1:])):
        if (dt.date.fromisoformat(d) - dt.date.fromisoformat(p)).days != 1:
            continue
        v = acc.va(days[p])
        if not v:
            continue
        val, poc, vah = v
        w = vah - val
        if w <= 0:
            continue
        segs = acc.m30(days[d])
        below_run, was_inside = 0, False
        for k, s in enumerate(segs):
            c = s[-1][4]
            if val <= c <= vah:
                was_inside = True
            if was_inside and c < val:
                below_run += 1
                if below_run == 2:
                    rest = [b for seg in segs[k + 1:] for b in seg]
                    ev.append({"day": pi + 1, "k": k, "d": c - (val - w / 2), "half": w / 2,
                               "hit": any(b[3] <= val - w / 2 for b in rest),
                               "hit_exact": any(b[3] <= c - w / 2 for b in rest)})
                    break
            else:
                below_run = 0
    return ev


def main():
    acc = _acc()
    days = acc.days_local()
    keys = sorted(days)
    ev = events_a(days)
    n = len(ev)
    k_hit = sum(e["hit"] for e in ev)
    lo, hi = acc.wilson(k_hit, n)
    drop = drop_matrix(days)
    ks = [min(e["k"], KMAX - 1) for e in ev]
    excl = sorted({e["day"] for e in ev})
    rows = []
    for name, ds, real in (("needed distance d = close_k - (VAL - w/2)", [e["d"] for e in ev], k_hit / n),
                           ("exact width d = w/2 from the close", [e["half"] for e in ev], sum(e["hit_exact"] for e in ev) / n)):
        r = placebo_draws(drop, ks, ds, excl)
        rows.append((name, real, float(r.mean()), float(np.percentile(r, 2.5)), float(np.percentile(r, 97.5))))
    lift = rows[0][1] - rows[0][2]
    verdict = ("the label adds %.1f points over the placebo (>= 10: YES)" % (100 * lift)) if lift >= 0.10 else \
        ("the label adds %.1f points over the placebo (>= 10: NO), so most of the 77%% is plain same-day volatility" % (100 * lift))
    L = ["# PLACEBO: how much of the 77% acceptance claim is just same-day volatility?", "",
         "Regime mix: NOT_IN_DATA (descriptive study, no regime spec frozen; %d days %s..%s of Binance spot 1m, F:/MTS/data/orderflow_1m)" % (len(days), keys[0], keys[-1]), "",
         "**Verdict: real Event A = %.0f%% [%.0f..%.0f] (n = %d); random day, same segment and distance = %.0f%% (95%% of draws %.0f..%.0f); %s.**" % (
             100 * k_hit / n, 100 * lo, 100 * hi, n, 100 * rows[0][2], 100 * rows[0][3], 100 * rows[0][4], verdict), "",
         "Method: `placebo80.py` imports `accept80.py` (days, va, m30). Each real Event A (two consecutive 30m closes below the prior day's VAL) keeps its 30m segment index k and the distance d it needed below its own close; "
         "a placebo draw gives every event a random UTC day that is not an Event-A day and asks whether the rest-of-day low reaches close_k - d. %d draws of %d events, seed %d. Descriptive: no fee, no trade rule, no return." % (N_DRAWS, n, SEED), "",
         "| variant | real hit rate | placebo mean | placebo 2.5% | placebo 97.5% | real - placebo |", "|---|---|---|---|---|---|"]
    for name, real, m, a, b in rows:
        L.append("| %s | %.1f%% | %.1f%% | %.1f%% | %.1f%% | %+.1f pts |" % (name, 100 * real, 100 * m, 100 * a, 100 * b, 100 * (real - m)))
    L += ["", "Excluded placebo days: the %d distinct Event-A days; eligible days per segment = days with that 30m segment, minus those." % len(excl),
          "Context: this is a continuation-probability check on one label, not an edge: nothing here is traded, so no fee-net result exists. Test: `test_placebo80.py` (synthetic drift and flat series, seed determinism)."]
    (HERE / "PLACEBO.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(L))


if __name__ == "__main__":
    sys.exit(main())
