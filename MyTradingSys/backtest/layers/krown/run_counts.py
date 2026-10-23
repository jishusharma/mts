"""S1 counts pass (confluence-s1-context-counts), part A: constants, bar loaders, event loaders.
Reads timestamps, side, entry price and stop distance only, never an outcome column. VALIDATION and HOLDOUT bars are never used:
every loader stops at 2024-07-01 and note() logs the min/max bar actually used (ACCESS_LOG.md).
"""
import csv
import datetime as dt
import json
import statistics
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import krown_context as kx  # noqa: E402

ROOT = HERE.parents[2]                                   # MyTradingSys/
REPO = ROOT.parent
RUN = ROOT / "research" / "krown_audit_2026-10-22" / "run"
SEALED = RUN / "sealed"
DATA = Path("F:/MTS/data")
NPZ = DATA / "bigtrade" / "cache" / "perp"
DAILY = DATA / "krown_daily" / "BTCUSDT_1d.csv"

DEV_START = 1640995200000          # 2022-01-01 UTC (OPERATOR_DECISIONS.md:878)
CUT = 1719792000000                # 2024-07-01 UTC exclusive: nothing at or after is used
EXT_START = 1577836800000          # 2020-01-01 UTC (DEV_EXT, OPERATOR_DECISIONS.md:883,894)
Y2023 = 1672531200000              # 2023-01-01 UTC: the 2022 | 2023-24H1 split
M15 = 900_000

ACCESS = []
DROPS = {}                      # layer -> (rows in scope, {status: count} for the rows dropped by the status filter)
SEMANTICS = []                  # lines for COUNTS.md section 1b


def note(name, tmin, tmax, n, extra=""):
    ACCESS.append((name, tmin, tmax, n, extra))
    if tmax is not None and tmax > CUT:
        raise SystemExit("ACCESS VIOLATION: %s reaches %s >= 2024-07-01" % (name, tmax))


def iso(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M")


def load_daily():
    t, o, h, l, c, v = [], [], [], [], [], []
    with open(DAILY, newline="") as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            ot = int(row[0])
            if ot >= CUT:
                break                                   # stream stop: later rows are never parsed
            t.append(ot), o.append(float(row[1])), h.append(float(row[2])), l.append(float(row[3]))
            c.append(float(row[4])), v.append(float(row[5]))
    note("krown_daily/BTCUSDT_1d.csv", t[0], t[-1], len(t), "streamed, stopped at the first row >= cut")
    return t, o, h, l, c, v


def load_npz(tf):
    z = np.load(NPZ / ("klines_%s.npz" % tf))
    tt = z["t"]
    keep = tt < CUT
    out = {k: z[k][keep] for k in ("t", "o", "h", "l", "c")}
    note("bigtrade/cache/perp/klines_%s.npz" % tf, int(out["t"][0]), int(out["t"][-1]), int(keep.sum()),
         "np.load reads whole arrays; mask applied before any value is used")
    return out

# ---- events -----------------------------------------------------------------------------------------------------

def spec(name, csv_name, ts, add, side, etype, tf, entry=None, risk=None, status="status", where=None):
    return dict(name=name, csv=csv_name, ts=ts, add=add, side=side, etype=etype, tf=tf, entry=entry, risk=risk,
                status=status, where=where)


H1, M5, H4 = 3_600_000, 300_000, 14_400_000
F, B = kx.FADE, kx.BREAKOUT
# decision_ts = event bar open + event tf (PRE_REG s2.3). `side`: column name, or +1/-1 for single-sided layers.
# Event type FADE/BREAKOUT per design s6.0; layers the design does not list are OURS (see OURS_TYPE).
SPECS = [
    spec("bb_top_reversal", "bb_top_reversal.csv", "timestamp", M15, -1, F, "15m", "entry", "risk_r"),
    spec("malkan_rsi", "malkan_rsi.csv", "entry_t", 0, "side", B, "1h", "entry", "risk_r"),
    spec("rsi_reclaim", "rsi_reclaim.csv", "entry_t", 0, "side", B, "1h", "entry", "risk_r"),
    spec("cc_msb", "cc_msb.csv", "entry_t", 0, "side", B, "1h", "entry", "risk_r"),
    spec("fabio_escalation", "fabio_escalation.csv", "entry_t", 0, "side", B, "1h", "entry", "risk_r"),
    spec("session_momentum", "session_momentum.csv", "t", M5, "side", B, "5m", "entry", "r"),
    spec("rsi_divergence_1h", "rsi_divergence.csv", "entry_t", 0, "side", F, "1h", "entry", "r", where=("timeframe", "1h")),
    spec("rsi_divergence_4h", "rsi_divergence.csv", "entry_t", 0, "side", F, "4h", "entry", "r", where=("timeframe", "4h")),
    spec("candle_pattern_1h", "candle_pattern_1h.csv", "event_time", 0, "side", F, "1h", "event_price", "risk_price"),
    spec("candle_pattern_4h", "candle_pattern_4h.csv", "event_time", 0, "side", F, "4h", "event_price", "risk_price"),
    spec("volume_1h", "volume_1h.csv", "timestamp", H1, "direction", B, "1h", None, "risk_range", where=("is_spike", True)),
    spec("volume_4h", "volume_4h.csv", "timestamp", H4, "direction", B, "4h", None, "risk_range", where=("is_spike", True)),
]
OURS_TYPE = {"rsi_divergence_1h", "rsi_divergence_4h", "candle_pattern_1h", "candle_pattern_4h", "session_momentum", "volume_1h",
             "volume_4h", "malkan_rsi", "rsi_reclaim", "cc_msb", "wlow_bounce"}
NOT_JOINED = [
    ("fabio_lvn_touch", "regenerated; table has no side column (long_* and short_* excursions both written): D1/D3 need a side", "NO_SIDE"),
    ("funding_extreme", "input F:/MTS/data/candle_close_dev_2022_2024 funding zips absent on JIS-NB: 0 rows written", "NOT_RUN"),
    ("session_levels", "input F:/MTS/data/candle_close_dev_2022_2024 1m archive absent on JIS-NB: 0 rows written", "NOT_RUN"),
    ("bigtrade", "excluded by the card (only post-fix rows; needs the fires dir)", "EXCLUDED"),
    ("oi_delta", "no rows (card D3)", "EXCLUDED"),
    ("turn_of_candle", "not a trigger (card D3)", "EXCLUDED"),
]


def load_events(sp):
    """Returns list of dicts {dts, side, entry, risk}. Only the columns named here are parsed (usecols)."""
    cols = {sp["ts"], sp["status"]}
    if isinstance(sp["side"], str):
        cols.add(sp["side"])
    for k in ("entry", "risk"):
        if sp[k]:
            cols.add(sp[k])
    if sp["where"]:
        cols.add(sp["where"][0])
    path = SEALED / sp["csv"]
    head = pd.read_csv(path, nrows=0).columns
    d = pd.read_csv(path, usecols=[c for c in cols if c in head])
    if sp["where"]:
        d = d[d[sp["where"][0]] == sp["where"][1]]
    if sp["status"] in d.columns:
        bad = d[d[sp["status"]] != "OK"][sp["status"]].value_counts().to_dict()
        DROPS[sp["name"]] = (len(d), bad)
        d = d[d[sp["status"]] == "OK"]
    d = d[d[sp["ts"]].notna()]
    out = []
    for _, r in d.iterrows():
        s = r[sp["side"]] if isinstance(sp["side"], str) else sp["side"]
        s = {"long": 1, "up": 1, "short": -1, "down": -1}.get(s, s)
        if s not in (1, -1):
            continue
        out.append({"dts": int(r[sp["ts"]]) + sp["add"], "side": int(s),
                    "entry": float(r[sp["entry"]]) if sp["entry"] and pd.notna(r[sp["entry"]]) else None,
                    "risk": float(r[sp["risk"]]) if sp["risk"] and pd.notna(r[sp["risk"]]) else None})
    return out


SEM_CHECKS = [
    # layer, csv, column a, column b, expected b - a (ms), where
    ("malkan_rsi", "malkan_rsi.csv", "timestamp", "entry_t", 3_600_000, None),
    ("rsi_reclaim", "rsi_reclaim.csv", "timestamp", "entry_t", 3_600_000, None),
    ("cc_msb", "cc_msb.csv", "event_t", "entry_t", 3_600_000, None),
    ("fabio_escalation", "fabio_escalation.csv", "timestamp", "entry_t", 3_600_000, None),
    ("rsi_divergence_1h", "rsi_divergence.csv", "t", "entry_t", 3_600_000, ("timeframe", "1h")),
    ("rsi_divergence_4h", "rsi_divergence.csv", "t", "entry_t", 14_400_000, ("timeframe", "4h")),
    ("bb_top_reversal", "bb_top_reversal.csv", "green_timestamp", "timestamp", 900_000, None),
]


def check_semantics():
    """Event timestamp rule per table, verified on the table own columns: next-bar-open minus event-bar-open equals the tf on every row."""
    for name, csv_name, a, b, want, where in SEM_CHECKS:
        cols = [a, b] + ([where[0]] if where else [])
        d = pd.read_csv(SEALED / csv_name, usecols=cols).dropna(subset=[a, b])
        if where:
            d = d[d[where[0]] == where[1]]
        diff = (d[b] - d[a]).astype("int64")
        ok = int((diff == want).sum())
        SEMANTICS.append("- %s: %s - %s == %d ms on %d of %d rows" % (name, b, a, want, ok, len(d)))
        assert ok == len(d), "%s: event timestamp semantics differ from the assumed rule" % name
    d = pd.read_csv(SEALED / "session_momentum.csv", usecols=["t"]).dropna()
    ok = int(((d["t"].astype("int64") % 86_400_000) == 1_500_000).sum())
    SEMANTICS.append("- session_momentum: t is the open of the 6th 5m bar (00:25 UTC), decision = t + 5m: %d of %d rows" % (ok, len(d)))
    assert ok == len(d)
    SEMANTICS.append("- candle_pattern: event_time is close_t = bar open + tf by the table definition (candle_pattern_event_table/REPORT.md, Method); decision = event_time")
    SEMANTICS.append("- volume: timestamp is the spike bar open (forward window starts at the next bar open, volume_event_table/REPORT.md); decision = timestamp + tf")
    SEMANTICS.append("- wlow_bounce: trigger_open is a 1h bar open (ISO, hour grid); decision = trigger_open + 1h")


def load_wlow():
    """wlow_bounce_bbrsi60 events.csv (in the repo, ISO strings): variant V1_primary only; long; trigger bar open + 1h."""
    p = ROOT / "research" / "wlow_bounce_bbrsi60_2026-10-16" / "events.csv"
    d = pd.read_csv(p, usecols=["variant", "trigger_open"])
    d = d[d["variant"] == "V1_primary"]
    out = []
    for s in d["trigger_open"]:
        ms = int(dt.datetime.strptime(s, "%Y-%m-%dT%H:%MZ").replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
        out.append({"dts": ms + H1, "side": 1, "entry": None, "risk": None})
    return out

# ---- joining ----------------------------------------------------------------------------------------------------

class Ctx:
    def __init__(self, daily_rows, h4_rows, c15):
        self.d, self.h4, self.c15 = daily_rows, h4_rows, c15

    def price(self, dts):
        """Close of the last 15m bar that closed at or before dts."""
        return self.c15.get((dts // M15) * M15 - M15)

    def at(self, dts):
        return kx.join_row(self.d, dts), kx.join_row(self.h4, dts), self.price(dts)


def score(ev, etype, ctx, bands):
    d, h4, px = ctx.at(ev["dts"])
    if d is None or h4 is None or px is None:
        return None
    s = ev["side"]
    d1 = kx.d1_direction(s, d["trend_1d_ours"], d["trend_1w_ours"])
    d2 = kx.d2_regime(etype, s, h4["bbwp_4h_ours"], h4["bbwp_4h_min6_ours"], h4["exp_dir_4h_ours"], bands["bbwp_high"])
    d3 = kx.d3_location(s, px, kx.parse_zones(d["zones_ours"]), d["atr14_1d"], d["range_top_ours"], d["range_bottom_ours"],
                        bands["near_atr"], bands["edge"])
    if d1 is None or d2 is None or d3 is None:
        return None
    return {"d1": d1, "d2": d2, "d3": d3, "S": d1 + d2 + d3, "px": px, "d_open": d["open_ms"], "h4_open": h4["open_ms"]}


def week_key(ms):
    y, w, _ = dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).isocalendar()
    return "%d-W%02d" % (y, w)


def day_key(ms):
    return ms // 86_400_000


def set_of(ms):
    return "2022" if ms < Y2023 else "2023-24H1"


# ---- band freeze ------------------------------------------------------------------------------------------------

D3_NEAR_GRID = (0.25, 0.5, 0.75, 1.0)
EDGE_GRID = (0.2, 0.25, 0.3333)
D3_NEAR_EXT = (0.05, 0.1, 0.15)                              # pass 2 values, added after pass 1 found no in-band point
EDGE_EXT = (0.05, 0.1, 0.15)
D2_GRID = (80, 85, 90)


def freeze_bands(events, ctx):
    """Pass 1 rule, written before the numbers were looked at (PRE_REG s1 F8; D3 targets +1 and -1 each 15-30 % of events, OURS):
    smallest near_atr, then smallest edge, with both pooled coverages inside 15-30 %. Pass 1 found no in-band point, so pass 2 (a
    POST-HOC rule chosen after seeing pass 1 coverage, still counts only, no outcome seen) adds tighter values and takes the loosest
    in-band point (largest near_atr, then largest edge). Both passes are in TRIALS.md. Population = events with D1, D2, D3 all available.
    D2: keep bbwp_high 85 unless pooled D2=+1 or D2=-1 is below 5 % of those events, then the smallest grid value that fixes it."""
    pooled = [(e, sp["etype"]) for _, (sp, evs) in events.items() for e in evs]
    def cover(near, edge):
        c = Counter()
        n = 0
        for e, et in pooled:
            d, h4, px = ctx.at(e["dts"])
            if d is None or h4 is None or px is None:
                continue
            if kx.d1_direction(e["side"], d["trend_1d_ours"], d["trend_1w_ours"]) is None:
                continue
            if kx.d2_regime(et, e["side"], h4["bbwp_4h_ours"], h4["bbwp_4h_min6_ours"], h4["exp_dir_4h_ours"]) is None:
                continue
            v = kx.d3_location(e["side"], px, kx.parse_zones(d["zones_ours"]), d["atr14_1d"], d["range_top_ours"],
                               d["range_bottom_ours"], near, edge)
            if v is None:
                continue
            n += 1
            c[v] += 1
        return (near, edge, n, c[1] / n if n else 0.0, c[-1] / n if n else 0.0, c[0] / n if n else 0.0)

    def inband(g):
        return g[2] and 0.15 <= g[3] <= 0.30 and 0.15 <= g[4] <= 0.30

    grid = [("pass 1",) + cover(n_, e_) for n_ in D3_NEAR_GRID for e_ in EDGE_GRID]
    pick = next((g for g in grid if inband(g[1:])), None)
    if pick is None:
        # DECISION (OURS): pass 1 found nothing in band (D3=+1 saturated, as REVIEW_OPUS F10 warned). Pass 2 adds tighter values
        # and picks, among ALL in-band points, the loosest (largest near_atr, then largest edge). Counts only; no outcome seen.
        done = {(g[1], g[2]) for g in grid}
        for n_ in D3_NEAR_EXT + D3_NEAR_GRID:
            for e_ in EDGE_EXT + EDGE_GRID:
                if (n_, e_) not in done:
                    grid.append(("pass 2",) + cover(n_, e_))
        ok = [g for g in grid if inband(g[1:])]
        pick = max(ok, key=lambda g: (g[1], g[2])) if ok else None
    d2grid = []
    for hi in D2_GRID:
        c = Counter()
        n = 0
        for e, et in pooled:
            d, h4, px = ctx.at(e["dts"])
            if d is None or h4 is None or px is None:
                continue
            if kx.d1_direction(e["side"], d["trend_1d_ours"], d["trend_1w_ours"]) is None:
                continue
            v = kx.d2_regime(et, e["side"], h4["bbwp_4h_ours"], h4["bbwp_4h_min6_ours"], h4["exp_dir_4h_ours"], hi)
            if v is None:
                continue
            n += 1
            c[v] += 1
        d2grid.append((hi, n, c[1] / n, c[-1] / n, c[0] / n))
    d2pick = next((g for g in d2grid if g[0] == 85 and g[2] >= 0.05 and g[3] >= 0.05), None)
    if d2pick is None:
        d2pick = next((g for g in d2grid if g[2] >= 0.05 and g[3] >= 0.05), next(g for g in d2grid if g[0] == 85))
    bands = {"near_atr": pick[1] if pick else kx.Z_NEAR_ATR, "edge": pick[2] if pick else kx.EDGE_FRAC, "bbwp_high": d2pick[0]}
    return grid, bands, {"d3_pick": pick, "d3_found": pick is not None, "d2_pick": d2pick, "d2grid": d2grid}


# ---- context / joined / access outputs -----------------------------------------------------------------------------

CTX_COLS = ["tf", "set", "open_ms", "open_utc", "available_at", "trend_1d_ours", "trend_1w_ours", "naive_trend_sma200",
            "naive_trend_ret20", "bbwp_1d_ours", "rsi_1d_ours", "rsi_zone_1d_ours", "atr14_1d", "zones_ours", "range_top_ours",
            "range_bottom_ours", "bbwp_4h_ours", "bbwp_4h_min6_ours", "exp_dir_4h_ours"]


def write_context_csv(daily, h4):
    with open(RUN / "context_dev.csv", "w", newline="", encoding="utf-8") as f:
        f.write("# Krown context rows, OURS impl. of KR-x (fields ending _ours); naive_trend_* are the OURS baselines (REVIEW_OPUS F12). "
                "Point-in-time: usable iff available_at < decision_ts. No outcome column. DEV_EXT 4h rows: NOT_AVAILABLE on JIS-NB.\n")
        w = csv.DictWriter(f, fieldnames=CTX_COLS, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for tf, rows in (("1d", daily), ("4h", h4)):
            for r in rows:
                if r["open_ms"] < EXT_START:
                    continue
                r = dict(r, tf=tf, open_utc=iso(r["open_ms"]), set="DEV_EXT" if r["open_ms"] < DEV_START else "DEV")
                w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in CTX_COLS})


def write_joined(scored):
    with open(RUN / "joined_events.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["layer", "decision_ts", "decision_utc", "side", "iso_week", "set", "usable", "d1", "d2", "d3", "S",
                    "daily_row_open_ms", "h4_row_open_ms"])
        for name, rows in scored.items():
            for e, sc in rows:
                w.writerow([name, e["dts"], iso(e["dts"]), e["side"], week_key(e["dts"]), set_of(e["dts"]), int(sc is not None)]
                           + ([sc["d1"], sc["d2"], sc["d3"], sc["S"], sc["d_open"], sc["h4_open"]] if sc else [""] * 6))


def write_access():
    with open(RUN / "ACCESS_LOG.md", "w", encoding="utf-8", newline="\n") as f:
        f.write("# ACCESS_LOG (S1): every file opened, with the min / max bar open time actually used\n\n")
        f.write("Cut: 2024-07-01 00:00 UTC (%d) exclusive. No bar at or after the cut was used: `note()` aborts the run otherwise.\n" % CUT)
        f.write("Event-table files are read with pandas `usecols` for timestamp, side, status, entry and stop columns only; "
                "mfe/mae/forward-return columns are not parsed.\n\n")
        f.write("| file | min bar/ts used | max bar/ts used | rows | note |\n|---|---|---|---|---|\n")
        for n, a, b, k, x in ACCESS:
            f.write("| %s | %s | %s | %d | %s |\n" % (n, iso(a), iso(b), k, x))
        mx = max(b for _, _, b, _, _ in ACCESS)
        f.write("\nMaximum bar/decision time used: %s (%d) <= %d (a decision time equal to the cut is the close of a bar that opened before it). PASS.\n" % (iso(mx), mx, CUT))
        f.write("\nDEV_EXT 1m files (F:/MTS/data/dev_ext_2019_2021) are absent on this machine (JIS-NB): not opened.\n")

# ---- counts -----------------------------------------------------------------------------------------------------

COSTS = (0.0010, 0.0014)           # OURS scenarios (REVIEW_OPUS amendment 3)
COST_R_CAP = 0.25                  # OURS (PROJECT_VISION economics line)
MDE_GATE = 0.10                    # OURS per S unit, week clustered (REVIEW_OPUS F8)


def cell_of(s):
    out = []
    if s <= -2:
        out.append("S<=-2")
    if -1 <= s <= 1:
        out.append("S in -1..1")
    if s >= 2:
        out.append("S>=2")
    if s == 3:
        out.append("S=+3")
    return out


def sd_of(xs):
    return statistics.pstdev(xs) if len(xs) > 1 else 0.0


def fmt(x, nd=3):
    return "n/a" if x is None else ("%.*f" % (nd, x))


def write_counts(events, scored, dups, grid, bands, why, daily, h4):
    L = []
    A = L.append
    layers = list(scored)
    m_fam = 2 + len(layers) + 2                         # context (a) + pooled + one slope per layer + T2 + T4 (OURS family size)
    usable = {n: [(e, sc) for e, sc in rows if sc] for n, rows in scored.items()}
    A("# COUNTS (S1): context table x DEV event tables, counts only")
    A("")
    A("Generated by `MyTradingSys/backtest/layers/krown/run_counts.py`. Built from timestamps, side, entry "
      "price and stop distance. **No outcome column was opened** (mfe_R, mae_R, forward return: never parsed; the forward-window `status == OK` "
      "flag is a data-availability flag, used only to keep labelled events). Class C2, weight CRUCIAL.")
    A("")
    A("**Fee wall wording (F3).** The fee-wall metric is cost % divided by the mean signed gross move %, never cost/R alone. "
      "Cost/R below is a feasibility filter only (cost/R < 0.25, OURS) and cost/R falling is not evidence of improvement. "
      "Mean gross move is NOT computed in S1 (it is an outcome); the column `mean_gross_move_pct` is reserved empty.")
    A("")
    A("**Labels.** Every Krown field is an OURS implementation of KR-x (OURS impl. of KR-L10 trend, KR-Q01 BBWP, KR-S02 RSI zone, KR-Z zones, "
      "KR-R01 range; the OURS detectors failed recall, 3/12 and 0 strict hits: RECALL.md:36). Naive trend baselines `naive_trend_sma200` "
      "(close vs SMA200) and `naive_trend_ret20` (sign of the 20d return) are columns of `context_dev.csv` so S3 can race D1 against them (F12).")
    A("")
    A("## 1. Inputs and sets")
    A("| set | what | source | state |\n|---|---|---|---|")
    A("| 2022 | events with decision_ts 2022-01-01..2022-12-31 | event tables regenerated into `run/sealed/` (git-ignored) | joined |")
    A("| 2023-24H1 | events with decision_ts 2023-01-01..2024-06-30 | same | joined |")
    nd = sum(1 for r in daily if EXT_START <= r["open_ms"] < DEV_START)
    A("| DEV_EXT | 2020-01-01..2021-12-31 | daily context rows from `krown_daily` (%d rows); **4h rows and event tables: not built.** The DEV_EXT 1m files "
      "(F:/MTS/data/dev_ext_2019_2021) are absent on JIS-NB and every event-table loader is DEV-only; DECISION (OURS): report DEV_EXT as context-day "
      "counts (section 7) and leave event counts to a host that has the files | partial |" % nd)
    A("")
    A("DECISION (OURS): decision_ts = event bar open + event tf (checked per table against its own entry/event columns, see section 1b); "
      "the price used by D3 is the close of the 15m bar that closes at or before decision_ts, i.e. the event bar own close, which the event itself needs to exist "
      "(an at-close observation, not a written context row, so the 1 min write latency does not apply to it; `Ctx.price` is unit-tested); "
      "a row is usable iff available_at (bar close + 1 min, OURS) < decision_ts; identical (decision_ts, side) rows inside one layer count once. "
      "Event type per layer is the design's s6.0 table; layers it does not list are marked OURS.")
    A("")
    A("### 1b. Event timestamp rule, verified on the tables own columns")
    for line in SEMANTICS:
        A(line)
    A("")
    A("## 2. Layer inventory")
    A("| layer | tf | event type | events | duplicates dropped | status != OK dropped (value: count) | usable (D1, D2, D3 all available) | distinct ISO weeks (usable) | distinct days | verdict (MDE gate) |")
    A("|---|---|---|---|---|---|---|---|---|---|")
    for n in layers:
        sp, evs = events[n]
        u = usable[n]
        wk = len({week_key(e["dts"]) for e, _ in u})
        dy = len({day_key(e["dts"]) for e, _ in u})
        sS = [sc["S"] for _, sc in u]
        ms = kx.mde_slope(len(u), wk, sd_of(sS), m=m_fam) if u and sd_of(sS) > 0 else None
        vd = "TESTABLE" if ms is not None and ms <= MDE_GATE else "DESCRIPTIVE"
        dr = DROPS.get(n)
        drs = "%d (%s)" % (sum(dr[1].values()), ", ".join("%s: %d" % kv for kv in dr[1].items())) if dr and dr[1] else "0"
        A("| %s | %s | %s%s | %d | %d | %s | %d | %d | %d | %s (mde_slope %s R/S) |" % (
            n, sp["tf"], sp["etype"], " (OURS)" if n in OURS_TYPE else "", len(evs), dups[n], drs, len(u), wk, dy, vd, fmt(ms)))
    for n, why_, st in NOT_JOINED:
        A("| %s | | | | | | | | | %s: %s |" % (n, st, why_))
    A("")
    A("Holm family size for the MDE column: m = 2 + %d layers + 2 = %d (OURS: context read (a), pooled test, one slope per joined layer, T2, T4). "
      "Slope MDE = (z_holm(m) + 0.84) x sd_R x sqrt(deff) / (sqrt(n) x sd_S), deff = 1 + (n/weeks - 1) x rho, sd_R = 1.5 R and rho = 0.1 (both OURS; "
      "sd_R from the `context_factors_2026-10-16/COUNTS_DEV_EXT.md` n_needed line, rho a conservative guess: no outcome is read)." % (len(layers), m_fam))
    A("")
    allu = [(n, e, sc) for n in layers for e, sc in usable[n]]
    uniq = {}
    for _, e, sc in allu:                                  # layers fire on the same bars: one pooled row per (decision_ts, side)
        uniq.setdefault((e["dts"], e["side"]), (e, sc))
    pooled_unique = list(uniq.values())
    pn = len(pooled_unique)
    pw = len({week_key(e["dts"]) for e, _ in pooled_unique})
    pd_ = len({day_key(e["dts"]) for e, _ in pooled_unique})
    pS = [sc["S"] for _, sc in pooled_unique]
    pm = kx.mde_slope(pn, pw, sd_of(pS), m=m_fam)
    pm_day = kx.mde_slope(pn, pd_, sd_of(pS), m=m_fam)
    A("**Pooled (all joined layers, one row per distinct (decision_ts, side); %d layer-events collapse to %d):** n = %d, %d distinct ISO weeks, %d distinct days, sd(S) = %.3f; week-clustered MDE of the pooled slope "
      "= %s R per S unit (gate %.2f): **%s**. Day-clustered (footnote only, F2): %s." % (
          len(allu), pn, pn, pw, pd_, sd_of(pS), fmt(pm), MDE_GATE, "TESTABLE" if pm is not None and pm <= MDE_GATE else "DESCRIPTIVE", fmt(pm_day)))
    A("")
    n_eff = max(1, int(pn / (1 + (pn / pw - 1) * 0.1)))        # events / design effect (rho 0.1, OURS): the effective n for the gate
    gate = subprocess.run([sys.executable, str(REPO / "scripts" / "dev" / "prereg_gate.py"), "--n", str(n_eff), "--sd", "1.5", "--cost", "0.07",
                           "--m", str(m_fam), "--sd-source", "context_factors_2026-10-16/COUNTS_DEV_EXT.md n_needed line (sd 1.5 R, OURS)"],
                          capture_output=True, text=True)
    A("`prereg_gate.py --n %d --sd 1.5 --cost 0.07 --m %d` (n = %d unique pooled events / design effect %.2f = effective n, week clustering, rho 0.1 OURS; "
      "cost 0.07 R = median cost in R of the context_factors ledger, COUNTS_DEV_EXT.md). The gate tests a MEAN against cost, not a slope on S; "
      "it does not replace the slope verdict above): exit %d" % (n_eff, m_fam, pn, pn / n_eff, gate.returncode))
    A("```\n" + (gate.stdout + gate.stderr).strip() + "\n```")
    A("")
    A("## 3. Shares and S histogram per layer (usable events)")
    A("| layer | n | D1 -1/0/+1 % | D2 -1/0/+1 % | D3 -1/0/+1 % | S=-3 | -2 | -1 | 0 | +1 | +2 | +3 |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|")

    def shares(vals):
        n = len(vals)
        c = Counter(vals)
        return "/".join("%.1f" % (100 * c[k] / n) if n else "n/a" for k in (-1, 0, 1))

    def row(name, u):
        cS = Counter(sc["S"] for _, sc in u)
        return "| %s | %d | %s | %s | %s | %s |" % (
            name, len(u), shares([sc["d1"] for _, sc in u]), shares([sc["d2"] for _, sc in u]), shares([sc["d3"] for _, sc in u]),
            " | ".join(str(cS[k]) for k in (-3, -2, -1, 0, 1, 2, 3)))
    for n in layers:
        A(row(n, usable[n]))
    A(row("POOLED (unique)", pooled_unique))
    A("")
    cS = Counter(pS)
    ge2 = sum(v for k, v in cS.items() if k >= 2) / pn
    le2 = sum(v for k, v in cS.items() if k <= -2) / pn
    A("Pooled shares against the review's expected shares (OURS approximations, REVIEW_OPUS F8): S=+3 **%.2f %%** (expected about 1.6 %%), "
      "S>=+2 **%.1f %%** (about 12 %%), S<=-2 **%.1f %%** (about 13 %%)." % (100 * cS[3] / pn, 100 * ge2, 100 * le2))
    A("")
    A("Usable share (every context field available at decision time): " + ", ".join(
        "%s %.0f %%" % (n, 100 * len(usable[n]) / max(1, len(events[n][1]))) for n in layers) + ".")
    A("")
    A("## 4. Cells: n, distinct ISO weeks, week-clustered MDE of a cell mean (R)")
    A("`mde_week` = (z_holm(m) + 0.84) x 1.5 R x sqrt(deff) / sqrt(n), deff as above (rho 0.1, OURS); `mean_gross_move_pct` is reserved and empty. "
      "Same sign in both sets is the later pass bar and is not tested here. DEV_EXT rows: no events (see section 1). Cells overlap by construction "
      "(S=+3 is inside S>=2). Full table also in `counts_cells.csv`.")
    A("| layer | cell | set | n | iso_weeks | mde_week | mean_gross_move_pct |")
    A("|---|---|---|---|---|---|---|")
    csvrows = []
    for n in layers + ["POOLED"]:
        pool = pooled_unique if n == "POOLED" else usable[n]
        for cell in ("S<=-2", "S in -1..1", "S>=2", "S=+3"):
            for st in ("2022", "2023-24H1", "DEV_EXT", "DEV (pooled)"):
                if st == "DEV_EXT":
                    k, w = 0, 0
                else:
                    sel = [e for e, sc in pool if cell in cell_of(sc["S"]) and (st == "DEV (pooled)" or set_of(e["dts"]) == st)]
                    k, w = len(sel), len({week_key(e["dts"]) for e in sel})
                md = kx.mde_mean(k, w, m=m_fam) if k else None
                A("| %s | %s | %s | %d | %d | %s | |" % (n, cell, st, k, w, fmt(md)))
                csvrows.append((n, cell, st, k, w, md))
    A("")
    A("## 5. Cost/R distribution (feasibility filter only, F3)")
    A("cost/R = round-trip cost % x entry price / stop distance; stop distance = the table's own R (`risk_r`, `r`, `risk_price` or `risk_range`: "
      "known at entry, not an outcome). Costs 0.10 % and 0.14 % round trip (OURS scenarios); the 0.25 cap is OURS. cost/R falling is not evidence of improvement.")
    A("| layer | n with stop | median cost/R @0.10 % | share < 0.25 @0.10 % | median cost/R @0.14 % | share < 0.25 @0.14 % |")
    A("|---|---|---|---|---|---|")
    for n in layers:
        xs = []
        for e, sc in usable[n]:
            ent = e["entry"] if e["entry"] else sc["px"]
            if e["risk"] and e["risk"] > 0 and ent:
                xs.append(ent / e["risk"])
        if not xs:
            A("| %s | 0 | n/a | n/a | n/a | n/a |" % n)
            continue
        c1 = [COSTS[0] * x for x in xs]
        c2 = [COSTS[1] * x for x in xs]
        A("| %s | %d | %.3f | %.1f %% | %.3f | %.1f %% |" % (n, len(xs), statistics.median(c1), 100 * sum(1 for x in c1 if x < COST_R_CAP) / len(xs),
                                                             statistics.median(c2), 100 * sum(1 for x in c2 if x < COST_R_CAP) / len(xs)))
    A("")
    A("wlow_bounce: events only (the file carries no stop).")
    A("")
    A("## 6. Frozen bands (from the counts and the grid below only; OURS)")
    A("Pass 1 rule, written before the numbers were looked at: D3 = smallest `near_atr` then smallest `edge` whose pooled D3=+1 and D3=-1 shares are both in 15-30 % "
      "(REVIEW_OPUS F10, OURS); D2 = keep BBWP_4h exhaustion at 85 unless pooled D2=+1 or D2=-1 is below 5 % of usable events. "
      "DECISION (OURS, post-hoc but before any outcome was opened): pass 1 (12 points) found no in-band point because D3=+1 is saturated, so pass 2 added "
      "tighter values and the pick is the loosest in-band point (largest near_atr, then largest edge); the original rule would have given the tightest point "
      "(near 0.05, edge 0.05). The coverage population is the usable events (D1, D2, D3 all available). Every grid point is a "
      "trial and is logged in `research/layer_lab/TRIALS.md`.")
    A("")
    A("| pass | D3 near_atr (x ATR14 1d) | range edge frac | pooled n | D3=+1 % | D3=-1 % | D3=0 % | both inside 15-30 % |")
    A("|---|---|---|---|---|---|---|---|")
    for g in grid:
        ok = g[3] and 0.15 <= g[4] <= 0.30 and 0.15 <= g[5] <= 0.30
        A("| %s | %s | %s | %d | %.1f | %.1f | %.1f | %s |" % (g[0], g[1], g[2], g[3], 100 * g[4], 100 * g[5], 100 * g[6], "YES" if ok else "no"))
    A("")
    A("| D2 bbwp_high | pooled n | D2=+1 % | D2=-1 % | D2=0 % |\n|---|---|---|---|---|")
    for g in why["d2grid"]:
        A("| %d | %d | %.1f | %.1f | %.1f |" % (g[0], g[1], 100 * g[2], 100 * g[3], 100 * g[4]))
    A("")
    if why["d3_found"]:
        g = why["d3_pick"]
        A("**FROZEN D3:** near_atr = %s, range edge = %s (pooled D3=+1 %.1f %%, D3=-1 %.1f %%); **FROZEN D2:** bbwp_high = %d (pooled D2=+1 %.1f %%, D2=-1 %.1f %%). "
          "D2 fresh-expansion rule: BBWP_4h min of the previous 6 bars <= 30 and now > 50 (OURS / SOURCED KR-Q02 confirm 50). "
          "No band changes after this file is committed." % (g[1], g[2], 100 * g[4], 100 * g[5], bands["bbwp_high"], 100 * why["d2_pick"][2], 100 * why["d2_pick"][3]))
    else:
        A("**FROZEN D3: no grid point put both D3=+1 and D3=-1 inside 15-30 %%.** DECISION (OURS): keep the defaults near_atr = %s, edge = %s and report "
          "their coverage in the grid above. **FROZEN D2:** bbwp_high = %d. No band changes after this file is committed." % (
              bands["near_atr"], bands["edge"], bands["bbwp_high"]))
    A("")
    A("## 7. Context-day counts (all calendar days, no events): DEV_EXT and DEV")
    A("| set | days with a full daily row | trend_1d up/range/down % | trend_1w up/range/down % | naive SMA200 up/down % | naive ret20 up/down % | ISO weeks |")
    A("|---|---|---|---|---|---|---|")
    for nm, lo, hi in (("DEV_EXT 2020-21", EXT_START, DEV_START), ("DEV 2022", DEV_START, Y2023), ("DEV 2023-24H1", Y2023, CUT)):
        rs = [r for r in daily if lo <= r["open_ms"] < hi and r["trend_1d_ours"] is not None and r["trend_1w_ours"] is not None
              and r["naive_trend_sma200"] is not None and r["naive_trend_ret20"] is not None]

        def tri(key):
            c = Counter(r[key] for r in rs)
            return "%.0f/%.0f/%.0f" % tuple(100 * c[k] / len(rs) for k in (1, 0, -1))

        def duo(key):
            c = Counter(r[key] for r in rs)
            return "%.0f/%.0f" % (100 * c[1] / len(rs), 100 * c[-1] / len(rs))
        A("| %s | %d | %s | %s | %s | %s | %d |" % (nm, len(rs), tri("trend_1d_ours"), tri("trend_1w_ours"), duo("naive_trend_sma200"),
                                                  duo("naive_trend_ret20"), len({week_key(r["open_ms"]) for r in rs})))
    A("")
    A("trend_1d is close to a year dummy (2022 bear, 2023-24H1 bull; F2): see the split above. 4h context (BBWP_4h) rows: DEV %d; DEV_EXT 0 (file absent)." %
      sum(1 for r in h4 if r["open_ms"] >= DEV_START))
    A("")
    A("## 8. Checks required by PRE_REG_S1_COUNTS.md s1")
    A("- F2: sections 2 and 4 carry n, iso_weeks, mde_week per layer and cell for sets 2022, 2023-24H1, DEV_EXT (DEV_EXT empty: files missing); day-clustered MDE only as a footnote (pooled line).")
    A("- F3: fee-wall wording in the header; section 5 is a feasibility filter; no gross-move or R-outcome value anywhere.")
    A("- F8: real shares and S histogram in section 3 against the expected shares; TESTABLE / DESCRIPTIVE flag in section 2; bands in section 6; `prereg_gate.py` run in section 2.")
    A("- F12: every Krown field is `_ours` / labelled; naive baselines are columns of `context_dev.csv`.")
    A("- Not met in full: DEV_EXT event counts (host lacks dev_ext_2019_2021 and all event loaders are DEV-only); funding_extreme, session_levels (inputs absent), fabio_lvn_touch (no side).")
    (RUN / "COUNTS.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    with open(RUN / "counts_cells.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["layer", "cell", "set", "n", "iso_weeks", "mde_week"])
        for r in csvrows:
            w.writerow([r[0], r[1], r[2], r[3], r[4], "" if r[5] is None else "%.4f" % r[5]])
    (RUN / "bands.json").write_text(json.dumps({"bands": bands, "label": "OURS, frozen from COUNTS.md counts only"}, indent=1) + "\n",
                                    encoding="utf-8", newline="\n")


def main():
    RUN.mkdir(parents=True, exist_ok=True)
    dt_, do_, dh_, dl_, dc_, dv_ = load_daily()
    daily = kx.build_daily_rows(dt_, do_, dh_, dl_, dc_, dv_)
    z1 = load_npz("1h")
    h4t, h4o, h4h, h4l, h4c = kx.aggregate_4h(z1["t"].tolist(), z1["o"].tolist(), z1["h"].tolist(), z1["l"].tolist(), z1["c"].tolist())
    h4 = kx.build_h4_rows(h4t, h4o, h4h, h4l, h4c)
    z15 = load_npz("15m")
    c15 = {int(a): float(b) for a, b in zip(z15["t"], z15["c"])}
    ctx = Ctx(daily, h4, c15)
    write_context_csv(daily, h4)

    check_semantics()
    events = {}
    for sp in SPECS:
        events[sp["name"]] = (sp, load_events(sp))
    events["wlow_bounce"] = (spec("wlow_bounce", "events.csv (repo)", "trigger_open", H1, 1, F, "1h"), load_wlow())
    dups = {}
    for name, (sp, evs) in list(events.items()):
        note("event table %s [%s]" % (sp["csv"], name), min(e["dts"] for e in evs), max(e["dts"] for e in evs), len(evs),
             "timestamp + side + status + entry + stop columns only")
        seen, keep = set(), []                           # identical (decision_ts, side) inside a layer count once: DECISION (OURS)
        for e in sorted(evs, key=lambda e: (e["dts"], e["side"])):
            k = (e["dts"], e["side"])
            if k not in seen:
                seen.add(k)
                keep.append(e)
        dups[name] = len(evs) - len(keep)
        events[name] = (sp, keep)

    grid, bands, why = freeze_bands(events, ctx)
    scored = {}
    for name, (sp, evs) in events.items():
        scored[name] = [(e, score(e, sp["etype"], ctx, bands)) for e in evs]
    write_joined(scored)
    write_counts(events, scored, dups, grid, bands, why, daily, h4)
    write_access()
    print("done", bands)


if __name__ == "__main__":
    main()