"""P-1 power and planted-edge harness (SYNTHESIS s4 P-1; VALIDATION 4d, 5b).

Units: event outcomes are in percent (0.10 = one fee). Events must be in time order.

| Parameter | Value | Label |
|---|---|---|
| Effect to detect | 0.10 (% mean) = one fee | SOURCED VALIDATION.md 5b(ii) |
| Alpha / power | 0.05 two-sided / 0.80 | OURS (conventional) |
| Multi-cell sizing | alpha divided by number of cells (Bonferroni, conservative vs the max-gap null), cell-vs-pooled factor k/(k-1) | OURS |
| Planted edge | +0.3 (%) on a random 20% of one cell's events | SOURCED VALIDATION.md 5b(i) |
| Null | circular shift of the label sequence, 1,000 shifts, statistic = max over cells of |cell mean - pooled mean| | SOURCED VALIDATION.md 4d (Westfall-Young style max statistic) |
| Flag rule | step-down: flag the largest-|gap| cell if it exceeds the 95th percentile of the null max gap, drop its events, repeat | OURS (95th per SYNTHESIS P1) |
"""
import math
from statistics import NormalDist

import numpy as np

_N = NormalDist()


def power_n(sd, effect=0.10, alpha=0.05, power=0.80, n_cells=1):
    """Events needed (per cell) to detect a mean shift `effect` with per-event sd `sd`.

    n_cells = 1: two-sided z test of one mean: n = ((z_{1-a/2} + z_power) * sd / effect)^2.
    n_cells = k > 1: one cell vs the pooled mean, alpha/k per cell, n multiplied by k/(k-1).
    """
    a = alpha / max(1, n_cells)
    z = _N.inv_cdf(1 - a / 2) + _N.inv_cdf(power)
    n = (z * sd / effect) ** 2
    if n_cells > 1:
        n *= n_cells / (n_cells - 1)
    return int(math.ceil(n))


def block_labels(n, n_cells, mean_block, rng):
    """Autocorrelated cell labels: contiguous blocks of random length (geometric, mean mean_block)."""
    runs, lens = [], []
    total = 0
    cur = int(rng.integers(n_cells))
    while total < n:
        L = int(rng.geometric(1.0 / mean_block))
        runs.append(cur)
        lens.append(L)
        total += L
        cur = int((cur + rng.integers(1, n_cells)) % n_cells) if n_cells > 1 else 0
    return np.repeat(np.array(runs, dtype=int), lens)[:n]


def inject_edge(outcomes, labels, cell, delta=0.3, frac=0.2, rng=None):
    """Add `delta` to a random `frac` of the events in `cell`. Returns (new outcomes, boolean mask)."""
    rng = rng or np.random.default_rng()
    out = np.array(outcomes, dtype=float, copy=True)
    idx = np.flatnonzero(np.asarray(labels) == cell)
    pick = rng.choice(idx, size=int(round(frac * len(idx))), replace=False)
    mask = np.zeros(len(out), dtype=bool)
    mask[pick] = True
    out[mask] += delta
    return out, mask


def remove_edge(outcomes, mask, delta=0.3):
    out = np.array(outcomes, dtype=float, copy=True)
    out[mask] -= delta
    return out


def _gaps(outcomes, labels, cells, pooled):
    sums = np.bincount(labels, weights=outcomes, minlength=cells)
    cnt = np.bincount(labels, minlength=cells)
    with np.errstate(invalid="ignore", divide="ignore"):
        return sums / cnt - pooled


def _null_max(y, lab, cells, n_shifts, rng):
    n = len(y)
    pooled = y.mean()
    out = np.empty(n_shifts)
    for i in range(n_shifts):
        k = int(rng.integers(1, n))
        out[i] = np.nanmax(np.abs(_gaps(y, np.roll(lab, k), cells, pooled)))
    return out


def shift_null_test(outcomes, labels, n_shifts=1000, q=0.95, rng=None):
    """Family-wise circular-shift null for the max between-cell gap, step-down.

    Step 1: observed max over cells of |cell mean - pooled mean| is compared with the q-quantile of the same
    statistic over `n_shifts` circular shifts of the label sequence (labels rolled, outcomes fixed; keeps label
    autocorrelation). If it exceeds, the argmax cell is flagged, its events are removed (so it no longer
    contaminates the pooled mean) and the test repeats on the rest, until nothing exceeds.
    Returns dict: gaps (step-1 gap per cell), max_gap, threshold (step-1), p_global (step 1), flagged (cells, in order found).
    """
    rng = rng or np.random.default_rng()
    y = np.asarray(outcomes, dtype=float)
    lab = np.asarray(labels, dtype=int)
    cells = int(lab.max()) + 1
    first = None
    flagged = []
    while len(np.unique(lab)) > 1 and len(y) > 2:
        obs = _gaps(y, lab, cells, y.mean())
        absobs = np.abs(obs)
        c = int(np.nanargmax(absobs))
        null_max = _null_max(y, lab, cells, n_shifts, rng)
        thr = float(np.quantile(null_max, q))
        if first is None:
            first = {
                "gaps": {j: float(obs[j]) for j in range(cells)},
                "max_gap": float(absobs[c]),
                "threshold": thr,
                "p_global": float((1 + (null_max >= absobs[c]).sum()) / (1 + n_shifts)),
            }
        if absobs[c] <= thr:
            break
        flagged.append(c)
        keep = lab != c
        y, lab = y[keep], lab[keep]
    if first is None:
        first = {"gaps": {}, "max_gap": float("nan"), "threshold": float("nan"), "p_global": 1.0}
    first["flagged"] = flagged
    return first
