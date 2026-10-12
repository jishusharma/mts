import sys
sys.dont_write_bytecode = True
"""Tom core outcome backtest on DAX vs matched-proof BTC (card tom-dax-backtest; THE SPEC is
research/tom_transfer_2026-10-11/PRE_REG_DAX.md, frozen). Rules are the unchanged Java engine (archive mode,
-Dmts.symbol=GER40), verdict.py and tom_bt.py; nothing is tuned for DAX.

Subcommands (work dir F:/MTS/data/dax_bt, env TOM_DAX_WORK):
  gen     refresh the 1m archive from the raw Dukascopy files, then TomSnapshotGen every 15 min into F:/MTS/data/dax_snapshots
          for every month whose raw days are all downloaded (contiguous runs; partial months are never generated).
  rows    snapshots -> verdict rows, per month, cached. DAX: closed-market snapshots dropped BEFORE any verdict (a real 1m bar
          must exist in the 2 minutes before asOf). BTC (market btc): the 2026-10-06 snapshots re-scored with the order-flow
          proofs masked exactly as on DAX, rows from 2026-06-26 on are never written (burned holdout, B147).
  report  simulate the four variants x verdict pair (as coded / DAX-fee), the null, dev/holdout split ->
          research/tom_transfer_2026-10-11/DAX_BT_REPORT.md + bt_runs/TRIAL_REGISTRY.csv rows.
  all     gen, rows, report.
Holdout (DAX 2026-04-11..) is read only with `report --read-holdout`, once (marker file), after the dev table exists.

Verdict pair: `coded` = Java net_rr (BTC perp fee term inside) and `daxfee` = net_rr := gross_rr on every candidate before
compute_verdict. `--shifts` is an EXTENSION (not in the pre-registration): see the report's note on the proof ceiling.
"""
import argparse
import copy
import csv
import datetime as dt
import gzip
import hashlib
import json
import multiprocessing as mp
import os
import random
import subprocess
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
import tom_bt as T  # noqa: E402
from fees import FEES_FDAX  # noqa: E402

WORK = Path(os.environ.get("TOM_DAX_WORK", r"F:\MTS\data\dax_bt"))
DAX_RAW = Path(os.environ.get("TOM_DAX_RAW", r"F:\MTS\data\dax_raw"))
DAX_ARCHIVE = Path(os.environ.get("TOM_DAX_ARCHIVE", r"F:\MTS\data\dax_archive"))
DAX_SNAPS = Path(os.environ.get("TOM_DAX_SNAPS", r"F:\MTS\data\dax_snapshots"))
BTC_SNAPS = Path(os.environ.get("TOM_BTC_SNAPS", r"F:\MTS\data\tom_snapshots_2026-10-06"))
BTC_KLINES = Path(os.environ.get("TOM_BT_RAW", r"F:\MTS\data\tom_raw")) / "klines"
JDK_BIN = Path(r"C:\tools\jdk-17.0.18\bin")
RESEARCH = ROOT / "MyTradingSys" / "research"
REPORT = RESEARCH / "tom_transfer_2026-10-11" / "DAX_BT_REPORT.md"
HOLDOUT_MARKER = RESEARCH / "tom_transfer_2026-10-11" / "HOLDOUT_READ_DAX.json"
REGISTRY = RESEARCH / "fast_track_2026-09-27" / "bt_runs" / "TRIAL_REGISTRY.csv"

UTC = dt.timezone.utc


def _ts(y, m, d):
    return dt.datetime(y, m, d, tzinfo=UTC).timestamp()


DAX_START = dt.date(2024, 11, 4)          # first snapshot day (2024-10-01..11-03 is warm-up for weekly profiles)
DAX_END = dt.date(2026, 10, 9)
T_DAX_START, T_DAX_HOLD = _ts(2024, 11, 4), _ts(2026, 4, 11)
T_BTC_DEV, T_BTC_BURNED = _ts(2025, 9, 1), _ts(2026, 6, 26)
VARIANTS = ["A", "episode", "watch_episode", "p4_episode"]   # the four of the 2026-10-06 BTC rerun
KINDS = ["daxfee", "coded"]                                    # DAX-fee is primary for this market; as-coded beside it

# Frozen legacy counter: SetupCandidatesBuilder.java:568-585 counts rejection_wick, absorption,
# finished_auction (only when favouring), delta_flip and cvd_aligned. B144 excludes volume_spike
# (579), still emitted at 615-616; book_imbalance is also uncounted (B131).
# PRE_REG masks cvd_aligned, delta_flip, finished_auction. ABSORPTION IS ALSO MASKED here: its condition 3 (java 685-687,
# `deltas[i] > 0 && close < open`) needs the delta sign, and DAX has delta == 0 exactly, so it can never fire there;
# "masked exactly as on DAX" requires it off on BTC too (deviation from the PRE_REG list, stated in the report).
MASK_OF = ("absorption", "cvd_aligned", "delta_flip", "finished_auction")
PROOF_COUNT_SCHEMA = "java-b144-no-volume-spike-v1"


# ---------------------------------------------------------------- proofs: parity count, masking, re-ranking
def java_count(c):
    """countSignals(direction) from proof JSON (SetupCandidatesBuilder.java:568-585, B144)."""
    p, d = c["proof"], c["direction"]
    n = 0
    if p["rejection_wick"] != "NONE":
        n += 1
    if p["absorption"]["detected"]:
        n += 1
    fa = p["finished_auction"]
    if fa["detected"] and fa["direction"] == ("sell" if d == "long" else "buy"):
        n += 1
    if p["delta_flip"]["detected"]:       # JSON `detected` = deltaFlipDetected && deltaFlipAtZone, as counted
        n += 1
    if p["cvd_aligned"]:
        n += 1
    return n


def _masked_part(c, mask):
    """How much of java_count the mask removes (a finished_auction that does not favour the trade is not counted)."""
    p, d = c["proof"], c["direction"]
    n = 0
    if "absorption" in mask and p["absorption"]["detected"]:
        n += 1
    fa = p["finished_auction"]
    if "finished_auction" in mask and fa["detected"] and fa["direction"] == ("sell" if d == "long" else "buy"):
        n += 1
    if "delta_flip" in mask and p["delta_flip"]["detected"]:
        n += 1
    if "cvd_aligned" in mask and p["cvd_aligned"]:
        n += 1
    return n


def _clear(c, mask):
    p = c["proof"]
    if "absorption" in mask:
        p["absorption"]["detected"] = False
        p["absorption"]["strength"] = "none"
    if "finished_auction" in mask:
        p["finished_auction"]["detected"] = False
        p["finished_auction"]["direction"] = ""
    if "delta_flip" in mask:
        p["delta_flip"]["detected"] = False
    if "cvd_aligned" in mask:
        p["cvd_aligned"] = False


def tf_rank(name, typ):
    """Zone tfRank of SetupCandidatesBuilder.extractZones (java 274-315, naked POC block 340-345, fvg 330)."""
    if name.startswith("naked_poc_"):
        return 11
    for pref, r in (("weekly_", 10), ("daily_", 9), ("4h_", 7), ("vwap", 6), ("prior_day_", 5),
                    ("1h_swing_", 4), ("15m_swing_", 3), ("5m_swing_", 2)):
        if name.startswith(pref):
            return r
    if name == "fvg_nearest" or typ == "fvg":
        return 1
    raise ValueError("unknown zone for tfRank: %s/%s" % (name, typ))


def rescore(s, mask=MASK_OF, shift=0, rerank=True):
    """In place. Masks the order-flow proofs of every rank <= 3 candidate, recomputes score.proof_count (Java count minus
    the masked proofs, plus `shift`), score.raw = min(95, 50 + 7 * proof_count + bonus) (java 175-181) and re-ranks by
    (raw desc, tfRank desc), stable, as java 183-188 (only the three candidates Java printed are visible: a fourth that
    masking would lift into the top 3 is unknowable). Returns the number of candidates whose count the mask changed.
    A candidate whose proof JSON does not reproduce its own proof_count raises ValueError (fail closed)."""
    cands = s.get("setup_candidates") or []
    changed, touched = 0, False
    for c in cands:
        if int(c.get("rank") or 999) > 3:
            continue                      # ExtraSetupBuilder rows (other proof schema); never the verdict's top
        jc = java_count(c)
        sc = c["score"]
        if jc != sc["proof_count"]:
            raise ValueError("proof JSON gives %d, score.proof_count is %s (%s)" % (jc, sc["proof_count"], c["zone"]["name"]))
        sub = _masked_part(c, mask)
        _clear(c, mask)
        new = jc - sub + shift
        if sub:
            changed += 1
        if new != jc:
            sc["proof_count"] = new
            sc["raw"] = min(95, 50 + 7 * new + sc["confluence_bonus"])
            touched = True
    if touched and rerank:
        vis = [c for c in cands if int(c.get("rank") or 999) <= 3]
        rest = [c for c in cands if int(c.get("rank") or 999) > 3]
        vis.sort(key=lambda c: (-c["score"]["raw"], -tf_rank(c["zone"]["name"], c["zone"]["type"])))
        for i, c in enumerate(vis, 1):
            c["rank"] = i
        s["setup_candidates"] = vis + rest
    return changed


def require_proof_schema(obj, path):
    """Reject pre-B144 row caches, including unversioned/empty caches; never silently reuse them."""
    if obj.get("proof_count_schema") != PROOF_COUNT_SCHEMA:
        raise ValueError("incompatible proof-count schema in %s; regenerate snapshots with current Java "
                         "and rerun rows --force" % path)


def daxfee(s):
    """DAX-fee verdict input: net_rr := gross_rr on every candidate (the Java net_rr carries the BTC perp fee term)."""
    for c in s.get("setup_candidates") or []:
        m = c.get("math")
        if isinstance(m, dict) and m.get("gross_rr") is not None:
            m["net_rr"] = m["gross_rr"]


def rows_for_snapshot(s0, parse_ts, proof_dir_of, compute_verdict=None, mask=MASK_OF, kinds=("coded", "daxfee"),
                      shifts=(0,), stats=None):
    """{'<kind>/<shift>': row} for one snapshot (s0 is not modified)."""
    if compute_verdict is None:
        from verdict import compute_verdict
    out = {}
    for sh in shifts:
        s1 = copy.deepcopy(s0)
        n = rescore(s1, mask, sh)
        if stats is not None and sh == shifts[0]:
            stats["mask_changed"] += n
        if "coded" in kinds:
            out["coded/%d" % sh] = T.snapshot_to_row(s1, parse_ts, compute_verdict, proof_dir_of)
        if "daxfee" in kinds:
            daxfee(s1)
            out["daxfee/%d" % sh] = T.snapshot_to_row(s1, parse_ts, compute_verdict, proof_dir_of)
    return out


# ---------------------------------------------------------------- bars helpers
def is_open(b, t_s, win_min=2):
    """Market-open filter: a real (non-filled) 1m bar opened in the `win_min` minutes before asOf."""
    i = b.idx(int(round(t_s * 1000)))
    for k in range(i - win_min, i):
        if 0 <= k < b.n and (b.real is None or b.real[k]):
            return True
    return False


def crossed_close(b, i, j):
    """True if any bar in [i, j] is a filled (closed-market) minute."""
    if b.real is None:
        return False
    return b.real.find(0, i, j + 1) >= 0


def draw_real_minute(b, day0_s, rng):
    """Uniform real-bar minute of the UTC day starting at day0_s whose next bar is real too (next-bar-open fill)."""
    cache = b.__dict__.setdefault("_real_day", {})
    ks = cache.get(day0_s)
    if ks is None:
        lo = max(0, b.idx(int(day0_s) * 1000))
        hi = min(b.n - 1, b.idx(int(day0_s) * 1000) + 1440)
        ks = [k for k in range(lo, hi) if b.real[k] and b.real[k + 1]]
        cache[day0_s] = ks
    return ks[rng.randrange(len(ks))]


def random_entry_null(trades, b, n_perm=200, seed=7):
    """tom_bt_report.random_entry_null for a market with closing hours: same day, same side, same stop/target distance (% of
    entry), same hold, next-bar-open fill; the entry minute is drawn among REAL bars (closed minutes cannot be entered).
    Returns (real mean gross, one-sided p, null mean) or None."""
    filled = [t for t in trades if t.get("filled") and t["reason"] in ("target", "stop", "timeout")]
    if len(filled) < 30:
        return None
    rng = random.Random(seed)
    real = sum(t["gross_r"] for t in filled) / len(filled)
    means = []
    for _ in range(n_perm):
        tot = cnt = 0
        for t in filled:
            day0 = int(t["t"] // 86400) * 86400
            try:
                k = draw_real_minute(b, day0, rng)
            except ValueError:
                continue
            e = b.o[k + 1]
            zp = float(t["zprice"])
            sp, tp = abs(zp - float(t["stop"])) / zp, abs(float(t["target"]) - zp) / zp
            sgn = 1.0 if t["dir"] == "long" else -1.0
            tfm = T.ZONE_TF_MIN[t["zone_tf"]]
            r = T.sim_limit_trade(b, k + 1, t["dir"], e, e * (1 - sgn * sp), e * (1 + sgn * tp), 1, 8 * tfm, FEES_FDAX, True, 0.0)
            if r["filled"] and r["reason"] in ("target", "stop", "timeout"):
                tot += r["gross_r"]
                cnt += 1
        if cnt:
            means.append(tot / cnt)
    if not means:
        return None
    p = (1 + sum(1 for m in means if m >= real)) / (1 + len(means))
    return real, p, sum(means) / len(means)


# ---------------------------------------------------------------- periods, holdout guard, archive completeness
def dax_period(t):
    return "warmup" if t < T_DAX_START else "dev" if t < T_DAX_HOLD else "holdout"


def btc_period(t):
    return "hist" if t < T_BTC_DEV else "dev" if t < T_BTC_BURNED else "burned"


def select_rows(rows, read_holdout, marker=HOLDOUT_MARKER):
    """Dev rows always; holdout rows only with read_holdout, and only if the marker does not exist yet (read once)."""
    keep = [r for r in rows if dax_period(r["t"]) == "dev"]
    if not read_holdout:
        return keep
    if Path(marker).exists():
        raise SystemExit("holdout already read (%s): it is read once" % marker)
    return keep + [r for r in rows if dax_period(r["t"]) == "holdout"]


def mark_holdout_read(n_rows, marker=HOLDOUT_MARKER):
    Path(marker).write_text(json.dumps({"read_utc": dt.datetime.now(UTC).isoformat(), "holdout_rows": n_rows}) + chr(10),
                            encoding="utf-8", newline=chr(10))


def complete_months(raw, start, end):
    """'YYYY-MM' of every month whose days inside [start, end] all have a raw file (an empty file = the feed's 404)."""
    out = []
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        first = max(dt.date(y, m, 1), start)
        nxt = dt.date(y + (m == 12), m % 12 + 1, 1)
        last = min(nxt - dt.timedelta(1), end)
        d, ok = first, True
        while d <= last:
            if not (Path(raw) / ("%s.bi5" % d.isoformat())).exists():
                ok = False
                break
            d += dt.timedelta(1)
        if ok:
            out.append("%04d-%02d" % (y, m))
        y, m = nxt.year, nxt.month
    return out


def contiguous_runs(months):
    runs = []
    for ym in months:
        y, m = int(ym[:4]), int(ym[5:])
        if runs and (runs[-1][1][0], runs[-1][1][1]) == ((y, m - 1) if m > 1 else (y - 1, 12)):
            runs[-1][1] = (y, m)
        else:
            runs.append([(y, m), (y, m)])
    return [("%04d-%02d" % a, "%04d-%02d" % b) for a, b in runs]


# ---------------------------------------------------------------- gen
def _java_env():
    env = dict(os.environ)
    if JDK_BIN.exists():
        env["PATH"] = str(JDK_BIN) + os.pathsep + env.get("PATH", "")
    return env


def cmd_gen(a):
    t0 = time.time()
    subprocess.run([sys.executable, "-I", str(HERE / "dax_data.py"), "convert", "--raw", str(DAX_RAW), "--out", str(DAX_ARCHIVE)],
                   check=True)
    start = max(DAX_START, dt.date.fromisoformat(a.start)) if a.start else DAX_START
    end = min(DAX_END, dt.date.fromisoformat(a.end)) if a.end else DAX_END
    months = complete_months(DAX_RAW, start, end)
    if a.months:
        months = [m for m in months if m in a.months]
    runs = contiguous_runs(months)
    print("complete months: %d; runs: %s" % (len(months), runs), flush=True)
    done_before = {p.stem.replace(".meta", "") for p in DAX_SNAPS.glob("*.meta.json")} if DAX_SNAPS.exists() else set()
    for first, last in runs:
        fy, fm = int(first[:4]), int(first[5:])
        ly, lm = int(last[:4]), int(last[5:])
        s_day = max(dt.date(fy, fm, 1), start)
        nxt = dt.date(ly + (lm == 12), lm % 12 + 1, 1)
        e_day = min(nxt - dt.timedelta(1), end)
        cmd = [sys.executable, "-I", str(HERE / "dax_engine.py"), "gen", "--raw", str(DAX_ARCHIVE), "--out", str(DAX_SNAPS),
               "--start", "%sT00:00:00Z" % s_day.isoformat(), "--end", "%sT23:59:00Z" % e_day.isoformat(),
               "--step", "15", "--shards", str(a.shards)]
        print(" ".join(cmd), flush=True)
        subprocess.run(cmd, check=True, env=_java_env())
    metas = [json.loads(p.read_text()) for p in sorted(DAX_SNAPS.glob("*.meta.json")) if p.stem.replace(".meta", "") not in done_before]
    n = sum(m["evaluated"] for m in metas)
    dt_s = time.time() - t0
    print("gen: %d snapshots evaluated in %.0f s incl. convert+compile = %.0f snapshots/minute" % (n, dt_s, n / dt_s * 60 if dt_s else 0), flush=True)


# ---------------------------------------------------------------- rows
_BARS = None


def _init_dax(klines):
    global _BARS
    _BARS = T.load_bars_1m(klines, fill_gaps=True)


def _rows_month(job):
    market, path, out_dir, shifts, mask, cut_t = job
    from snapshots import parse_ts
    from verdict import compute_verdict, proof_dir_of
    name = Path(path).name.replace(".jsonl.gz", "")
    out = Path(out_dir) / (name + ".rows.jsonl")
    meta = Path(out_dir) / (name + ".rows.meta.json")
    if out.exists():
        require_proof_schema(json.loads(meta.read_text(encoding="utf-8")) if meta.exists() else {}, meta)
        with open(out, encoding="utf-8") as fh:
            for line in fh:
                require_proof_schema(json.loads(line), out)
        return name, None
    stats = Counter()
    tmp = out.with_suffix(".part")
    with gzip.open(path, "rt", encoding="utf-8") as fh, open(tmp, "w", encoding="utf-8", newline="\n") as fo:
        for line in fh:
            s = json.loads(line)
            t = parse_ts(s["timestamp_utc"])
            stats["snapshots_kept_by_java"] += 1
            if cut_t is not None and t >= cut_t:
                stats["cut"] += 1
                continue
            if market == "dax" and not is_open(_BARS, t):
                stats["closed_dropped"] += 1
                continue
            keys = rows_for_snapshot(s, parse_ts, proof_dir_of, compute_verdict, mask, ("coded", "daxfee"), shifts, stats)
            fo.write(json.dumps({"proof_count_schema": PROOF_COUNT_SCHEMA, "t": t, "k": keys}) + "\n")
            stats["rows"] += 1
    tmp.replace(out)
    meta.write_text(json.dumps(dict(stats, proof_count_schema=PROOF_COUNT_SCHEMA)) + "\n", encoding="utf-8", newline="\n")
    return name, dict(stats)


def cmd_rows(a):
    for market in (["dax", "btc"] if a.market == "both" else [a.market]):
        snap_dir = DAX_SNAPS if market == "dax" else BTC_SNAPS
        out_dir = WORK / ("rows_" + market)
        out_dir.mkdir(parents=True, exist_ok=True)
        if a.force:
            for p in list(out_dir.glob("*.rows.jsonl")) + list(out_dir.glob("*.rows.meta.json")):
                p.unlink()
        files = [str(p) for p in sorted(snap_dir.glob("*.jsonl.gz"))
                 if p.name.replace(".jsonl.gz", "") in (a.months or [p.name.replace(".jsonl.gz", "")])
                 and (snap_dir / (p.name.replace(".jsonl.gz", "") + ".meta.json")).exists()]
        mask = () if (market == "btc" and a.mask == "none") else MASK_OF   # DAX is always masked (no-op on exact-zero deltas)
        jobs = [(market, f, str(out_dir), tuple(a.shifts), mask, T_BTC_BURNED if market == "btc" else None) for f in files]
        t0 = time.time()
        init = (_init_dax, (str(DAX_ARCHIVE / "klines"),)) if market == "dax" else (None, ())
        with mp.Pool(a.procs, initializer=init[0], initargs=init[1]) as pool:
            for name, st in pool.imap_unordered(_rows_month, jobs):
                print(market, name, st, "%.0fs" % (time.time() - t0), flush=True)


def load_rows(market, key, months=None):
    rows = []
    for p in sorted((WORK / ("rows_" + market)).glob("*.rows.jsonl")):
        if months and p.name[:7] not in months:
            continue
        meta = p.with_name(p.name.replace(".rows.jsonl", ".rows.meta.json"))
        require_proof_schema(json.loads(meta.read_text(encoding="utf-8")) if meta.exists() else {}, meta)
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                d = json.loads(line)
                require_proof_schema(d, p)
                if key not in d["k"]:
                    raise SystemExit("rows lack key %s (rerun `rows --force --shifts ...`)" % key)
                rows.append(d["k"][key])
    rows.sort(key=lambda r: r["t"])
    return rows


# ---------------------------------------------------------------- simulation + report
def f2(x):
    return "%.2f" % x


def f3(x):
    return "%.3f" % x


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:16]


def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def resolved(trades):
    return [t for t in trades if t.get("filled") and t["reason"] in ("target", "stop", "timeout")]


def sharpe(nets):
    if len(nets) < 3:
        return None
    m = sum(nets) / len(nets)
    sd = (sum((x - m) ** 2 for x in nets) / (len(nets) - 1)) ** 0.5
    return m / sd if sd else None


def verdict_line(s, label):
    """Protocol pass bar: >= 100 filled trades and net R 95% CI lower bound > 0, else 'no edge shown' / 'insufficient N'."""
    if not s.get("n_filled"):
        return "insufficient N (0 filled)"
    if s["n_filled"] < 100:
        return "insufficient N (%d < 100)" % s["n_filled"]
    return "PASS: edge shown" if s["net_ci"][0] > 0 else "no edge shown"


def simulate(market, rows, b, variant, fees, slip_pts=0.0):
    sigs = T.signals(rows, variant)
    return T.run_variant(sigs, b, fees=fees, stop_first=True, slip=0.0, slip_pts=slip_pts)


def cell(s):
    if not s.get("n_filled"):
        return "%d | 0 | - | - | - | -" % s.get("n_signals", 0)
    flag = " (n<30)" if s["n_filled"] < 30 else ""
    return "%d | %d%s | %.0f%% | %.0f%% | %s [%s, %s] | %s [%s, %s]" % (
        s["n_signals"], s["n_filled"], flag, 100 * s["fill_rate"], 100 * s["win"], f2(s["mean_gross"]), f2(s["gross_ci"][0]),
        f2(s["gross_ci"][1]), f2(s["mean_net"]), f2(s["net_ci"][0]), f2(s["net_ci"][1]))


HDR = ("| market / verdict / shift / variant | period | n signals | n filled | fill | win | mean R gross [95% CI] | mean R net [95% CI] |"
       " null gross (real / null / p) | held across a close | pass bar |\n|---|---|---|---|---|---|---|---|---|---|---|\n")


def build_report(a):
    periods_dax = ["dev"] + (["holdout"] if a.read_holdout else [])
    shifts = list(a.shifts)
    months = a.months or None
    md_rows, reg, stress, notes = [], [], [], []
    acct = {}
    # ---- DAX
    b_dax = T.load_bars_1m(DAX_ARCHIVE / "klines", fill_gaps=True)
    lo_d, hi_d = DAX_START, DAX_END
    if months:
        lo_d = dt.date(int(min(months)[:4]), int(min(months)[5:]), 1)
        hi_d = dt.date(int(max(months)[:4]) + (max(months)[5:] == "12"), int(max(months)[5:]) % 12 + 1, 1)
    n_hole_days = _data_holes(b_dax, lo_d, hi_d)
    dax_meta = [json.loads(p.read_text()) for p in sorted(DAX_SNAPS.glob("*.meta.json")) if not months or p.name[:7] in months]
    rmeta = [json.loads(p.read_text()) for p in sorted((WORK / "rows_dax").glob("*.rows.meta.json")) if not months or p.name[:7] in months]
    acct["dax"] = dict(months=len(dax_meta), evaluated=sum(m["evaluated"] for m in dax_meta), kept=sum(m["kept"] for m in dax_meta),
                       errors=sum(m["errors"] for m in dax_meta), closed=sum(m.get("closed_dropped", 0) for m in rmeta),
                       rows=sum(m.get("rows", 0) for m in rmeta), holdout_rows=0, mask_changed=sum(m.get("mask_changed", 0) for m in rmeta))
    b_btc = None
    runs_summary = []
    for market in ("dax", "btc"):
        if market == "btc":
            if not (WORK / "rows_btc").exists():
                continue
            b_btc = T.load_bars_1m(BTC_KLINES)
            bm = [json.loads(p.read_text()) for p in sorted((WORK / "rows_btc").glob("*.rows.meta.json")) if not months or p.name[:7] in months]
            acct["btc"] = dict(rows=sum(m.get("rows", 0) for m in bm), mask_changed=sum(m.get("mask_changed", 0) for m in bm),
                               cut=sum(m.get("cut", 0) for m in bm))
        b = b_dax if market == "dax" else b_btc
        fees = FEES_FDAX if market == "dax" else T.FEES_DERIBIT
        for kind in KINDS:
            for sh in shifts:
                rows = load_rows(market, "%s/%d" % (kind, sh), months)
                if market == "dax":
                    rows = select_rows(rows, a.read_holdout)
                else:
                    rows = [r for r in rows if btc_period(r["t"]) == "dev"]   # BTC: dev only (hist is outside the comparison, holdout burned)
                for var in VARIANTS:
                    trades = simulate(market, rows, b, var, fees)
                    for t in trades:
                        t["period"] = dax_period(t["t"]) if market == "dax" else btc_period(t["t"])
                    plist = periods_dax if market == "dax" else ["dev"]
                    for per in plist:
                        tr = [t for t in trades if t["period"] == per]
                        s = T.summarize(tr)
                        fl = resolved(tr)
                        null = None
                        if len(fl) >= 30:
                            if market == "dax":
                                null = random_entry_null(tr, b)
                            else:
                                import tom_bt_report as TR
                                null = TR.random_entry_null(tr, b)
                        held = sum(1 for t in fl if crossed_close(b, t["fill_i"], t["exit_i"])) if market == "dax" else 0
                        label = "%s / %s / s%d / %s" % (market.upper() if market == "dax" else "BTC-matched", kind, sh, var)
                        nul = "%s / %s / %s" % (f3(null[0]), f3(null[2]), f3(null[1])) if null else "-"
                        if sh == 0 or s.get("n_filled"):   # extension arms with no signal at all are left out of the table (still registered)
                            md_rows.append("| %s | %s | %s | %s | %s | %s |\n" % (
                                label, per, cell(s), nul, held if market == "dax" else "n/a", verdict_line(s, label)))
                        if market == "dax" and per == plist[-1] or market == "btc" and per == "dev":
                            nets = [t["net_r"] for t in fl]
                            reg.append(["%s/%s/%s/s%d" % (market, kind, var, sh), len(fl),
                                        "%.4f" % s["mean_net"] if s.get("n_filled") else "",
                                        "%.4f" % sharpe(nets) if sharpe(nets) is not None else ""])
                        if market == "dax" and per == "dev" and fl:
                            risks = sorted(abs(float(t["zprice"]) - float(t["stop"])) / float(t["zprice"]) * 100 for t in fl)
                            ts = simulate(market, rows, b, var, fees, slip_pts=1.0)
                            ss = T.summarize([t for t in ts if dax_period(t["t"]) == "dev"])
                            stress.append("| %s / %s / s%d | %s | %s | %s | %s | %s |\n" % (
                                kind, var, sh, s["n_filled"], f2(s["mean_net"]),
                                "%s [%s, %s]" % (f2(ss["mean_net"]), f2(ss["net_ci"][0]), f2(ss["net_ci"][1])) if ss.get("n_filled") else "-",
                                "%.3f%%" % risks[len(risks) // 2],
                                "target %d / stop %d / timeout %d" % tuple(s["exits"][k] for k in ("target", "stop", "timeout"))))
    return md_rows, stress, reg, acct, n_hole_days


def _data_holes(b, lo_d, hi_d):
    """Runs of more than 4 days of filled (bar-less) minutes between two dates: download holes or long holidays."""
    if b.real is None:
        return 0
    holes = 0
    i = max(0, b.idx(int(dt.datetime(lo_d.year, lo_d.month, lo_d.day, tzinfo=UTC).timestamp()) * 1000))
    n = min(b.n, b.idx(int(dt.datetime(hi_d.year, hi_d.month, hi_d.day, tzinfo=UTC).timestamp()) * 1000))
    while i < n:
        if b.real[i] == 0:
            j = i
            while j < n and b.real[j] == 0:
                j += 1
            if (j - i) > 4 * 1440:
                holes += 1
            i = j
        else:
            i += 1
    return holes


def cmd_report(a):
    t0 = time.time()
    if a.read_holdout:
        if a.smoke:
            raise SystemExit("--smoke and --read-holdout cannot be combined")
        if not REPORT.exists() or "SMOKE" in REPORT.read_text(encoding="utf-8")[:400]:
            raise SystemExit("the holdout is read after the dev table is written: run `report` (no flag) on the full data first")
        if HOLDOUT_MARKER.exists():
            raise SystemExit("holdout already read (%s): it is read once" % HOLDOUT_MARKER)
    md_rows, stress, reg, acct, holes = build_report(a)
    head = git("rev-parse", "HEAD")
    run_id = "dax_bt_%s%s%s" % (dt.datetime.now(UTC).strftime("%Y%m%d"), "_SMOKE" if a.smoke else "", "_holdout" if a.read_holdout else "")
    md = []
    if a.smoke:
        md.append("> **SMOKE (partial data): %s only, dev period only. These numbers test the pipeline; they are NOT a result and "
                  "must not be quoted as one. The full run overwrites this file.**\n" % (", ".join(a.months) if a.months else "whatever months are in the archive"))
    md.append("# DAX_BT_REPORT: untuned Tom core on DAX vs matched-proof BTC (card tom-dax-backtest)\n")
    md.append("Spec: `PRE_REG_DAX.md` (frozen 2026-10-11). Run `%s`, code HEAD `%s`, %s.\n" % (
        run_id, head, dt.datetime.now(UTC).strftime("%Y-%m-%d %H:%MZ")))
    md.append("Hashes: SetupCandidatesBuilder.java `%s`, verdict.py `%s`, tom_bt.py `%s`, tom_dax_bt.py `%s`, fees.py `%s`.\n" % (
        sha(ROOT / "src/main/java/datafeed/SetupCandidatesBuilder.java"), sha(HERE / "verdict.py"), sha(HERE / "tom_bt.py"),
        sha(HERE / "tom_dax_bt.py"), sha(HERE / "fees.py")))
    d = acct["dax"]
    md.append("## 1. Data and accounting\n")
    md.append("- DAX snapshots (TomSnapshotGen, 15 min, -Dmts.symbol=GER40): %d month files; %d evaluated, %d kept by Java (>= 1 candidate), %d errors. "
              "Market-open filter (a real 1m bar in the 2 minutes before asOf) dropped %d closed-market snapshots before any verdict; %d rows remain. "
              "Order-flow mask changed the proof count of %d DAX candidates (expected 0: the archive's taker-buy is exactly half the volume, so every delta is 0).\n" % (
                  d["months"], d["evaluated"], d["kept"], d["errors"], d["closed"], d["rows"], d["mask_changed"]))
    md.append("- DAX 1m archive `%s`; runs of > 4 days with no bar (download holes or holidays; filled flat for the simulator only): %d.\n" % (
        DAX_ARCHIVE / "klines", holes))
    if "btc" in acct:
        bt = acct["btc"]
        md.append("- BTC matched-proof: 2026-10-06 snapshots re-scored with absorption, cvd_aligned, delta_flip and finished_auction masked; %d rows, "
                  "mask changed %d candidates; %d snapshots from 2026-06-26 on were never read (burned holdout, B147).\n" % (bt["rows"], bt["mask_changed"], bt["cut"]))
    md.append("- Periods: DAX dev = 2024-11-04..2026-04-10%s. BTC-matched: dev only, 2025-09-01..2026-06-25 (hist is not part of the comparison; the holdout is burned).\n" % (
        ", holdout = 2026-04-11..2026-10-09 (READ in this run, marker `HOLDOUT_READ_DAX.json`)" if a.read_holdout else "; the holdout was NOT read"))
    md.append("\n## 2. Results (one-trade-at-a-time, limit at zone price, stop/target from the rank-1 candidate, 8 zone-tf bars)\n")
    md.append("Fees: DAX = `FEES_FDAX` (0.000005 of price per side on every leg); BTC = Deribit (maker 0, taker 0.0005) as in the BTC rerun. "
              "`daxfee` = net_rr := gross_rr before the verdict; `coded` = Java net_rr. Shift 0 is the pre-registered rule; shift > 0 are EXTENSION arms "
              "(section 3). Pass bar: >= 100 filled trades in a period and net R 95% CI lower bound > 0.\n\n")
    md.append(HDR + "".join(md_rows))
    md.append("\n### DAX stress: + 1 index point of slippage on stop and timeout legs (dev)\n\n| arm | n filled | mean net R | with +1 pt [95% CI] | median stop distance | exit mix |\n|---|---|---|---|---|---|\n" + "".join(stress))
    md.append("\n## 3. Proof-ceiling finding (the pre-registered rule cannot trade on a masked proof set)\n")
    md.append("With the order-flow proofs masked, only rejection_wick can count: the proof count is at most 1. "
              "B144 excludes volume_spike from the current Java counter even when its detected flag is emitted. "
              "With this ceiling, WATCH requires shift >= 2 and SETUP_FORMING requires shift >= 4 at minimum. "
              "`compute_verdict` needs proof >= 3 for WATCH and >= 5 for SETUP_FORMING, so at shift 0 the verdict can never leave WAIT_PROOF "
              "and every variant has 0 signals on DAX and on matched BTC. The pre-registered comparison is therefore degenerate by construction "
              "(PRE_REG assumed WATCH reachable). Extension arms `--shifts 1,2,3` add k to every "
              "candidate's proof count (WATCH needs masked proof >= 3-k; SETUP_FORMING >= 5-k), i.e. they relax the proof gate to what the data can "
              "show. They are NOT in the pre-registration, are registered as trials (variant suffix `/s<k>`), and any reading needs the supervisor's "
              "decision on how to count them.\n")
    md.append("\n## 4. Deviations and caveats (all stated, none tuned)\n")
    md.append("- **Current Java proof parity (B144).** Volume spikes remain visible but do not count. "
              "Snapshots with incompatible counts fail closed; unversioned or incompatible row caches must be regenerated. "
              "The historical pre-registration is unchanged and no shifts were tuned to compensate.\n")
    md.append("- **Absorption is masked too.** PRE_REG lists cvd_aligned, delta_flip, finished_auction. Absorption condition 3 (`SetupCandidatesBuilder.java:685-687`) "
              "needs the delta sign, which DAX does not have, so it cannot fire there; masking it on BTC is what \"exactly as on DAX\" requires.\n")
    md.append("- **Delta noise fixed in the archive format.** `dax_data.convert` printed taker-buy with 6 decimals, so micro volumes (0.001335) gave delta = +-1e-6 "
              "and the engine saw phantom aggressor splits (delta_flip, finished_auction, last_3_delta). It now prints 7 decimals: delta is exactly 0. "
              "The rows stage masks DAX the same way as BTC as a guard; the accounting line above shows how many DAX candidates the mask changed.\n")
    md.append("- **Re-ranking sees only the 3 candidates Java printed.** After masking, candidates are re-sorted by (raw, tfRank) as Java does, but a "
              "4th candidate that masking would have lifted into the top 3 is not in the snapshot.\n")
    md.append("- **Other order-flow dependence in the verdict is not masked (PRE_REG masks proofs only):** the CVD-slope gates in `compute_verdict` and "
              "`cvd.last_3_delta` in the proof-direction check still see BTC order flow; on DAX they are flat. Residual BTC/DAX asymmetry.\n")
    md.append("- **DAX `cvd.last_3_delta` is constant `negative,negative,negative`** (the engine classifies delta 0 as negative), so the proof-direction check "
              "(`math_object_builder.py` 'last_3_delta=neg,neg,neg vs LONG') marks every DAX long as `contradiction`: a long SETUP_FORMING is capped to WATCH. "
              "Only the SETUP_FORMING-based variants (A, episode, shift >= 4 under the current masked ceiling) are touched; "
              "the pre-registration did not foresee it.\n")
    md.append("- **Net R means are driven by tiny-stop trades.** The engine places stops at the nearest swing beyond the zone, which can sit a few cents from it "
              "(a BTC candidate with a 0.03 USD stop costs 1588 R in taker fees). Read the gross column and the exit mix beside every net mean.\n")
    md.append("- **Null** is `random_entry_null` (200 draws, same day, side and distances); on DAX the entry minute is drawn among real bars only "
              "(closed minutes cannot be entered). BTC uses `tom_bt_report.random_entry_null` unchanged.\n")
    md.append("- **Closed minutes** are flat bars at the last close with volume 0 for the simulator only; the timeout counts clock bars; a gap through the "
              "stop fills at the reopening bar's open (`min/max(open, stop)`). `held across a close` counts filled trades whose fill..exit span a closed minute. "
              "A limit fill on a reopening gap is taken at the limit price (as on BTC), slightly optimistic.\n")
    md.append("- Days the feed refused (download holes) look like closed days: their snapshots are dropped by the open filter, and a trade spanning a hole "
              "would see flat bars; the hole count in section 1 is the check.\n")
    md.append("- Funding is not modelled (DAX future: none). Stop-first on ambiguous bars. Trial rows: `bt_runs/%s`, run id `%s`.\n" % (
        "TRIAL_REGISTRY_SMOKE.csv (smoke rows are kept apart from the real trial count)" if a.smoke else "TRIAL_REGISTRY.csv", run_id))
    REPORT.write_text("\n".join(md), encoding="utf-8", newline="\n")
    if a.read_holdout:
        mark_holdout_read(acct["dax"]["holdout_rows"])
    # registry (a re-render of the same run id is not a new trial)
    # a smoke run (partial data, pipeline test, no selection) goes to its own file so the honest trial count of real runs stays clean
    registry = REGISTRY.with_name("TRIAL_REGISTRY_SMOKE.csv") if a.smoke else REGISTRY
    registry.parent.mkdir(parents=True, exist_ok=True)
    new = not registry.exists()
    already = (not new) and any(l.startswith(run_id + ",") for l in open(registry, encoding="utf-8"))
    if not already:
        with open(registry, "a", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh, lineterminator="\n")
            if new:
                w.writerow(["run_id", "date", "variant", "n_trades", "mean_R_net", "sharpe_per_trade"])
            for r in reg:
                w.writerow([run_id, dt.date.today().isoformat()] + r)
    print("wrote", REPORT, "(%d registry rows, %.0fs)" % (len(reg), time.time() - t0))


def main(argv=None):
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    for name in ("gen", "rows", "report", "all"):
        p = sp.add_parser(name)
        p.add_argument("--months", nargs="*", help="restrict to these YYYY-MM (smoke runs)")
        p.add_argument("--shifts", type=lambda s: [int(x) for x in s.split(",")], default=[0])
        p.add_argument("--start"); p.add_argument("--end")
        p.add_argument("--shards", type=int, default=1)
        p.add_argument("--procs", type=int, default=4)
        p.add_argument("--market", choices=["dax", "btc", "both"], default="both")
        p.add_argument("--mask", choices=["all", "none"], default="all", help="btc rows only: none = identity check against the old rows")
        p.add_argument("--force", action="store_true")
        p.add_argument("--smoke", action="store_true")
        p.add_argument("--read-holdout", dest="read_holdout", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd in ("gen", "all"):
        cmd_gen(a)
    if a.cmd in ("rows", "all"):
        cmd_rows(a)
    if a.cmd in ("report", "all"):
        cmd_report(a)


if __name__ == "__main__":
    mp.freeze_support()
    main()
