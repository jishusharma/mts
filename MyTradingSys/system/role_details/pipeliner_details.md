# Pipeliner details (read at Job 2; not injected by the hook)

## Job 2: allocation
`traffic.py status` prints PROPOSED lines; act on each in order:
- `[this machine] start sessions for ...`: only in a standalone Pipeliner session: `start_session` one role worker per card (`You are <Role>.` + card id, model Sonnet, announce it; the brief ends with the no-questions rule and the `sync.py start` boot). Inside a coordinator: hand the lines to the coordinator.
- `[other machine] ...`: one `mts_signal.py send "<card ids>: please start" --to <host> --kind ask` line; a silent host gets nothing.
- `[JIS-NUC] codex_run.py tick` or `gemini_queue.py run`: run it only when this session is on JIS-NUC; otherwise signal.
- `[Pipeliner]`, `[Session_Planner]`, `[operator]`: one signal line or Control Room Inbox entry; never do their job.
- SPEND per login (from `traffic.py budget`): a login in SPEND with ready cards and no running session gets work first; a login in THROTTLE gets only model-free work (Codex lab, DSA desk, CI). No reading for a login = say so in the report, send nothing for it.
- Once per day: `python scripts/dev/traffic.py measure --hours 24`; record idle and duplicate counts in the Log of TRAFFIC_CONTROLLER.md (via `sync.py ship`).
- Leakage watch: no runtime, order, account, secret or e-mail data in any commit, card, signal or prompt to another model (GPT, Gemini, DSA). An idle login or lane with ready work, a card in two lanes, a polling agent or timer: fix the allocation.

