"""Matched day-block inference for event vs control arms (analysis version 2 design; no outcomes run here).

Spec (see ANALYSIS_V2_DESIGN.md):
- Block = UTC day. Observations of one day (event clustering) are averaged first, per arm.
- Common clock: only days with >= 1 observation in BOTH arms enter; other days are dropped and counted.
- Day contrast D_d = mean(event_d) - mean(control_d). Statistic = mean_d D_d (equal day weight).
- p-value: two-sided sign-flip randomization of the D_d (exact enumeration when days <= EXACT_MAX, else seeded Monte Carlo).
- CI: seeded percentile bootstrap resampling whole days with replacement.
"""
import itertools

import numpy as np

EXACT_MAX = 16


def day_contrasts(event_vals, event_days, ctrl_vals, ctrl_days):
    ev, ed = np.asarray(event_vals, float), np.asarray(event_days)
    cv, cd = np.asarray(ctrl_vals, float), np.asarray(ctrl_days)
    common = sorted(set(ed.tolist()) & set(cd.tolist()))
    d = np.array([ev[ed == k].mean() - cv[cd == k].mean() for k in common], float)
    dropped = len(set(ed.tolist()) | set(cd.tolist())) - len(common)
    return np.array(common), d, dropped


def paired_day_inference(event_vals, event_days, ctrl_vals, ctrl_days, seed=0, n_mc=20000, n_boot=5000, alpha=0.05):
    days, d, dropped = day_contrasts(event_vals, event_days, ctrl_vals, ctrl_days)
    n = len(d)
    if n == 0:
        return {"n_days": 0, "dropped_days": dropped, "contrast": float("nan"), "p_two_sided": float("nan"),
                "ci": (float("nan"), float("nan"))}
    obs = float(d.mean())
    tol = 1e-12 * max(1.0, abs(obs))
    if n <= EXACT_MAX:
        signs = np.array(list(itertools.product((-1.0, 1.0), repeat=n)))
        stats = (signs * d).mean(axis=1)
        p = float((np.abs(stats) >= abs(obs) - tol).mean())
    else:
        rng = np.random.default_rng(seed)
        signs = rng.choice((-1.0, 1.0), size=(n_mc, n))
        stats = (signs * d).mean(axis=1)
        p = float(((np.abs(stats) >= abs(obs) - tol).sum() + 1) / (n_mc + 1))
    rng = np.random.default_rng(seed + 1)
    boots = d[rng.integers(0, n, size=(n_boot, n))].mean(axis=1)
    ci = (float(np.quantile(boots, alpha / 2)), float(np.quantile(boots, 1 - alpha / 2)))
    return {"n_days": n, "dropped_days": dropped, "contrast": obs, "p_two_sided": p, "ci": ci}
