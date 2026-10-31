# OI pairing recheck (C24 oi_after_flush.py)

Bybit OI is stamped at snapshot time t = bar open, so a flush bar's own OI change is oi[t+5m]/oi[t] (I[i+1]/I[i]).
The old code used I[i]/I[i-1], the previous bar's change. Thresholds (-0.25% price, -0.2% OI, +/-0.2% rebuild band,
8-bar chop <= 0.8%) are OURS. Data: Bybit linear BTCUSDT public, 07-02 .. 10-30 (34,559 bars).

| Group (OI path after flush) | n old | n new | 1h mean old | 1h mean new | 4h mean old | 4h mean new |
|---|---|---|---|---|---|---|
| OI rebuilds >= +0.2% | 18 | 58 | -0.10% | -0.07% | +0.00% | +0.05% |
| OI flat | 9 | 45 | +0.08% | +0.02% | +0.10% | +0.05% |
| OI keeps falling <= -0.2% | 22 | 38 | +0.10% | -0.03% | -0.01% | -0.04% |

Base (every 30 min): 1h +0.01%, 4h +0.03%.

Old pairing reproduces 18/9/22. New pairing gives 58/45/38: the flush filter now selects the true OI-drop bars, so
n roughly triples. Forward-return claim: no group's mean differs from base by more than ~0.1% at either horizon under
either pairing, so the earlier "OI path favours X" reading is not supported by the old numbers (n<=22) and is not
supported by the new ones either; the old small-n sign differences (e.g. keeps-falling 1h +0.10%) flipped to -0.03%.
Treat as no edge, not a reversed edge. Not a fee-net OOS test.
