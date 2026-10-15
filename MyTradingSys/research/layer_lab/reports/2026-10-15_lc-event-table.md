# LC2 event table — DEV result

**DONE — 1,278 first-touch events; 1,050 reached their next same-side KEEP level (82.2%).** Event CSV and feature separation are in `MyTradingSys/research/levels_confluence_2026-10-14/`.

## Work and evidence

- Built [event_table.py](../../levels_confluence_2026-10-14/event_table.py:114), producing [event_table.csv](../../levels_confluence_2026-10-14/event_table.csv) with 1,278 rows and 65 columns. It uses KEEP families from LC1; source bars cover DEV 2024-12-01..2025-03-31, with 2024-11-21..2024-11-30 solely as indicator/level seed. Last touch is 2025-03-31; no VALIDATION or HOLDOUT bars were loaded.
- Columns include side, level/source, first same-side next-level touch, MFE/MAE in percent and R, K1-K5 stop prices/path MFE/MAE/status, L2 filled, B1-B3 on 1h/4h/6h/12h/1D, and E1-E4. K1 observed labels: STOP_THEN_1R_MORE 691; STOP_THEN_TARGET 200; NOT_STOPPED 387.
- Indicator timing: only fully closed 5m bars precede the touch; HTF aggregates require their close strictly before the touch ([feature/bias code](../../levels_confluence_2026-10-14/event_table.py:49), [indicator code](../../levels_confluence_2026-10-14/event_table.py:68)). Kline CVD uses taker-buy volume proxy; footprint delta is included where archived files exist.
- [separation.md](../../levels_confluence_2026-10-14/separation.md:5) reports 16 side-aligned one-at-a-time feature contrasts with UTC-day block-bootstrap 95% CIs. Positive contrasts whose lower bound exceeded zero: E1 RSI 40/60 hold, +1.190 MFE_R (CI +0.414..+2.042); E4 outer Bollinger, +0.918 MFE_R (CI +0.053..+1.898). **LC3 pre-registration, maximum two of six:** KEEP levels + E1 RSI hold; KEEP levels + E4 outer Bollinger. No trading rules or LC3 simulation were added.
- Trial ledger [TRIALS.md](../TRIALS.md:13): 17 arms (one event table + 16 contrasts).
- Verification: `python -m pytest MyTradingSys/research/levels_confluence_2026-10-14/test_event_table.py -q` — **3 passed**. Coverage: hand-derived Bollinger position, touch bar excluded from entry inputs, and bias unaffected by the touch bar ([tests](../../levels_confluence_2026-10-14/test_event_table.py:9)).

## Findings and limits

| Severity | File:line | Finding | Evidence / treatment |
|---|---|---|---|
| LOW | `event_table.py:22` | FORMULAS.md has no Bollinger definition. | Used SMA(20), population standard deviation, bands at ±2 SD; this is an OURS measurement convention and is covered by a hand-computed test. It is not trader-sourced. |
| LOW | `event_table.py:86` | STOP_THEN_TARGET / STOP_THEN_1R_MORE only classify stops followed by the measured next-level target; stops with no later target stay NOT_STOPPED under the requested three-state output vocabulary. | CSV preserves path MFE/MAE per K arm for diagnosis. |
| LOW | `separation.md:3` | “Good” means L2 reached within the UTC day; “bad” means not reached. | Outcome labeling is descriptive, not a rule or evidence of profitability. No P&L simulation was run. |

## Reproduction

`python MyTradingSys/research/levels_confluence_2026-10-14/event_table.py`

`python -m pytest MyTradingSys/research/levels_confluence_2026-10-14/test_event_table.py -q`
