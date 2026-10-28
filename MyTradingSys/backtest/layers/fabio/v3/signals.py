"""Fabio v3 signals S1-S9 and the section-2 helpers (FABIO_V3_SPEC.md sections 2 and 3). Pure functions, no state.

Conventions (spec section 2): every function f(bars, i, ...) reads bars[0..i] ONLY (look-ahead canary T49/T64);
s = +1 long / buyers, -1 short / sellers; v[i] = buy_vol + sell_vol, d[i] = delta; a window [a, i] is valid only if
t[i] - t[a] == (i - a) * 60000, else the signal returns None (or 0 / False / {0,0} for signals whose result is not
a dict). Parameters are passed explicitly (spec :365). Function-level defaults exist so tests T01-T50 stay valid
(spec :366); they are NOT selected grid values. NS-grid parameters without a spec default (z_hi of S3) have no
default and raise ValueError when omitted.

Provenance labels (spec 7.1): P01 N (NS-grid, caller), P02 k_bal 0.8 / POC band 0.25 (NS-fixed), P03 p (NS-grid) /
drift q 0.25 (NS-fixed), P04 L 60, z_hi (NS-grid), r_abs 0.25, r_ctl 1.0 (NS-fixed), P05 big trade = 99th / 99.9th
percentile of the prior 30 days (data, NS-fixed), P06 tier VR 1.5, 20 d, min 10 (NS-fixed), P07 m (NS-grid / 15
NS-fixed), P08 S5 trigger on the close (FABIO), P09 S5D (FABIO), P10 S6 anchor (FABIO), P11 S7 gate on / VA 0.70
(FABIO / NS-fixed), P13 S8(a) 15 bars (NS-fixed), P14 S8(b) rule N 60 (FABIO / NS-fixed), P15 S8(c) (FABIO),
P16 S8(d) one-bar look-back (FABIO / NS-fixed), P35 LVN rule (NS-fixed), P41 B_prof 50, VA/LVN algorithm, ATR (SIM).
"""
import functools
import math
import statistics

from MyTradingSys.backtest.layers.fabio.orderflow_bars import parse_fp

from .costs import MIN_MS

B_PROF = 50.0          # P41 SIM, spec section 1: profile bin 50 USD (fp 10 USD bins re-binned); tests may pass any bin size
BAL_POC_BAND = 0.25    # P02 NS-fixed: |c - poc| <= 0.25 * R
K_BAL = 0.8            # P02 NS-fixed (function default; grid statement "k_bal 0.8", spec 7.2)
DRIFT_Q = 0.25         # P03 NS-fixed: drift q = 0.25
EFFORT_L = 60          # P04 NS-fixed: S3 L = 60
R_ABS = 0.25           # P04 NS-fixed
R_CTL = 1.0            # P04 NS-fixed
VR_TIER = 1.5          # P06 NS-fixed: tier "999" iff VR >= 1.5
VR_DAYS = 20           # P06 NS-fixed: prior 20 valid weekdays
VR_MIN_DAYS = 10       # P06 NS-fixed: fewer than 10 prior days -> "99"
VA_PCT = 0.70          # P11 NS-fixed: value area 70%
LVN_FRAC = 0.5         # P35 NS-fixed: LVN <= 0.5 * median (fabio_of_model.py:101-104 algorithm, spec section 2)
S8_AGE = 15            # P13 NS-fixed: S8(a) 15 bars
S8_N = 60              # P14 NS-fixed: S8(b) balance window N 60
S8_Z_HI = 2.5          # P04 NS-grid value used as the S8 function default by the spec signature (spec :90, 7.2 "z_hi 2.5")
S8_P = 0.10            # P03 NS-grid value used as the S8 function default by the spec signature (spec :90)


# ---------------------------------------------------------------- low-level helpers
def contiguous(bars, a, i):
    """Spec section 1: window [a, i] valid only if t[i] - t[a] == (i - a) * 60000."""
    if a < 0 or a > i or i >= len(bars):
        return False
    return bars[i]["t"] - bars[a]["t"] == (i - a) * MIN_MS


@functools.lru_cache(maxsize=16384)
def _parse(fp):
    if not fp:
        return ()
    return tuple(parse_fp(fp))


def _tier_cols(tier):
    if tier == "99":
        return "b99_buy_vol", "b99_sell_vol"
    if tier == "999":
        return "b999_buy_vol", "b999_sell_vol"
    raise ValueError("tier must be '99' or '999', got %r" % (tier,))


def _vol(b):
    return b["buy_vol"] + b["sell_vol"]


def _zscore(prev, x):
    """z(x; L) = (x - mean(prev)) / pstdev(prev) (population sd). pstdev == 0 -> None (spec section 2)."""
    n = len(prev)
    if n == 0:
        return None
    if min(prev) == max(prev):          # exact pstdev == 0 without float noise
        return None
    mean = math.fsum(prev) / n
    sd = math.sqrt(math.fsum((v - mean) ** 2 for v in prev) / n)
    if sd == 0.0:
        return None
    return (x - mean) / sd


# ---------------------------------------------------------------- section 2 helpers
def true_range(bars, j):
    """TR[j] = max(h-l, |h - c[j-1]|, |l - c[j-1]|), j >= 1 (FORMULAS.md section 12)."""
    b, pc = bars[j], bars[j - 1]["c"]
    return max(b["h"] - b["l"], abs(b["h"] - pc), abs(b["l"] - pc))


def atr(bars, i, N):
    """ATR_N(i) = mean(TR[i-N+1..i]) (plain SMA of TR, FORMULAS.md section 12); needs i >= N, else None."""
    if N < 1 or i < N or not contiguous(bars, i - N, i):
        return None
    return math.fsum(true_range(bars, j) for j in range(i - N + 1, i + 1)) / N


def build_profile(bars, a, i, bin_size):
    """P(window): dict bin -> sum(buy + sell) over the fp entries of bars a..i, re-binned k = floor(binlow/B)*B (spec section 2)."""
    prof = {}
    for j in range(a, i + 1):
        for lo, bu, se in _parse(bars[j]["fp"]):
            k = math.floor(lo / bin_size + 1e-9) * bin_size
            prof[k] = prof.get(k, 0.0) + bu + se
    return prof


def _dense(profile, bin_size):
    """Dense volume list from the lowest to the highest bin: (lo, v)."""
    lo = min(profile)
    hi = max(profile)
    n = int(round((hi - lo) / bin_size)) + 1
    v = [0.0] * n
    for k, vol in profile.items():
        v[int(round((k - lo) / bin_size))] += vol
    return lo, v


def poc_center(profile, bin_size):
    """POC = bin with max volume, ties -> lower bin; poc_center = bin + B/2 (spec section 2). None for an empty profile."""
    if not profile:
        return None
    lo, v = _dense(profile, bin_size)
    k = max(range(len(v)), key=lambda x: (v[x], -x))
    return lo + k * bin_size + bin_size / 2.0


def value_area(profile, bin_size):
    """70% value area (spec section 2, algorithm of fabio_of_model.py:84-99 with bin as a parameter).

    Returns {"VAL", "VAH", "poc", "poc_center", "total"} or None for an empty / zero-volume profile.
    """
    if not profile:
        return None
    lo, v = _dense(profile, bin_size)
    n = len(v)
    total = math.fsum(v)
    if not total > 0:
        return None
    poc_i = max(range(n), key=lambda x: (v[x], -x))
    a = z = poc_i
    acc = v[poc_i]
    while acc < VA_PCT * total and (a > 0 or z < n - 1):
        up = (v[z + 1] if z + 1 < n else 0.0) + (v[z + 2] if z + 2 < n else 0.0)
        dn = (v[a - 1] if a - 1 >= 0 else 0.0) + (v[a - 2] if a - 2 >= 0 else 0.0)
        if z >= n - 1 or (a > 0 and dn > up):
            for _ in range(min(2, a)):
                a -= 1
                acc += v[a]
        else:
            for _ in range(min(2, n - 1 - z)):
                z += 1
                acc += v[z]
    return {"VAL": lo + a * bin_size, "VAH": lo + z * bin_size + bin_size, "poc": lo + poc_i * bin_size,
            "poc_center": lo + poc_i * bin_size + bin_size / 2.0, "total": total}


def lvn_levels(profile, bin_size):
    """LVN prices (bin centres, ascending): interior i with v[i] < v[i-1] and v[i] <= v[i+1] and v[i] <= 0.5*med, med =
    upper median of the nonzero v (spec section 2; fabio_of_model.py:101-104)."""
    if not profile:
        return []
    lo, v = _dense(profile, bin_size)
    nz = sorted(x for x in v if x > 0)
    if not nz:
        return []
    med = nz[len(nz) // 2]
    return [lo + k * bin_size + bin_size / 2.0 for k in range(1, len(v) - 1)
            if v[k] < v[k - 1] and v[k] <= v[k + 1] and v[k] <= LVN_FRAC * med]


def select_lvn(lvns, s, X, O, c):
    """LVN* (model A, spec section 4): candidates have s*(X - lvn) >= 0.25*s*(X - O) and s*(c - lvn) > 0; the one nearest
    to X wins. None if no candidate. 0.25 = P35 NS-fixed retrace."""
    thr = 0.25 * s * (X - O)
    cands = [x for x in lvns if s * (X - x) >= thr and s * (c - x) > 0]
    if not cands:
        return None
    return min(cands, key=lambda x: (abs(X - x), x))


# ---------------------------------------------------------------- S1 / S2
def balance(bars, i, N, k_bal=K_BAL, bin_size=B_PROF):
    """S1 balance -> {"H", "L", "R", "poc"} or None (spec section 3).

    W = [i-N+1, i]; H = max h, L = min l, R = H - L, poc = poc_center(P(W)). Balance iff R <= k_bal*sqrt(N)*ATR_N(i)
    AND |c[i] - poc| <= 0.25*R. Needs i >= N (ATR). All bars read, i-N..i, must be contiguous.
    """
    if N < 1 or i < N:
        return None
    A = atr(bars, i, N)            # includes the contiguity check of [i-N, i]
    if A is None:
        return None
    a = i - N + 1
    H = max(bars[j]["h"] for j in range(a, i + 1))
    L = min(bars[j]["l"] for j in range(a, i + 1))
    R = H - L
    if R > k_bal * math.sqrt(N) * A:                    # P02 k_bal (NS-fixed 0.8)
        return None
    poc = poc_center(build_profile(bars, a, i, bin_size), bin_size)
    if poc is None:
        return None
    if abs(bars[i]["c"] - poc) > BAL_POC_BAND * R:      # P02 POC band 0.25 (NS-fixed)
        return None
    return {"H": H, "L": L, "R": R, "poc": poc}


def _s2_from(bars, i, N, p, q, bal):
    """S2 given an already computed S1 result at i."""
    if bal is None:
        return 0
    a = i - N + 1
    sv = math.fsum(_vol(bars[j]) for j in range(a, i + 1))
    if not sv > 0 or not bal["R"] > 0:
        return 0
    P = math.fsum(bars[j]["delta"] for j in range(a, i + 1)) / sv
    drift = abs(bars[i]["c"] - bars[a]["o"]) / bal["R"]
    if abs(P) >= p and drift <= q:                       # P03 p (NS-grid), q (NS-fixed 0.25)
        return 1 if P > 0 else -1
    return 0


def pressure(bars, i, N, p, q=DRIFT_Q, k_bal=K_BAL, bin_size=B_PROF):
    """S2 pressure -> +1 accumulation / -1 distribution / 0 (spec section 3). Only where S1(i) is not None.

    P = sum(d[W]) / sum(v[W]); drift = |c[i] - o[i-N+1]| / R; S2 = sign(P) iff |P| >= p and drift <= q.
    """
    return _s2_from(bars, i, N, p, q, balance(bars, i, N, k_bal, bin_size))


# ---------------------------------------------------------------- S3
def _effort(bars, i, L, z_hi, r_abs, r_ctl):
    """-> (control, absorbed) in {-1, 0, +1}; (0, 0) when either z is undefined (spec section 3 S3)."""
    if L < 1 or i < L or not contiguous(bars, i - L, i):
        return 0, 0
    prev = bars[i - L:i]
    e = _zscore([b["delta"] for b in prev], bars[i]["delta"])
    res = _zscore([b["c"] - b["o"] for b in prev], bars[i]["c"] - bars[i]["o"])
    if e is None or res is None:
        return 0, 0
    control = absorbed = 0
    for s in (1, -1):
        if s * e >= z_hi:
            if s * res >= r_ctl:
                control = s
            if s * res <= r_abs:
                absorbed = s
    return control, absorbed


def effort_result(bars, i, L=EFFORT_L, z_hi=None, r_abs=R_ABS, r_ctl=R_CTL):
    """S3 effort vs result -> {"control": s|0, "absorbed": s|0} (spec section 3).

    e = z(d_i; L), res = z(r_i; L), r = c - o. For s in {+1,-1}: CONTROL = s if s*e >= z_hi and s*res >= r_ctl;
    ABSORBED = s if s*e >= z_hi and s*res <= r_abs (side s aggressed, no result or against; bias -s).
    z_hi is NS-grid (P04): there is no default; omitting it raises ValueError.
    """
    if z_hi is None:
        raise ValueError("z_hi is required (NS-grid P04, no selected value)")
    c, a = _effort(bars, i, L, z_hi, r_abs, r_ctl)
    return {"control": c, "absorbed": a}


def effort_arrays(bars, i_end, L=EFFORT_L, z_hi=None, r_abs=R_ABS, r_ctl=R_CTL):
    """(ctrl, absb) lists of length i_end+1: ctrl[j] / absb[j] = S3(j).control / .absorbed (0 where undefined)."""
    if z_hi is None:
        raise ValueError("z_hi is required (NS-grid P04, no selected value)")
    ctrl, absb = [], []
    for j in range(i_end + 1):
        c, a = _effort(bars, j, L, z_hi, r_abs, r_ctl)
        ctrl.append(c)
        absb.append(a)
    return ctrl, absb


# ---------------------------------------------------------------- S4 / tier
def volume_tier(today_vol, prior_vols, min_days=VR_MIN_DAYS):
    """Adaptive big-trade tier (spec section 3 S4): "999" iff VR >= 1.5 else "99".

    VR = session volume so far / median of the prior valid weekdays' volume over the same elapsed minutes (the last
    20 given, oldest first, P06); fewer than min_days (10) prior days -> "99".
    """
    pv = list(prior_vols)[-VR_DAYS:]
    if len(pv) < min_days:
        return "99"
    med = statistics.median(pv)
    if not med > 0:
        return "99"
    return "999" if today_vol / med >= VR_TIER else "99"


def net_big(bars, i, m, tier="99"):
    """net(i; m) = sum over [i-m+1, i] of (bT_buy_vol - bT_sell_vol); None if the window is invalid."""
    if m < 1 or i - m + 1 < 0 or not contiguous(bars, i - m + 1, i):
        return None
    kb, ks = _tier_cols(tier)
    return math.fsum(bars[j][kb] - bars[j][ks] for j in range(i - m + 1, i + 1))


def big_push(bars, i, m, s, tier="99"):
    """S4 -> bool: s * net(i; m) > 0 (spec section 3)."""
    net = net_big(bars, i, m, tier)
    return net is not None and s * net > 0


# ---------------------------------------------------------------- S5 / S5D
def breakout(bars, i, N, k_bal, p, m, tier="99", bin_size=B_PROF):
    """S5 -> +1 / -1 / 0 (spec section 3): break WITH the pressure.

    S5 = s if S2(i-1) == s, s*(c[i] - E_s) > 0 with E_{+1} = H(i-1), E_{-1} = L(i-1), and S4(i, m, s). Trigger on the
    close (P08 FABIO).
    """
    if i < 1 or not contiguous(bars, i - 1, i):
        return 0
    bal = balance(bars, i - 1, N, k_bal, bin_size)
    s = _s2_from(bars, i - 1, N, p, DRIFT_Q, bal)
    if s == 0:
        return 0
    E = bal["H"] if s > 0 else bal["L"]
    if s * (bars[i]["c"] - E) > 0 and big_push(bars, i, m, s, tier):
        return s
    return 0


def failed_auction(bars, i, N, k_bal, p, m, absorbed, tier="99", bin_size=B_PROF):
    """S5D -> {"s", "lvl", "edge"} or None (spec section 3, v3.1; P09 FABIO): break AGAINST absorbed pressure.

    S1(i-1) not None and S2(i-1) == -s, some j in [i-N, i-1] with absb[j] == -s (the pressing side was absorbed),
    s*(c[i] - E_s) > 0 and S4(i, m, s). edge = E_s; lvl = absorption level of the LAST such j: l[j] if s = +1, h[j]
    if s = -1. `absorbed` is the absb array (index = bar index; indexes past its end count as 0).
    """
    if i < 1 or not contiguous(bars, i - 1, i):
        return None
    bal = balance(bars, i - 1, N, k_bal, bin_size)
    sig = _s2_from(bars, i - 1, N, p, DRIFT_Q, bal)
    if sig == 0:
        return None
    s = -sig                                           # side -s = sig pressed
    E = bal["H"] if s > 0 else bal["L"]
    if not s * (bars[i]["c"] - E) > 0 or not big_push(bars, i, m, s, tier):
        return None
    jj = None
    for j in range(i - 1, i - N - 1, -1):
        if 0 <= j < len(absorbed) and absorbed[j] == sig:
            jj = j
            break
    if jj is None:
        return None
    return {"s": s, "lvl": bars[jj]["l"] if s > 0 else bars[jj]["h"], "edge": E}


# ---------------------------------------------------------------- S6 / S9 / S7
def control_level(bars, ctrl, a, i, s):
    """S6 (spec section 3, P10 FABIO): last j in (a, i] with ctrl[j] == s; l[j] if s = +1, h[j] if s = -1; else None."""
    for j in range(i, a, -1):
        if j < len(ctrl) and ctrl[j] == s:
            return bars[j]["l"] if s > 0 else bars[j]["h"]
    return None


def defended_level(bars, absorbed, a, i, s):
    """S9 (spec section 3, v3.1; P20 FABIO): last j in (a, i] with absb[j] == s (our side absorbed there = the level the
    other side defends); h[j] if s = +1, l[j] if s = -1; else None."""
    for j in range(i, a, -1):
        if j < len(absorbed) and absorbed[j] == s:
            return bars[j]["h"] if s > 0 else bars[j]["l"]
    return None


def curve(bars, i, sess_open, bin_size=B_PROF):
    """S7 -> "premium" / "fair" / "discount" (spec section 3): session profile [sess_open, i], value area as section 2;
    premium if c[i] > VAH, discount if c[i] < VAL, else fair. None if the window is not contiguous or empty."""
    if not contiguous(bars, sess_open, i):
        return None
    va = value_area(build_profile(bars, sess_open, i, bin_size), bin_size)
    if va is None:
        return None
    c = bars[i]["c"]
    if c > va["VAH"]:
        return "premium"
    if c < va["VAL"]:
        return "discount"
    return "fair"


# ---------------------------------------------------------------- S8
def exhaustion(bars, i, trade, k_bal=K_BAL, tier="99", bin_size=B_PROF, z_hi=S8_Z_HI, p=S8_P, climax=False, cache=None):
    """S8 exhaustion -> bool (spec section 3; exit taker at o[i+1], applied by manage.py).

    trade = {"s", "e_i" (entry bar), "lvl" (last S6 level or None)}. S3 inside uses L 60 and z_hi. True if any of:
    (a) i - e_i >= 15 and s*net(i; 15) <= 0                                   (P13, concept 0j:4)
    (b) a new balance favouring the other side: S1(i, 60, k_bal) not None, i-59 > e_i and
        (S2(i, 60, p) == -s OR n(s) > n(-s)), n(x) = count of j in [i-59, i] with S3(j).absorbed == x   (P14)
    (c) S3(i).control == -s and s*(c[i] - lvl) < 0                           (P15)
    (d) only if climax: bar x = i-1 made a new trade extreme with s*net(x; 1) > 0 and S3(i).absorbed == s   (P16)
    Too few bars (or a gap) for a clause -> that clause is False; never raises on data. `cache` (optional dict) memoizes S3.
    """
    s, e_i, lvl = trade["s"], trade["e_i"], trade.get("lvl")
    if cache is None:
        cache = {}

    def s3(j):
        key = (j, z_hi)
        if key not in cache:
            cache[key] = _effort(bars, j, EFFORT_L, z_hi, R_ABS, R_CTL)
        return cache[key]

    # (a)
    if i - e_i >= S8_AGE:
        net = net_big(bars, i, S8_AGE, tier)
        if net is not None and s * net <= 0:
            return True
    # (b)
    if i - (S8_N - 1) > e_i:
        bal = balance(bars, i, S8_N, k_bal, bin_size)
        if bal is not None:
            if _s2_from(bars, i, S8_N, p, DRIFT_Q, bal) == -s:
                return True
            n_s = n_o = 0
            for j in range(i - S8_N + 1, i + 1):
                ab = s3(j)[1]
                if ab == s:
                    n_s += 1
                elif ab == -s:
                    n_o += 1
            if n_s > n_o:
                return True
    # (c)
    if lvl is not None and s3(i)[0] == -s and s * (bars[i]["c"] - lvl) < 0:
        return True
    # (d)
    if climax:
        x = i - 1
        if x - 1 >= e_i and x >= 0:
            key = "h" if s > 0 else "l"
            ext_x = bars[x][key]
            prev = [bars[j][key] for j in range(e_i, x)]
            ext_prev = max(prev) if s > 0 else min(prev)
            if s * (ext_x - ext_prev) > 0:
                nx = net_big(bars, x, 1, tier)
                if nx is not None and s * nx > 0 and s3(i)[1] == s:
                    return True
    return False
