# GPT / Codex status check, 2026-10-14 ~14:35Z (JIS-NB Claude session, read over the NUC SSH gate)

Operator ask (NB chat): look at what GPT has been doing with the operator's own prompts, ask a cheap GPT model directly, find what needs correcting.
Sources: F:/codex_home/sessions on JIS-NUC (Codex Desktop chats), `codex_run.py status` run on JIS-NUC, NUC worktrees, origin/fast-track.

## The operator's own Codex chats (last 3 days)
| UTC | Ask | Outcome |
|---|---|---|
| 10-13 19:00 | Levels idea, built and disposed in 1-2-3 adds (leveraged) | 117 signals Dec-Mar, 8 sizing variants all negative (about -$1,140 to -$1,263 on $50 risk/trade). Report shipped: research/levels_sizing_2026-10-14/REPORT.md. Agrees with EUR-LOW-US-SWEEP-20261014 (Claude): adds and leverage do not create an edge. |
| 10-14 06:18 | Candle-close signatures at levels by market phase | Lab rounds: 126 DEV arms 0 pass; independent audit FIX-FIRST (8 findings). Corrected rerun (branch nuc/codex-candle-research, F:/MTS/mts-candle-research) still open in the chat; 1 commit + about 25 files not shipped. |
| 10-14 14:21 | Audit all work; how are support levels set without lookahead? | Shipped: research/pivot_pattern_audit_2026-10-14/REPORT.md (7563aa22). |

## Asked GPT directly (gpt-6-luna, effort low, about 8k tokens, files pasted in; its read-only sandbox cannot run over SSH)
Defects it lists for the candle-close work, checked against the audit report:
- Fixed: broken study import that exited 0 with 8 skipped tests; placebo draws that changed when future data was cut; funding timestamps 0-31 ms off the 8h slot; bootstrap lift dividing both groups by the signal count.
- Open: no root verification.json for the latest rerun; encounter-day rule (engine.py:166 groups by `floor('D')` on the bar index, the pre-registration says encounter-open UTC day; Claude spot-check: line confirmed); phase labels do not prove ranges/trends; first-event signal vs all-nearby control; 1 h outcome too short for bottom claims; small unvalidated positive cells.
Ship order it gives: fix the day rule + test, rerun, root verification.json, keep the result labelled exploratory, then ship.

## Lab (unattended MTS-CodexLab) is stuck
- Every tick since about 08:00Z: `ERROR git: path MyTradingSys/research/layer_lab/INDEX.md is unmerged`. Tree jis-nuc/codex-lab ahead 35 / behind 67, 45 staged files.
- Before that, 03:30-12:00 IST, the tick committed `claim lc-levels-hold` every 30 min without running it.
- Allowance is not the problem (5 h window 46%, week 40%). Repair card: `codex-lab-unstick-nuc` (SONNET, prio 1, host JIS-NUC).
