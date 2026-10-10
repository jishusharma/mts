import sys
sys.dont_write_bytecode = True
"""Descriptive diagnostics on the EXISTING Tom outcome backtest (card tom-probe-diag-btc, PROBE_PLAN H2/H3/H4).

No rule change, no tuning: signals, fills and exits come unchanged from tom_bt.signals / tom_bt.run_variant. This module
only adds, per filled trade, what the price did (MFE / MAE in R), when it was entered (session clock) and how it was
selected (first per session, proof count, tier), then tabulates gross R with bootstrap CIs.

Holdout 2026-06-26.. is burned (B147): rows at or after it are dropped before any signal is built.

Conventions (hand-checked in test_tom_probe_diag.py):
- R = |entry - stop|. MFE / MAE are in R. A 1m bar's high/low order is unknown, so:
  * MFE counts bars strictly AFTER the fill bar (the fill bar's high may precede the fill);
  * a stopped trade's stop bar is excluded from MFE (the simulator is stop-first), included in MAE;
  * MAE counts the fill bar (the simulator assumes the stop comes after the fill).
- mfe_exit / mae_exit: fill .. exit of the simulated trade. mfe_4h / mae_4h: fill .. fill + 240 1m bars regardless of
  the exit (what a manager could have had). mfe_4h_pre_stop: the 4 h MFE truncated before the first bar that touches
  the stop ("MFE before the stop").
- Sessions: local opens converted with zoneinfo (DST-correct): Asia 09:00 Asia/Tokyo, DAX 09:00 Europe/Berlin,
  London 08:00 Europe/London, US_open 09:30 America/New_York, US_close 16:00 America/New_York. Opens are generated
  every calendar day (BTC trades 24/7); the weekday/weekend split is a separate axis (UTC day of the entry).
  DAX 09:00 CET and London 08:00 UK are the same UTC instant in every DST regime, so they form one label DAX/London.
- Entry time = the fill minute (not the signal time).

Pre-declared GO / SKIP rules (written before the data was read; PROBE_PLAN gives no numbers, these are the reading of it):
- M (management): GO iff >= 25 % of trades reach MFE >= 1 R before the stop (4 h window) AND >= 10 % reach 2 R.
- Q (selection): GO iff any selection comparison (first-per-session vs rest, first-per-UTC-day vs rest, each proof
  level vs rest, each tier vs rest; groups with n >= 100) has a Bonferroni bootstrap CI of the gross R difference
  excluding 0.
- S (session): GO iff any session window (5 labels x {0-2h, 2-4h} after the open, n >= 100) has a mean gross R higher
  than all other trades with a Bonferroni CI of the difference above 0 (a significantly WORSE window is informational).
"""
import datetime as dt
import json
import os
import statistics
import sys as _sys
from collections import defaultdict
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
_sys.path.insert(0, str(HERE))
_sys.path.insert(0, str(ROOT))
import tom_bt as T  # noqa: E402

ROWS_DIR = Path(os.environ.get("TOM_PROBE_ROWS", r"F:\MTS\data\tom_bt_2026-10-07"))
RAW_DIR = Path(os.environ.get("TOM_RAW_DIR", r"F:\MTS\data\tom_raw")) / "klines"
OUT_TRADES = Path(os.environ.get("TOM_PROBE_OUT", r"F:\MTS\data\tom_probe_diag"))
DOC = ROOT / "MyTradingSys" / "research" / "tom_transfer_2026-10-11" / "DIAG_BTC.md"

T_DEV = dt.datetime(2025, 9, 1, tzinfo=dt.timezone.utc).timestamp()
T_HOLD = dt.datetime(2026, 6, 26, tzinfo=dt.timezone.utc).timestamp()  # burned holdout: never read
WINDOW_BARS = 240  # 4 h of 1m bars

SESSIONS = [("Asia", "Asia/Tokyo", 9, 0), ("DAX", "Europe/Berlin", 9, 0), ("London", "Europe/London", 8, 0),
            ("US_open", "America/New_York", 9, 30), ("US_close", "America/New_York", 16, 0)]
_TZ = {name: ZoneInfo(tz) for name, tz, _, _ in SESSIONS}

M_SHARE_1R, M_SHARE_2R = 0.25, 0.10
MIN_GROUP_N = 100


# ---------------------------------------------------------------- excursions
def excursions(b, fill_i, exit_i, reason, side, entry, stop, window=WINDOW_BARS):
    """MFE / MAE in R for one filled trade. See module docstring for the bar-order conventions."""
    sgn = 1.0 if side == "long" else -1.0
    risk = abs(entry - stop)
    n = b.n
    last_mfe = exit_i - 1 if reason == "stop" else exit_i

    def fav(i):
        return sgn * ((b.h[i] if sgn > 0 else b.l[i]) - entry) / risk

    def adv(i):
        return sgn * (entry - (b.l[i] if sgn > 0 else b.h[i])) / risk

    mfe_exit = max([0.0] + [fav(i) for i in range(fill_i + 1, min(last_mfe, n - 1) + 1)])
    mae_exit = max([0.0] + [adv(i) for i in range(fill_i, min(exit_i, n - 1) + 1)])
    end = min(fill_i + window, n - 1)
    mfe_4h = max([0.0] + [fav(i) for i in range(fill_i + 1, end + 1)])
    mae_4h = max([0.0] + [adv(i) for i in range(fill_i, end + 1)])
    mfe_ps = 0.0
    for i in range(fill_i + 1, end + 1):
        touched = (b.l[i] <= stop) if sgn > 0 else (b.h[i] >= stop)
        if touched:
            break
        mfe_ps = max(mfe_ps, fav(i))
    return dict(mfe_exit=mfe_exit, mae_exit=mae_exit, mfe_4h=mfe_4h, mae_4h=mae_4h, mfe_4h_pre_stop=mfe_ps,
                win_complete=(fill_i + window) <= n - 1)


# ---------------------------------------------------------------- sessions
def _latest_opens(ts_s):
    """[(label, open_ts_int)] latest open at or before ts for each session; equal instants merge into one label."""
    by_ts = {}
    for name, _tz, hh, mm in SESSIONS:
        tz = _TZ[name]
        u = dt.datetime.fromtimestamp(ts_s, dt.timezone.utc)
        d = u.astimezone(tz).date()
        for back in (0, 1):
            dd = d - dt.timedelta(days=back)
            op = dt.datetime(dd.year, dd.month, dd.day, hh, mm, tzinfo=tz)
            if op.timestamp() <= ts_s + 1e-6:
                by_ts.setdefault(int(round(op.timestamp())), []).append(name)
                break
    return [("/".join(names), ts) for ts, names in by_ts.items()]


def session_of(ts_s):
    """(label, open_ts, hours_since_open) of the most recent session open before ts."""
    label, ots = max(_latest_opens(ts_s), key=lambda x: x[1])
    return label, float(ots), (ts_s - ots) / 3600.0


def hour_bucket(h):
    return "0-2h" if h < 2.0 else "2-4h" if h < 4.0 else "later"


def day_kind(ts_s):
    return "weekend" if dt.datetime.fromtimestamp(ts_s, dt.timezone.utc).weekday() >= 5 else "weekday"


def windows_of(ts_s, max_h=4.0):
    """Every session window (label, bucket) that contains ts: opens at most max_h hours old. Overlaps allowed."""
    out = []
    order = {nm: i for i, (nm, _a, _b, _c) in enumerate(SESSIONS)}
    for label, ots in sorted(_latest_opens(ts_s), key=lambda x: order[x[0].split("/")[0]]):
        h = (ts_s - ots) / 3600.0
        if h < max_h:
            out.append((label, hour_bucket(h)))
    return out


# ---------------------------------------------------------------- data
def load_rows(rows_dir=ROWS_DIR):
    """Rows strictly before the burned holdout; later rows are never kept."""
    rows = []
    for p in sorted(Path(rows_dir).glob("*.rows.jsonl")):
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                r = json.loads(line)
                if r["t"] < T_HOLD:
                    rows.append(r)
    rows.sort(key=lambda r: r["t"])
    return rows


def period_of(t):
    return "hist_2022-01..2025-08" if t < T_DEV else "dev_2025-09..2026-06-25"


def build_trades(rows, b, variant):
    """Filled, resolved trades of tom_bt.run_variant(default fees) with excursions + session + selection tags."""
    sigs = T.signals(rows, variant)
    trs = T.run_variant(sigs, b)
    out = []
    for t in trs:
        if not (t.get("filled") and t["reason"] in ("target", "stop", "timeout")):
            continue
        entry = float(t["zprice"])
        stop = float(t["stop"])
        ts = (b.t0 + t["fill_i"] * 60000) / 1000.0
        x = excursions(b, t["fill_i"], t["exit_i"], t["reason"], t["dir"], entry, stop)
        label, ots, hrs = session_of(ts)
        d = dict(sig_t=t["t"], entry_ts=ts, side=t["dir"], reason=t["reason"], gross_r=t["gross_r"], proof=t.get("proof"),
                 tier=t.get("tier"), setup=t.get("setup"), zone_tf=t["zone_tf"], t=t["t"], zprice=t["zprice"],
                 stop=t["stop"], target=t["target"], dir=t["dir"], filled=True,
                 stop_pct=abs(entry - stop) / entry * 100.0, period=period_of(t["t"]),
                 sess=label, sess_open=ots, sess_hrs=hrs, sess_bucket=hour_bucket(hrs), day_kind=day_kind(ts),
                 utc_day=int(ts // 86400), windows=windows_of(ts))
        d.update(x)
        out.append(d)
    out.sort(key=lambda d: d["entry_ts"])
    first_sess, first_day = set(), set()
    for d in out:  # chronological by entry
        k = (d["sess"], d["sess_open"])
        d["first_in_session"] = k not in first_sess
        first_sess.add(k)
        d["first_in_day"] = d["utc_day"] not in first_day
        first_day.add(d["utc_day"])
    return out


# ---------------------------------------------------------------- tables
def _ci(x):
    lo, hi = T.boot_ci(x)
    return lo, hi


def _stat(trs, null_fn=None):
    g = [t["gross_r"] for t in trs]
    n = len(g)
    if n == 0:
        return "0 | - | - | - | - | -"
    lo, hi = _ci(g)
    tgt = sum(1 for t in trs if t["reason"] == "target")
    null = ""
    if null_fn is not None:
        nv = null_fn(trs)
        null = "%+.2f" % nv if nv is not None else "n<30"
    return "%d | %+.3f [%+.3f, %+.3f] | %+.3f | %d | %.1f%% | %s" % (
        n, sum(g) / n, lo, hi, statistics.median(g), tgt, 100.0 * (sum(1 for x in g if x > 0)) / n, null)


GR_HDR = ("| group | n | share | mean gross R [95% CI] | median R | target hits | R>0 | null mean R |\n"
          "|---|---|---|---|---|---|---|---|\n")


def gr_table(groups, total_n, null_fn=None):
    s = GR_HDR
    for name, trs in groups:
        n = len(trs)
        s += "| %s | %s | %.1f%% | %s |\n" % (name, n, 100.0 * n / total_n if total_n else 0, _stat(trs, null_fn).split(" | ", 1)[1])
    return s


def group_by(trades, fn, order=None):
    d = defaultdict(list)
    for t in trades:
        d[fn(t)].append(t)
    keys = order if order else sorted(d, key=str)
    return [(str(k), d[k]) for k in keys if k in d]


def share_row(label, trs, key, thr=(1, 2, 3)):
    n = len(trs)
    if n == 0:
        return "| %s | 0 | - | - | - | - | - |\n" % label
    parts = []
    for k in thr:
        c = sum(1 for t in trs if t[key] >= k)
        lo, hi = T.wilson(c, n)
        parts.append("%.1f%% [%.1f-%.1f]" % (100.0 * c / n, 100 * lo, 100 * hi))
    mfe = [t["mfe_exit"] for t in trs]
    mae = [t["mae_exit"] for t in trs]
    ratio = [t["mfe_exit"] / t["mae_exit"] for t in trs if t["mae_exit"] > 0]
    return "| %s | %d | %s | %.2f | %.2f | %.2f |\n" % (label, n, " | ".join(parts), statistics.median(mfe),
                                                         statistics.median(mae), statistics.median(ratio) if ratio else float("nan"))


MFE_HDR = ("| group | n | MFE>=1R | MFE>=2R | MFE>=3R | median MFE_exit | median MAE_exit | median MFE/MAE |\n"
           "|---|---|---|---|---|---|---|---|\n")


def mfe_tables(trades, key):
    s = MFE_HDR
    stopped = [t for t in trades if t["reason"] == "stop"]
    s += share_row("all filled", trades, key)
    s += share_row("stopped out", stopped, key)
    s += share_row("target", [t for t in trades if t["reason"] == "target"], key)
    s += share_row("timeout", [t for t in trades if t["reason"] == "timeout"], key)
    return s


# ---------------------------------------------------------------- verdict rules
def m_verdict(trades):
    n = len(trades)
    s1 = sum(1 for t in trades if t["mfe_4h_pre_stop"] >= 1) / n
    s2 = sum(1 for t in trades if t["mfe_4h_pre_stop"] >= 2) / n
    go = s1 >= M_SHARE_1R and s2 >= M_SHARE_2R
    return go, s1, s2


def q_verdict(trades):
    """Selection comparisons (group vs the rest), Bonferroni across the comparisons actually made."""
    comps = []
    comps.append(("first signal per session vs rest", [t for t in trades if t["first_in_session"]], [t for t in trades if not t["first_in_session"]]))
    comps.append(("first signal per UTC day vs rest", [t for t in trades if t["first_in_day"]], [t for t in trades if not t["first_in_day"]]))
    for p in sorted({t["proof"] for t in trades}, key=str):
        comps.append(("proof=%s vs rest" % p, [t for t in trades if t["proof"] == p], [t for t in trades if t["proof"] != p]))
    for tier in sorted({t["tier"] for t in trades}, key=str):
        comps.append(("tier=%s vs rest" % tier, [t for t in trades if t["tier"] == tier], [t for t in trades if t["tier"] != tier]))
    comps = [c for c in comps if len(c[1]) >= MIN_GROUP_N and len(c[2]) >= MIN_GROUP_N]
    m = max(1, len(comps))
    rows, go = [], False
    for label, a, rest in comps:
        d, lo, hi = T.diff_ci([t["gross_r"] for t in a], [t["gross_r"] for t in rest], alpha=0.05 / m)
        sig = lo > 0 or hi < 0
        go = go or sig
        rows.append((label, len(a), len(rest), d, lo, hi, sig))
    return go, rows, m


def s_verdict(trades):
    wins = defaultdict(list)
    for t in trades:
        for w in t["windows"]:
            wins[w].append(t)
    order = [nm if nm != "DAX" and nm != "London" else "DAX/London" for nm, _a, _b, _c in SESSIONS]
    labels = []
    for o in order:
        if o not in labels:
            labels.append(o)
    cands = [(lab, bk) for lab in labels for bk in ("0-2h", "2-4h") if len(wins.get((lab, bk), [])) >= MIN_GROUP_N]
    m = max(1, len(cands))
    rows, go = [], False
    for lab, bk in cands:
        a = wins[(lab, bk)]
        ida = {id(t) for t in a}
        rest = [t for t in trades if id(t) not in ida]
        d, lo, hi = T.diff_ci([t["gross_r"] for t in a], [t["gross_r"] for t in rest], alpha=0.05 / m)
        better = lo > 0
        go = go or better
        rows.append(("%s %s" % (lab, bk), len(a), len(rest), d, lo, hi, better))
    return go, rows, m


# ---------------------------------------------------------------- report
def make_null_fn(b):
    from tom_bt_report import random_entry_null  # reuse of the existing helper (same-day random entry, same geometry)

    cache = {}

    def fn(trs):
        key = tuple(id(t) for t in trs)
        if key not in cache:
            r = random_entry_null(trs, b, n_perm=100)
            cache[key] = r[2] if r else None
        return cache[key]
    return fn


def section(variant, trades, b, null_fn):
    N = len(trades)
    md = []
    md.append("\n## Variant `%s`: %d filled trades (hist %d, dev %d)\n" % (
        variant, N, sum(1 for t in trades if t["period"].startswith("hist")), sum(1 for t in trades if t["period"].startswith("dev"))))
    fr = N and (sum(t["gross_r"] for t in trades) / N)
    risks = sorted(t["stop_pct"] for t in trades)
    md.append("Mean gross R %+.3f; exit mix %s; median stop %.3f%% of price; 4 h window complete for %d of %d trades; "
              "entries %s .. %s.\n" % (
                  fr, dict(sorted(((k, sum(1 for t in trades if t["reason"] == k)) for k in ("target", "stop", "timeout")))),
                  risks[len(risks) // 2], sum(1 for t in trades if t["win_complete"]), N,
                  dt.datetime.fromtimestamp(trades[0]["entry_ts"], dt.timezone.utc).strftime("%Y-%m-%d"),
                  dt.datetime.fromtimestamp(trades[-1]["entry_ts"], dt.timezone.utc).strftime("%Y-%m-%d")))
    md.append("\n### by period (gross R)\n" + gr_table(group_by(trades, lambda t: t["period"]) + [("ALL", trades)], N, null_fn))

    md.append("\n### a) MFE / MAE in R\n")
    md.append("MFE before the simulated exit (stopped trades: before the stop):\n\n" + mfe_tables(trades, "mfe_exit"))
    md.append("\nMFE over the 4 h after the fill, truncated before the first bar that touches the stop (\"MFE before the stop\"):\n\n"
              + mfe_tables(trades, "mfe_4h_pre_stop"))
    md.append("\nMFE over the full 4 h after the fill, ignoring the stop (upper bound of what a manager could have had):\n\n"
              + mfe_tables(trades, "mfe_4h"))
    md.append("\n4 h MAE medians: all %.2f R, stopped %.2f R.\n" % (
        statistics.median([t["mae_4h"] for t in trades]), statistics.median([t["mae_4h"] for t in trades if t["reason"] == "stop"] or [float("nan")])))

    md.append("\n### b) Session (entry = fill minute; most recent session open; null = same-day random entry, 100 draws)\n")
    labels = ["Asia", "DAX/London", "US_open", "US_close"]
    part = []
    for lab in labels:
        for bk in ("0-2h", "2-4h", "later"):
            part.append(("%s %s" % (lab, bk), [t for t in trades if t["sess"] == lab and t["sess_bucket"] == bk]))
    md.append("Partition by the most recent open of the five (DAX 09:00 CET and London 08:00 UK coincide in UTC, one label):\n\n"
              + gr_table(part, N, null_fn))
    md.append("\nBy session label only:\n\n" + gr_table(group_by(trades, lambda t: t["sess"], labels), N, null_fn))
    md.append("\nBy hours since the most recent open:\n\n" + gr_table(group_by(trades, lambda t: t["sess_bucket"], ["0-2h", "2-4h", "later"]), N, null_fn))
    wins = defaultdict(list)
    for t in trades:
        for w in t["windows"]:
            wins[w].append(t)
    ow = [("%s %s (overlaps allowed)" % w, wins[w]) for w in sorted(wins, key=lambda w: (labels.index(w[0]), w[1]))]
    none = [t for t in trades if not t["windows"]]
    md.append("\nWindow view (a trade can sit in several 0-4 h windows); outside every window last:\n\n"
              + gr_table(ow + [("outside every 0-4h window", none)], N, null_fn))
    md.append("\nWeekday vs weekend (UTC day of the fill):\n\n" + gr_table(group_by(trades, lambda t: t["day_kind"], ["weekday", "weekend"]), N, null_fn))

    md.append("\n### c) Selection\n")
    md.append("First filled trade per session instance (same label + open) vs the rest; first per UTC day vs the rest "
              "(one-at-a-time filtering of tom_bt.run_variant applies before this split):\n\n"
              + gr_table([("first in session", [t for t in trades if t["first_in_session"]]),
                          ("not first in session", [t for t in trades if not t["first_in_session"]]),
                          ("first in UTC day", [t for t in trades if t["first_in_day"]]),
                          ("not first in UTC day", [t for t in trades if not t["first_in_day"]])], N, null_fn))
    md.append("\nBy proof count:\n\n" + gr_table(group_by(trades, lambda t: t["proof"]), N, null_fn))
    md.append("\nBy tier (math.tier of the rank-1 candidate):\n\n" + gr_table(group_by(trades, lambda t: t["tier"]), N, null_fn))
    md.append("\nBy setup type:\n\n" + gr_table(group_by(trades, lambda t: t["setup"]), N, null_fn))

    gm, s1, s2 = m_verdict(trades)
    gq, qrows, qm = q_verdict(trades)
    gs, srows, sm = s_verdict(trades)
    md.append("\n### Verdict inputs (`%s`)\n" % variant)
    md.append("- M: MFE >= 1R before the stop (4 h) in %.1f%% of trades, >= 2R in %.1f%% (rule: GO iff >= %.0f%% and >= %.0f%%) -> **%s**\n" % (
        100 * s1, 100 * s2, 100 * M_SHARE_1R, 100 * M_SHARE_2R, "GO" if gm else "SKIP"))
    md.append("- Q: %d comparisons with both sides n >= %d, Bonferroni alpha = 0.05/%d -> **%s**\n\n" % (len(qrows), MIN_GROUP_N, qm, "GO" if gq else "SKIP"))
    md.append("| comparison | n group | n rest | diff gross R | Bonferroni CI | excludes 0 |\n|---|---|---|---|---|---|\n")
    for lab, na, nr, d, lo, hi, sig in qrows:
        md.append("| %s | %d | %d | %+.3f | [%+.3f, %+.3f] | %s |\n" % (lab, na, nr, d, lo, hi, "yes" if sig else "no"))
    md.append("\n- S: %d windows with n >= %d, Bonferroni alpha = 0.05/%d, window vs all other trades -> **%s**\n\n" % (len(srows), MIN_GROUP_N, sm, "GO" if gs else "SKIP"))
    md.append("| window | n window | n rest | diff gross R | Bonferroni CI | CI above 0 |\n|---|---|---|---|---|---|\n")
    for lab, na, nr, d, lo, hi, ok in srows:
        md.append("| %s | %d | %d | %+.3f | [%+.3f, %+.3f] | %s |\n" % (lab, na, nr, d, lo, hi, "yes" if ok else "no"))
    return "".join(md), dict(M=gm, Q=gq, S=gs, s1=s1, s2=s2, qrows=qrows, srows=srows)


def main(variants=("watch_episode", "p4_episode")):
    rows = load_rows()
    b = T.load_bars_1m(RAW_DIR)
    OUT_TRADES.mkdir(parents=True, exist_ok=True)
    null_fn = make_null_fn(b)
    docs, res, ns = [], {}, {}
    for v in variants:
        trades = build_trades(rows, b, v)
        ns[v] = len(trades)
        with open(OUT_TRADES / ("trades_%s.jsonl" % v), "w", encoding="utf-8", newline="\n") as fh:
            for t in trades:
                fh.write(json.dumps({k: x for k, x in t.items() if k != "windows"}) + "\n")
        text, r = section(v, trades, b, null_fn)
        docs.append(text)
        res[v] = r
        print(v, len(trades), "M", r["M"], "Q", r["Q"], "S", r["S"], flush=True)
    return rows, b, docs, res, ns


def write_doc(rows, b, docs, res, ns, path=DOC):
    pri = "watch_episode"
    nl = "\n"
    head = [
        "# DIAG_BTC: Tom probe diagnostics on the existing BTC backtest (H2 selection / H3 management / H4 session)" + nl + nl,
        "Card `tom-probe-diag-btc`. Generated by `MyTradingSys/backtest/tom_probe_diag.py` (rerun: "
        "`python MyTradingSys/backtest/tom_probe_diag.py`). Descriptive only: no rule change, no tuning; nothing here "
        "becomes a rule without a PROBE_PLAN pre-registration." + nl + nl,
        "## Data used" + nl + nl,
        "- Rows: `%s` (%d rows with t < 2026-06-26 after dropping the burned holdout; holdout rows were never kept). "
        "1m bars: `%s` (%d bars, zero gaps checked at load)." % (ROWS_DIR, len(rows), RAW_DIR, b.n) + nl,
        "- Periods: hist = 2022-01-20..2025-08-31, dev = 2025-09-01..2026-06-25. Holdout 2026-06-26.. excluded (burned, B147)." + nl,
        "- Trades: `tom_bt.signals(rows, variant)` + `tom_bt.run_variant(..., default fees)` unchanged (limit at zone price, "
        "stop/target from the rank-1 candidate, 8 zone-tf bars, one trade at a time, stop-first). Variants with trades: "
        "`watch_episode` (n = %d, WATCH+SETUP_FORMING episodes, proof >= 3; primary) and `p4_episode` (n = %d, proof >= 4; a "
        "subset). `episode` and `A` (the live SETUP_FORMING rule) have 0 trades in this history." % (ns.get(pri, 0), ns.get("p4_episode", 0)) + nl,
        "- Per-trade audit rows: `F:/MTS/data/tom_probe_diag/trades_<variant>.jsonl`." + nl,
        "- Conventions, session clock and the pre-declared GO/SKIP rules: module docstring of `tom_probe_diag.py` "
        "(rules were fixed before the data was read)." + nl,
        "- Null column: `tom_bt_report.random_entry_null` (same UTC day, same direction and stop/target distance, "
        "next-bar-open fill, 100 draws) applied to the SAME trades of each bucket. It randomises the time inside the day, so "
        "real minus null reads as the value of the actual entry timing; it is not a session-matched null." + nl,
        "- Gross R is dominated by rare target hits (planned R:R is large, stops are ~0.08 % of price): read the median and "
        "the target-hit count beside every mean." + nl,
    ]
    r = res[pri]
    g = ["GO" if x else "SKIP" for x in (r["S"], r["Q"], r["M"])]
    out = [nl + "## GO / SKIP per axis (primary variant `%s`)" % pri + nl + nl]
    out.append("- **S (session): %s.** Rule: a 0-2h / 2-4h session window beats all other trades with a Bonferroni CI above 0 "
               "(n >= %d). Windows tested: %d; passing: %d." % (g[0], MIN_GROUP_N, len(r["srows"]), sum(1 for x in r["srows"] if x[6])) + nl)
    out.append("- **Q (selection): %s.** Rule: any selection split (first per session / day, proof level, tier) has a Bonferroni "
               "CI of the gross R difference excluding 0. Comparisons: %d; excluding 0: %d." % (g[1], len(r["qrows"]), sum(1 for x in r["qrows"] if x[6])) + nl)
    out.append("- **M (management): %s.** Rule: GO iff MFE >= 1R before the stop in >= %.0f%% of trades and >= 2R in >= %.0f%%. "
               "Observed %.1f%% and %.1f%%." % (g[2], 100 * M_SHARE_1R, 100 * M_SHARE_2R, 100 * r["s1"], 100 * r["s2"]) + nl)
    if "p4_episode" in res:
        q = res["p4_episode"]
        out.append("- Consistency check on `p4_episode` (n = %d): S %s, Q %s, M %s." % (
            ns["p4_episode"], "GO" if q["S"] else "SKIP", "GO" if q["Q"] else "SKIP", "GO" if q["M"] else "SKIP") + nl)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("".join(head) + "".join(out) + nl.join(docs), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    rows, b, docs, res, ns = main()
    write_doc(rows, b, docs, res, ns)
    print("wrote", DOC)
