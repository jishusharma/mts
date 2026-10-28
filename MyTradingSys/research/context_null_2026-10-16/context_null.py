"""Context-matched null for a signal trigger. DEV split only, no market data is read here (the caller passes arrays).

Question: does the trigger add anything over the market context it fired in?  The Fable gross-effect screen's
location-only control arm lost money (FABLE_RUNS_AUDIT.md: n=1,439, mean -0.008 %, t_cost -6.0), so "beats zero" is the
wrong bar: a trigger must beat bars that share its context.

For each event bar t (decision at the close of bar t, entry = close[t+d], exit = close[t+d+h], return in %) draw K
control bars from the same array/split with the same context key, every key computed from bars <= t only:
  hour   UTC hour of the bar's open time
  vol    tercile of trailing realised vol; cut points from a trailing window ending at the bar (never full-sample)
  trend  tom_bt.trend_tag of the trailing 30-day return (imported, not copied)
  level  optional caller-supplied point-in-time bucket per bar (int, <0 = unknown -> event cannot be matched)
Controls never overlap any event's [t, t+d+h] window (plus the cooldown on both sides) and are spaced >= cooldown apart.

Result (percent): trigger_effect = mean over matched events of (event fwd - mean of its controls' fwd), day-clustered SE
(screen.cluster_mean_se); context_effect = matched-control mean minus the unconditional mean (screen.diff_cluster);
event_mean - uncond_mean = context_effect + trigger_effect exactly (checked in the tests).

Parameters marked OURS were chosen by judgement, not by any outcome: K=20, kmin=K//2, vol window = 6 h, cut window = 30 d,
trend window 30 d / threshold tom_bt default (0.075).
Never run this on a real signal set outside its one-run PRE_REG: reading outcomes burns it.
"""
import importlib.util
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from MyTradingSys.backtest import tom_bt  # noqa: E402  (causal trend tag, reused not copied)


def _load_screen():
    p = HERE.parent / "gross_effect_screen_2026-10-15" / "screen.py"
    spec = importlib.util.spec_from_file_location("gross_effect_screen_screen", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


screen = _load_screen()     # cluster_mean_se, diff_cluster, tstat, apply_cooldown, TS0, CUTOFF_MS, C_PCT, CM_PCT

TS0_MS = screen.TS0
DEV_END_MS = screen.CUTOFF_MS          # DEV bars have open time < 2024-07-01
REUSE_WARN = 5.0                       # OURS: mean uses per distinct control bar above which the SE is flagged
KEY_NAMES = ("hour", "vol", "trend", "level")
TREND_CODE = {"range": 0, "trend_up": 1, "trend_down": 2}


@dataclass
class Config:
    bar_min: int = 1                    # bar length in minutes (1 or 5)
    ts0_ms: int = TS0_MS                # open time of bar 0
    K: int = 20                         # controls per event (OURS)
    kmin: int = None                    # fewer controls than this -> event unmatched (OURS: K // 2)
    cooldown: int = 0                   # bars; the signal's own cooldown, applied to the controls too
    vol_win_min: int = 360              # trailing realised-vol window (OURS)
    cut_win_days: int = 30              # trailing window for the vol tercile cut points (OURS)
    trend_days: int = 30
    trend_thr: float = 0.075            # tom_bt.trend_tag default
    match: tuple = KEY_NAMES            # ablation: which keys are matched (level only if a column is passed)
    seed: int = 0
    split_end_ms: int = DEV_END_MS      # guard: a bar opening at/after this is refused (VALIDATION/HOLDOUT sealed)

    def __post_init__(self):
        if self.kmin is None:
            self.kmin = max(1, self.K // 2)

    @property
    def bpd(self):
        return 1440 // self.bar_min

    @property
    def barms(self):
        return self.bar_min * 60_000


# ---------------------------------------------------------------- causal context pieces
def rolling_rv(C, vw):
    """rv[i] = stdev of the log returns of bars i-vw+1..i (needs bars <= i only); NaN until vw returns exist."""
    C = np.asarray(C, float)
    n = len(C)
    rv = np.full(n, np.nan)
    if n <= vw:
        return rv
    lr = np.zeros(n)
    lr[1:] = np.diff(np.log(C))
    cs = np.concatenate(([0.0], np.cumsum(lr)))
    cs2 = np.concatenate(([0.0], np.cumsum(lr * lr)))
    k = np.arange(vw, n)                       # window = returns k-vw+1..k
    s = cs[k + 1] - cs[k + 1 - vw]
    s2 = cs2[k + 1] - cs2[k + 1 - vw]
    var = (s2 - s * s / vw) / (vw - 1)
    rv[k] = np.sqrt(np.maximum(var, 0.0))
    return rv


def vol_bucket(rv, t, cut_win):
    """0/1/2 = low/mid/high: rv[t] against the tercile cut points of rv[t-cut_win+1..t] (a trailing window ending at t)."""
    w = rv[max(0, t - cut_win + 1):t + 1]
    w = w[~np.isnan(w)]
    if len(w) < cut_win // 2 or np.isnan(rv[t]):
        return None
    c1, c2 = np.quantile(w, [1.0 / 3.0, 2.0 / 3.0])
    return int(rv[t] > c1) + int(rv[t] > c2)


def ret_trailing(C, t, n_back):
    return None if t < n_back else C[t] / C[t - n_back] - 1.0


def trend_code(C, t, cfg):
    r = ret_trailing(C, t, cfg.trend_days * cfg.bpd)
    return None if r is None else TREND_CODE[tom_bt.trend_tag(r, cfg.trend_thr)]


def hour_of(i, cfg):
    return ((cfg.ts0_ms + i * cfg.barms) // 3_600_000) % 24


def context_key(C, t, cfg, level=None, vol_fn=vol_bucket, rv=None):
    """Context key of bar t from C (+ level) alone. Truncation-invariant: context_key(C[:t+1], t) == context_key(C, t).
    Returns None when the history is too short or an active key is unknown."""
    if rv is None:
        rv = rolling_rv(C, cfg.vol_win_min // cfg.bar_min)
    parts = []
    if "hour" in cfg.match:
        parts.append(hour_of(t, cfg))
    if "vol" in cfg.match:
        v = vol_fn(rv, t, cfg.cut_win_days * cfg.bpd)
        if v is None:
            return None
        parts.append(v)
    if "trend" in cfg.match:
        tc = trend_code(C, t, cfg)
        if tc is None:
            return None
        parts.append(tc)
    if "level" in cfg.match and level is not None:
        lv = level[t]
        if lv is None or lv < 0 or (isinstance(lv, float) and np.isnan(lv)):
            return None
        parts.append(int(lv))
    return tuple(parts)


# ---------------------------------------------------------------- returns
def fwd_returns(C, d, h):
    """r[t] = 100 * (C[t+d+h] / C[t+d] - 1); NaN where t+d+h is past the end."""
    C = np.asarray(C, float)
    n = len(C)
    out = np.full(n, np.nan)
    if n > d + h:
        out[:n - d - h] = 100.0 * (C[d + h:] / C[d:n - h] - 1.0)
    return out


# ---------------------------------------------------------------- the harness
def run(C, events, h, d, cfg=None, level=None, lo=0, hi=None, vol_fn=None):
    """Matched-control comparison. C: close array (bar i opens at cfg.ts0_ms + i * bar ms). events: bar indices t.
    Events must already obey the signal's own cooldown. level: optional point-in-time int column, len(C)."""
    cfg = cfg or Config()
    vol_fn = vol_fn or vol_bucket
    C = np.asarray(C, float)
    n = len(C)
    hi = n if hi is None else min(hi, n)
    if cfg.ts0_ms + (hi - 1) * cfg.barms >= cfg.split_end_ms:
        raise ValueError("bars at/after the DEV cutoff (2024-07-01) are refused: VALIDATION/HOLDOUT are sealed")
    if level is not None and len(level) != n:
        raise ValueError("level column must have one entry per bar")
    ev = sorted(set(int(t) for t in events))
    W = d + h
    fwd = fwd_returns(C, d, h)
    fwd[hi - W:] = np.nan                       # an exit past the split end is never read
    fwd[:lo] = np.nan
    rv = rolling_rv(C, cfg.vol_win_min // cfg.bar_min)
    cut_win = cfg.cut_win_days * cfg.bpd

    # bars a control may not use: inside (or within cooldown of) any event's [t, t+W] window
    forbid = np.zeros(n + 1, int)
    for t in ev:
        a = max(0, t - W - cfg.cooldown)
        b = min(n, t + W + cfg.cooldown + 1)
        forbid[a] += 1
        forbid[b] -= 1
    free = np.cumsum(forbid)[:n] == 0
    valid = free & ~np.isnan(fwd)

    hours = ((cfg.ts0_ms + np.arange(n) * cfg.barms) // 3_600_000) % 24
    day = (cfg.ts0_ms + np.arange(n) * cfg.barms) // 86_400_000
    nb = cfg.trend_days * cfg.bpd
    trend = np.full(n, -1, int)
    if n > nb:
        r30 = C[nb:] / C[:-nb] - 1.0
        trend[nb:] = [TREND_CODE[tom_bt.trend_tag(r, cfg.trend_thr)] for r in r30]
    use_lvl = "level" in cfg.match and level is not None
    lvl = np.asarray(level, float) if use_lvl else None
    rng = np.random.default_rng(cfg.seed)
    vcache = {}
    vpos = 1 if "hour" in cfg.match else 0       # position of the vol bucket in the key tuple

    def vb(j):
        if j not in vcache:
            vcache[j] = vol_fn(rv, j, cut_win)
        return vcache[j]

    used = set()                                # distinct control bars drawn, for the reuse diagnostic
    rows = []                                   # (event fwd, mean control fwd, day, n controls)
    unmatched = dict(no_fwd=0, no_context=0, too_few_controls=0)
    for t in ev:
        if t < lo or t >= hi - W or np.isnan(fwd[t]):
            unmatched["no_fwd"] += 1
            continue
        key = context_key(C, t, cfg, level=lvl, vol_fn=vol_fn, rv=rv)
        if key is None:
            unmatched["no_context"] += 1
            continue
        cand = valid.copy()
        if "hour" in cfg.match:
            cand &= hours == hours[t]
        if "trend" in cfg.match:
            cand &= (trend == trend[t]) & (trend >= 0)
        if use_lvl:
            cand &= (lvl == lvl[t]) & (lvl >= 0)
        cand[:max(lo, 1)] = False
        pool = np.flatnonzero(cand)
        rng.shuffle(pool)
        chosen = []
        for j in pool:
            if len(chosen) >= cfg.K:
                break
            if "vol" in cfg.match and vb(int(j)) != key[vpos]:
                continue
            if any(abs(int(j) - c) <= cfg.cooldown for c in chosen):
                continue
            chosen.append(int(j))
        if len(chosen) < cfg.kmin:
            unmatched["too_few_controls"] += 1
            continue
        used.update(chosen)
        rows.append((fwd[t], float(np.mean(fwd[chosen])), int(day[t]), len(chosen)))

    n_dropped = sum(unmatched.values())
    res = dict(n_events=len(ev), n_matched=len(rows), n_unmatched=n_dropped, unmatched=unmatched, K=cfg.K,
               h=h, d=d, match=cfg.match)
    # unconditional mean: same eligible bars as the controls (outside every event window, so the trigger cannot leak into
    # the context number), every (d+h)-th bar so the windows do not overlap
    uidx = np.flatnonzero(valid)[::max(W, 1)]
    ufwd, uday = fwd[uidx], day[uidx]
    res["uncond_mean"] = float(ufwd.mean()) if len(ufwd) else float("nan")
    res["n_uncond"] = len(uidx)
    if not rows:
        res.update(event_mean=np.nan, control_mean=np.nan, trigger_effect=np.nan, trigger_se=np.nan, trigger_t=np.nan,
                   context_effect=np.nan, context_se=np.nan, context_t=np.nan)
        return res
    e = np.array([r[0] for r in rows])
    m = np.array([r[1] for r in rows])
    dy = np.array([r[2] for r in rows])
    x = e - m
    te, tse = screen.cluster_mean_se(x, dy)
    res.update(event_mean=float(e.mean()), control_mean=float(m.mean()), trigger_effect=float(te),
               trigger_se=float(tse), trigger_t=float(screen.tstat(te, tse)),
               n_controls_mean=float(np.mean([r[3] for r in rows])), n_controls_distinct=len(used),
               control_reuse=float(sum(r[3] for r in rows) / max(len(used), 1)))
    g = np.concatenate((m, ufwd))
    f = np.concatenate((np.ones(len(m)), np.zeros(len(ufwd))))
    cd_ = np.concatenate((dy, uday))
    ce, cse = screen.diff_cluster(g, f, cd_)
    res.update(context_effect=float(ce), context_se=float(cse), context_t=float(screen.tstat(ce, cse)))
    return res


def format_report(res):
    u = res["unmatched"]
    reuse = res.get("control_reuse", float("nan"))
    lines = [
        f"context-null  h={res['h']} d={res['d']} K={res['K']} match={','.join(res['match'])}",
        f"  n events {res['n_events']}  n matched {res['n_matched']}  n unmatched (dropped) {res['n_unmatched']} "
        f"(no_fwd {u['no_fwd']}, no_context {u['no_context']}, too_few_controls {u['too_few_controls']})",
        f"  controls: {res.get('n_controls_distinct', 0)} distinct bars, each used {reuse:.1f}x on average"
        + ("  WARNING: heavy control reuse, SE understated (pool too thin for this many events)" if reuse > REUSE_WARN else ""),
        f"  trigger effect  {res['trigger_effect']:+.4f} %  SE {res['trigger_se']:.4f}  t {res['trigger_t']:+.2f}"
        f"   (event mean {res['event_mean']:+.4f} % minus matched-control mean {res['control_mean']:+.4f} %)",
        f"  context-only effect {res['context_effect']:+.4f} %  SE {res['context_se']:.4f}  t {res['context_t']:+.2f}"
        f"   (matched-control mean minus unconditional mean {res['uncond_mean']:+.4f} %, n_uncond {res['n_uncond']})",
        f"  round trip cost: taker {screen.C_PCT:.2f} %, maker-in {screen.CM_PCT:.2f} %  "
        f"(trigger effect minus taker {res['trigger_effect'] - screen.C_PCT:+.4f} %)",
    ]
    return "\n".join(lines)
