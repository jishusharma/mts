"""Independent recount of the daily default-cell trade count (C0): pivots via pz.pivots_known (full recompute per bar,
not study.Pivots), its own entry and trade loop. Counts only; no return is printed (the power gate blocked)."""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from MyTradingSys.backtest.bt.bt_data import load_klines  # noqa: E402
from MyTradingSys.backtest.layers.pizzino import pizzino_indicators as pz  # noqa: E402

END = 1_719_792_000_000  # 2024-07-01 UTC
bars = [b for b in load_klines(Path("F:/MTS/Dumps/backtest/spot_2017/BTCUSDT/1d"), end_ms=END) if b["t"] < END]
H = [b["h"] for b in bars]; L = [b["l"] for b in bars]; C = [b["c"] for b in bars]; O = [b["o"] for b in bars]
n_tr, busy_until, i = 0, -1, 0
for i in range(len(bars) - 1):
    kp = {n: pz.pivots_known(H, L, n, i) for n in (1, 2, 3)}
    st = []
    for n in (1, 2, 3):
        st.append(pz.swing_state([p.price for p in kp[n] if p.kind == "H"], [p.price for p in kp[n] if p.kind == "L"], C[i])[0])
    if i < busy_until:
        continue
    hi1 = [p.price for p in kp[1] if p.kind == "H"]; lo1 = [p.price for p in kp[1] if p.kind == "L"]
    hi3 = [p.price for p in kp[3] if p.kind == "H"]; lo3 = [p.price for p in kp[3] if p.kind == "L"]
    if not (hi1 and lo1 and hi3 and lo3):
        continue
    mid = (hi3[-1] + lo3[-1]) / 2
    a = max(0, i - 23)
    for sg, side in ((1, "long"), (-1, "short")):
        if sg * sum(st) < 2 or not (sg * (C[i] - mid) > 0):
            continue
        ok = any(
            (r := pz.break_retest(X, C[a:i + 1], H[a:i + 1], L[a:i + 1], direction="up" if sg > 0 else "down"))["retest_bar"]
            == i - a and r["outcome"] == "hold" for X in ((hi1[-1] if sg > 0 else lo1[-1]), mid))
        if not ok:
            continue
        entry, stop = O[i + 1], (lo1[-1] if sg > 0 else hi1[-1])
        plan = pz.plan_trade(side, entry, stop, hi1 if sg > 0 else lo1)
        if not plan["take"]:
            continue
        j, done = i + 1, False
        while j < len(bars) and j <= i + 1 + 20:
            if j == i + 21 or sg * (O[j] - stop) <= 0 or sg * (O[j] - plan["target"]) >= 0 \
                    or (L[j] <= stop if sg > 0 else H[j] >= stop) or (H[j] >= plan["target"] if sg > 0 else L[j] <= plan["target"]):
                done = True
                break
            j += 1
        if done:
            n_tr += 1
            busy_until = j
        break
print("recount C0_default 1d DEV-stage n", n_tr)
