# Lead handover | written 2026-10-25T21:40Z by thinker-loader (Fable design session) | discussions since last rotation: 2 | verify: python scripts/dev/supervisor.py handover --verify --kind lead
EXAMPLE: the form of CONTEXT_FILES_DESIGN.md section 10a filled with the state known on 2026-10-25 (STATUS.md, REPORT_pilots_2026-10-25.md, REFINE_2026-10-25.md, SUPER_SESSION.md). Numbers are that day's; nothing here is live state.

## Vision
MTS trades crypto on Deribit testnet only; what trades is decided by fee-net out-of-sample results, never doctrine (PROJECT_VISION.md; operator 2026-10-13: no fixed core, every system is a layer).
Banned everywhere: mainnet, schedulers, deploys by builders, runtime data in the public repo (go private at mainnet or the first fee-net OOS pass).
Every parameter is SOURCED (trader quote + file:line) or OURS (chosen on DEV, checked once on VALIDATION, holdout read once).

## Priorities now
1. Live parity (T09-F1: live volume_fvg trades the opposite side, 0/24 agree; F2 bracket untested; F3 RSI events uncovered) - cards t09-f1/f2/f3, lane JIS-NB, live_path; number: 0 live layers trading an untested rule.
2. Card supply before any wave: refine pass first (pilot 2 ran out of ready cards 2 h early; 10 of 28 refined cards were already on trunk); number: >= 12 ready, 0 STALE dispatched.
3. Gate speed: test registration forces the 20-50 min full gate (card registering-a-test-in-scripts-dev-run-ex, CRITICAL); number: gate median < 2 min with registration.
4. Context cost: CONTEXT_FILES_DESIGN cards C1-C7; number: calls to first edit median 12 -> 8, rewrites 18.2 -> <= 1 per session.
5. Evidence for the layers: LC1 level families all DROP under a distance-matched control (T05 S1); funding/CVD fade 1h not an edge (+0.050 R, CI crosses 0); number: one layer with a fee-net DEV PASS before any VALIDATION read.

## Decisions
- d-super-session-D1..D6 | 2026-10-24 | one coordinator, card `model` field is the control, 2 workers default, notes file rewritten every wake, one 3 h... (SUPER_SESSION.md)
- d-youtube-on-gemini | 2026-10-25 | all YouTube work to Gemini on the NUC (Claude: HTTP 429 on 3/3)
- d-one-ship-at-a-time | 2026-10-24 | gates fell from 50+ min to ~2.5 min median
- d-levels-parked | 2026-10-21 | levels-confluence layer parked: no fee-net edge in 240 DEV variants (-0.119 R filled)
- d-lean-no-gates | 2026-10-20 | propose removals, never new paperwork gates (D10 operator style)
- d-layers-not-core | 2026-10-13 | Tom, Fabio and the rest are layers; fee-net OOS decides

## Open questions
- Lead model: Opus or Sonnet by default? default Sonnet; Opus when the operator names it (WORKERS rule 6a) - operator
- Pilot 3 start: after 12+ ready cards and the registration-gate fix? default yes, both first - a run
- Review stamps for T05/T06/T07/T09 (hold A-20261018-5)? default: Checker pass this week, cards stay open until then - Checker
- Levels: one more DEV iteration on the wide-stop arm (K0 finding)? default no, parked - operator
- lc-validation: read VALIDATION? default no (no DEV PASS) - rule, not a question
- Go-private timing: at mainnet or first fee-net OOS pass? default: whichever first, no change - operator

## Board
ready 52 | raw ~96 | active ~10 | cards total 256 (`tasks.py list`, 2026-10-25)
waves running: 0 | last wave: pilot 2, 13 cards shipped, cherry 0 each, 18:48Z-20:50Z
last ship: 6868a4650 (context files design) | CI: green, last 11b8f95c | budget: login C week 40% (cap 45%), 5 h 18%; login B week 96% (STALE reading)

## Ruled out
- Claude workers for YouTube (429); a long-lived 24 h coordinator (84% of context, 454 rewrites in one session); `clear_session` while a ship or worker is live in the same session (3 refusals).
- Parallel ships on one machine (tests past the 240 s cap); forward-fixing a red trunk (revert within 10 min).
- Opus "for quality" (2.5x tokens per ship; only when named or `approved_by` + crucial); Haiku on raw cards (3 came back empty).
- Hand-written NEXT_SESSION.md as the handover (sends workers to shipped work); more hook removals for context (negligible).
- A second lease to stop desk double-closes (tc4: fixed with a CAS re-read instead, SHIPPED@fb6479e15).

## Discussions
- self-healing context files -> design shipped 6868a4650; cards C1-C5 proposed (raw, await operator yes) -> refine: not requested yet
- Lead role (one session to talk to) -> section 10; cards C6-C7 proposed -> refine: not requested yet

## Missed last time
(machine-written by `context_gap.py fold` at the next ship; the design session read these before its first edit and no brief named them:)
MyTradingSys/system/handover/SUPERVISOR_C.md, MyTradingSys/system/roles/supervisor.md, roles/builder.md, scripts/dev/role_loader.py, .claude/settings.json (hooks), `tasks.py brief tc4-desk-done-once`
