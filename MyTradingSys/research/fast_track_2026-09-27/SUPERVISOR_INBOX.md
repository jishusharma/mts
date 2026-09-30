# SUPERVISOR INBOX - notes for the Opus supervisor session

The supervisor reads this file on every wake (every 3 h at :17) and after acting moves each handled note to
SUPERVISOR_LOG.md as "- inbox <date>: <note> -> <action>". Append notes below the line, one per bullet:
`- 2026-09-29 22:30 IST | from: operator/DSA | <note>`
Direct routes that act immediately: paste into the supervisor session, or (from another Claude session on this machine) SendMessage.

---
- 2026-09-30 19:40 UTC | from: MTS-2026-09-30-1005Z-CLD-ANA-connected-system | DSA lane: pack 13 trade-reconstruction specs `python scripts/worker/queue_tool.py pack --lane dsa MyTradingSys/research/fast_track_2026-09-27/nuc_specs/21*.md` (2101-2113, lint OK). Gate each reply with verify_extract_quotes.py; outputs extracts/processed/<trader>/recon/. Monitoring: re-enable mts-dsa-feeder (gates DSA replies -> DSA_GATE_LOG.md) on the account with headroom (B; A is at 100% until Fri 09:00 UTC). NUC Qwen specs for Fabio v3 S1-S8 follow once FABIO_V3_SPEC.md lands. Cloud cannot pack or monitor the queue.
- 2026-09-30 20:10 UTC | from: MTS-2026-09-30-1005Z-CLD-ANA-connected-system | Desktop runs on real history (cloud has no data): `python MyTradingSys/backtest/layers/rsi/run_rsi_backtest.py --family malkan_40_60` (then malkan_mtf, rsi_ma_events) and `python MyTradingSys/backtest/layers/run_bracket_grid.py --layer all` (54 trials/layer; writes Q1_BRACKET_GRID.md). Findings to triage: TOM_CORE_BT_REVIEW H1 (all 19 live-rule signals short, 301 of 320 proof-5 rows downgraded uncounted -> check archive-mode long gating) and H2 (null not like-for-like); FORMULA_AUDIT MISMATCH cc_structure.classify_msb - LIVE: imported by layers/alerts/live_layers.py (cryptocred -> jishu_4); emits MSB on breaks of non-latest swings (audit row 14 probe); supervisor-owned fix, stage .new and 4 fee sets (B080). malkan_mtf.state_asof uses HTF open times (look-ahead in research use; not imported by layers/alerts).
