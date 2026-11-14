"""Session-adjusted variance clock for the candle-flip null (card flip-engine-follow-up-session-adjusted-s).

The flat null spends the bar's variance evenly over time: remaining variance = t_left * sigma_bar^2. Volatility is not flat across the UTC day,
so the session-adjusted null spends it by an intraday profile fitted on the fit window only (2024):

    w_h        = mean squared 1m log return in UTC hour h, normalised so the 24 w_h average 1   (OURS: hour-of-day only, no weekday term)
    W(a, b)    = sum of w over the 1m bars a..b-1
    t_left_s   = W(remaining minutes of the bar) / mean over the 14 prior bars of W(whole bar)

so d = (price - ref) / (ATR14 / 1.5958) is unchanged and only the clock changes: null P(keeps) = Phi(|d| / sqrt(t_left_s)). A flat profile gives
t_left_s = t_left exactly (the old null). t_left_s may exceed 1 when the bar sits in a busier part of the day than the 14 bars before it.
"""
import numpy as np

MIN_MS = 60000
PRIOR_BARS = 14        # same window as the ATR14 that sets sigma_bar


def hour_profile(c, t0_ms, upto=None):
    """Hour-of-day variance weights (length 24, mean 1) from the 1m closes c[:upto] (default all); minute i opens at t0_ms + i * 60000."""
    c = np.asarray(c, float)
    if upto is not None:
        c = c[:upto]
    r = np.diff(np.log(c))                                        # return into minute i+1
    hr = ((t0_ms // MIN_MS + np.arange(1, len(c))) // 60) % 24
    s = np.bincount(hr, weights=r * r, minlength=24)
    n = np.bincount(hr, minlength=24)
    v = s / np.maximum(n, 1)
    return v / v.mean()


def weight_cumsum(profile, t0_ms, n_min):
    """cw[k] = total weight of the first k 1m bars (cw has n_min + 1 entries)."""
    hr = ((t0_ms // MIN_MS + np.arange(n_min)) // 60) % 24
    return np.concatenate([[0.0], np.cumsum(np.asarray(profile, float)[hr])])


def session_t_left(cw, B, J, S, prior=PRIOR_BARS):
    """Variance-time left for rows at bar index B, evaluation offset J (price = close of the J-th 1m bar of the bar), bar length S minutes.
    Needs B >= prior (the caller already drops the first 20 bars)."""
    B, J = np.asarray(B, int), np.asarray(J, int)
    rem = cw[(B + 1) * S] - cw[B * S + J + 1]
    bar_w = lambda b: cw[(b + 1) * S] - cw[b * S]
    prev = sum(bar_w(B - k) for k in range(1, prior + 1)) / prior
    return rem / prev
