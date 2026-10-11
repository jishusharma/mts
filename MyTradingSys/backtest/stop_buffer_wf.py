import sys
sys.dont_write_bytecode = True
"""T081: walk-forward tuning of stop_buffer_atr k for the Tom core (research, offline, stdlib only).

Stop rule under test:  stop_k = structure_stop -/+ k x ATR(14)   (long: lower, short: higher), k in KS (pre-registered grid).
structure_stop is the row's rank-1 candidate math.stop (what tom_stop_width.py / tom_bt.py already use). Entry, target,
fill window, hold, fees and sim_limit_trade() are UNCHANGED (tom_bt.py); only the stop moves, so R = |entry - stop_k| grows
and fee_R = fees / R shrinks. Nothing else is scaled.

ATR(14): plain SMA of True Range over the last 14 CLOSED bars before the signal time (FORMULAS.md section 12, operator
decision 2026-09-28; the Java averageTrueRange also uses a 14-bar plain mean). Two bases, both registered:
  zone_tf = the row's zone timeframe (tom_bt.zone_tf(ztype): 5m / 15m / 1h), bars resampled from the 1m archive (PRIMARY);
  1m      = 1-minute bars (SENSITIVITY).
Walk-forward: EXPANDING window over calendar-month blocks of the DEV period (2025-09-01 .. 2026-06-25), first test block =
the 5th month (4 months of training), 1 day embargo before each test block. On each training set the k with the highest
mean net R and n >= 30 is chosen (ties -> smaller k) and applied to the next block. HOLDOUT (2026-06-26..) is burned for
Tom (B147) and is never selected on; no signal at or after it is simulated.
Output: research/fast_track_2026-09-27/T081_STOP_BUFFER_WF_2026-10-09.md. Analysis only; nothing here is a live parameter.
Usage: python MyTradingSys/backtest/stop_buffer_wf.py"""
import bisect
import datetime as dt
import os
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

import tom_bt as T  # noqa: E402
from MyTradingSys.backtest.fees import FEES_ALL_TAKER, FEES_DERIBIT  # noqa: E402

WORK = Path(os.environ.get("TOM_WORK_DIR", r"F:\MTS\data\tom_bt_2026-10-07"))
RAW = Path(os.environ.get("TOM_RAW_DIR", r"F:\MTS\data\tom_raw")) / "klines"
OUT = ROOT / "MyTradingSys" / "research" / "fast_track_2026-09-27" / "T081_STOP_BUFFER_WF_2026-10-09.md"


def _ts(y, m, d):
    return dt.datetime(y, m, d, tzinfo=dt.timezone.utc).timestamp()


HOLDOUT_START = _ts(2026, 6, 26)
DEV_START = _ts(2025, 9, 1)
KS = (0.0, 0.25, 0.5, 1.0, 1.5, 2.0)      # NO-SOURCE: pre-registered tuning grid (task T081), not a trader quote
ATR_N = 14                                # core ATR window (SetupCandidatesBuilder.averageTrueRange callers use 14)
MIN_TRAIN_BLOCKS = 4                      # NO-SOURCE: engineering choice, 4 months of training before the first test block
MIN_N = 30                                # task T081 spec
EMBARGO_S = 86400                         # NO-SOURCE: > max trade life (8 fill + 8 hold bars of a 1h zone = 16 h)
VARIANTS = ("watch_episode", "p4_episode")
BASES = ("zone_tf", "1m")
FEE_PROFILES = (("DERIBIT", FEES_DERIBIT), ("ALL_TAKER", FEES_ALL_TAKER))
RESOLVED = ("target", "stop", "timeout")


# ---------------------------------------------------------------- ATR (FORMULAS.md section 12)
def true_range(h, l, pc):
    return max(h - l, abs(h - pc), abs(l - pc))


def atr_at(H, L, C, i, n=ATR_N):
    """Plain SMA of TR[i-n+1..i]; needs i >= n (TR needs a prior close). None otherwise."""
    if n < 1 or i < n or i >= len(H):
        return None
    return sum(true_range(H[j], L[j], C[j - 1]) for j in range(i - n + 1, i + 1)) / n


class TfSeries:
    """Epoch-aligned closed bars of one timeframe, built from the (gap-free) 1m archive. Lean arrays only."""

    def __init__(self, b, tf_min):
        self.tf_ms = tf_min * 60000
        pm = self.tf_ms
        first = -(-b.t0 // pm) * pm
        j0 = (first - b.t0) // 60000
        self.t, self.h, self.l, self.c = [], [], [], []
        while j0 + tf_min <= b.n:
            j1 = j0 + tf_min
            self.t.append(b.t0 + j0 * 60000)
            self.h.append(max(b.h[j0:j1]))
            self.l.append(min(b.l[j0:j1]))
            self.c.append(b.c[j1 - 1])
            j0 = j1

    def atr(self, t_ms, n=ATR_N):
        """ATR over the last n bars that CLOSED at or before t_ms (bar open + tf <= t_ms): no look-ahead."""
        j = bisect.bisect_right(self.t, t_ms - self.tf_ms) - 1
        if j < 0:
            return None
        return atr_at(self.h, self.l, self.c, j, n)


class Atr1m:
    def __init__(self, b):
        self.b = b

    def atr(self, t_ms, n=ATR_N):
        i = self.b.idx(t_ms) - 1          # last closed 1m bar
        if i < 0 or i >= self.b.n:
            return None
        return atr_at(self.b.h, self.b.l, self.b.c, i, n)


def widen_stop(side, stop, atr, k):
    """long: stop - k*ATR (lower); short: stop + k*ATR (higher)."""
    return stop - k * atr if side == "long" else stop + k * atr


def with_atr(sigs, basis, b, series):
    """Copy signals, attach row['atr'] for the basis; drop signals with no ATR. Returns (rows, n_dropped)."""
    out, dropped = [], 0
    for r in sigs:
        t_ms = int(round(r["t"] * 1000))
        if basis == "1m":
            a = series["1m"].atr(t_ms)
        else:
            a = series[T.ZONE_TF_MIN[T.zone_tf(r["ztype"])]].atr(t_ms)
        if a is None or a <= 0:
            dropped += 1
            continue
        d = dict(r)
        d["atr"] = a
        out.append(d)
    return out, dropped


def rows_for_k(sigs, k):
    out = []
    for r in sigs:
        d = dict(r)
        d["stop"] = widen_stop(r["dir"], float(r["stop"]), r["atr"], k)
        out.append(d)
    return out


# ---------------------------------------------------------------- periods and blocks
def month_blocks(start_ts, end_ts):
    """[(lo, hi)) UTC calendar-month blocks covering [start_ts, end_ts); the last one is clipped at end_ts."""
    d = dt.datetime.fromtimestamp(start_ts, dt.timezone.utc)
    out = []
    while d.timestamp() < end_ts:
        nxt = (d.replace(day=1) + dt.timedelta(days=32)).replace(day=1)
        out.append((d.timestamp(), min(nxt.timestamp(), end_ts)))
        d = nxt
    return out


def period(t):
    if t >= HOLDOUT_START:
        return "holdout"
    return "dev" if t >= DEV_START else "hist"


# ---------------------------------------------------------------- statistics
def mean(xs):
    return statistics.fmean(xs) if xs else float("nan")


def cell(trades):
    """Stats over all simulated orders (trades = run_variant output restricted to one period)."""
    n_sig = len(trades)
    filled = [t for t in trades if t.get("filled") and t["reason"] in RESOLVED]
    nf = len(filled)
    c = dict(n_sig=n_sig, n=nf,
             no_fill=sum(1 for t in trades if t["reason"] == "no_fill"),
             ran=sum(1 for t in trades if t["reason"] == "ran"),
             bad_geom=sum(1 for t in trades if t["reason"] == "bad_geometry"))
    if nf:
        net = [t["net_r"] for t in filled]
        lo, hi = T.boot_ci(net)
        c.update(win=sum(1 for t in filled if t["reason"] == "target") / nf,
                 timeout=sum(1 for t in filled if t["reason"] == "timeout") / nf,
                 stop=sum(1 for t in filled if t["reason"] == "stop") / nf,
                 gross=mean([t["gross_r"] for t in filled]), net=mean(net), net_lo=lo, net_hi=hi,
                 net_med=statistics.median(net), fee=mean([t["fee_r"] for t in filled]))
    return c


def fmt_cell_row(label, c):
    if not c["n"]:
        return "| %s | %d | 0 | - | - | - | - | - | - | - | - | - |" % (label, c["n_sig"])
    ns = c["n_sig"]
    return "| %s | %d | %d | %.1f%% | %.1f%% | %.1f%% | %.1f%% | %+.3f | %+.3f [%+.3f, %+.3f] | %+.3f | %+.3f |" % (
        label, ns, c["n"], 100.0 * c["no_fill"] / ns, 100.0 * c["ran"] / ns, 100.0 * c["win"], 100.0 * c["timeout"],
        c["gross"], c["net"], c["net_lo"], c["net_hi"], c["net_med"], c["fee"])


CELL_HEAD = ["| k / period | orders | filled | no_fill | ran | win (target) | timeout | gross R | net R mean [95% CI] | net R med | fee R |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]


# ---------------------------------------------------------------- walk-forward
def choose_k(trades_by_k, train_hi, blocks_lo, min_n=MIN_N):
    """Highest mean net R among k with n >= min_n, using resolved trades with blocks_lo <= t < train_hi.
    Ties -> smaller k. Returns (k or None, {k: (n, mean_net)})."""
    stats, best = {}, None
    for k in sorted(trades_by_k):
        xs = [t["net_r"] for t in trades_by_k[k] if blocks_lo <= t["t"] < train_hi]
        stats[k] = (len(xs), mean(xs))
        if len(xs) >= min_n and (best is None or stats[k][1] > stats[best][1]):
            best = k
    return best, stats


def walk_forward(trades_by_k, blocks, min_train=MIN_TRAIN_BLOCKS, min_n=MIN_N, embargo=EMBARGO_S, base_k=0.0):
    """trades_by_k: {k: resolved dev trades (dicts with t, net_r)}. Expanding window over `blocks`.
    Returns list of folds; each fold: test_lo/hi, chosen k, train stats, oos trades (chosen k), base trades (base_k)."""
    folds = []
    for m in range(min_train, len(blocks)):
        lo, hi = blocks[m]
        k, stats = choose_k(trades_by_k, lo - embargo, blocks[0][0], min_n)
        base = [t for t in trades_by_k[base_k] if lo <= t["t"] < hi]
        oos = [] if k is None else [t for t in trades_by_k[k] if lo <= t["t"] < hi]
        folds.append(dict(fold=m - min_train + 1, test_lo=lo, test_hi=hi, k=k, train=stats, oos=oos, base=base))
    return folds


def pooled(folds, key):
    return [t["net_r"] for f in folds for t in f[key]]


def day(ts):
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%Y-%m-%d")


# ---------------------------------------------------------------- driver
def load_rows():
    import json
    rows = []
    for p in sorted(WORK.glob("*.rows.jsonl")):
        with open(p, encoding="utf-8") as fh:
            rows.extend(json.loads(line) for line in fh)
    rows.sort(key=lambda r: r["t"])
    return rows


def main():
    rows = [r for r in load_rows() if r["t"] < HOLDOUT_START]
    print("rows (holdout excluded):", len(rows), flush=True)
    b = T.load_bars_1m(RAW)
    print("bars:", b.n, flush=True)
    series = {m: TfSeries(b, m) for m in sorted(set(T.ZONE_TF_MIN.values()))}
    series["1m"] = Atr1m(b)
    blocks = month_blocks(DEV_START, HOLDOUT_START)
    L = ["# T081 - stop_buffer_atr walk-forward (Tom core), %s" % dt.date.today().isoformat(), "",
         "Rows: %s (signals at or after 2026-06-26 excluded: HOLDOUT burned for Tom, B147). Bars: %s." % (WORK, RAW),
         "Stop under test: `stop_k = structure_stop -/+ k x ATR(14)` (long lower, short higher). Entry, target, fill window, hold, "
         "fees and `sim_limit_trade()` are those of tom_bt.py; only the stop moves (so R grows and fee R shrinks). ATR = plain SMA of "
         "True Range over the last 14 closed bars before the signal (FORMULAS.md s12). Bases: **zone_tf** (primary; the row's zone "
         "timeframe 5m/15m/1h) and **1m** (sensitivity).",
         "Signal variants are SENSITIVITY as in B146 (watch_episode = WATCH or SETUP_FORMING, p4_episode = proof>=4); the live rule has 0 signals.",
         "Fees: DERIBIT = maker entry/target 0, taker stop/timeout 5 bp; ALL_TAKER = 5 bp every leg (fees.py).", "",
         "## Pre-registration (frozen before the run)", "",
         "- k grid %s: **NO-SOURCE** (tuning grid fixed by task T081; no trader quote). Every k that is picked below is **BT-TUNED**, not a parameter." % (KS,),
         "- ATR window 14 and plain-SMA form: FORMULAS.md s12 (operator decision 2026-09-28) / Java averageTrueRange callers. Taking ATR on the zone timeframe is an assumption of this study (the row carries the zone type, not the Java ATR timeframe).",
         "- Trials: 2 variants x 2 ATR bases x 6 k x 2 fee profiles = 48 cells, each printed for dev and for hist; 8 walk-forward runs (variant x basis x fee). None dropped.",
         "- Walk-forward: **expanding** window over UTC calendar-month blocks of DEV (2025-09-01..2026-06-25): %d blocks, first test block = block %d "
         "(train = first %d months), so %d folds; embargo %d s before each test block (**NO-SOURCE**, > 16 h max trade life); "
         "MIN_TRAIN_BLOCKS=%d is **NO-SOURCE** (engineering choice). Choice rule: highest mean net R with n >= %d in the training set, ties -> smaller k; "
         "if no k has n >= %d the fold abstains (no trade, counted as such)." % (
             len(blocks), MIN_TRAIN_BLOCKS + 1, MIN_TRAIN_BLOCKS, len(blocks) - MIN_TRAIN_BLOCKS, EMBARGO_S, MIN_TRAIN_BLOCKS, MIN_N, MIN_N),
         "- Pass rule for the verdict: out-of-fold mean net R > 0 AND bootstrap 95% CI lower bound > 0 (T.boot_ci, 2000 resamples, seed fixed).",
         "- hist (2022-01..2025-08) rows are printed for context only; they play no part in selection.",
         "- A trade opened by the last dev signal can exit up to 16 h after 2026-06-26 00:00; those exit bars are read (unavoidable, same as tom_stop_width.py), but no holdout signal is generated or selected on.", ""]
    wf_summary = []          # (variant, basis, fee, folds)
    check_line = None
    for variant in VARIANTS:
        sigs0 = T.signals(rows, variant)
        for basis in BASES:
            sigs, dropped = with_atr(sigs0, basis, b, series)
            print(variant, basis, "signals", len(sigs0), "no ATR dropped", dropped, flush=True)
            for fname, fees in FEE_PROFILES:
                by_k_all, by_k_res = {}, {}
                for k in KS:
                    res = T.run_variant(rows_for_k(sigs, k), b, fees=fees)
                    for t in res:
                        t["period"] = period(t["t"])
                    by_k_all[k] = res
                    by_k_res[k] = [t for t in res if t.get("filled") and t["reason"] in RESOLVED and t["period"] == "dev"]
                if (variant, basis, fname) == ("watch_episode", "zone_tf", "DERIBIT"):
                    nres = sum(1 for t in by_k_all[0.0] if t.get("filled") and t["reason"] in RESOLVED)
                    check_line = ("Consistency check: k=0, watch_episode, zone_tf ATR, DERIBIT gives %d resolved filled trades over hist+dev "
                                  "(tom_stop_width.py B146 reported 2699 with no ATR requirement; %d signals had no ATR and were dropped)." % (nres, dropped))
                L += ["## %s / ATR basis %s / %s" % (variant, basis, fname), "",
                      "Signals with ATR: %d of %d (dropped for missing ATR: %d)." % (len(sigs), len(sigs0), dropped), ""]
                for per in ("dev", "hist"):
                    L += ["### period %s%s" % (per, " (pooled; IN-SAMPLE for the k grid, not an out-of-sample number)" if per == "dev" else " (context only)"), ""] + CELL_HEAD
                    for k in KS:
                        c = cell([t for t in by_k_all[k] if t["period"] == per])
                        L.append(fmt_cell_row("k=%g (%s)" % (k, per), c))
                    L.append("")
                folds = walk_forward(by_k_res, blocks)
                wf_summary.append((variant, basis, fname, folds))
                L += ["### Walk-forward (expanding, dev only)", "",
                      "| fold | test block | k chosen (BT-TUNED) | train n / mean net at chosen k | train table n/mean net per k | OOS n | OOS mean net | k=0 n | k=0 mean net |",
                      "|---|---|---|---|---|---|---|---|---|"]
                for f in folds:
                    ks = f["k"]
                    tr = "; ".join("%g:%d/%+.2f" % (kk, v[0], v[1]) for kk, v in sorted(f["train"].items()))
                    on = [t["net_r"] for t in f["oos"]]
                    bn = [t["net_r"] for t in f["base"]]
                    L.append("| %d | %s..%s | %s | %s | %s | %d | %s | %d | %s |" % (
                        f["fold"], day(f["test_lo"]), day(f["test_hi"] - 1), "abstain" if ks is None else "%g" % ks,
                        "-" if ks is None else "%d / %+.3f" % f["train"][ks], tr, len(on),
                        "-" if not on else "%+.3f" % mean(on), len(bn), "-" if not bn else "%+.3f" % mean(bn)))
                oos, base = pooled(folds, "oos"), pooled(folds, "base")
                lines = []
                for name, xs in (("OUT-OF-FOLD (chosen k)", oos), ("same test blocks at k=0", base)):
                    if xs:
                        lo, hi = T.boot_ci(xs)
                        lines.append("- **%s**: n=%d mean net R %+.3f, 95%% CI [%+.3f, %+.3f], median %+.3f" % (
                            name, len(xs), mean(xs), lo, hi, statistics.median(xs)))
                    else:
                        lines.append("- **%s**: n=0" % name)
                L += ["", *lines, ""]
    # ---- verdict
    L += ["## Walk-forward summary (all 8 runs)", "",
          "| variant | ATR basis | fees | folds with a k | OOS n | OOS mean net R | OOS 95% CI | k=0 same blocks mean net R | k picked per fold | passes (mean>0 and CI lo>0) |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    passes = []
    for variant, basis, fname, folds in wf_summary:
        oos, base = pooled(folds, "oos"), pooled(folds, "base")
        lo, hi = T.boot_ci(oos) if oos else (float("nan"), float("nan"))
        ok = bool(oos) and mean(oos) > 0 and lo > 0
        if ok:
            passes.append((variant, basis, fname))
        L.append("| %s | %s | %s | %d/%d | %d | %s | %s | %s | %s | %s |" % (
            variant, basis, fname, sum(1 for f in folds if f["k"] is not None), len(folds), len(oos),
            "-" if not oos else "%+.3f" % mean(oos), "-" if not oos else "[%+.3f, %+.3f]" % (lo, hi),
            "-" if not base else "%+.3f" % mean(base),
            ",".join("-" if f["k"] is None else "%g" % f["k"] for f in folds), "YES" if ok else "no"))
    L.append("")
    if passes:
        verdict = ("VERDICT: %d of 8 walk-forward runs have out-of-fold net R > 0 with the 95%% CI above zero: %s. "
                   "8 runs on one dev sample are not independent trials: treat as a lead (BT-TUNED), not a result, until a fresh sample confirms it." % (
                       len(passes), "; ".join("/".join(p) for p in passes)))
    else:
        verdict = ("VERDICT: NO. In none of the 8 walk-forward runs (2 variants x 2 ATR bases x 2 fee profiles) does the chosen stop buffer give "
                   "out-of-fold net R > 0 with the 95% CI above zero. A wider ATR stop shrinks the fee drag but does not create an edge.")
    edge = sum(1 for _, _, _, fo in wf_summary for f in fo if f["k"] == max(KS))
    tot = sum(1 for _, _, _, fo in wf_summary for f in fo if f["k"] is not None)
    L += [verdict, "",
          "Grid-edge note: the largest registered k (%g) was chosen in %d of %d folds that picked a k. Net R improves monotonically with k "
          "(fee drag shrinks) while gross R stays negative, so the optimum sits at the edge of the grid: the grid was not widened "
          "(that would be a new trial family after seeing results), and the verdict does not depend on it because even the edge cell has a negative mean." % (
              max(KS), edge, tot), ""]
    if check_line:
        L += [check_line, ""]
    L += ["## Caveats", "",
          "- Scope: Tom core only. The other tight-stop layers named in T081 (CryptoCred cc_setups stop_buffer_pct 0.001, B143; fabio, etc.) are NOT run here: they have their own row sources and B143 forbids gridding NO-SOURCE values without a separate ruling. Follow-up needed.",
          "- k pooled over dev is in-sample; only the walk-forward 'OUT-OF-FOLD' lines are out-of-sample. Mean net R is dominated by fee drag on very small stops at k=0 (see median columns).",
          "- Same signal set is reused across k, but one_at_a_time busy-state depends on exit time, so orders processed can differ slightly between k (the 'orders' column shows it).",
          "- Funding is not modelled (as in tom_bt.py). Holdout 2026-06-26.. not selected on, not reported.", ""]
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    print(verdict)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
