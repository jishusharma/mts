# Finding Report: Krown Free Setups, Alerts, and App Search

**Task**: `gemini-krown-free-setups-alerts-app-search`  
**Date**: 2026-10-30 (UTC)  
**Worker**: Gemini Flash worker  
**Artifact Written**: `MyTradingSys/research/krown_free_2026-10-31/KROWN_FREE_SETUPS.md`

---

## 1. Commands Executed

1. Channel caption fetch:
   ```powershell
   python scripts/dev/fetch_captions_timed.py --analyst Krown --channel "@ECKrown" --latest 10 --out MyTradingSys/research/krown_free_2026-10-31/transcripts
   ```
   - Fetched 10 timed transcripts into `MyTradingSys/research/krown_free_2026-10-31/transcripts/` (SOURCED).
   - Saved canonical raw transcripts to `raw_transcripts_canonical/` (SOURCED).

2. Quote verification:
   ```powershell
   python scripts/dev/verify_extract_quotes.py MyTradingSys/research/krown_free_2026-10-31/KROWN_FREE_SETUPS.md
   ```
   - Result: `PASS: 0 problem(s)` across 22 verified caption quotes (SOURCED).

---

## 2. Findings Summary

### Free Setups
- Discretionary Daily/Multi-day Setups:
  - **5/21 Corrective Setup**: 5 EMA crosses 21 EMA -> target 55 EMA (`dLq5Jyir3Iw` [00:09:09]). Stop loss: `NOT_IN_DATA`.
  - **13/34 Corrective Cross**: 13 EMA crosses 34 EMA -> target 89 EMA (`dLq5Jyir3Iw` [00:09:26]). Stop loss: `NOT_IN_DATA`.
  - **Silver Cross (21/55 EMA)**: 21 EMA crosses 55 EMA (`bXug2l6qICc` [00:00:44]). 1-month hit-rate: 83% green, median +7.4% since 2018; 1-year hit-rate: 100% green (6 of 6), median +219% (`bXug2l6qICc` [00:02:40]). Stop loss: `NOT_IN_DATA`.
  - **2-Day Corrective Cross**: Close below pivot (~$81,000) forces 2-day corrective setup to 55 EMA (~$77,350) (`zay_owGmjo0` [00:04:36]). 10 days out from 55 EMA test: 56% green, median +2% (`zay_owGmjo0` [00:07:51]). Stop loss: `NOT_IN_DATA`.
  - **10-Day 5 EMA Reconnect**: Reconnect with red 5 EMA on 10-day bar -> 62% green within 10 days, median return +4.8% to +5.0% (`LMRNBdMiQ2g` [00:12:54], `ro6tMlqbbBI` [00:03:51]). Stop loss: `NOT_IN_DATA`.
  - **10-Day Reconnect + Stoch Confluence**: 10-day 5 EMA reconnect combined with 10-day stochastic in overbought zone (>80) -> 83% green within 10-20 days, median return +22.1% (`ro6tMlqbbBI` [00:08:26]).

- Fully Mechanical Shortlist Setup:
  - **Free AI Bot ("The Devious Scalper")**: Video `OR3Q2Vf1lrM` [00:10:56 - 00:13:30].
    - Timeframe: 4-Hour.
    - Entry: Next bar open when on bar close: (1) Range Deviation prints blue signal, (2) BBWP(13) <= 50th percentile, (3) Price > Daily 50 EMA.
    - Stop Loss: `Entry - 2 * ATR(14)`.
    - Breakeven: Move stop to breakeven at +1R unrealized gain.
    - Exit Target: Range Deviation prints red state or Chandelier trailing stop (3x ATR(14)).
    - Status: 100% testable complete setup.

### App and Free Alerts
- **Krown Trading App ("Free Market Dynamics")**:
  - `app.krowntrading.net` tested unreachable (HTTP 443 refused/blocked, 0 signals).
  - Phrase "Free Market Dynamics" is not spoken in recent YouTube videos; it was a link tree anchor to a dashboard URL.
- **Free Alerts**:
  - No free signal or alert service is offered; Eric Krown explicitly adheres to "no signals".
  - Mentions of "free" are restricted to educational courses ("TA 101" / "Options 101" in `P3rDSh187TE`), open order flow charts (`M_p2k4uvRKc`), and affiliate credits (`ro6tMlqbbBI`).
