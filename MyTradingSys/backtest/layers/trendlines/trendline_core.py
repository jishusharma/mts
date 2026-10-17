"""
MyTradingSys/backtest/layers/trendlines/trendline_core.py - causal, versioned trend-line detector.

Implements research/trendlines_2026-10-17/TRENDLINE_CONTRACT.md (v1); formulas: layers/FORMULAS.md section 19.
Bars are dicts {t,o,h,l,c,v} of CLOSED bars on one timeframe (aggregate 1m with
layers/timeframe/tf_resample.resample; see `resample_closed`).

Causality: `TrendlineDetector.update(bar)` is the only way state advances, one closed bar at a time, so
nothing right of the current bar can be read. State is append-only: events are never edited or removed.
Every event carries `bar` (index of the bar that caused it) and `known_at` (index of the bar close at which
a live system could first have written it; a line proposed at availability of pivot b replays bars ib+1..t,
so those events have bar < known_at).

Why not reuse existing pivot code (read first): `cryptocred/cc_structure.find_swings` is a batch scan
(needs the full series, no incremental/truncation form), has no close-series arm, drops a bar that is both
swing high and low (`elif`) and logs no tie rejects; `bigtrade/bigmoves.zigzag_pivots` is an ATR-leg zigzag
(different anchor definition; contract P1/P2/P4 need k-bar fractals with strict ties). Bar aggregation is
reused, not rewritten.

Parameters: k=3, spacing 10..200, age cap 500, tolerances 0.10/0.25/1.0 x ATR_b, ATR 14 are OURS (contract).
"""
import json
import math
from pathlib import Path

CONTRACT_VERSION = "trendline_contract_v1"
ATR_LEN = 14
VOL_LEN = 20
PEN_TOL = 0.10      # L6 / E7 poke
TOUCH_TOL = 0.25    # E5, L7, E3, B6
RESET_DIST = 1.0    # E6
RETEST_WINDOW = 20  # B6


def resample_closed(bars_1m, tf):
    """Closed-bar aggregation via the shared resampler (contract F6)."""
    from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
    reg = json.loads((Path(__file__).resolve().parent.parent / "timeframe" / "registry.json").read_text())
    return resample(bars_1m, tf, reg)


def true_range(bars, i):
    """Wilder TR, defined for i >= 1 (FORMULAS section 12)."""
    pc = bars[i - 1]["c"]
    return max(bars[i]["h"] - bars[i]["l"], abs(bars[i]["h"] - pc), abs(bars[i]["l"] - pc))


def atr_sma(bars, i, n=ATR_LEN):
    """Plain SMA of TR over bars i-n+1..i; None until n TRs exist (first at i = n)."""
    if i < n:
        return None
    return sum(true_range(bars, j) for j in range(i - n + 1, i + 1)) / n


def line_price(transform, ia, pa, ib, pb, t):
    """FORMULAS 19.2. Line through (ia,pa),(ib,pb) evaluated at bar index t."""
    f = (t - ia) / (ib - ia)
    if transform == "linear":
        return pa + (pb - pa) * f
    return math.exp(math.log(pa) + (math.log(pb) - math.log(pa)) * f)


def _close_loc(bar):
    r = bar["h"] - bar["l"]
    return (bar["c"] - bar["l"]) / r if r else None


def _body_range(bar):
    r = bar["h"] - bar["l"]
    return abs(bar["c"] - bar["o"]) / r if r else None


class TrendlineDetector:
    """One instance = one (timeframe, price arm, transform) family. Eligibility arms A, B, V are tracked
    per line (events carry `arm`); max_age=None is the no-cap arm."""

    def __init__(self, tf="1h", k=3, transform="log", price_arm="wick", max_age=500,
                 min_spacing=10, max_spacing=200):
        if transform not in ("log", "linear"):
            raise ValueError("transform must be log or linear")
        if price_arm not in ("wick", "close"):
            raise ValueError("price_arm must be wick or close")
        if k < 1:
            raise ValueError("k must be >= 1")
        self.tf, self.k, self.transform, self.price_arm = tf, k, transform, price_arm
        self.max_age, self.min_spacing, self.max_spacing = max_age, min_spacing, max_spacing
        self.bars = []
        self.atr = []
        self.pivots = []    # {side,i,price,available_at}
        self.lines = {}     # id -> line record
        self.events = []    # append-only
        self.rejects = []   # append-only: tie, flat, penetration, spacing

    # ---- helpers
    def _ev(self, line, state, bar, **kw):
        e = {"line": line["id"], "state": state, "bar": bar, "known_at": len(self.bars) - 1}
        e.update(kw)
        self.events.append(e)

    def _rej(self, why, **kw):
        r = {"reject": why, "known_at": len(self.bars) - 1}
        r.update(kw)
        self.rejects.append(r)

    def _px(self, side, i):
        b = self.bars[i]
        if self.price_arm == "close":
            return b["c"]
        return b["l"] if side == "support" else b["h"]

    def _L(self, ln, j):
        return line_price(self.transform, ln["ia"], ln["pa"], ln["ib"], ln["pb"], j)

    # ---- one closed bar
    def update(self, bar):
        self.bars.append(bar)
        t = len(self.bars) - 1
        self.atr.append(atr_sma(self.bars, t))
        new_pivots = self._confirm_pivots(t)
        for ln in list(self.lines.values()):   # lines born below replay from ib+1 themselves
            self._advance(ln, t)
        for p in new_pivots:
            self._third_anchor(p, t)
        for p in new_pivots:
            self._pair(p, t)
        return t

    def feed(self, bars):
        for b in bars:
            self.update(b)
        return self

    # ---- pivots (P1-P6, FORMULAS 19.1)
    def _confirm_pivots(self, t):
        k = self.k
        i = t - k
        if i < k:
            return []
        out = []
        for side in ("support", "resistance"):
            x = self._px(side, i)
            sgn = 1 if side == "support" else -1   # support: candidate strictly below all 2k neighbours
            strict, equal = True, False
            for j in list(range(i - k, i)) + list(range(i + 1, i + k + 1)):
                y = self._px(side, j)
                if sgn * (y - x) < 0:
                    strict = equal = False
                    break
                if y == x:
                    strict, equal = False, True
            if strict:
                p = {"side": side, "i": i, "price": x, "available_at": t}
                self.pivots.append(p)
                out.append(p)
            elif equal:
                self._rej("tie", side=side, i=i)
        return out

    # ---- candidate lines (L1-L11)
    def _pair(self, b, t):
        side, ib, pb = b["side"], b["i"], b["price"]
        atr_b = self.atr[ib]
        if atr_b is None:   # P9: no line before bar 15 (ATR needs 14 TRs)
            return
        for a in [p for p in self.pivots if p["side"] == side and p["i"] < ib]:
            ia, pa = a["i"], a["price"]
            rising = pb > pa if side == "support" else pb < pa
            if abs(pb - pa) <= TOUCH_TOL * atr_b:
                self._rej("flat", side=side, ia=ia, ib=ib)    # L7: horizontal-control family
                continue
            if not rising:
                continue
            sp = ib - ia
            if sp < self.min_spacing or sp > self.max_spacing:
                self._rej("spacing", side=side, ia=ia, ib=ib)
                continue
            if self._broken_anchor(side, ia):
                continue   # E11
            lid = "|".join((self.tf, side, self.price_arm, self.transform, str(ia), str(ib)))
            if lid in self.lines:
                continue
            ln = {"id": lid, "side": side, "ia": ia, "ib": ib, "pa": pa, "pb": pb,
                  "transform": self.transform, "price_arm": self.price_arm, "version": 1,
                  "atr_b": atr_b, "available_at": t,
                  "slope_atr": (pb - pa) / sp / atr_b,
                  "slope_log": (math.log(pb) - math.log(pa)) / sp if pa > 0 and pb > 0 else None,
                  "state": "proposed", "episodes": 0, "open_episode": False, "eligible": set(),
                  "broken_at": None, "retest_done": False, "reclaim_done": False, "retired": False,
                  "thirds": []}
            if not self._penetration_ok(ln):
                self._rej("penetration", side=side, ia=ia, ib=ib)
                continue
            self.lines[lid] = ln
            self._ev(ln, "proposed", t, ia=ia, ib=ib, slope_atr=ln["slope_atr"], slope_log=ln["slope_log"],
                     atr_b=atr_b, line_tf=self.tf, price_arm=self.price_arm, transform=self.transform)
            if self._volume_ok(ia) and self._volume_ok(ib):
                ln["eligible"].add("V")
                self._ev(ln, "eligible", t, arm="V")
            for j in range(ib + 1, t + 1):   # replay bars already closed at availability of b
                self._advance(ln, j)

    def _broken_anchor(self, side, ia):
        return any(ln["side"] == side and ln["broken_at"] is not None and ia in (ln["ia"], ln["ib"])
                   for ln in self.lines.values())

    def _penetration_ok(self, ln):
        """L6: strict external test over anchor bars ia..ib only."""
        tol = PEN_TOL * ln["atr_b"]
        for j in range(ln["ia"], ln["ib"] + 1):
            L = self._L(ln, j)
            bar = self.bars[j]
            if ln["side"] == "support":
                if bar["l"] < L - tol or bar["c"] < L:
                    return False
            elif bar["h"] > L + tol or bar["c"] > L:
                return False
        return True

    def _volume_ok(self, i):
        """E4: volume >= 2.0 x mean of the 20 bars BEFORE the anchor bar."""
        if i < VOL_LEN:
            return False
        m = sum(self.bars[j].get("v", 0) for j in range(i - VOL_LEN, i)) / VOL_LEN
        return m > 0 and self.bars[i].get("v", 0) >= 2.0 * m

    # ---- state machine per line and bar (E5-E10, B1-B8)
    def _advance(self, ln, j):
        if j <= ln["ib"] or ln["retired"]:
            return
        if ln["broken_at"] is None and self.max_age is not None and j - ln["ib"] > self.max_age:
            ln["retired"] = True
            self._ev(ln, "retired", j)
            return
        bar = self.bars[j]
        L = self._L(ln, j)
        atr_b = ln["atr_b"]
        sup = ln["side"] == "support"
        if ln["broken_at"] is not None:
            self._after_break(ln, j, bar, L, sup, atr_b)
            return
        if (bar["c"] < L) if sup else (bar["c"] > L):    # B1, margin 0
            ln["broken_at"] = j
            ln["state"] = "broken"
            ln["open_episode"] = False
            self._ev(ln, "broken", j, dist_atr=abs(bar["c"] - L) / atr_b, close_loc=_close_loc(bar),
                     body_range=_body_range(bar))
            return
        inside = (bar["l"] - L) if sup else (L - bar["h"])        # extreme's distance on the line's inside
        outside = (L - bar["l"]) if sup else (bar["h"] - L)
        if outside > PEN_TOL * atr_b:
            self._ev(ln, "poke", j)                               # E7: stop harvest, still a contact
        if inside <= TOUCH_TOL * atr_b:                           # E5 contact
            if not ln["open_episode"]:
                ln["open_episode"] = True
                ln["episodes"] += 1
                if ln["state"] == "proposed":
                    ln["state"] = "touched"
                self._ev(ln, "touched", j, episode=ln["episodes"])
        elif inside > RESET_DIST * atr_b and ln["open_episode"]:  # E6 reset ends the episode
            ln["open_episode"] = False
            if "A" not in ln["eligible"]:
                ln["eligible"].add("A")
                self._ev(ln, "eligible", j, arm="A")
        # else: gap bar (E9), episode state unchanged

    def _after_break(self, ln, j, bar, L, sup, atr_b):
        if j - ln["broken_at"] > RETEST_WINDOW or ln["reclaim_done"]:
            return
        reach = bar["h"] >= L - TOUCH_TOL * atr_b if sup else bar["l"] <= L + TOUCH_TOL * atr_b
        if reach and not ln["retest_done"]:
            ln["retest_done"] = True
            self._ev(ln, "retested", j)
        if (bar["c"] >= L if sup else bar["c"] <= L):
            ln["reclaim_done"] = True
            self._ev(ln, "reclaimed", j)

    def _third_anchor(self, c, t):
        """E3 arm B: a later available same-side pivot within 0.25 ATR_b of the line."""
        for ln in self.lines.values():
            if (ln["side"] != c["side"] or c["i"] <= ln["ib"] or ln["broken_at"] is not None
                    or ln["retired"] or "B" in ln["eligible"]):
                continue
            if abs(c["price"] - self._L(ln, c["i"])) <= TOUCH_TOL * ln["atr_b"]:
                ln["eligible"].add("B")
                ln["thirds"].append(c["i"])
                self._ev(ln, "eligible", t, arm="B", ic=c["i"])

    # ---- L11 selector
    def nearest(self, side, arm="A"):
        """Nearest live eligible line to the last close; ties -> newer ib, then newer ia. None if none."""
        t = len(self.bars) - 1
        best, key = None, None
        for ln in self.lines.values():
            if ln["side"] != side or arm not in ln["eligible"] or ln["broken_at"] is not None or ln["retired"]:
                continue
            k = (abs(self.bars[t]["c"] - self._L(ln, t)), -ln["ib"], -ln["ia"])
            if key is None or k < key:
                best, key = ln, k
        return best

    def visible_events(self, t):
        """Events a live system could have written at the close of bar t."""
        return [e for e in self.events if e["known_at"] <= t]


def detect(bars, **kw):
    """Batch convenience: feed all bars through a fresh detector."""
    return TrendlineDetector(**kw).feed(bars)
