"""Blind recomputation of Bollinger Bands, Wilder RSI and Stochastic RSI.

Written from the definition texts inside each packet. Standard library only.
Reads packets from blind_packets/ next to this file, writes replies_haiku.json
next to this file.
"""
import glob
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PACKET_DIR = os.path.join(HERE, "blind_packets")
OUT_PATH = os.path.join(HERE, "replies_haiku.json")


# ---------------------------------------------------------------- Bollinger
def bollinger_last(closes, n=20, mult=2.0):
    """Return (mid, upper, lower) at the last close.

    mid = SMA of the last n closes.
    sd  = POPULATION standard deviation of those n closes (divide by n).
    upper/lower = mid +/- mult * sd.
    """
    if len(closes) < n:
        return None, None, None
    window = closes[-n:]
    mid = sum(window) / n
    var = sum((x - mid) ** 2 for x in window) / n
    sd = math.sqrt(var)
    return mid, mid + mult * sd, mid - mult * sd


# ---------------------------------------------------------------- Wilder RSI
def _rsi_from_avgs(avg_gain, avg_loss):
    if avg_loss == 0:
        # Packet rule: 100 when avg_gain > 0, otherwise 50 (flat window).
        return 100.0 if avg_gain > 0 else 50.0
    rs = avg_gain / avg_loss
    return 100.0 - 100.0 / (1.0 + rs)


def rsi_series(closes, period):
    """Wilder RSI aligned with closes; None for indices 0..period-1.

    delta[i] = close[i] - close[i-1], i = 1..n-1.
    Seed at index `period`: plain mean of gains / losses over the first
    `period` deltas (delta[1..period]).
    Indices after the seed: Wilder smoothing with gain[i], loss[i].
    """
    n = len(closes)
    out = [None] * n
    if n <= period:
        return out
    delta = [None] * n
    for i in range(1, n):
        delta[i] = closes[i] - closes[i - 1]

    seed_deltas = delta[1:period + 1]
    avg_gain = sum(max(d, 0.0) for d in seed_deltas) / period
    avg_loss = sum(max(-d, 0.0) for d in seed_deltas) / period
    out[period] = _rsi_from_avgs(avg_gain, avg_loss)

    for i in range(period + 1, n):
        gain_i = max(delta[i], 0.0)
        loss_i = max(-delta[i], 0.0)
        avg_gain = (avg_gain * (period - 1) + gain_i) / period
        avg_loss = (avg_loss * (period - 1) + loss_i) / period
        out[i] = _rsi_from_avgs(avg_gain, avg_loss)
    return out


# ---------------------------------------------------------------- Stochastic RSI
def stochrsi_series(closes, rsi_len=14, stoch_len=14, k_len=3, d_len=3):
    """Return (K, D) series aligned with closes (None where undefined).

    r   = Wilder RSI(rsi_len).
    raw = 100 * (r - min_r) / (max_r - min_r) over the last stoch_len r values
          (all must exist); raw = 0 when max == min.
    K   = SMA(raw, k_len); D = SMA(K, d_len).
    """
    n = len(closes)
    r = rsi_series(closes, rsi_len)

    raw = [None] * n
    for t in range(n):
        start = t - stoch_len + 1
        if start < 0:
            continue
        win = r[start:t + 1]
        if any(v is None for v in win):
            continue
        mx = max(win)
        mn = min(win)
        if mx != mn:
            raw[t] = 100.0 * (r[t] - mn) / (mx - mn)
        else:
            raw[t] = 0.0

    K = [None] * n
    for t in range(n):
        start = t - k_len + 1
        if start < 0:
            continue
        win = raw[start:t + 1]
        if any(v is None for v in win):
            continue
        K[t] = sum(win) / k_len

    D = [None] * n
    for t in range(n):
        start = t - d_len + 1
        if start < 0:
            continue
        win = K[start:t + 1]
        if any(v is None for v in win):
            continue
        D[t] = sum(win) / d_len
    return K, D


# ---------------------------------------------------------------- self checks
def _close(a, b, tol=1e-5):
    return a is not None and abs(a - b) <= tol


def self_check():
    # Bollinger worked example: n=4, mult=2.
    closes = [8, 10, 10, 12, 14, 12]
    mid, up, low = bollinger_last(closes[2:], n=4, mult=2.0)
    assert _close(mid, 12.0), mid
    assert _close(up, 14.828427, 1e-5), up
    assert _close(low, 9.171573, 1e-5), low
    mid, up, low = bollinger_last(closes[:4], n=4, mult=2.0)
    assert _close(mid, 10.0) and _close(up, 12.828427, 1e-5) and _close(low, 7.171573, 1e-5)

    # RSI worked example: period=3, closes [10,12,11,14] -> rsi[3] = 83.3333.
    r3 = rsi_series([10, 12, 11, 14], 3)
    assert r3[0] is None and r3[1] is None and r3[2] is None
    assert _close(r3[3], 83.33333, 1e-4), r3[3]

    # RSI worked example: period=2, closes [10,11,10,12,11,13]
    r2 = rsi_series([10, 11, 10, 12, 11, 13], 2)
    assert _close(r2[2], 50.0), r2[2]
    assert _close(r2[3], 83.33333, 1e-4), r2[3]
    assert _close(r2[4], 50.0), r2[4]
    assert _close(r2[5], 80.76923, 1e-4), r2[5]

    # StochRSI worked example: rsi_len 2, stoch_len 3, closes [10,11,10,12,11,13]
    ex = [10, 11, 10, 12, 11, 13]
    K2, _ = stochrsi_series(ex, rsi_len=2, stoch_len=3, k_len=2, d_len=1)
    assert _close(K2[5], 46.15385, 1e-4), K2[5]
    K1, _ = stochrsi_series(ex, rsi_len=2, stoch_len=3, k_len=1, d_len=1)
    assert _close(K1[5], 92.30769, 1e-4), K1[5]
    assert _close(K1[4], 0.0), K1[4]
    print("self-checks passed")


# ---------------------------------------------------------------- main
def compute_packet(pk):
    closes = [float(x) for x in pk["closes"]]
    assert len(closes) == 500, len(closes)
    ind = pk["indicator"]
    values = {}
    if ind == "BB":
        mid, up, low = bollinger_last(closes, n=20, mult=2.0)
        values = {"BB_mid": mid, "BB_up": up, "BB_low": low}
    elif ind == "RSI":
        values = {"RSI": rsi_series(closes, 14)[-1]}
    elif ind == "STOCHRSI":
        K, D = stochrsi_series(closes, rsi_len=14, stoch_len=14, k_len=3, d_len=3)
        values = {"StochRSI_K": K[-1], "StochRSI_D": D[-1]}
    else:
        raise ValueError("unknown indicator " + str(ind))

    out = {}
    for key in pk["answer_keys"]:
        assert key in values, (pk["id"], key)
        v = values[key]
        assert v is not None, (pk["id"], key)
        out[key] = float(v)
    return out


def main():
    self_check()
    replies = {}
    paths = sorted(glob.glob(os.path.join(PACKET_DIR, "*.json")))
    assert len(paths) == 21, len(paths)
    for p in paths:
        with open(p, "r", encoding="utf-8") as f:
            pk = json.load(f)
        replies[pk["id"]] = compute_packet(pk)
        print(pk["id"], replies[pk["id"]])
    with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(replies, f, indent=2)
    print("wrote", OUT_PATH, "with", len(replies), "packets")


if __name__ == "__main__":
    main()
