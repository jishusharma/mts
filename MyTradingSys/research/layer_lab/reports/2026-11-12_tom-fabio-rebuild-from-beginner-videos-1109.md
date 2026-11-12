# Layer Lab Report: Tom/Fabio Rebuild Step 1 - Beginner & How-To Rulebook

- Card: tom-fabio-rebuild-from-beginner-videos-1109
- Date: 2026-11-12 (UTC)
- Lane: CODEX (Gemini 3.8 Flash Low on NUC)
- Deliverables:
  - `MyTradingSys/research/tom_fabio_rebuild_2026-11-09/RULEBOOK.md:1-240`
- Verification Command: `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/tom_fabio_rebuild_2026-11-09/RULEBOOK.md` (exit code 0, 35 quotes PASS).

---

## 1. Summary & Findings

Past tests of Tom Vorwald and Fabio Valentini concepts across 12 iterations yielded zero fee-net edge on BTCUSDT. Review of the primary source material reveals that past backtests coded proxies rather than the traders' actual stated rules:
1. Intraday Noise vs Swing Horizons: Past tests coded 5m, 15m, and 1h bars (`MyTradingSys/research/tom_fabio_course_correction_2026-11-07/CENSUS_5M15M_1109.md:21-25`, SOURCED) where round-trip fees (10 bps) on tight stops (median 39.5 bps, SOURCED `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/CENSUS_5M15M_1109.md:32`) incurred a massive friction penalty of 0.25 R per trade. In contrast, Tom's beginner swing method waits for daily closing prices (`MyTradingSys/research/tom_fabio_rebuild_2026-11-09/RULEBOOK.md:162`, SOURCED: M7ompiwv5co), slashing fee drag by an order of magnitude (0.015-0.040 R).
2. Missing Order Flow Proof: Past tests coded geometric wick heuristics as proxies for absorption and failed auctions (`MyTradingSys/research/tom_fabio_course_correction_2026-11-07/AUCTION_CENSUS_1108.md:19-25`, SOURCED). The traders explicitly state that absorption requires microstructural proof (delta divergence and limit absorption; `MyTradingSys/research/tom_fabio_rebuild_2026-11-09/RULEBOOK.md:42`, `MyTradingSys/research/tom_fabio_rebuild_2026-11-09/RULEBOOK.md:50`).
3. Reward-to-Risk Constraints: Censuses enforced 1:1 fixed R:R brackets (`MyTradingSys/research/tom_fabio_course_correction_2026-11-07/AUCTION_CENSUS_1108.md:25`, SOURCED). Tom explicitly requires a minimum R:R threshold >= 1.5 (`MyTradingSys/research/tom_fabio_rebuild_2026-11-09/RULEBOOK.md:150`, SOURCED: M7ompiwv5co) and notes that 1:1 requires unachievable >51% win rates before fees (`MyTradingSys/research/tom_fabio_rebuild_2026-11-09/RULEBOOK.md:166`, SOURCED: 3JqMyzE8jIQ).

---

## 2. Quantitative Rule Inventory

- Total Extracted Rules in Rulebook: 35 rules (OURS)
  - Category A (Entry & Trigger): 8 rules (SOURCED verbatim quotes)
  - Category B (Filter & Context): 7 rules (SOURCED verbatim quotes)
  - Category C (Stop Loss & Invalidation): 5 rules (SOURCED verbatim quotes)
  - Category D (Target & Exit): 4 rules (SOURCED verbatim quotes)
  - Category E (Trade Management & Risk Math): 5 rules (SOURCED verbatim quotes)
  - Category F (No-Trade & Invalidation): 6 rules (SOURCED verbatim quotes)

All 35 verbatim quotes were machine-verified against canonical transcripts (`raw_transcripts_canonical/` raw files) with exact transcript thirds confirmed.

---

## 3. CANNOT_SEE & GAP Tables

The rulebook incorporates:
- CANNOT_SEE Table: Maps 7 microstructural requirements invisible to standard candlestick feeds (intrabar absorption delta, tape rejection speed, L2 book depth, footprint diagonal imbalances, resting limit heatmaps, liquidation streams, velocity during absorption) to our nearest available data feeds.
- GAP Table: Systematically categorizes discrepancies between the 11-08 / 11-09 censuses and the source rulebook (6 rules CODED DIFFERENTLY, 2 rules completely MISSING).

---

## 4. Next Steps

As specified in the card notes:
- Code rule 1 alone (swing volume impulse breakout on daily bars).
- Add one rule at a time and measure fee-net incremental attribution.
- Deploy to testnet forward from the first version.
