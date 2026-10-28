# BTC candle-close DEV event study

0/126 pooled arms pass; 105,541 correlated event rows from 1,313,280 BTC minute bars. Every pooled mean is negative after the 14bp screen (-26.83 to -4.68bp/event). No strategy adoption.

Full methodology, probabilities, uncertainty and limits: ../candle_close_2026-10-14/REPORT.md. Runs and aborted attempts: ../TRIALS.md. Code: ../candle_close_2026-10-14/study.py. Tests: test_study.py, eight synthetic checks including full event generation. Independent verifier: verify_result.py, 30 hashes +126 raw-row event reconstructions +126 arm count/mean checks, PASS.

Data: public Binance BTCUSDT perpetual 1m, January 2022-June 2024; UTC 1/2/3/5/15/30/60m triggers at prior 4h/day/week highs/lows. Outcomes: next-open to 60min-later open. Long/short direction adjusted. No validation/holdout, funding/fill P&L or macro-reversal probability claim.

Command: `python MyTradingSys/research/layer_lab/candle_close_2026-10-14/study.py`. Output overwrite guard blocks accidental reruns. Tests and verifier do not add statistical trials.

Critical assessment: MATCH for mechanical event/return reconstruction; NOT_IN_DATA for anonymous source, true fills/funding and cycle predictions; control opportunity weighting is FIX-FIRST before interpreting conditional lift as skill. Follow-up cards: candle-close-independent-audit, candle-close-cycle-labels.
