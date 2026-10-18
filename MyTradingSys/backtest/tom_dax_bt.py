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
  report  simulate the four variants using per-instrument Java net RR, the null, dev/holdout split ->
          research/tom_transfer_2026-10-11/DAX_BT_REPORT.md + bt_runs/TRIAL_REGISTRY.csv rows.
  all     gen, rows, report.
Reports require --split-manifest HOLDOUT_CLEAN.json from the split owner.
Reports also require --readiness-manifest <JSON> answering all twelve PRE_REG_TEMPLATE items.
Holdout is read only with `report --read-holdout`, once (durable reservation), after full development for that split.

Primary verdict: `coded` preserves Java's per-instrument net_rr (GER40 uses FDAX fees). Gross-only selection is removed.
Reviewed contract: layer_lab/reports/2026-10-11_lab-audit-tom-dax-bt.md H5 addendum; original pre-registration preserved.
`--shifts` is an EXTENSION (not in the pre-registration): see the report's note on the proof ceiling.
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
import re
import shutil
import subprocess
import time
import math
from array import array
from collections import Counter
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "MyTradingSys/runtime"))
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
KINDS = ["coded"]                     # primary: Java per-instrument net RR; no gross-only arm

# Frozen legacy counter: SetupCandidatesBuilder.java:568-585 counts rejection_wick, absorption,
# finished_auction (only when favouring), delta_flip and cvd_aligned. B144 excludes volume_spike
# (579), still emitted at 615-616; book_imbalance is also uncounted (B131).
# PRE_REG masks cvd_aligned, delta_flip, finished_auction. ABSORPTION IS ALSO MASKED here: its condition 3 (java 685-687,
# `deltas[i] > 0 && close < open`) needs the delta sign, and DAX has delta == 0 exactly, so it can never fire there;
# "masked exactly as on DAX" requires it off on BTC too (deviation from the PRE_REG list, stated in the report).
MASK_OF = ("absorption", "cvd_aligned", "delta_flip", "finished_auction")
PROOF_COUNT_SCHEMA = "java-b144-no-volume-spike-net-rr-primary-unavailable-flow-v3"


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
    A candidate whose proof JSON does not reproduce its own proof_count raises ValueError (fail closed).
    Masking cvd_aligned also marks snapshot CVD unavailable before downstream direction/verdict gates."""
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
    if "cvd_aligned" in mask:
        # H6: half-volume CFD placeholders have zero delta, but Java labels
        # zero as negative. Missing aggressor data is neither bearish nor bullish.
        # Clear both the direction check's last_3_delta and the verdict's slope;
        # do not expose placeholder numeric CVD as an observed zero either.
        s["cvd"] = dict(availability="UNAVAILABLE", value=None, slope="unavailable",
                        last_3_delta=[], cvd_recent={}, confidence="UNAVAILABLE")
        conditions = s.get("conditions") or {}
        conditions["cvd_slope"] = "unavailable"
        s["conditions"] = conditions
    return changed


def require_proof_schema(obj, path):
    """Reject incompatible adapter row caches, including unversioned/empty caches; never silently reuse them."""
    if obj.get("proof_count_schema") != PROOF_COUNT_SCHEMA:
        raise ValueError("incompatible proof-count schema in %s; regenerate snapshots with current Java "
                         "and rerun rows --force" % path)


def exact_net_rr(top, fee_per_side=FEES_FDAX["entry"]):
    """Unrounded net RR (FORMULAS.md section 17) from the decision geometry Java serialized: zone.price, math.stop, math.target.

    Java rounds net_rr (and these prices) to 2 decimals in the snapshot JSON, so a value just under the floor
    reads as exactly the floor. This recomputes it; None when the geometry is absent or unusable.
    """
    try:
        entry = float((top.get("zone") or {})["price"])
        m = top.get("math") or {}
        stop, target = float(m["stop"]), float(m["target"])
    except (KeyError, TypeError, ValueError):
        return None
    risk = abs(entry - stop)
    if not all(math.isfinite(x) for x in (entry, stop, target)) or risk == 0:
        return None
    cost = 2.0 * fee_per_side * entry
    return (abs(target - entry) - cost) / (risk + cost)


def exact_rr_verdict(snapshot, proof_dir, floor, compute_verdict):
    """compute_verdict with the top candidate's rounded net_rr tightened to its exact value when that is below the floor.

    Only ever lowers net_rr (min of Java's and the recomputed value), so a candidate the producer already rejects stays
    rejected and display rounding never lifts a below-floor candidate over the floor. The input snapshot is not modified.
    """
    top = next((c for c in (snapshot.get("setup_candidates") or [])
                if c is not None and int(c.get("rank") or 999) <= 3), None)
    exact = exact_net_rr(top) if top is not None else None
    if exact is not None and exact < floor:
        snapshot = copy.deepcopy(snapshot)
        top = next(c for c in snapshot["setup_candidates"] if c is not None and int(c.get("rank") or 999) <= 3)
        m = top.setdefault("math", {})
        try:
            java = float(m.get("net_rr"))
        except (TypeError, ValueError):
            java = exact
        m["net_rr"] = min(java, exact)
    return compute_verdict(snapshot, proof_dir, floor=floor)


def rows_for_snapshot(s0, parse_ts, proof_dir_of, compute_verdict=None, mask=MASK_OF, kinds=("coded",),
                      shifts=(0,), stats=None):
    """{'<kind>/<shift>': row} for one snapshot (s0 is not modified)."""
    if any(kind != "coded" for kind in kinds):
        raise ValueError("only coded per-instrument net RR is supported; gross-only selection was removed (H5)")
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
    return out


# ---------------------------------------------------------------- bars helpers
def sim_limit_trade(b, i0, side, entry, stop, target, fill_window, hold_bars, fees=FEES_FDAX,
                    stop_first=True, slip=0.0, slip_pts=0.0, entry_end_i=None):
    """DAX bracket: elapsed-minute clocks, execution only on real bars (audit H4).

    Order expiry is unchanged. A holding deadline on a filler minute is deferred
    to the next real open: stop gaps take priority, then target gaps, then timeout.
    Intrabar prices after that open cannot affect the already expired position.
    No reopening in coverage leaves open_at_end, never a fabricated close.
    The mask marks executable data, not the cause of a missing minute; coverage
    validation remains separate from execution.
    """
    if b.real is None and entry_end_i is None:
        return T.sim_limit_trade(b, i0, side, entry, stop, target, fill_window, hold_bars,
                                 fees, stop_first, slip, slip_pts)
    if b.real is not None and len(b.real) != b.n:
        raise ValueError("invalid real-bar mask: coverage must match the bars")
    sgn = 1.0 if side == "long" else -1.0
    if not (sgn * (stop - entry) < 0 and sgn * (target - entry) > 0):
        return dict(filled=False, reason="bad_geometry")
    risk = abs(entry - stop)
    fill_i = None
    for i in range(i0, min(i0 + fill_window, b.n)):
        if (b.real is not None and not b.real[i]) or (entry_end_i is not None and i >= entry_end_i):
            continue
        if (b.l[i] <= entry) if sgn > 0 else (b.h[i] >= entry):
            fill_i = i
            break
        if (b.h[i] >= target) if sgn > 0 else (b.l[i] <= target):
            return dict(filled=False, reason="ran")
    if fill_i is None:
        return dict(filled=False, reason="no_fill" if i0 + fill_window <= b.n else "open_at_end")

    def done(kind, px, j, amb):
        if kind in ("stop", "timeout"):
            px = px - sgn * slip * px - sgn * slip_pts
        gross = sgn * (px - entry) / risk
        fee_r = (fees["entry"] * entry + fees[kind] * px) / risk
        return dict(filled=True, reason=kind, gross_r=gross, net_r=gross - fee_r, fee_r=fee_r,
                    fill_i=fill_i, exit_i=j, bars_held=j - fill_i, ambiguous=amb)

    # Preserve the shared bracket's conservative fill-bar stop and fee model.
    if (b.l[fill_i] <= stop) if sgn > 0 else (b.h[fill_i] >= stop):
        px = min(b.o[fill_i], stop) if sgn > 0 else max(b.o[fill_i], stop)
        return done("stop", px, fill_i, 0)
    amb = 0
    last = fill_i + hold_bars
    for j in range(fill_i + 1, b.n):
        if b.real is not None and not b.real[j]:
            continue
        if j > last:
            # Expired during closure: only the first executable opening price.
            if sgn * (b.o[j] - stop) <= 0:
                return done("stop", b.o[j], j, amb)
            if sgn * (b.o[j] - target) >= 0:
                return done("target", target, j, amb)
            return done("timeout", b.o[j], j, amb)
        s_hit = (b.l[j] <= stop) if sgn > 0 else (b.h[j] >= stop)
        t_hit = (b.h[j] >= target) if sgn > 0 else (b.l[j] <= target)
        if s_hit and t_hit:
            amb += 1
        if s_hit and (stop_first or not t_hit):
            px = min(b.o[j], stop) if sgn > 0 else max(b.o[j], stop)
            return done("stop", px, j, amb)
        if t_hit:
            return done("target", target, j, amb)
        if j == last:
            return done("timeout", b.c[j], j, amb)
    return dict(filled=True, reason="open_at_end", fill_i=fill_i)


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


def validate_session(session):
    """Explicit owner-frozen local window; no inferred trader hours."""
    try:
        tz = ZoneInfo(session["timezone"])
        start, end = (dt.datetime.strptime(session[k], "%H:%M").time() for k in ("start", "end"))
        if any(value.strftime("%H:%M") != session[key] for key, value in (("start", start), ("end", end))):
            raise ValueError("HH:MM required")
        if start == end:
            raise ValueError("empty/whole-day window")
    except (KeyError, TypeError, ValueError, ZoneInfoNotFoundError) as exc:
        raise ValueError("null session requires timezone and distinct HH:MM start/end") from exc
    return tz, start, end


def load_null_session(path):
    if not path:
        raise ValueError("null session manifest required (owner's pre-registration addendum)")
    session = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_session(session)
    if not isinstance(session.get("source"), str) or not session["source"].strip():
        raise ValueError("null session manifest requires trader quote + file:line in source")
    return session


def session_bounds(t, session):
    tz, start, end = validate_session(session)
    local = dt.datetime.fromtimestamp(t, tz)
    date = local.date()
    overnight = end < start
    if overnight and local.time() < end:
        date -= dt.timedelta(days=1)
    lo = dt.datetime.combine(date, start, tzinfo=tz).timestamp()
    hi = dt.datetime.combine(date + dt.timedelta(days=int(overnight)), end, tzinfo=tz).timestamp()
    return lo, hi


def session_opportunities(sigs, b, session):
    validate_session(session)
    out = []
    for r in sigs:
        lo, hi = session_bounds(r["t"], session)
        i = b.idx(int(round(r["t"] * 1000)))
        if lo <= r["t"] < hi and 0 <= i < b.n and (b.real is None or b.real[i]):
            out.append(r)
    return out


def random_entry_null(opportunities, b, n_perm=200, seed=7, session=None):
    """Randomise ORIGINAL variant opportunities, before scheduling/fill selection.

    Rebase entry/current-open and stop/entry, target/entry ratios at a real
    minute in the same local session. Orders use the strategy's touch model,
    eight zone-TF bars and scheduler. Session constrains submissions and fills;
    pending orders and positions retain their original elapsed lifetimes.
    Counts include empty draws; inference requires 30 real resolved fills.
    """
    validate_session(session)
    if not isinstance(n_perm, int) or isinstance(n_perm, bool) or n_perm < 1:
        raise ValueError("null draws must be a positive integer")
    sigs = session_opportunities(opportunities, b, session)
    real_trades, real_counts = run_dax_opportunities(sigs, b, FEES_FDAX, session=session)
    real_filled = resolved(real_trades)
    real = sum(t["gross_r"] for t in real_filled) / len(real_filled) if real_filled else None
    rng, draws, means, cache = random.Random(seed), [], [], {}
    for draw in range(n_perm):
        samples, missing = [], 0
        for source_i, r in enumerate(sigs):
            bounds = session_bounds(r["t"], session)
            if bounds not in cache:
                lo, hi = bounds
                cache[bounds] = [k for k in range(max(0, b.idx(int(lo*1000))),
                                                min(b.n, b.idx(int(hi*1000))))
                                 if b.real is None or b.real[k]]
            ks = cache[bounds]
            if not ks:
                missing += 1
                continue
            k = ks[rng.randrange(len(ks))]
            i = b.idx(int(round(r["t"] * 1000)))
            zp = float(r["zprice"])
            if zp <= 0 or b.o[i] <= 0 or b.o[k] <= 0:
                raise ValueError("null requires positive entry/reference prices")
            sgn = 1 if r["dir"] == "long" else -1
            if sgn * (zp - b.o[i]) > 0:
                raise ValueError("null opportunity has marketable rather than passive entry")
            e = b.o[k] * (zp / b.o[i])
            sample = dict(r, t=(b.t0+k*60000)/1000, zprice=e,
                          stop=e*float(r["stop"])/zp, target=e*float(r["target"])/zp,
                          source_i=source_i)
            samples.append(sample)
        trades, counts = run_dax_opportunities(sorted(samples, key=lambda r: (r["t"], r["source_i"])), b, FEES_FDAX, session=session)
        filled = resolved(trades)
        mean = sum(t["gross_r"] for t in filled)/len(filled) if filled else None
        if mean is not None:
            means.append(mean)
        draws.append(dict(counts, draw=draw, sampled=len(samples), missing_session=missing,
                          mean_gross=mean, trades=trades))
    p = ((1+sum(m >= real for m in means))/(1+len(means))
         if len(real_filled) >= 30 and means else None)
    return dict(seed=seed, n_perm=n_perm, session=dict(session), opportunities=len(opportunities),
                eligible_opportunities=len(sigs), outside_session=len(opportunities)-len(sigs),
                real_counts=real_counts, real_mean=real, p=p,
                null_mean=sum(means)/len(means) if means else None,
                nonempty_draws=len(means), empty_draws=n_perm-len(means), draws=draws)


# ---------------------------------------------------------------- periods, holdout guard, archive completeness
def load_readiness(path):
    """Freeze an owner-supplied readiness declaration before any outcome access.

    JSON: {"items": {"1": {"status": "ANSWERED", "answer": "...",
    "evidence": "file:line"}, ... "12": {...}}}. Keys are the twelve
    numbered headings of PRE_REG_TEMPLATE.md. WAIVED needs an explicit reason
    in answer, evidence of authorization, and a named approver. This validates
    completeness, not the scientific truth of the owner's evidence. No default
    production manifest or implicit waiver exists.
    """
    def supplied(value):
        return (isinstance(value, str) and bool(value.strip()) and
                value.strip().upper() not in {"TODO", "NOT_ANSWERED", "NOT_IN_DATA"})

    try:
        if not path:
            raise ValueError("path required")
        raw = Path(path).read_bytes()
        obj = json.loads(raw)
        items = obj["items"]
        if not isinstance(items, dict) or set(items) != {str(i) for i in range(1, 13)}:
            raise ValueError("items must cover exactly PRE_REG_TEMPLATE headings 1..12")
        for key, item in items.items():
            if not isinstance(item, dict) or item.get("status") not in ("ANSWERED", "WAIVED"):
                raise ValueError("item %s must be ANSWERED or WAIVED" % key)
            if not supplied(item.get("answer")) or not supplied(item.get("evidence")):
                raise ValueError("item %s needs an answer and evidence" % key)
            if item["status"] == "WAIVED" and not supplied(item.get("approver")):
                raise ValueError("item %s waiver needs a named approver" % key)
        return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), items=items)
    except (OSError, ValueError, KeyError, TypeError) as e:
        raise ValueError("invalid or absent readiness manifest: %s" % e) from e


def load_split(path):
    """Owner-supplied clean split; no historical default or inferred clean dates.

    design_end_utc is the latest design exposure. Embargo must separate it from
    holdout_start_utc; development prices/signals end at holdout minus embargo.
    Dates are UTC ISO-8601 strings. The holdout start may be forward-dated.
    """
    try:
        if not path:
            raise ValueError("path required")
        obj = json.loads(Path(path).read_text(encoding="utf-8"))
        times = []
        for key in ("design_end_utc", "holdout_start_utc"):
            d = dt.datetime.fromisoformat(obj[key].replace("Z", "+00:00"))
            if d.utcoffset() != dt.timedelta(0):
                raise ValueError("%s must specify UTC" % key)
            times.append(d.timestamp())
        embargo = obj["embargo_s"]
        if isinstance(embargo, bool) or not isinstance(embargo, (int, float)) or not math.isfinite(embargo) or embargo < 0:
            raise ValueError("embargo_s must be a finite nonnegative number")
        design, hold = times
        if design < T_DAX_START or design >= hold or design + embargo > hold:
            raise ValueError("design exposure and embargo must precede the holdout")
        return dict(design_end_utc=obj["design_end_utc"], holdout_start_utc=obj["holdout_start_utc"],
                    embargo_s=embargo, holdout_start=hold, dev_end=hold-embargo,
                    identity=hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest())
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
        raise ValueError("invalid or absent split manifest: %s" % e) from e


def dax_period(t, split=None):
    # Legacy labels retained only for standalone helpers; reports always supply a split.
    hold = split["holdout_start"] if split else T_DAX_HOLD
    end = split["dev_end"] if split else hold
    return "warmup" if t < T_DAX_START else "dev" if t < end else "embargo" if t < hold else "holdout"


def slice_bars(b, start_s=None, end_s=None):
    """Only complete 1m bars inside [start, end); never a bar straddling the cutoff."""
    lo = max(0, math.ceil((start_s*1000-b.t0)/60000)) if start_s is not None else 0
    hi = min(b.n, math.floor((end_s*1000-b.t0)/60000)) if end_s is not None else b.n
    hi = max(lo, hi)
    return T.Bars1m(b.t0+60000*lo, *(a[lo:hi] for a in (b.o, b.h, b.l, b.c, b.v, b.tbv)),
                    real=b.real[lo:hi] if b.real is not None else None)


def load_development_bars(path, end_s):
    """Filter timestamps BEFORE parsing prices; no holdout OHLC enters development.

    Same archive/deduplication/gap-fill convention as T.load_bars_1m, scoped here
    so the shared engine and live path remain untouched.
    """
    rows = {}
    for p in sorted(Path(path).glob("*.csv")):
        with open(p, newline="", encoding="utf-8") as fh:
            for r in csv.reader(fh):
                if not r or not r[0].isdigit():
                    continue
                t = int(r[0])
                if t + 60000 > end_s*1000 or t in rows:
                    continue
                rows[t] = tuple(float(r[k]) for k in (1, 2, 3, 4, 5, 9))
    if not rows:
        raise ValueError("no development klines before split cutoff")
    vals = [array("d") for _ in range(6)]
    real, prev = bytearray(), None
    for t in sorted(rows):
        if prev is not None:
            if (t-prev) % 60000:
                raise ValueError("DAX bars must be minute-aligned")
            for _ in range((t-prev)//60000-1):
                close = vals[3][-1]
                for a, v in zip(vals, (close, close, close, close, 0., 0.)):
                    a.append(v)
                real.append(0)
        for a, v in zip(vals, rows[t]):
            a.append(v)
        real.append(1)
        prev = t
    return T.Bars1m(min(rows), *vals, real=real)


def btc_period(t):
    return "hist" if t < T_BTC_DEV else "dev" if t < T_BTC_BURNED else "burned"


def select_rows(rows, read_holdout, marker=HOLDOUT_MARKER, split=None):
    """Dev rows always; holdout rows only with read_holdout, and only if the marker does not exist yet (read once)."""
    keep = [r for r in rows if dax_period(r["t"], split) == "dev"]
    if not read_holdout:
        return keep
    if Path(marker).exists():
        raise SystemExit("holdout already read (%s): it is read once" % marker)
    return keep + [r for r in rows if dax_period(r["t"], split) == "holdout"]


def mark_holdout_read(n_rows, marker=HOLDOUT_MARKER, split=None):
    # Exclusive durable reservation before evaluation: failures do not permit a second look.
    with open(marker, "x", encoding="utf-8", newline="\n") as fh:
        json.dump(dict(read_utc=dt.datetime.now(UTC).isoformat(), holdout_rows=n_rows,
                       split_identity=split["identity"] if split else None), fh)
        fh.write("\n")
        fh.flush()
        os.fsync(fh.fileno())


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


def require_download_coverage(raw, start, end):
    """Do not interpret an undownloaded day as a scheduled market closure (H4).

    The existing generator's coverage contract requires a .bi5 for every date,
    including downloaded empty closed days. The bar mask alone cannot prove that.
    """
    d = start
    while d <= end:
        path = Path(raw) / ("%s.bi5" % d.isoformat())
        if not path.is_file():
            raise SystemExit("incomplete DAX download coverage: missing %s; cannot treat missing data as market closure" % path)
        d += dt.timedelta(days=1)


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


def generation_environment():
    from dax_engine import shot
    env = _java_env()
    binaries = [shutil.which(name, path=env.get("PATH")) for name in ("java", "javac")]
    if any(p is None for p in binaries):
        raise ValueError("snapshot producer requires Java and javac identities")
    return {str(p): file_hash(p) for p in [*binaries, *shot.engine_jars()]}


def gen_end(e_day, cut_t):
    """Last snapshot minute: end of e_day, never later than the last complete development minute."""
    last = dt.datetime(e_day.year, e_day.month, e_day.day, 23, 59, tzinfo=UTC).timestamp()
    if cut_t is not None:
        last = min(last, cut_t - 60)
    return dt.datetime.fromtimestamp(last, UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def month_start_ts(name):
    return dt.datetime(int(name[:4]), int(name[5:7]), 1, tzinfo=UTC).timestamp()


def month_in_scope(name, cut_t):
    """A month file belongs to development only if its first minute precedes the authorized cutoff."""
    return cut_t is None or month_start_ts(name[:7]) < cut_t


def producer_bars_identity(cut_t):
    """Identity of the execution bars exactly as the row stage loads them (see _init_dax); recorded at generation."""
    klines = DAX_ARCHIVE / "klines"
    return bars_identity(load_development_bars(klines, cut_t) if cut_t is not None else T.load_bars_1m(klines, fill_gaps=True))


def require_producer_bars(origin, bars, producer):
    """R4: the snapshots and the execution bars must describe the same data. Absent identity = regenerate (fail closed)."""
    recorded = (origin or {}).get("bars")
    if not recorded:
        raise ValueError("snapshot producer lacks the execution bars identity in %s; regenerate through gen" % producer)
    if bars is None:
        raise ValueError("execution bars not loaded; cannot bind snapshot producer %s" % producer)
    if recorded != bars_identity(bars):
        raise ValueError("snapshot producer execution data differs from the current execution bars (%s); "
                         "regenerate snapshots through gen" % producer)


def cmd_gen(a):
    t0 = time.time()
    split = load_split(getattr(a, "split_manifest", None))   # manifest first: no conversion/data access without it
    cut_t = None if getattr(a, "read_holdout", False) else split["dev_end"]
    convert_cmd = [sys.executable, "-I", str(HERE / "dax_data.py"), "convert", "--raw", str(DAX_RAW), "--out", str(DAX_ARCHIVE)]
    convert_cmd += ["--end-ms", str(int(cut_t * 1000))] if cut_t is not None else ["--read-holdout"]
    subprocess.run(convert_cmd, check=True)
    start = max(DAX_START, dt.date.fromisoformat(a.start)) if a.start else DAX_START
    end = min(DAX_END, dt.date.fromisoformat(a.end)) if a.end else DAX_END
    if cut_t is not None:
        end = min(end, dt.datetime.fromtimestamp(cut_t - 60, UTC).date())
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
               "--start", "%sT00:00:00Z" % s_day.isoformat(), "--end", gen_end(e_day, cut_t),
               "--step", "15", "--shards", str(a.shards)]
        print(" ".join(cmd), flush=True)
        inputs = dict(codes=generation_codes(), environment=generation_environment(), command=cmd,
                      data={str(p): file_hash(p) for p in sorted((DAX_ARCHIVE / "klines").glob("*.csv"))},
                      bars=producer_bars_identity(cut_t))
        existing = set(DAX_SNAPS.glob("*.jsonl.gz"))
        for p in existing:
            origin_path = p.with_name(p.name.replace(".jsonl.gz", ".inputs.json"))
            origin = json.loads(origin_path.read_text(encoding="utf-8")) if origin_path.exists() else {}
            if origin.get("codes") != inputs["codes"] or origin.get("data") != inputs["data"] or \
                    origin.get("bars") != inputs["bars"] or \
                    origin.get("environment") != inputs["environment"] or \
                    origin.get("snapshot_sha256") != file_hash(p):
                raise ValueError("cache input snapshot provenance absent/stale in %s; use a fresh snapshot directory" % p)
        subprocess.run(cmd, check=True, env=_java_env())
        after = dict(codes=generation_codes(), environment=generation_environment(), command=cmd,
                     data={str(p): file_hash(p) for p in sorted((DAX_ARCHIVE / "klines").glob("*.csv"))},
                     bars=producer_bars_identity(cut_t))
        if inputs != after:
            raise ValueError("cache inputs changed during snapshot generation; use a fresh snapshot directory")
        for p in set(DAX_SNAPS.glob("*.jsonl.gz")) - existing:
            origin_path = p.with_name(p.name.replace(".jsonl.gz", ".inputs.json"))
            origin_path.write_text(json.dumps(dict(inputs, snapshot_sha256=file_hash(p)), sort_keys=True) + "\n",
                                   encoding="utf-8", newline="\n")
    metas = [json.loads(p.read_text()) for p in sorted(DAX_SNAPS.glob("*.meta.json")) if p.stem.replace(".meta", "") not in done_before]
    n = sum(m["evaluated"] for m in metas)
    dt_s = time.time() - t0
    print("gen: %d snapshots evaluated in %.0f s incl. convert+compile = %.0f snapshots/minute" % (n, dt_s, n / dt_s * 60 if dt_s else 0), flush=True)


# ---------------------------------------------------------------- rows
_BARS = None


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode("utf-8")).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()


def code_identity():
    # Hash the actual dependencies, including uncommitted changes, without git.
    paths = list((ROOT / "src/main/java/datafeed").glob("*.java"))
    paths += list((RESEARCH / "core_readiness_2026-09-27/harness/java").glob("*.java"))
    paths += [HERE / name for name in ("tom_dax_bt.py", "tom_bt.py", "verdict.py", "fees.py",
                                      "snapshots.py", "dax_engine.py", "dax_data.py", "tom_bt_report.py")]
    paths += [ROOT / "MyTradingSys/runtime" / name for name in ("math_object_builder.py", "net_rr_floor.py")]
    paths += [ROOT / "MyTradingSys/system/net_rr_floor.json"]
    paths += [ROOT / "pom.xml", ROOT / "scripts/dev/shot.py"]
    return {p.relative_to(ROOT).as_posix(): file_hash(p) for p in sorted(set(paths))}


def generation_codes():
    return {k: v for k, v in code_identity().items() if k.endswith(".java") or
            k.endswith(("dax_engine.py", "dax_data.py", "tom_dax_bt.py", "net_rr_floor.json", "pom.xml", "shot.py"))}


def bars_identity(b):
    h = hashlib.sha256()
    for name in ("o", "h", "l", "c", "v", "tbv", "real"):
        value = getattr(b, name)
        h.update(name.encode())
        h.update(b"absent" if value is None else bytes(value))
    return dict(t0=b.t0, n=b.n, sha256=h.hexdigest())


def freeze_run(manifest):
    """Shared accounting identity for an outcome or explicitly labelled recall look.

    A fresh look uses a fresh look_id; only an identical manifest is a rerender.
    Files are create-only, and never infer historical producers from today's HEAD.
    """
    run_id = "dax_bt_" + digest(manifest)
    path = WORK / "runs" / (run_id + ".json")
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(manifest, sort_keys=True, indent=2) + "\n"
    if path.exists():
        if path.read_text(encoding="utf-8") != raw:
            raise ValueError("immutable run manifest mismatch: %s" % path)
    else:
        with open(path, "x", encoding="utf-8", newline="\n") as fh:
            fh.write(raw)
    return run_id, path, raw


def cache_inputs(market, path, shifts, mask, cut_t, floor):
    path = Path(path).resolve()
    producer = path.with_name(path.name.replace(".jsonl.gz", ".inputs.json"))
    if not producer.is_file():
        raise ValueError("cache input provenance missing for %s; regenerate through gen" % path)
    origin = json.loads(producer.read_text(encoding="utf-8")) if producer.is_file() else None
    if origin is not None and (origin.get("codes") != generation_codes() or
                               origin.get("snapshot_sha256") != file_hash(path)):
        raise ValueError("cache input snapshot producer mismatch in %s; regenerate through gen" % producer)
    if market == "dax" and cut_t is not None:
        command = (origin or {}).get("command") or []
        if "--end" not in command:
            raise ValueError("snapshot producer end absent in %s; regenerate through gen" % producer)
        from snapshots import parse_ts
        if parse_ts(command[command.index("--end") + 1]) >= cut_t:
            raise ValueError("snapshot %s was generated past the development cutoff; regenerate through gen" % path)
    if market == "dax":
        if _BARS is None:
            if not (origin or {}).get("bars"):
                raise ValueError("snapshot producer lacks the execution bars identity in %s; regenerate through gen" % producer)
        else:
            require_producer_bars(origin, _BARS, producer)   # before any row is built or reused
    source_meta = path.with_name(path.name.replace(".jsonl.gz", ".meta.json"))
    return dict(schema="dax-inputs-v1", market=market, snapshot=str(path),
                snapshot_sha256=file_hash(path),
                snapshot_meta_sha256=file_hash(source_meta) if source_meta.exists() else None,
                producer=origin,
                codes=code_identity(), floor=floor, mask=sorted(mask), shifts=sorted(set(shifts)),
                kinds=list(KINDS), cut_t=cut_t,
                bars=bars_identity(_BARS) if market == "dax" and _BARS is not None else None)


def validate_cache(out, meta, expected=None, mask=None, shifts=None, bars=None, verify_bars=True):
    obj = json.loads(meta.read_text(encoding="utf-8")) if meta.exists() else {}
    require_proof_schema(obj, meta)
    frozen = obj.get("inputs")
    if not frozen or obj.get("input_id") != digest(frozen) or obj.get("rows_sha256") != file_hash(out):
        raise ValueError("cache input identity/content missing or changed in %s; rerun rows --force" % meta)
    from net_rr_floor import load_floor
    if expected is None:
        expected = cache_inputs(frozen["market"], frozen["snapshot"], frozen["shifts"],
                                frozen["mask"], frozen["cut_t"], load_floor())
        if frozen["market"] == "dax":
            if not verify_bars:
                expected["bars"] = frozen["bars"]  # pre-reservation envelope counting only
            elif bars is None and frozen["cut_t"] is None:
                raise ValueError("cache input requires explicitly reserved full bars")
            elif bars is None:
                bars = load_development_bars(DAX_ARCHIVE / "klines", frozen["cut_t"])
            if verify_bars:
                require_producer_bars(frozen.get("producer"), bars, frozen["snapshot"])
                expected["bars"] = bars_identity(bars)
    if frozen != expected or (mask is not None and frozen["mask"] != sorted(mask)) or \
            (shifts is not None and frozen["shifts"] != sorted(set(shifts))):
        raise ValueError("cache input mismatch in %s; rerun rows --force" % meta)
    return obj


_TS_KEY = re.compile(r'"timestamp_utc"\s*:\s*"([^"]+)"')


def _init_dax(klines, cut_t=None):
    global _BARS
    _BARS = load_development_bars(klines, cut_t) if cut_t is not None else T.load_bars_1m(klines, fill_gaps=True)


def _rows_month(job):
    market, path, out_dir, shifts, mask, cut_t = job
    from snapshots import parse_ts
    from verdict import compute_verdict, proof_dir_of
    from net_rr_floor import load_floor
    floor = load_floor()                 # one frozen floor for this month, recorded with the rows
    name = Path(path).name.replace(".jsonl.gz", "")
    out = Path(out_dir) / (name + ".rows.jsonl")
    meta = Path(out_dir) / (name + ".rows.meta.json")
    if out.exists():
        require_proof_schema(json.loads(meta.read_text(encoding="utf-8")) if meta.exists() else {}, meta)
        inputs = cache_inputs(market, path, shifts, mask, cut_t, floor)
        validate_cache(out, meta, expected=inputs)
        with open(out, encoding="utf-8") as fh:
            for line in fh:
                require_proof_schema(json.loads(line), out)
        return name, None
    inputs = cache_inputs(market, path, shifts, mask, cut_t, floor)
    input_id = digest(inputs)
    stats = Counter()
    tmp = out.with_suffix(".part")
    with gzip.open(path, "rt", encoding="utf-8") as fh, open(tmp, "w", encoding="utf-8", newline="\n") as fo:
        for line in fh:
            hit = _TS_KEY.search(line)
            if hit is None:
                raise ValueError("snapshot line lacks timestamp_utc in %s" % path)
            t = parse_ts(hit.group(1))
            stats["snapshots_kept_by_java"] += 1
            if cut_t is not None and t >= cut_t:
                stats["cut"] += 1          # payload of an excluded timestamp is never decoded
                continue
            s = json.loads(line)
            if parse_ts(s["timestamp_utc"]) != t:
                raise ValueError("snapshot timestamp key ambiguous in %s" % path)
            if market == "dax" and not is_open(_BARS, t):
                stats["closed_dropped"] += 1
                continue
            if market == "dax":
                frozen_verdict = lambda snap, pd: exact_rr_verdict(snap, pd, floor, compute_verdict)
            else:
                frozen_verdict = lambda snap, pd: compute_verdict(snap, pd, floor=floor)
            keys = rows_for_snapshot(s, parse_ts, proof_dir_of, frozen_verdict, mask, KINDS, shifts, stats)
            fo.write(json.dumps({"proof_count_schema": PROOF_COUNT_SCHEMA, "input_id": input_id, "t": t, "k": keys}) + "\n")
            stats["rows"] += 1
    if inputs != cache_inputs(market, path, shifts, mask, cut_t, floor):
        raise ValueError("cache inputs changed during row generation; discard rows and rerun --force")
    tmp.replace(out)
    meta.write_text(json.dumps(dict(stats, proof_count_schema=PROOF_COUNT_SCHEMA, inputs=inputs,
                                   input_id=input_id, rows_sha256=file_hash(out), net_rr_floor=floor,
                                   rr_selection="Java per-instrument net_rr, tightened to the exact unrounded value recomputed from serialized geometry (dax)", fdax_fee_per_side=FEES_FDAX["entry"],
                                   execution_math_sha=sha(ROOT / "src/main/java/datafeed/ExecutionMathConstants.java")))
                    + "\n", encoding="utf-8", newline="\n")
    return name, dict(stats)


def cmd_rows(a):
    split = load_split(getattr(a, "split_manifest", None)) if a.market in ("dax", "both") else None
    if split and a.read_holdout:
        require_full_dev(a, split)
    for market in (["dax", "btc"] if a.market == "both" else [a.market]):
        snap_dir = DAX_SNAPS if market == "dax" else BTC_SNAPS
        out_dir = WORK / ("rows_" + market)
        out_dir.mkdir(parents=True, exist_ok=True)
        if a.force:
            for p in list(out_dir.glob("*.rows.jsonl")) + list(out_dir.glob("*.rows.meta.json")):
                p.unlink()
        files = [str(p) for p in sorted(snap_dir.glob("*.jsonl.gz"))
                 if p.name.replace(".jsonl.gz", "") in (a.months or [p.name.replace(".jsonl.gz", "")])
                 and (snap_dir / (p.name.replace(".jsonl.gz", "") + ".meta.json")).exists()
                 and (market != "dax" or month_in_scope(p.name, None if a.read_holdout else split["dev_end"]))]
        mask = () if (market == "btc" and a.mask == "none") else MASK_OF   # DAX is always masked (no-op on exact-zero deltas)
        cut_t = T_BTC_BURNED if market == "btc" else None if a.read_holdout else split["dev_end"]
        jobs = [(market, f, str(out_dir), tuple(a.shifts), mask, cut_t) for f in files]
        t0 = time.time()
        init = (_init_dax, (str(DAX_ARCHIVE / "klines"), cut_t)) if market == "dax" else (None, ())
        with mp.Pool(a.procs, initializer=init[0], initargs=init[1]) as pool:
            for name, st in pool.imap_unordered(_rows_month, jobs):
                print(market, name, st, "%.0fs" % (time.time() - t0), flush=True)


def load_rows(market, key, months=None, split=None, read_holdout=False, counts=None, mask=None, shifts=None,
              bars=None, verify_bars=True):
    rows = []
    for p in sorted((WORK / ("rows_" + market)).glob("*.rows.jsonl")):
        if months and p.name[:7] not in months:
            continue
        if market == "dax" and split and not read_holdout and not month_in_scope(p.name, split["dev_end"]):
            continue
        meta = p.with_name(p.name.replace(".rows.jsonl", ".rows.meta.json"))
        frozen = validate_cache(p, meta, mask=mask, shifts=shifts, bars=bars, verify_bars=verify_bars)
        if frozen["inputs"]["market"] != market:
            raise ValueError("cache input market mismatch in %s" % p)
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                d = json.loads(line)
                require_proof_schema(d, p)
                if d.get("input_id") != frozen["input_id"]:
                    raise ValueError("cache input envelope mismatch in %s" % p)
                if market == "dax" and split:
                    per = dax_period(d["t"], split)
                    if counts is not None:
                        counts[per] = counts.get(per, 0) + 1
                    if per != "dev" and not (read_holdout and per == "holdout"):
                        continue  # no verdict/outcome payload consumed for excluded timestamps
                if key not in d["k"]:
                    raise SystemExit("rows lack key %s (rerun `rows --force --shifts ...`)" % key)
                rows.append(d["k"][key])
    rows.sort(key=lambda r: r["t"])
    return rows


# ---------------------------------------------------------------- simulation + report
def f2(x):
    return "%.2f" % x


def f3(x):
    return "-" if x is None else "%.3f" % x


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


def simulate(market, rows, b, variant, fees, slip_pts=0.0, split=None, period="dev", session=None):
    if market == "dax" and split:
        rows = [r for r in rows if dax_period(r["t"], split) == period]
        b = slice_bars(b, T_DAX_START if period == "dev" else split["holdout_start"],
                       split["dev_end"] if period == "dev" else None)
    sigs = T.signals(rows, variant)
    if market != "dax":
        return T.run_variant(sigs, b, fees=fees, stop_first=True, slip=0.0, slip_pts=slip_pts)
    if session is not None:
        sigs = session_opportunities(sigs, b, session)
    out, _ = run_dax_opportunities(sigs, b, fees, slip_pts, session=session)
    return [t for t in out if t["reason"] != "open_at_end"]


def run_dax_opportunities(sigs, b, fees, slip_pts=0.0, session=None):
    # DAX-local counterpart of T.run_variant: preserve scheduling and signal
    # geometry while routing every strategy/stress execution through the mask.
    out, busy_until_i = [], -1
    counts = dict(opportunities=len(sigs), submitted=0, busy_skipped=0, outside_bars=0,
                  filled=0, resolved=0, no_fill=0, ran=0, bad_geometry=0, open_at_end=0)
    for r in sigs:
        tf = T.zone_tf(r["ztype"])
        tfm = T.ZONE_TF_MIN[tf]
        i0 = b.idx(int(round(r["t"] * 1000)))
        if i0 < 0 or i0 >= b.n:
            counts["outside_bars"] += 1
            continue
        if i0 <= busy_until_i:
            counts["busy_skipped"] += 1
            continue
        counts["submitted"] += 1
        entry_end_i = b.idx(int(session_bounds(r["t"], session)[1]*1000)) if session else None
        res = sim_limit_trade(b, i0, r["dir"], float(r["zprice"]), float(r["stop"]), float(r["target"]),
                              8 * tfm, 8 * tfm, fees, True, 0.0, slip_pts, entry_end_i=entry_end_i)
        if res["filled"]:
            counts["filled"] += 1
        if res["reason"] in ("target", "stop", "timeout"):
            counts["resolved"] += 1
        else:
            counts[res["reason"]] += 1
        busy_until_i = (b.n-1 if res["reason"] == "open_at_end" else
                        res["exit_i"] if res["filled"] else
                        i0 + 8 * tfm - 1 if res["reason"] == "no_fill" else i0)
        t = dict(r)
        t.update(res)
        t["zone_tf"] = tf
        t["signal_i"] = i0
        out.append(t)
    return out, counts


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
    readiness = load_readiness(getattr(a, "readiness_manifest", None))
    split = load_split(getattr(a, "split_manifest", None))
    session = load_null_session(getattr(a, "null_session", None))
    ident = binding_identity(a, split, readiness, session, a.shifts)
    if a.read_holdout:
        require_full_dev(a, split)
        require_run_binding(ident, REPORT.read_text(encoding="utf-8"), split["identity"])   # before the read-once reservation
        counts = {}
        load_rows("dax", "%s/%d" % (KINDS[0], a.shifts[0]), None, split=split, counts=counts, verify_bars=False)
        mark_holdout_read(counts.get("holdout", 0), HOLDOUT_MARKER, split)
    periods_dax = ["dev"] + (["holdout"] if a.read_holdout else [])
    shifts = sorted(set(a.shifts))
    months = a.months or None
    md_rows, reg, stress, notes = [], [], [], []
    acct = {"readiness": readiness, "null_session": session, "null_draws": []}
    # ---- DAX
    dev_last_day = dt.datetime.fromtimestamp(split["dev_end"]-1, UTC).date()
    lo_d, hi_d = DAX_START, (dt.datetime.now(UTC).date() if a.read_holdout else dev_last_day)
    if months:
        lo_d = dt.date(int(min(months)[:4]), int(min(months)[5:]), 1)
        hi_d = dt.date(int(max(months)[:4]) + (max(months)[5:] == "12"), int(max(months)[5:]) % 12 + 1, 1)
    coverage_end = hi_d - dt.timedelta(days=1) if months else hi_d
    if not a.read_holdout:
        coverage_end = min(coverage_end, dt.datetime.fromtimestamp(split["dev_end"]-1, UTC).date())
    require_download_coverage(DAX_RAW, max(DAX_START, lo_d), coverage_end)
    b_dax = (T.load_bars_1m(DAX_ARCHIVE / "klines", fill_gaps=True) if a.read_holdout else
             load_development_bars(DAX_ARCHIVE / "klines", split["dev_end"]))
    n_hole_days = _data_holes(b_dax, lo_d, hi_d if months else hi_d + dt.timedelta(days=1))
    scope_cut = None if a.read_holdout else split["dev_end"]
    dax_meta = [json.loads(p.read_text()) for p in sorted(DAX_SNAPS.glob("*.meta.json"))
                if (not months or p.name[:7] in months) and month_in_scope(p.name, scope_cut)]
    rmeta = [json.loads(p.read_text()) for p in sorted((WORK / "rows_dax").glob("*.rows.meta.json"))
             if (not months or p.name[:7] in months) and month_in_scope(p.name, scope_cut)]
    acct["dax"] = dict(months=len(dax_meta), evaluated=sum(m["evaluated"] for m in dax_meta), kept=sum(m["kept"] for m in dax_meta),
                       errors=sum(m["errors"] for m in dax_meta), closed=sum(m.get("closed_dropped", 0) for m in rmeta),
                       rows=sum(m.get("rows", 0) for m in rmeta), holdout_rows=0, mask_changed=sum(m.get("mask_changed", 0) for m in rmeta))
    end_day = dt.datetime.fromtimestamp(split["dev_end"]-1, UTC).date()
    expected = set()
    day = DAX_START.replace(day=1)
    while day <= end_day:
        expected.add(day.strftime("%Y-%m"))
        day = dt.date(day.year+(day.month == 12), day.month % 12+1, 1)
    snap_months = {p.name[:7] for p in DAX_SNAPS.glob("*.meta.json")}
    row_months = {p.name[:7] for p in (WORK / "rows_dax").glob("*.rows.meta.json")
                  if p.with_name(p.name.replace(".rows.meta.json", ".rows.jsonl")).is_file()}
    all_metas = {}
    for p in DAX_SNAPS.glob("*.meta.json"):
        try:
            all_metas[p.name[:7]] = json.loads(p.read_text())
        except ValueError:
            all_metas[p.name[:7]] = None      # unreadable meta: month incomplete
    acct["dax"]["full_dev"] = (not a.read_holdout and not a.months and not getattr(a, "smoke", False) and
                                expected <= snap_months and expected <= row_months and
                                dev_months_complete(all_metas, expected, split["dev_end"]) and
                                all(ident["snapshots"].get(m) for m in expected) and
                                acct["dax"]["errors"] == 0 and n_hole_days == 0)
    b_btc = None
    from net_rr_floor import load_floor
    selected_markets = ("dax", "btc") if getattr(a, "market", "both") == "both" else (getattr(a, "market", "dax"),)
    row_files = [p for market in selected_markets for p in sorted((WORK / ("rows_" + market)).glob("*.rows.jsonl"))
                 if (not months or p.name[:7] in months) and (market != "dax" or month_in_scope(p.name, scope_cut))]
    cache_ids = {}
    for p in row_files:
        market = p.parent.name.removeprefix("rows_")
        mask = () if market == "btc" and getattr(a, "mask", "all") == "none" else MASK_OF
        meta = p.with_name(p.name.replace(".rows.jsonl", ".rows.meta.json"))
        frozen = validate_cache(p, meta, mask=mask, shifts=shifts,
                                bars=b_dax if market == "dax" else None)
        if frozen["inputs"]["market"] != market:
            raise ValueError("cache input market mismatch in %s" % meta)
        if market == "dax" and frozen["inputs"]["cut_t"] != (None if a.read_holdout else split["dev_end"]):
            raise ValueError("cache input split cutoff mismatch in %s; rerun rows --force" % meta)
        cache_ids[str(p)] = dict(input_id=frozen["input_id"], rows_sha256=frozen["rows_sha256"],
                                 inputs=frozen["inputs"])
    acct["run_manifest"] = dict(ident, market=list(selected_markets),
        months=sorted(months) if months else None, smoke=getattr(a, "smoke", False),
        read_holdout=a.read_holdout, look_id=getattr(a, "look_id", ""), full_dev=acct["dax"]["full_dev"],
        dax_bars=bars_identity(b_dax), caches=cache_ids)
    if "btc" in selected_markets and (WORK / "rows_btc").exists():
        b_btc = T.load_bars_1m(BTC_KLINES)
        acct["run_manifest"]["btc_bars"] = bars_identity(b_btc)
    freeze_run(acct["run_manifest"])  # durable frozen inputs before any outcome evaluation
    runs_summary = []
    for market in (("dax", "btc") if getattr(a, "market", "both") == "both" else (getattr(a, "market", "dax"),)):
        if market == "btc":
            if not (WORK / "rows_btc").exists():
                continue
            bm = [json.loads(p.read_text()) for p in sorted((WORK / "rows_btc").glob("*.rows.meta.json")) if not months or p.name[:7] in months]
            acct["btc"] = dict(rows=sum(m.get("rows", 0) for m in bm), mask_changed=sum(m.get("mask_changed", 0) for m in bm),
                               cut=sum(m.get("cut", 0) for m in bm))
        b = b_dax if market == "dax" else b_btc
        fees = FEES_FDAX if market == "dax" else T.FEES_DERIBIT
        for kind in KINDS:
            for sh in shifts:
                counts = {}
                rows = load_rows(market, "%s/%d" % (kind, sh), months,
                                 split=split if market == "dax" else None,
                                 read_holdout=a.read_holdout, counts=counts,
                                 mask=() if market == "btc" and getattr(a, "mask", "all") == "none" else MASK_OF,
                                 shifts=shifts, bars=b if market == "dax" else None)
                if market == "dax":
                    # Count envelope timestamps once, independent of arms/variants/fills.
                    acct["dax"]["holdout_rows"] = max(acct["dax"]["holdout_rows"], counts.get("holdout", 0),
                        sum(dax_period(r["t"], split) == "holdout" for r in rows))
                    rows = [r for r in rows if dax_period(r["t"], split) in periods_dax]
                else:
                    rows = [r for r in rows if btc_period(r["t"]) == "dev"]   # BTC: dev only (hist is outside the comparison, holdout burned)
                for var in VARIANTS:
                    trades = []
                    for per in (periods_dax if market == "dax" else ["dev"]):
                        trades.extend(simulate(market, rows, b, var, fees,
                                               split=split if market == "dax" else None, period=per,
                                               session=session if market == "dax" else None))
                    for t in trades:
                        t["period"] = dax_period(t["t"], split) if market == "dax" else btc_period(t["t"])
                    plist = periods_dax if market == "dax" else ["dev"]
                    for per in plist:
                        period_b = (slice_bars(b, T_DAX_START if per == "dev" else split["holdout_start"],
                                              split["dev_end"] if per == "dev" else None) if market == "dax" else b)
                        tr = [t for t in trades if t["period"] == per]
                        s = T.summarize(tr)
                        fl = resolved(tr)
                        null = None
                        if market == "dax":
                            original = T.signals([r for r in rows if dax_period(r["t"], split) == per], var)
                            null = random_entry_null(original, period_b, session=session)
                            acct["null_draws"].append(dict(kind=kind, shift=sh, variant=var, period=per, result=null))
                        elif len(fl) >= 30:
                            import tom_bt_report as TR
                            null = TR.random_entry_null(tr, b)
                        held = sum(1 for t in fl if crossed_close(period_b, t["fill_i"], t["exit_i"])) if market == "dax" else 0
                        label = "%s / %s / s%d / %s" % (market.upper() if market == "dax" else "BTC-matched", kind, sh, var)
                        nul = ("%s / %s / %s" % (f3(null["real_mean"]), f3(null["null_mean"]), f3(null["p"]))
                               if market == "dax" else
                               "%s / %s / %s" % (f3(null[0]), f3(null[2]), f3(null[1])) if null else "-")
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
                            ts = simulate(market, rows, b, var, fees, slip_pts=1.0, split=split, session=session)
                            ss = T.summarize(ts)
                            stress.append("| %s / %s / s%d | %s | %s | %s | %s | %s |\n" % (
                                kind, var, sh, s["n_filled"], f2(s["mean_net"]),
                                "%s [%s, %s]" % (f2(ss["mean_net"]), f2(ss["net_ci"][0]), f2(ss["net_ci"][1])) if ss.get("n_filled") else "-",
                                "%.3f%%" % risks[len(risks) // 2],
                                "target %d / stop %d / timeout %d" % tuple(s["exits"][k] for k in ("target", "stop", "timeout"))))
    if acct["run_manifest"]["codes"] != code_identity() or acct["run_manifest"]["floor"] != load_floor():
        raise ValueError("run inputs changed during outcome evaluation; report refused")
    if split != load_split(a.split_manifest) or readiness != load_readiness(a.readiness_manifest) or \
            session != load_null_session(getattr(a, "null_session", None)):
        raise ValueError("run manifests changed during outcome evaluation; report refused")
    for p in row_files:
        meta = p.with_name(p.name.replace(".rows.jsonl", ".rows.meta.json"))
        frozen = validate_cache(p, meta, bars=b_dax if p.parent.name == "rows_dax" else None)
        if cache_ids[str(p)]["input_id"] != frozen["input_id"] or \
                cache_ids[str(p)]["rows_sha256"] != frozen["rows_sha256"]:
            raise ValueError("cache inputs changed during outcome evaluation; report refused")
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


SNAP_STEP_MIN = 15      # frozen cadence (cmd_gen --step): 96 scheduled observations per 1440-minute day
BIND_KEYS = ("schema", "codes", "floor", "market", "split", "readiness", "session", "mask", "shifts", "kinds",
             "variants", "seeds", "fees", "snapshots", "dev_bars")


def snapshot_month_complete(meta, name, cut_t):
    """True only if the producer's meta proves every scheduled observation of the month (to the dev cutoff) was evaluated.

    Needs the producer's own first/last evaluated instant: the count alone cannot show where the sampling happened.
    A meta without them (older producer) is stale and fails closed."""
    try:
        step = int(meta["step_min"])
        first, last, n = int(meta["first_ms"]), int(meta["last_ms"]), int(meta["evaluated"])
    except (KeyError, TypeError, ValueError):
        return False
    if step != SNAP_STEP_MIN or step <= 0 or last < first or (last - first) % (step * 60000) or             n != (last - first) // (step * 60000) + 1:
        return False
    y, m = int(name[:4]), int(name[5:7])
    start = max(month_start_ts(name[:7]), dt.datetime(DAX_START.year, DAX_START.month, DAX_START.day, tzinfo=UTC).timestamp())
    nxt = dt.datetime(y + (m == 12), m % 12 + 1, 1, tzinfo=UTC).timestamp()
    end = nxt - 60 if cut_t is None else min(nxt - 60, cut_t - 60)
    first_s, last_s = first / 1000, last / 1000
    return start <= first_s < start + step * 60 and end - step * 60 < last_s <= end


def dev_months_complete(metas, expected, cut_t):
    """metas: {'YYYY-MM': meta}. Every expected development month must be present and fully sampled."""
    return all(m in metas and snapshot_month_complete(metas[m], m, cut_t) for m in expected)


def snapshot_identity(cut_t):
    """{'YYYY-MM': sha256 of the snapshot file} for each in-scope month with a meta; None where the file is missing
    or does not match the hash its producer recorded in .inputs.json (never trust the recorded value alone)."""
    out = {}
    for meta in sorted(DAX_SNAPS.glob("*.meta.json")) if DAX_SNAPS.exists() else []:
        if not month_in_scope(meta.name, cut_t):
            continue
        snap = meta.with_name(meta.name.replace(".meta.json", ".jsonl.gz"))
        origin = meta.with_name(meta.name.replace(".meta.json", ".inputs.json"))
        try:
            actual = file_hash(snap)
            recorded = json.loads(origin.read_text(encoding="utf-8")).get("snapshot_sha256")
        except (OSError, ValueError, AttributeError):
            actual = recorded = None
        out[meta.name[:7]] = actual if actual and actual == recorded else None
    return out


def binding_identity(a, split, readiness, session, shifts):
    """Everything a holdout run must share with the completed development run, computed from the development window only."""
    from net_rr_floor import load_floor
    markets = ["dax", "btc"] if getattr(a, "market", "both") == "both" else [getattr(a, "market", "dax")]
    return dict(schema="dax-run-v1", codes=code_identity(), floor=load_floor(), market=markets, split=split,
                readiness=readiness, session=session, mask=getattr(a, "mask", "all"), shifts=sorted(set(shifts)),
                kinds=list(KINDS), variants=list(VARIANTS),
                seeds=dict(null=7, null_draws=200, bootstrap=12345, bootstrap_draws=2000, diff=99),
                fees=dict(dax=FEES_FDAX, btc=T.FEES_DERIBIT), snapshots=snapshot_identity(split["dev_end"]),
                dev_bars=bars_identity(load_development_bars(DAX_ARCHIVE / "klines", split["dev_end"])))


def require_run_binding(manifest, report_text, split_identity):
    """The holdout may be read only by a run whose arms, code, data rules, session and readiness equal those of the
    durable completed full-development run named in the report token."""
    hit = re.search(r"Full development completed for split %s run (dax_bt_[0-9a-f]{64})\s" % re.escape(split_identity), report_text or "")
    if not hit:
        raise SystemExit("holdout requires full development report bound to a completed run for this split manifest")
    run_id = hit.group(1)
    path = WORK / "runs" / (run_id + ".json")
    try:
        done = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise SystemExit("holdout requires full development: completed run manifest %s not readable" % path)
    if not isinstance(done, dict) or "dax_bt_" + digest(done) != run_id or done.get("full_dev") is not True or             done.get("read_holdout") or (done.get("split") or {}).get("identity") != split_identity:
        raise SystemExit("holdout requires full development: %s is not a completed development run of this split" % path)
    norm = lambda v: json.loads(json.dumps(v, sort_keys=True))     # tuples vs lists after a JSON round trip
    diff = [k for k in BIND_KEYS if norm(done.get(k)) != norm(manifest.get(k))]
    if diff:
        raise SystemExit("holdout run differs from the completed development run %s in: %s" % (run_id, ", ".join(diff)))
    return run_id


def require_full_dev(a, split):
    if getattr(a, "smoke", False) or a.months:
        raise SystemExit("holdout requires full development; smoke/month restrictions refused")
    if not REPORT.exists() or not re.search(r"Full development completed for split %s run dax_bt_[0-9a-f]{64}\s" % re.escape(split["identity"]),
                                            REPORT.read_text(encoding="utf-8")):
        raise SystemExit("holdout requires full development report for this split manifest")
    if HOLDOUT_MARKER.exists():
        raise SystemExit("holdout already read (%s): it is read once" % HOLDOUT_MARKER)


def cmd_report(a):
    t0 = time.time()
    split = load_split(getattr(a, "split_manifest", None))
    md_rows, stress, reg, acct, holes = build_report(a)
    manifest = acct["run_manifest"]
    run_id, manifest_path, raw_manifest = freeze_run(manifest)
    md = []
    if a.smoke:
        md.append("> **SMOKE (partial data): %s only, dev period only. These numbers test the pipeline; they are NOT a result and "
                  "must not be quoted as one. The full run overwrites this file.**\n" % (", ".join(a.months) if a.months else "whatever months are in the archive"))
    md.append("# DAX_BT_REPORT: untuned Tom core on DAX vs matched-proof BTC (card tom-dax-backtest)\n")
    md.append("Spec: `PRE_REG_DAX.md` (frozen 2026-10-11). Run `%s`, %s.\n" % (
        run_id, dt.datetime.now(UTC).strftime("%Y-%m-%d %H:%MZ")))
    md.append("Immutable run manifest `%s` (SHA-256 `%s`); hashes identify the frozen producers and inputs.\n"
              "\n```json\n%s```\n" % (manifest_path, digest(manifest), raw_manifest))
    d = acct["dax"]
    md.append("## 1. Data and accounting\n")
    ready = acct["readiness"]
    md.append("- Readiness manifest `%s`, SHA-256 `%s`, frozen before outcome access. "
              "All twelve PRE_REG_TEMPLATE items are answered or explicitly waived; "
              "evidence validity remains the owner's responsibility.\n" % (ready["path"], ready["sha256"]))
    md.append("\n| readiness item | status | answer / waiver reason | evidence | approver |\n"
              "|---|---|---|---|---|\n")
    for key in map(str, range(1, 13)):
        item = ready["items"][key]
        cells = [key, item["status"], item["answer"], item["evidence"], item.get("approver", "")]
        md.append("| " + " | ".join(str(v).replace("|", "\\|").replace("\n", " ").replace("\r", " ") for v in cells) + " |\n")
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
    md.append("- Split manifest `%s`, identity `%s`: design exposure ends %s; holdout starts %s; embargo %s seconds. "
              "Development signals and complete bars precede %s UTC. Boundary-unresolved orders are dropped; "
              "strategy, stress and null outcomes are isolated. Holdout rows: %d (%s).\n" % (
                  a.split_manifest, split["identity"], split["design_end_utc"], split["holdout_start_utc"],
                  split["embargo_s"], dt.datetime.fromtimestamp(split["dev_end"], UTC).isoformat(),
                  d["holdout_rows"], "read once" if a.read_holdout else "excluded, outcomes not read"))
    if not a.read_holdout and d["full_dev"]:
        md.append("Full development completed for split %s run %s\n" % (split["identity"], run_id))
    md.append("\n## 2. Results (one-trade-at-a-time, limit at zone price, stop/target from the rank-1 candidate, 8 zone-tf bars)\n")
    md.append("Fees: DAX = `FEES_FDAX` (0.000005 of price per side on every leg); BTC = Deribit (maker 0, taker 0.0005) as in the BTC rerun. "
              "Primary `coded` preserves Java per-instrument net_rr; GER40 uses FDAX fees. Gross-only selection is removed "
              "(H5 addendum in layer_lab/reports/2026-10-11_lab-audit-tom-dax-bt.md; original PRE_REG_DAX.md preserved). "
              "The row metadata freezes the verdict floor and records the FDAX fee and execution-math hash. "
              "Shift 0 uses the reviewed rule; shift > 0 are EXTENSION arms "
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
    md.append("- **DAX null**: original variant opportunities before fill/scheduling selection; 200 draws, seed 7; "
              "same local session, passive entry/current-open ratio, side, stop/entry and target/entry ratios, "
              "eight zone-TF bar order/hold clocks, real-bar touch fills and one-at-a-time scheduling. "
              "Window constrains submissions and entry fills; pending orders/positions keep their clocks across session end. "
              "Eight bars remain an inherited protocol choice, not a newly sourced Tom rule. "
              "Frozen session addendum: `%s`. BTC null unchanged.\n" % json.dumps(acct["null_session"], sort_keys=True))
    accounting = ["\n### DAX null opportunity and fill accounting\n\n"]
    for arm in acct["null_draws"]:
        result = arm["result"]
        label = "%s/s%d/%s/%s" % (arm["kind"], arm["shift"], arm["variant"], arm["period"])
        accounting.append("%s: seed %d, %d requested draws, %d nonempty, %d empty; %d session-eligible opportunities, %d outside session.\n" % (
            label, result["seed"], result["n_perm"], result["nonempty_draws"], result["empty_draws"],
            result["eligible_opportunities"], result["outside_session"]))
        accounting.append("\n| arm / period | opportunities | draw | sampled | submitted | busy skipped | filled | resolved | no fill | ran | unresolved | bad geometry | missing session |\n"
                          "|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")
        for name, counts in [("real", result["real_counts"])] + [(str(d["draw"]), d) for d in result["draws"]]:
            accounting.append("| %s | %d | %s | %d | %d | %d | %d | %d | %d | %d | %d | %d | %d |\n" % (
                label, result["opportunities"], name, counts.get("sampled", result["eligible_opportunities"]),
                counts["submitted"], counts["busy_skipped"], counts["filled"], counts["resolved"],
                counts["no_fill"], counts["ran"], counts["open_at_end"], counts["bad_geometry"], counts.get("missing_session", 0)))
        accounting.append("\n")
    md.append("".join(accounting))
    md.append("- **Closed minutes** are flat bars at the last close with volume 0 for the simulator only; the timeout counts clock bars; a gap through the "
              "stop fills at the reopening bar's open (`min/max(open, stop)`). `held across a close` counts filled trades whose fill..exit span a closed minute. "
              "A limit fill on a reopening gap is taken at the limit price (as on BTC), slightly optimistic.\n")
    md.append("- Days the feed refused (download holes) look like closed days: their snapshots are dropped by the open filter, and a trade spanning a hole "
              "would see flat bars; the hole count in section 1 is the check.\n")
    md.append("- Funding is not modelled (DAX future: none). Stop-first on ambiguous bars. Trial rows: `bt_runs/%s`, run id `%s`.\n" % (
        "TRIAL_REGISTRY_SMOKE.csv (smoke rows are kept apart from the real trial count)" if a.smoke else "TRIAL_REGISTRY.csv", run_id))
    REPORT.write_text("\n".join(md), encoding="utf-8", newline="\n")
    # registry (a re-render of the same run id is not a new trial)
    # a smoke run (partial data, pipeline test, no selection) goes to its own file so the honest trial count of real runs stays clean
    registry = REGISTRY.with_name("TRIAL_REGISTRY_SMOKE.csv") if a.smoke else REGISTRY
    registry.parent.mkdir(parents=True, exist_ok=True)
    new = not registry.exists()
    existing = set()
    if not new:
        with open(registry, encoding="utf-8", newline="") as fh:
            existing = {(r["run_id"], r["variant"]) for r in csv.DictReader(fh)}
    pending = [r for r in reg if (run_id, r[0]) not in existing]
    if pending:
        with open(registry, "a", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh, lineterminator="\n")
            if new:
                w.writerow(["run_id", "date", "variant", "n_trades", "mean_R_net", "sharpe_per_trade"])
            for r in pending:
                w.writerow([run_id, dt.datetime.now(UTC).date().isoformat()] + r)
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
        p.add_argument("--look-id", default="", help="unique label for a fresh experiment/recall look; identical frozen inputs and label rerender idempotently")
        p.add_argument("--smoke", action="store_true")
        p.add_argument("--read-holdout", dest="read_holdout", action="store_true")
        p.add_argument("--split-manifest", type=Path, help="owner's HOLDOUT_CLEAN.json; required for reports")
        p.add_argument("--readiness-manifest", type=Path, help="owner's JSON items 1..12: ANSWERED + answer/evidence, or WAIVED + answer/evidence/approver; required for reports")
        p.add_argument("--null-session", type=Path, help="owner's frozen session addendum JSON: timezone/start/end/source; required for reports")
    a = ap.parse_args(argv)
    if a.cmd == "all":   # every manifest is validated before conversion, generation or any data access
        load_readiness(a.readiness_manifest)
        load_split(a.split_manifest)
        load_null_session(a.null_session)
    if a.cmd in ("gen", "all"):
        cmd_gen(a)
    if a.cmd in ("rows", "all"):
        cmd_rows(a)
    if a.cmd in ("report", "all"):
        cmd_report(a)


if __name__ == "__main__":
    mp.freeze_support()
    main()
