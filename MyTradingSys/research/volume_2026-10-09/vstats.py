"""Inference for the volume study (PRE_REG section 5-6). numpy only; same statistic and bootstrap scheme as
candle pilot stats_lite.block_boot_family (studentised single-step max-T, circular block bootstrap), vectorised.

rc_family: events E x horizons H, both signs. stat[e,h] = mean(val[h] | ev[e]) - mean(val[h]) (continuation orientation supplied by the caller
via `val` already multiplied by the event direction). Sign +1 tests continuation, sign -1 tests reversal.
maxT over (e,h,sign) is max over (e,h) of |centred studentised replicate|.
"""
import sys
sys.dont_write_bytecode = True
import numpy as np


def _prefix(a):
    z = np.zeros(a.shape[:-1] + (a.shape[-1] + 1,))
    np.cumsum(a, axis=-1, out=z[..., 1:])
    return z


def _starts(m, block, reps, seed):
    nb = int(np.ceil(m / float(block)))
    rng = np.random.default_rng(seed)
    return rng.integers(0, m, size=(reps, nb)), nb


def rc_family(EV, VAL, block, min_n, reps=1000, seed=12345, chunk=100):
    """EV: (E, m) bool; VAL: (E, H, m) float orientation-adjusted forward returns (continuation positive);
    min_n: int. Returns dict of arrays shaped (E, H): n, stat, sd, t, live, and p_adj_cont / p_adj_rev / p_raw_cont / p_raw_rev."""
    E, m = EV.shape
    H = VAL.shape[1]
    evf = EV.astype(float)
    n = EV.sum(axis=1)
    live = n >= min_n                                           # (E,)
    # doubled (circular) prefix sums
    evd = np.concatenate([evf, evf], axis=1)                    # (E, 2m)
    PC = _prefix(evd)                                           # (E, 2m+1)
    PSF = np.empty((E, H, 2 * m + 1))
    PA = np.empty((E, H, 2 * m + 1))
    for h in range(H):
        vd = np.concatenate([VAL[:, h, :], VAL[:, h, :]], axis=1)  # (E, 2m)
        PSF[:, h, :] = _prefix(evd * vd)
        PA[:, h, :] = _prefix(vd)
    sum_ev_val = (evf[:, None, :] * VAL).sum(axis=2)            # (E,H)
    sum_all = VAL.sum(axis=2)
    with np.errstate(invalid="ignore", divide="ignore"):
        stat = sum_ev_val / n[:, None] - sum_all / m
    starts, nb = _starts(m, block, reps, seed)
    tot = nb * block
    boot = np.empty((E, H, reps))
    for r0 in range(0, reps, chunk):
        S = starts[r0:r0 + chunk]                               # (R, nb)
        R = S.shape[0]
        S2 = (S + block).reshape(-1)
        S1 = S.reshape(-1)
        cnt = (PC[:, S2] - PC[:, S1]).reshape(E, R, nb).sum(axis=2)         # (E,R)
        for h in range(H):
            sf = (PSF[:, h, S2] - PSF[:, h, S1]).reshape(E, R, nb).sum(axis=2)
            sa = (PA[:, h, S2] - PA[:, h, S1]).reshape(E, R, nb).sum(axis=2)
            with np.errstate(invalid="ignore", divide="ignore"):
                b = np.where(cnt > 0, sf / cnt - sa / tot, 0.0)
            boot[:, h, r0:r0 + R] = b
    mb = boot.mean(axis=2)
    sd = boot.std(axis=2, ddof=1)
    sd = np.where(sd > 0, sd, 1e-12)
    t = stat / sd
    cen = (boot - mb[:, :, None]) / sd[:, :, None]              # (E,H,reps)
    livemask = np.broadcast_to(live[:, None], (E, H))
    absmax = np.where(livemask[:, :, None], np.abs(cen), -np.inf).max(axis=(0, 1)) if live.any() else np.full(reps, -np.inf)
    out = {"n": n, "stat": stat, "sd": sd, "t": t, "live": live}
    p_raw_c = (np.sum(cen >= t[:, :, None], axis=2) + 1.0) / (reps + 1)
    p_raw_r = (np.sum(-cen >= -t[:, :, None], axis=2) + 1.0) / (reps + 1)
    p_adj_c = (np.sum(absmax[None, None, :] >= t[:, :, None], axis=2) + 1.0) / (reps + 1)
    p_adj_r = (np.sum(absmax[None, None, :] >= -t[:, :, None], axis=2) + 1.0) / (reps + 1)
    out.update({"p_raw_cont": p_raw_c, "p_raw_rev": p_raw_r, "p_adj_cont": p_adj_c, "p_adj_rev": p_adj_r})
    return out


def bh_qvalues(p):
    p = np.asarray(p, dtype=float)
    m = len(p)
    order = np.argsort(p)
    q = np.empty(m)
    prev = 1.0
    for rank in range(m, 0, -1):
        i = order[rank - 1]
        prev = min(prev, p[i] * m / rank)
        q[i] = prev
    return q


def mean_ci(ev, val, block, reps=1000, seed=12345):
    """Circular block bootstrap 95 percent CI of mean(val | ev). Returns (mean, lo, hi)."""
    m = len(ev)
    evf = ev.astype(float)
    n = evf.sum()
    if n == 0:
        return (np.nan, np.nan, np.nan)
    pc = _prefix(np.concatenate([evf, evf]))
    ps = _prefix(np.concatenate([evf * val, evf * val]))
    starts, nb = _starts(m, block, reps, seed)
    cnt = (pc[starts + block] - pc[starts]).sum(axis=1)
    sf = (ps[starts + block] - ps[starts]).sum(axis=1)
    ok = cnt > 0
    b = np.sort(sf[ok] / cnt[ok])
    return (float((evf * val).sum() / n), float(b[int(0.025 * len(b))]), float(b[min(len(b) - 1, int(0.975 * len(b)))]))


def contrast(evA, evB, val, block, reps=1000, seed=12345):
    """mean(val | A) - mean(val | B) with circular block bootstrap. Returns dict(nA, nB, diff, lo, hi, p_two)."""
    m = len(val)
    a, b = evA.astype(float), evB.astype(float)
    nA, nB = a.sum(), b.sum()
    if nA < 2 or nB < 2:
        return {"nA": int(nA), "nB": int(nB), "diff": np.nan, "lo": np.nan, "hi": np.nan, "p_two": np.nan}
    pa, pb = _prefix(np.concatenate([a, a])), _prefix(np.concatenate([b, b]))
    psa, psb = _prefix(np.concatenate([a * val, a * val])), _prefix(np.concatenate([b * val, b * val]))
    starts, nb = _starts(m, block, reps, seed)
    ca, cb = (pa[starts + block] - pa[starts]).sum(axis=1), (pb[starts + block] - pb[starts]).sum(axis=1)
    sa, sb = (psa[starts + block] - psa[starts]).sum(axis=1), (psb[starts + block] - psb[starts]).sum(axis=1)
    ok = (ca > 0) & (cb > 0)
    d = sa[ok] / ca[ok] - sb[ok] / cb[ok]
    diff = float((a * val).sum() / nA - (b * val).sum() / nB)
    ds = np.sort(d)
    cen = d - d.mean()
    p_two = float((np.sum(np.abs(cen) >= abs(diff)) + 1.0) / (len(d) + 1))
    return {"nA": int(nA), "nB": int(nB), "diff": diff, "meanA": float((a * val).sum() / nA), "meanB": float((b * val).sum() / nB),
            "lo": float(ds[int(0.025 * len(ds))]),
            "hi": float(ds[min(len(ds) - 1, int(0.975 * len(ds)))]), "p_two": p_two}


def mde(sd, n, z_alpha=1.645, z_power=0.8416):
    """Analytic minimum detectable mean difference (one-sided alpha .05, power 80 percent) for n events vs the large all-bar baseline."""
    return (z_alpha + z_power) * sd / np.sqrt(max(n, 1))


def pooled_contrast(cntA, sumA, cntB, sumB, block, reps=1000, seed=12345):
    """Pooled difference (sum sumA / sum cntA) - (sum sumB / sum cntB) with a circular block bootstrap over the bar index.
    cnt*: number of event instances at each bar (float), sum*: sum of their oriented returns at each bar.
    Returns dict(nA, nB, diff, lo, hi, p_one) with p_one = share of centred replicates >= diff (H1: diff > 0)."""
    m = len(cntA)
    nA, nB = float(cntA.sum()), float(cntB.sum())
    if nA < 2 or nB < 2:
        return {"nA": nA, "nB": nB, "diff": np.nan, "lo": np.nan, "hi": np.nan, "p_one": np.nan}
    pcA, psA = _prefix(np.concatenate([cntA, cntA])), _prefix(np.concatenate([sumA, sumA]))
    pcB, psB = _prefix(np.concatenate([cntB, cntB])), _prefix(np.concatenate([sumB, sumB]))
    starts, nb = _starts(m, block, reps, seed)
    ca, sa = (pcA[starts + block] - pcA[starts]).sum(axis=1), (psA[starts + block] - psA[starts]).sum(axis=1)
    cb, sb = (pcB[starts + block] - pcB[starts]).sum(axis=1), (psB[starts + block] - psB[starts]).sum(axis=1)
    ok = (ca > 0) & (cb > 0)
    d = sa[ok] / ca[ok] - sb[ok] / cb[ok]
    diff = float(sumA.sum() / nA - sumB.sum() / nB)
    cen = d - d.mean()
    ds = np.sort(d)
    return {"nA": int(nA), "nB": int(nB), "diff": diff, "meanA": float(sumA.sum() / nA), "meanB": float(sumB.sum() / nB),
            "lo": float(ds[int(0.025 * len(ds))]), "hi": float(ds[min(len(ds) - 1, int(0.975 * len(ds)))]),
            "p_one": float((np.sum(cen >= diff) + 1.0) / (len(d) + 1))}
