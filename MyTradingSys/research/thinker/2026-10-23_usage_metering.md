# Usage metering and full-capacity workflow (Thinker LITE, Sonnet; operator ask 2026-10-23)
MODEL: Sonnet, lite (open on Opus for deep design). Nothing built.

## Facts (each from a command run this session)
- `traffic.py budget --no-fetch`: logins A/B/C all NORMAL; A 5h=3% week=97%, C 5h=13% week=99% with reset 2026-10-23T09:00Z: week room is about to be wasted on A and C (readings 6h+ old for A, B).
- `supervisor.py:577` K_DEFAULT = 0.12 weekly points per 5h point is labelled GUESS ("until two readings in one window measure it"). Per-step metering replaces this guess.
- `codex_run.py status`: lab runs on JIS-NUC only; this machine sees queue (5 ready) but not allowance. Codex meter must be read on the NUC (ssh gate), not locally.
- get_usage is an MCP tool (session-only). A shell hook (`.claude/settings.json` PreToolUse matcher at line 151 already fires on Agent|Task|Workflow) cannot call it; a hook can only print an instruction or run a script.
- `tasks.py list`: no card named usage-pilot-krown-s0 exists yet; confluence-s0-registry is raw, HAIKU, p2 (the operator says p1: card is created below at p1; the existing one is the work card).
- Granularity: get_usage percent is integer. A Haiku step costs under 1% of a 5h window, so before/after reads show 0 for most steps. This is the main design problem.

## Options
| # | Option | Cost | ROI | Risk / undo |
|---|---|---|---|---|
| A | Percent ledger: Supervisor calls get_usage before/after each Agent step, appends a CSV row via a new `usage_log.py row` | ~2 tool calls per step (small), 1 script + 1 hook reminder = 2 Sonnet S cards | Replaces K_DEFAULT guess; shows per-lane burn | Integer % too coarse for cheap steps (rows read 0); parallel agents blur attribution. Undo: delete script |
| B | Token ledger: `usage_log.py` parses each subagent/session transcript JSONL (input, output, cache tokens, model) per card; get_usage % is read only per 5h window, then % per token is calibrated by regression | 1 script (M card) + calibration after ~30 rows; no extra tool calls per step | Exact per-step cost for every Claude step incl. Haiku; % is derived, not read 2x per step. Feeds routing (cost per card kind) | Needs transcript path stable (NOT_IN_DATA: confirm path with `ls ~/.claude/projects`); Codex/Gemini not covered by transcripts |
| C | Both: B as the base ledger, A only at window edges (start and end of each 5h window and every 10 steps) to calibrate; plus idle-lane check and ultracode rule | A + B cards + 1 check card (~5 cards) | Full-capacity loop: idle-lane flag turns unused 5h room into queued work | Most moving parts; build in order B, A-lite, check |
| D | Do nothing: keep BUDGET lines per login | 0 | none | Week room on A/C keeps being wasted |

RECOMMEND: C, starting with the pilot on B+A rows, because % alone cannot see a Haiku step and tokens alone cannot see the plan limit; the pair gives both.
DECISION (OURS): the pilot writes both columns so the operator can see which one is enough; revisit after 30 rows.

## Pilot design (card usage-pilot-krown-s0)
Run confluence-s0-registry (HAIKU) as the work. `MyTradingSys/research/USAGE_PILOT.csv` header:
`ts_utc,lane,model,card,step,pct5h_before,pct5h_after,pctweek_before,pctweek_after,fable_week_before,fable_week_after,tokens_in,tokens_out,tokens_cache,minutes,source`
`source` = get_usage | codex_status | gemini_manual | transcript. One row per step. Row 0 is a baseline pair (two reads, no work, 5 min apart) to show get_usage noise. Parameters: sampling points OURS.
Other lanes: Codex = `codex_run.py status` over the NUC gate (allowance points, parse real format, count); Gemini/Antigravity = NOT_IN_DATA: no command known; `grep -ril antigravity scripts MyTradingSys/system` to find one, else manual column filled by the operator, never blocking.

## Roles, hooks, checks the workflow needs
- Thinker: this note; owns the design. Session_Planner: refines the raw cards, adds step list to confluence-s0-registry so each step is one measurable unit. Builder: the scripts below. Supervisor: runs the pilot, calls get_usage at step edges, reads idle-lane flag in `supervisor.py plan`.
- Hook (no scheduler): extend the existing Agent|Task|Workflow PreToolUse (settings.json:151) to print `USAGE: call get_usage, then usage_log.py before <card>` and a PostToolUse twin printing the `after` instruction. A hook cannot call MCP, so it is a reminder plus a script; the script refuses a row without both reads.
- Check: `usage_log.py idle` flags a lane whose 5h < 40% with ready cards in its lane (or Claude week room > pace with no worker running) and a window within 60 min of reset. Wired into `supervisor.py plan` output as an IDLE line. Thresholds OURS.
- Context rule (operator: let context build where needed): turn_meter caps stay for unattended workers; the ledger adds a `ctx_ok` tag per card kind (audit and review cards may build context; run cards may not). OURS, tune from rows.
- Ultracode: opt-in only when the card or operator text contains the word `ultracode`; no hook enables it. The ledger logs it as model=`sonnet+workflow` so its cost is separate. DECISION (OURS): no auto-detection of cases where it would help.

## Raw cards (created via tasks.py new)
1. usage-pilot-krown-s0 (HAIKU p1): run pilot, write USAGE_PILOT.csv.
2. usage-log-script (SONNET p1, build): `scripts/dev/usage_log.py` row/idle/summary + transcript token parser + test that fails on old code.
3. usage-hook-agent-reminder (SONNET p2, build): PreToolUse/PostToolUse reminder on Agent|Workflow.
4. usage-idle-lane-check (SONNET p2, build): idle flag in supervisor plan; replaces K_DEFAULT once 2 readings per window exist.
5. usage-codex-gemini-meter (SONNET p3, audit): find the Gemini/Antigravity quota command; add Codex status parse over NUC gate.

NEXT: Session_Planner refines cards 1-2 first (card 1 blocked on 2 only for token columns; it can start with % columns).

Card ids (in order 1-5): usage-pilot-run-confluence-s0-registry-o, usage-log-py-per-step-usage-ledger-trans, hook-reminder-get-usage-before-after-age, idle-lane-check-in-supervisor-plan-repla, find-gemini-antigravity-quota-command-an.
