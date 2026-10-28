# EVENT-PROBABILITY LAYER — DESIGN (PARKED)
# Version 0.1 | 2026-09-13
# Status: DESIGN ONLY. Not implemented. Awaiting data prerequisite.
# Source: 4-AI research (Claude, GPT, Grok, Gemini), 2026-09-12/13.

## WHY

State classifier is slow. Freezes at "B" for hours while price breaks
value and trends. Engine repeatedly proposes CT against the trend.
Deterministic verdicts hide uncertainty.

Proposal: model P(event | observable state). Not replace engine.
Add a conditional-information layer above it. Alert on dominant-event
change, not on single-field noise.

## KEY FINDING (all 4 AIs agree)

Named events (bull trap, absorption, failed auction, liquidity run)
are PARTICIPANT-INTENT labels. Snapshot data cannot ground-truth them.
P(absorption) is a probability over a label you cannot verify.

Fix: redefine catalog as OBSERVABLE FORWARD KLINE OUTCOMES.
- break-and-hold (price closes beyond level, stays N bars)
- break-and-fail (returns inside within N bars)
- range-hold
- range-break
- trend-continuation
- trend-reversal

These are derivable from klines we already have. Verifiable.

## DATA PREREQUISITE (hard)

Conditional frequency tables need 100+ events per cell.
3-4 features × 3-5 bins each = 27-500 cells.
Required sample: 5,000-50,000 labeled events.

Current (2026-09-14): ~227 snapshots, 759 labeled outcomes. Rate ~716/day.
Outcome labeler now running. Accumulates forward 30/60/120m returns.

ETA to 5,000-gate: ~6 days at observed rate (~716/day). ETA to 50,000: ~2 months. (Prior 3-6mo estimate was stale by 15-30x.)

## EVIDENCE SUMMARY

| Claim | Evidence |
|---|---|
| Full probabilistic replacement of engine | NO VALIDATED EVIDENCE |
| Add conditional layer above deterministic gates | SUPPORTED |
| Named-event catalog on snapshot data | ONTOLOGICALLY BROKEN |
| Observable-outcome catalog | METHODOLOGICALLY SOUND |
| HMM / ML / deep learning | NOT JUSTIFIED |
| MVP = Dirichlet-smoothed frequency table on coarse buckets | BEST EVIDENCE/COMPLEXITY FIT |
| Raw probability threshold → trade | REJECTED |
| EV + costs → trade | SUPPORTED |
| Fractional Kelly for sizing | SUPPORTED |
| Deterministic gates stay hard (structure, risk, invalidation) | STRONGLY JUSTIFIED |

## SEQUENCE (when we build)

1. **Data accumulation** (NOW — running). Outcome labeler.
2. **Catalog definition** (after 500+ labels). Forward kline outcomes only.
3. **Frequency table MVP** (after 5,000 labels). Dirichlet smoothing.
4. **BOCPD gate** (optional, later). ~100 lines NumPy.
5. **EV mapping** (with realized payoff log). Replaces raw threshold.

## DO NOT BUILD

- 12-event Bayesian catalog
- HMM/regime-switching for event detection
- Any ML/DL layer
- Any absolute P(event) claim
- Any threshold-based execution rule

## REFERENCES

- Jaquart et al. 2021, T1, 94k obs — 1m BTC prediction, edge dies post-costs.
- Anghel 2021, T1, 1M obs — technical rules beat ML post data-snooping.
- Cont et al. 2014, T1 — OFI 65% R² (contemporaneous, not predictive).
- Koutmos & Wei, T1 — BTC crash risk, 3,577 daily, OI significant.
- Zakamulin 2015, T1, 155yr — deterministic MA rules no OOS edge.
- Adams & MacKay 2007, T1 — BOCPD methodology (not trading edge).
- Kelly estimation-risk literature, T1 — full Kelly overbets on errors.

# END
