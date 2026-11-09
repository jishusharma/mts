"""eh-f1-testnet-design: the sequential promote / kill rule for testnet forward runs, simulated on
synthetic fee-net R streams (numpy only; no market data, no HOLDOUT bars, no repo imports).

Rule (DESIGN.md Q1, all OURS unless stated):
  observation      x_i = fee-net R of closed trade i (one observation per UTC-day cluster when symbols
                   are pooled, Q3); fixed-R exits make x_i bounded: a <= x_i <= b (Q4)
  PROMOTE process  E+_n = mean over lambda in a grid of prod_i (1 + lambda * (x_i - mu0)),
                   mu0 = 0 R, lambda in (0, 1/(mu0 - a)]: a test supermartingale under H0: mean <= mu0
                   (Ville's inequality: P(sup E+ >= 1/alpha) <= alpha for ANY stopping rule)
  KILL process     E-_n = mean over the grid of prod_i (1 - lambda * (x_i - delta)),
                   delta = the smallest edge worth a slot, lambda in (0, 1/(b - delta)]:
                   a test supermartingale under H1: mean >= delta
  decision         PROMOTE at the first n >= n_min_promote with E+_n >= 1/alpha_slot
                   KILL    at the first n >= n_min_kill    with E-_n >= 1/beta
                   RETIRE  at n_max (undecided: neither a proven edge nor a proven loser; the slot is freed)
The grid mixture is itself a supermartingale (a convex mixture of supermartingales), so every weekly
look is free: no alpha is spent on interim readouts.

Synthetic R shapes (the brief's measured shapes): A = 30-40 % hit at a 2.5 R target, B = 45-50 % at 1 R;
each with a time-stop leg (mean 0) and a per-trade cost in R; the hit probability is solved from the
true mean so that each cell has an exact mean. Comparators: Krown R7 FAIL-A/B/C (FORWARD_PREREG.md s3)
and the Malkan card rule (kill at n = 30 if mean <= 0, never promote).

Run: python sim_sequential.py            (prints the DESIGN.md tables; ~20 s)
     python sim_sequential.py --quick    (fewer paths, for the test)
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass

import numpy as np

SEED = 20261109

# --- rule parameters (OURS; DESIGN.md Q1) ---------------------------------------------------------
MU0 = 0.0                # promote null: mean fee-net R <= 0 (the brief's null)
A_LOWER = -3.0           # lowest admissible R per observation (a stop gapped 2 R through is a review event)
DELTA_KILL = 0.25        # smallest edge worth a testnet slot, R per trade (OURS; R1 'plausible' was 0.30)
ALPHA_SLOT = 0.05 / 4    # family alpha 0.05 over K = 4 concurrent slots -> 1/alpha = 80 (Q2)
BETA_KILL = 0.10         # false-kill budget per run -> 1/beta = 10
N_MIN_PROMOTE = 30       # no promotion before 30 closed trades (Krown FAIL-C and the DEV screen use 30)
N_MIN_KILL = 10          # no statistical kill before 10 closed trades
N_MAX = 150              # retire undecided at 150 trades (or 12 months, whichever first; months not simulated)
LAMBDA_FRACS = (1 / 16, 1 / 8, 1 / 4, 1 / 2, 3 / 4)   # fractions of lambda_max, uniform mixture (never all-in)

# --- synthetic shapes (OURS, numbers from the wave's RESULT files) ---------------------------------
# cost_r: the mean fee_r the wave measured on 4h trades (eh-h5 0.042 R, eh-h1 0.041 R, R6 0.022 R)
COST_R_4H = 0.05
P_TIME = 0.20            # share of trades that end on the time stop (eh-h5 29 %, R6 10 %)
TIME_HALF_WIDTH = 0.6    # time-stop outcomes are uniform on [-0.6, +0.6] R (mean 0)


@dataclass(frozen=True)
class Shape:
    name: str
    target: float      # gross R at the target
    cost_r: float      # cost in R subtracted from every trade
    p_time: float = P_TIME

    def hit_prob(self, mean: float) -> float:
        """Hit probability among non-time trades that gives the requested true mean net R."""
        p = ((mean + self.cost_r) / (1.0 - self.p_time) + 1.0) / (self.target + 1.0)
        if not 0.0 < p < 1.0:
            raise ValueError(f"mean {mean} is not reachable with shape {self.name}")
        return p

    @property
    def upper(self) -> float:
        return self.target - self.cost_r

    @property
    def lower(self) -> float:
        return -1.0 - self.cost_r


SHAPE_A = Shape("A: 2.5R target", 2.5, COST_R_4H)
SHAPE_B = Shape("B: 1R target", 1.0, COST_R_4H)


def gen_stream(rng: np.random.Generator, shape: Shape, mean: float, paths: int, n: int) -> np.ndarray:
    """(paths, n) fee-net R draws with exact mean `mean`."""
    p = shape.hit_prob(mean)
    u = rng.random((paths, n))
    is_time = u < shape.p_time
    v = rng.random((paths, n))
    win = v < p
    r = np.where(win, shape.target, -1.0)
    t = rng.uniform(-TIME_HALF_WIDTH, TIME_HALF_WIDTH, (paths, n))
    r = np.where(is_time, t, r) - shape.cost_r
    return r


def gen_pairs(rng: np.random.Generator, shape: Shape, mean: float, paths: int, n_pairs: int,
              rho: float) -> np.ndarray:
    """(paths, 2*n_pairs) R draws where trades 2k and 2k+1 are a same-day BTC/ETH pair whose win/loss
    outcomes share a Gaussian latent with correlation rho (no time-stop leg; exact mean per trade)."""
    p = ((mean + shape.cost_r) + 1.0) / (shape.target + 1.0)
    z1 = rng.standard_normal((paths, n_pairs))
    z2 = rho * z1 + np.sqrt(1.0 - rho * rho) * rng.standard_normal((paths, n_pairs))
    thr = _norm_ppf(p)
    w1 = z1 < thr
    w2 = z2 < thr
    r1 = np.where(w1, shape.target, -1.0) - shape.cost_r
    r2 = np.where(w2, shape.target, -1.0) - shape.cost_r
    out = np.empty((paths, 2 * n_pairs))
    out[:, 0::2] = r1
    out[:, 1::2] = r2
    return out


def _norm_ppf(p: float) -> float:
    """Inverse normal CDF by bisection (no scipy)."""
    lo, hi = -10.0, 10.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if _norm_cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def _norm_cdf(x: float) -> float:
    from math import erf, sqrt
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


# --- the e-processes --------------------------------------------------------------------------------
def _log_mixture(logs: np.ndarray) -> np.ndarray:
    """logs: (G, paths, n) log-wealth per grid point -> (paths, n) log of the uniform mixture."""
    m = logs.max(axis=0)
    return m + np.log(np.mean(np.exp(logs - m), axis=0))


def e_promote(x: np.ndarray, mu0: float = MU0, a: float = A_LOWER,
              fracs=LAMBDA_FRACS) -> np.ndarray:
    """Cumulative e-process for H0: mean <= mu0. x: (paths, n), every x >= a."""
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        x = x[None, :]
    if np.any(x < a):
        raise ValueError("an observation is below the admissible lower bound a; review that trade")
    lam_max = 1.0 / (mu0 - a)
    logs = np.stack([np.cumsum(np.log1p(f * lam_max * (x - mu0)), axis=1) for f in fracs])
    return np.exp(_log_mixture(logs))


def e_kill(x: np.ndarray, delta: float = DELTA_KILL, b: float = SHAPE_A.upper,
           fracs=LAMBDA_FRACS) -> np.ndarray:
    """Cumulative e-process for H1: mean >= delta. x: (paths, n), every x <= b."""
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        x = x[None, :]
    if np.any(x > b):
        raise ValueError("an observation is above the admissible upper bound b; review that trade")
    lam_max = 1.0 / (b - delta)
    logs = np.stack([np.cumsum(np.log1p(-f * lam_max * (x - delta)), axis=1) for f in fracs])
    return np.exp(_log_mixture(logs))


@dataclass(frozen=True)
class RuleCfg:
    alpha: float = ALPHA_SLOT
    beta: float = BETA_KILL
    n_min_promote: int = N_MIN_PROMOTE
    n_min_kill: int = N_MIN_KILL
    n_max: int = N_MAX
    delta: float = DELTA_KILL
    mu0: float = MU0
    a: float = A_LOWER
    b: float = SHAPE_A.upper


def decide(x: np.ndarray, cfg: RuleCfg = RuleCfg()) -> tuple[np.ndarray, np.ndarray]:
    """Apply the rule trade by trade. Returns (decision code per path, n at decision).
    codes: 1 = PROMOTE, -1 = KILL, 0 = RETIRE at n_max."""
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        x = x[None, :]
    x = x[:, : cfg.n_max]
    paths, n = x.shape
    ep = e_promote(x, cfg.mu0, cfg.a)
    ek = e_kill(x, cfg.delta, cfg.b)
    idx = np.arange(1, n + 1)[None, :]
    promote_ok = (ep >= 1.0 / cfg.alpha) & (idx >= cfg.n_min_promote)
    kill_ok = (ek >= 1.0 / cfg.beta) & (idx >= cfg.n_min_kill)
    first_p = np.where(promote_ok.any(axis=1), promote_ok.argmax(axis=1) + 1, n + 1)
    first_k = np.where(kill_ok.any(axis=1), kill_ok.argmax(axis=1) + 1, n + 1)
    code = np.zeros(paths, dtype=int)
    n_dec = np.full(paths, n, dtype=int)
    # a kill and a promote on the same trade cannot both hold (E+ large means E- small); kill wins ties
    kill_first = first_k <= first_p
    code[kill_first & (first_k <= n)] = -1
    n_dec[kill_first & (first_k <= n)] = first_k[kill_first & (first_k <= n)]
    prom = (~kill_first) & (first_p <= n)
    code[prom] = 1
    n_dec[prom] = first_p[prom]
    return code, n_dec


# --- comparators ----------------------------------------------------------------------------------
def krown_abc(x: np.ndarray, dd_r: float = 12.0, streak: int = 12, n_c: int = 30, z: float = 1.28,
              n_max: int = N_MAX) -> np.ndarray:
    """Krown R7 FAIL-A (drawdown), FAIL-B (losing streak), FAIL-C (n >= 30, mean + z SE < 0).
    Returns the kill trade index per path, or n_max + 1 if never killed. Never promotes."""
    x = np.asarray(x, dtype=float)[:, :n_max]
    paths, n = x.shape
    cum = np.cumsum(x, axis=1)
    peak = np.maximum.accumulate(np.maximum(cum, 0.0), axis=1)
    fail_a = (peak - cum) >= dd_r
    loser = x < 0
    run = np.zeros_like(x, dtype=int)
    cur = np.zeros(paths, dtype=int)
    for i in range(n):
        cur = np.where(loser[:, i], cur + 1, 0)
        run[:, i] = cur
    fail_b = run >= streak
    idx = np.arange(1, n + 1)[None, :]
    mean = cum / idx
    sq = np.cumsum(x * x, axis=1)
    var = np.maximum((sq - idx * mean * mean) / np.maximum(idx - 1, 1), 0.0)
    se = np.sqrt(var / idx)
    fail_c = (idx >= n_c) & (mean + z * se < 0)
    anyfail = fail_a | fail_b | fail_c
    return np.where(anyfail.any(axis=1), anyfail.argmax(axis=1) + 1, n + 1)


def malkan30(x: np.ndarray, n_at: int = 30) -> np.ndarray:
    """The malkan-level-short-testnet-forward-1109 card rule: after 30 closed trades net R <= 0 -> kill.
    Returns 1 (killed at 30) or 0 per path."""
    x = np.asarray(x, dtype=float)
    return (x[:, :n_at].sum(axis=1) <= 0).astype(int)


# --- tables ---------------------------------------------------------------------------------------
MEANS = (-0.30, -0.20, -0.087, 0.0, 0.10, 0.25, 0.40, 0.60)


def table_rule(rng, shape: Shape, cfg: RuleCfg, paths: int, title: str) -> str:
    lines = [f"### {title}", "",
             "| true mean R | hit % (non-time) | P(promote) | P(kill) | P(retire at n_max) | "
             "median n to decision | mean n | P(decided by 60) |",
             "|---|---|---|---|---|---|---|---|"]
    for m in MEANS:
        x = gen_stream(rng, shape, m, paths, cfg.n_max)
        code, nd = decide(x, cfg)
        pp = float(np.mean(code == 1))
        pk = float(np.mean(code == -1))
        pr = float(np.mean(code == 0))
        dec = code != 0
        med = int(np.median(nd[dec])) if dec.any() else cfg.n_max
        by60 = float(np.mean(dec & (nd <= 60)))
        lines.append(f"| {m:+.3f} | {100 * shape.hit_prob(m):.0f} | {pp:.3f} | {pk:.3f} | {pr:.3f} | "
                     f"{med} | {nd.mean():.0f} | {by60:.2f} |")
    return "\n".join(lines) + "\n"


def table_comparators(rng, shape: Shape, paths: int, n_max: int = N_MAX) -> str:
    lines = ["### Comparators on shape A (kill probability by n_max = 150; Krown A/B/C and the 30-trade card rule)", "",
             "| true mean R | Krown A/B/C P(kill) | Krown median n to kill | card rule P(kill at 30) |",
             "|---|---|---|---|"]
    for m in MEANS:
        x = gen_stream(rng, shape, m, paths, n_max)
        kn = krown_abc(x, n_max=n_max)
        killed = kn <= n_max
        med = int(np.median(kn[killed])) if killed.any() else n_max
        lines.append(f"| {m:+.3f} | {killed.mean():.3f} | {med} | {malkan30(x).mean():.3f} |")
    return "\n".join(lines) + "\n"


def table_pooling(rng, shape: Shape, cfg: RuleCfg, paths: int, rho: float = 0.7) -> str:
    """Same-day BTC/ETH pairs with outcome correlation rho: naive pooling (each leg one observation)
    vs the cluster-mean rule (one observation = mean R of the pair) vs BTC alone."""
    lines = [f"### Pooling (Q3): same-day pairs, latent outcome correlation rho = {rho}, shape A, 1/alpha = {1 / cfg.alpha:.0f}", "",
             "| true mean R | naive pooled P(promote) | cluster-mean P(promote) | BTC-alone P(promote) | "
             "naive P(kill) | cluster-mean P(kill) | BTC-alone P(kill) | cluster-mean median n (clusters) |",
             "|---|---|---|---|---|---|---|---|"]
    for m in (-0.087, 0.0, 0.25, 0.40):
        n_pairs = cfg.n_max
        x = gen_pairs(rng, shape, m, paths, n_pairs, rho)
        naive_code, _ = decide(x[:, : cfg.n_max], cfg)
        clus = 0.5 * (x[:, 0::2] + x[:, 1::2])
        clus_code, clus_n = decide(clus, cfg)
        solo_code, _ = decide(x[:, 0::2], cfg)
        dec = clus_code != 0
        med = int(np.median(clus_n[dec])) if dec.any() else cfg.n_max
        lines.append(f"| {m:+.3f} | {np.mean(naive_code == 1):.3f} | {np.mean(clus_code == 1):.3f} | "
                     f"{np.mean(solo_code == 1):.3f} | {np.mean(naive_code == -1):.3f} | "
                     f"{np.mean(clus_code == -1):.3f} | {np.mean(solo_code == -1):.3f} | {med} |")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--paths", type=int, default=4000)
    args = ap.parse_args(argv)
    paths = 500 if args.quick else args.paths
    rng = np.random.default_rng(SEED)
    cfg = RuleCfg()
    out = [f"seed {SEED}, paths {paths}, n_max {cfg.n_max}, 1/alpha {1 / cfg.alpha:.0f}, 1/beta {1 / cfg.beta:.0f}, "
           f"delta_kill {cfg.delta}, n_min promote/kill {cfg.n_min_promote}/{cfg.n_min_kill}, a {cfg.a}, b {cfg.b:.2f}",
           ""]
    out.append(table_rule(rng, SHAPE_A, cfg, paths, "Shape A (2.5R target, 30-40 % hit), 1/alpha = 80 (4 slots)"))
    out.append(table_rule(rng, SHAPE_B, RuleCfg(b=SHAPE_B.upper), paths, "Shape B (1R target, 45-50 % hit), 1/alpha = 80"))
    out.append(table_rule(rng, SHAPE_A, RuleCfg(alpha=0.05), paths, "Shape A, single slot 1/alpha = 20 (for comparison; not the rule)"))
    out.append(table_rule(rng, SHAPE_A, RuleCfg(n_max=300), paths, "Shape A, 1/alpha = 80, if the run were allowed 300 trades (information only)"))
    out.append(table_comparators(rng, SHAPE_A, paths))
    out.append(table_pooling(rng, SHAPE_A, cfg, paths))
    text = "\n".join(out)
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
