# Research agenda, BTC perp (2026-10-06)

Session: MTS-2026-10-06-1300Z-CLD-ANA-research-agenda-p1 (Cloud). Operator asked: research what MTS should research for BTC futures, then start it.
Full page: "MTS Research Agenda" (claude.ai artifact, private to the operator). This file is the in-repo record of the agenda and who is running what.

## Ranked items and status
| item | topic | status / where |
|---|---|---|
| P1 | Fee-adjusted edge, maker-fill / adverse selection | Done on 4.7 days (cloud): `P1_COST_FLOOR_2026-10-06.md`. Full-archive rerun: desktop RC session, started 2026-10-06 12:55Z. |
| P2 | Fabio v3 holdout read, per `PRE_REG_FABIO_V3.md` | Desktop RC session, started 2026-10-06 12:55Z. |
| P3 | OI + liquidation + funding event studies (T063 arm A1) | Waiting on data: rerun when n >= 30 per arm (late Oct 2026). |
| P4 | Quarter-hour opening order imbalance, 4-12h (Kim and Hansen replication) | Desktop RC session, started 2026-10-06 12:55Z. |
| P5 | Funding-settlement clock and perp-spot basis | Not started; needs funding archive (2025-09 onward). |
| P6 | Volatility timing (stops/size), incl. T060 time-series shape | Not started. |
| P7 | Large-trade / absorption events for Fabio | After P2. |
| P8 | Cross-venue lead-lag, multi-venue CVD (T035) | Needs new Deribit+Binance recording. |
| P9 | Option-expiry gamma days | Parked; needs Deribit OI-by-strike history. |

Do not pursue: whale/on-chain lead signals, ICT/SMC stand-alone rules, session direction, more indicator surveys or T053 hedge scalping before P1 clears the fee floor.

## Rules for the running sessions
Research only; no live-path file, process, HALT file or trade touched; each task pre-registered in its note before outcomes are computed; results land as new notes in `MyTradingSys/research/`.

## Handoff state (2026-10-06 16:35Z, written when cloud credit ran out)
- Done: P1 on 4.7 days (`P1_COST_FLOOR_2026-10-06.md`); P1 pooled full-archive mean +0.02 bp (aggregate only, tables missing); P2 holdout L3-FAIL already read 2026-10-04 (models A/B/D zero OOS trades, C mean -0.104 R, CI -0.209..-0.005; per desktop session, cited `PRE_REG_FABIO_V3.md` lines 43-48, not re-verified by cloud).
- INVALID: `P4_QUARTER_HOUR_IMBALANCE_20261006_FINAL.md` tested 00/06/12/18 UTC opens, not every quarter hour. Corrected pre-reg is `PRE_REG_P4_CORRECTED_2026-10-06.md` (cb93b87 on origin/research/agenda-2026-10-06); the corrected run has NOT been done.
- Still to do (owner: desktop session): (1) P4 corrected run; (2) real P1 tables per offset x fill rule x hold x month with day-block bootstrap CI95, explaining the sign difference from the 4.7-day run; (3) P5 funding-settlement clock study (items/T069); (4) P6 volatility timing, read-only (items/T070); (5) P7 absorption events after P2 (items/T071); (6) P3 / T068 OI arm rerun when n >= 30 per arm, late Oct 2026.
- Note: origin/research/agenda-2026-10-06 also carries unrelated desktop commits (launcher/watchdog files, DEVICES.md, T055 C1/C2 rerun 4c74cd7). Merge only the research notes from it; do not merge that branch whole.
