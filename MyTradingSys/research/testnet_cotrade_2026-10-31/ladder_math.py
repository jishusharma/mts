"""Worst case of the operator's doubling-total ladder (OURS example numbers). Independent of repo code.
Adds as the operator said: X, 2X (total 3X), 3X (total 6X), 6X, ... -> adds 1,2,3,6,12,24,48, totals 1,3,6,12,24,48,96.
Short ladder from P0 up, one rung every SPACING; one stop STOP_GAP above the last rung.
P&L both linear (USD) and inverse (Deribit BTC-PERPETUAL: amount in USD, pnl BTC = amt*(1/exit-1/entry) for a short... sign handled)."""
import sys; sys.dont_write_bytecode = True
X, P0, SPACING, STOP_GAP = 100, 100000.0, 0.004, 0.004
adds, tot = [], 0
for k in range(7):
    a = X * (k + 1) if k < 2 else tot
    adds.append(a); tot += a
print("adds", adds)
for n in range(1, 8):
    a = adds[:n]; px = [P0 * (1 + SPACING * i) for i in range(n)]
    stop = px[-1] * (1 + STOP_GAP); T = sum(a)
    avg = T / sum(s / p for s, p in zip(a, px))          # inverse-contract average (harmonic)
    lin = sum(s * (stop / p - 1) for s, p in zip(a, px))  # USD loss if linear
    inv_btc = sum(s * (1 / p - 1 / stop) for s, p in zip(a, px))  # inverse short loss in BTC = amt*(1/entry - 1/stop)
    inv_usd = inv_btc * stop
    move = (stop / P0 - 1) * 100
    win1 = a[0] * SPACING  # 1 rung win example: first add closes +0.4%
    print(f"steps={n} total=${T} stop_move_from_P0={move:.2f}% avg_entry={avg:.0f} loss_lin=${lin:.2f} loss_inv=${abs(inv_usd):.2f} "
          f"loss_%_of_total={lin/T*100:.2f}% margin10x=${T/10:.0f} margin20x=${T/20:.0f} back_to_avg_needs={(avg/stop-1)*100:.2f}%")
