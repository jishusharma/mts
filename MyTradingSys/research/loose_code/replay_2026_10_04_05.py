"""G1/M1/M2 partial replay (research/_archive/loose_2026-10/REPLAY_2026-10-04_05.md). Candidates are transcribed from MARKET_ANALYSIS_2026-10-05.md
(line refs in the report); ledger / snapshots / apparatus_log are not on the pushed ref.
net_rr per backtest/layers/FORMULAS.md section 17 (written independently here): cost = 2*0.0005*entry;
net = (|target-entry| - cost) / (|entry-stop| + cost)."""
TAKER = 0.0005


def net_rr(entry, target, stop):
    cost = 2 * TAKER * entry
    return (abs(target - entry) - cost) / (abs(entry - stop) + cost)


# name, side, entry, stop, nodes ascending-from-entry (label, price), reported target/nrr, source lines
C = [
 ("A 05Z rank-1 ct_long @ weekly_val", +1, 85814.27, 85277.90,
  [("weekly POC", 86510.37), ("daily VAH", 86550.05), ("weekly VAH", 86865.93)], (86700.42, 1.29), "MA:28,37"),
 ("B 05Z rank-2 ct_long @ 1h_swing_low", +1, 85277.90, 85107.34,
  [("daily POC", 85542.56), ("weekly POC", 86510.37), ("runner 86910.94", 86910.94)], (86510.37, 4.48), "MA:28,35,38"),
 ("C 13:31-13:42 reclaim ct_long @ prior_day_val (stop = entry-190, doc line 135 '~190-pt stop')", +1, 85798.75, 85608.75,
  [("daily POC", 86039.88), ("weekly POC", 86094.95), ("daily VAH", 86430.39), ("weekly VAH", 86645.67)], (None, 2.68), "MA:106,107,109,135"),
]
if __name__ == "__main__":
    print("check vs reported (engine target):")
    for n, s, e, st, nodes, rep, src in C:
        if rep[0]:
            print(f"  {n[:2]} recomputed {net_rr(e, rep[0], st):.2f} vs reported {rep[1]}")
    print()
    for n, s, e, st, nodes, rep, src in C:
        print(n, f"[{src}] risk={abs(e-st):.2f}")
        for k, (lab, p) in enumerate(nodes, 1):
            print(f"   node{k} {lab:16s} {p:9.2f} gross={(p-e)/abs(e-st):5.2f} net={net_rr(e,p,st):5.2f}")
    print()
    for p in (0.30, 0.35, 0.40, 0.444, 0.50):
        print(f"hit rate {p:.3f} -> break-even net_rr {(1-p)/p:.2f}")
