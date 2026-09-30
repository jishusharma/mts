# SUPERVISOR INBOX - notes for the Opus supervisor session

The supervisor reads this file on every wake (every 3 h at :17) and after acting moves each handled note to
SUPERVISOR_LOG.md as "- inbox <date>: <note> -> <action>". Append notes below the line, one per bullet:
`- 2026-09-29 22:30 IST | from: operator/DSA | <note>`
Direct routes that act immediately: paste into the supervisor session, or (from another Claude session on this machine) SendMessage.

---
- 2026-09-30 19:40 UTC | from: MTS-2026-09-30-1005Z-CLD-ANA-connected-system | DSA lane: pack 13 trade-reconstruction specs `python scripts/worker/queue_tool.py pack --lane dsa MyTradingSys/research/fast_track_2026-09-27/nuc_specs/21*.md` (2101-2113, lint OK). Gate each reply with verify_extract_quotes.py; outputs extracts/processed/<trader>/recon/. Monitoring: re-enable mts-dsa-feeder (gates DSA replies -> DSA_GATE_LOG.md) on the account with headroom (B; A is at 100% until Fri 09:00 UTC). NUC Qwen specs for Fabio v3 S1-S8 follow once FABIO_V3_SPEC.md lands. Cloud cannot pack or monitor the queue.
