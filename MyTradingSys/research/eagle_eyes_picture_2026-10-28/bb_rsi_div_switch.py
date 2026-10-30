"""BB + RSI divergence direction-switch study on BTCUSDT 15m (Binance spot, public). Research only, no orders.
Divergence = repo Malkan rules (rsi_divergence, close to close, 3-10 bars). Triggers/exits = OURS, operator's chart read 10-30."""
import json, os, sys, tempfile, time, urllib.request, statistics as st
from datetime import datetime, timezone

REPO = sys.argv[1]
sys.path.insert(0, REPO)
from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
from MyTradingSys.backtest.layers.rsi.rsi_divergence import rsi_divergence
from MyTradingSys.backtest.fees import BINANCE_TAKER

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(tempfile.gettempdir(), "btc15m_bbdiv.json")  # public klines, never committed
FEE = BINANCE_TAKER * 2  # round trip from backtest/fees.py; slippage and funding not modelled


def fetch():
    if os.path.exists(CACHE) and time.time() - os.path.getmtime(CACHE) < 1800:
        return json.load(open(CACHE))
    start = int(datetime(2024, 10, 30, tzinfo=timezone.utc).timestamp() * 1000); out = []
    while True:
        u = "https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=1000&startTime=%d" % start
        with urllib.request.urlopen(u, timeout=20) as r:
            b = json.loads(r.read())
        if not b:
            break
        out += [[x[0], float(x[1]), float(x[2]), float(x[3]), float(x[4])] for x in b]
        if len(b) < 1000:
            break
        start = b[-1][0] + 1
    json.dump(out, open(CACHE, "w"))
    return out


B = fetch()[:-1]  # drop the forming bar
T = [x[0] for x in B]; O = [x[1] for x in B]; H = [x[2] for x in B]; L = [x[3] for x in B]; C = [x[4] for x in B]
N = len(C)
R = rsi_core(C, 14)
RM = [None] * N
for i in range(N):
    w = R[max(0, i - 13):i + 1]
    if i >= 13 and all(v is not None for v in w):
        RM[i] = sum(w) / 14
MID = [None] * N; UP = [None] * N; LO = [None] * N
for i in range(19, N):
    w = C[i - 19:i + 1]; m = sum(w) / 20; sd = st.pstdev(w)
    MID[i], UP[i], LO[i] = m, m + 2 * sd, m - 2 * sd

ts = [datetime.fromtimestamp(t / 1000, timezone.utc).strftime("%Y-%m-%d %H:%M") for t in T]
EV = {k: rsi_divergence(C, R, ts, 3, 10, kind=k) for k in ("bullish", "bearish")}


def zone_ok(e, side):  # divergence starts from the weak/strong zone (Malkan 40/60), OURS as a filter
    return e["rsi_a"] <= 40 if side == 1 else e["rsi_a"] >= 60


def band_ok(e, side):  # the band "dance": price touched the outer band between A and B
    a, b = e["a_i"], e["b_i"]
    if side == 1:
        return any(LO[k] is not None and L[k] <= LO[k] for k in range(a, b + 1))
    return any(UP[k] is not None and H[k] >= UP[k] for k in range(a, b + 1))


def trigger(e, side, mode, W=16):
    """Bar j whose CLOSE fires; enter at O[j+1]. None if disarmed or window expires."""
    i, b = e["i"], e["b_i"]
    if mode == "T0":
        return i
    for j in range(i, min(N - 1, i + W)):
        if R[j] is None or RM[j] is None:
            return None
        if side * (C[j] - C[b]) < 0:  # new extreme past B: setup broken
            return None
        cross = R[j] > RM[j] and R[j] > 40 if side == 1 else R[j] < RM[j] and R[j] < 60
        if mode == "T2":
            cross = cross and side * (C[j] - MID[j]) > 0
        if cross:
            return j
    return None


def run(side, mode, xmode, filt):
    out = []; busy = -1
    for e in EV["bullish" if side == 1 else "bearish"]:
        if filt == "zone" and not zone_ok(e, side):
            continue
        if filt == "band" and not band_ok(e, side):
            continue
        j = trigger(e, side, mode)
        if j is None or j + 1 >= N or j + 1 <= busy:
            continue
        k0 = j + 1; px = O[k0]
        stop = min(L[e["b_i"]:j + 1]) if side == 1 else max(H[e["b_i"]:j + 1])
        if side * (px - stop) <= 0:
            continue
        hit60 = False; exit_px = None; k = k0
        for k in range(k0, min(N, k0 + 96)):
            if side == 1 and L[k] <= stop or side == -1 and H[k] >= stop:
                exit_px = stop if side * (O[k] - stop) > 0 else O[k]; break
            if xmode == "band":
                if side == 1 and H[k] >= UP[k]:
                    exit_px = max(UP[k], O[k]); break
                if side == -1 and L[k] <= LO[k]:
                    exit_px = min(LO[k], O[k]); break
            else:  # RSI reaches 60 (40 for shorts) then closes back through its average
                if side * (R[k] - (60 if side == 1 else 40)) >= 0:
                    hit60 = True
                if hit60 and side * (R[k] - RM[k]) < 0 and k + 1 < N:
                    k += 1; exit_px = O[k]; break
        if exit_px is None:
            exit_px = C[k]
        net = side * (exit_px - px) / px - FEE
        out.append((T[k0], net, k - k0, ts[k0]))
        busy = k
    return out


def stats(tr):
    if not tr:
        return "n=0"
    x = [t[1] for t in tr]; w = [v for v in x if v > 0]; lo = [v for v in x if v <= 0]
    pf = sum(w) / -sum(lo) if lo and sum(lo) else float("inf")
    return "n=%4d win %3.0f%% mean %+.3f%% total %+6.1f%% PF %.2f hold %.0f bars" % (
        len(x), 100 * len(w) / len(x), 100 * st.mean(x), 100 * sum(x), pf, st.mean(t[2] for t in tr))


SPLIT = int(datetime(2025, 10, 30, tzinfo=timezone.utc).timestamp() * 1000)
print("bars %d  %s -> %s" % (N, ts[0], ts[-1]))
print("\n-- recent divergences (10-29 12:00 .. 10-30 17:00) --")
for k, side in (("bullish", 1), ("bearish", -1)):
    for e in EV[k]:
        if e["a_t"] >= "2026-10-29 12:00":
            j1 = trigger(e, side, "T1"); j2 = trigger(e, side, "T2")
            print("%s A %s c%.0f rsi %.1f -> B %s c%.0f rsi %.1f | zone %s band %s | T1 %s T2 %s" % (
                k[:4], e["a_t"], e["close_a"], e["rsi_a"], e["b_t"], e["close_b"], e["rsi_b"], zone_ok(e, side), band_ok(e, side),
                ts[j1] if j1 else "-", ts[j2] if j2 else "-"))
print("\n-- backtest, fee-net 0.10%% RT (taker both sides), IS = 2024-10-30..2025-10-29, OOS = 2025-10-30..now --")
for filt in ("none", "zone", "band"):
    for mode in ("T0", "T1", "T2"):
        for xm in ("rsi", "band"):
            for side in (1, -1):
                tr = run(side, mode, xm, filt)
                a = [t for t in tr if t[0] < SPLIT]; b = [t for t in tr if t[0] >= SPLIT]
                print("%-4s %s exit=%-4s %-5s IS %s | OOS %s" % (filt, mode, xm, "LONG" if side == 1 else "SHORT", stats(a), stats(b)))


print("\n-- the operator's case, zone T2 trades since 10-29 12:00 (net after fee) --")
for side in (1, -1):
    for xm in ("rsi", "band"):
        for t in run(side, "T2", xm, "zone"):
            if t[3] >= "2026-10-29 12:00":
                print("%-5s exit=%-4s in %s net %+.2f%% held %d bars" % ("LONG" if side == 1 else "SHORT", xm, t[3], 100 * t[1], t[2]))


def sar(filt, mode="T2"):
    """Always in: flip on each confirmed trigger (long on bull, short on bear). No stop, no target."""
    sig = []
    for side, k in ((1, "bullish"), (-1, "bearish")):
        for e in EV[k]:
            if filt == "zone" and not zone_ok(e, side):
                continue
            j = trigger(e, side, mode)
            if j is not None and j + 1 < N:
                sig.append((j + 1, side))
    sig.sort(); out = []; pos = 0; pin = 0; tin = 0
    for k, side in sig:
        if side == pos:
            continue
        if pos:
            out.append((T[tin], pos * (O[k] - pin) / pin - FEE, k - tin, ts[tin]))
        pos, pin, tin = side, O[k], k
    return out


print("\n-- stop-and-reverse (always in, flip on each trigger) --")
for filt in ("none", "zone"):
    for mode in ("T1", "T2"):
        tr = sar(filt, mode)
        a = [t for t in tr if t[0] < SPLIT]; b = [t for t in tr if t[0] >= SPLIT]
        print("%-4s %s IS %s | OOS %s" % (filt, mode, stats(a), stats(b)))
