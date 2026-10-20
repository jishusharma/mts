# ROLES: helper sessions you open by name (operator 2026-10-17)

A role = a session started with one line; the role itself lives here, so a lost or over-budget session is replaced by pasting that line again. Pinning is only a sidebar shortcut. Channels (signals, desk, shot, sync) are unchanged. Recipes: MTS Home section "How to use MTS" (`scripts/dev/make_home.py`).

**Start prompt, identical for every role** (replace NAME): `You are NAME.` The role_loader hook (UserPromptSubmit) loads MyTradingSys/system/roles/<role>.md from origin/fast-track; the first reply must be the `ROLE LOADED: NAME vN · token word-word · <path> @ <sha>` banner (`python scripts/dev/role_loader.py banner NAME` prints the expected one). No banner or `ROLE NOT LOADED` = do not work with that session; open a new one.

**Aliases** (`ALIASES` in `scripts/dev/role_loader.py`): `Artifacts_Guy` -> `1985Artifacts_Guy`; `Q&A_Helper`, `Network_Admin_Guy` -> `Admin_Guy`; `Traffic_Controller` -> `Pipeliner`.

## Rows
| Role | File | Purpose | Model | Runs Where |
|---|---|---|---|---|
| MTS_Doctor | [roles/mts_doctor.md](roles/mts_doctor.md) | AI health + process audit, other-model verification of every change | Sonnet | any device (at most 1/day) |
| 1985Artifacts_Guy | [roles/1985artifacts_guy.md](roles/1985artifacts_guy.md) | Owns published pages and links; republishes when repo copy is newer | Sonnet | jishusharma1985 login |
| Eagle_Eyes | [roles/eagle_eyes.md](roles/eagle_eyes.md) | Observes and records: reads chart screenshots against live files | Sonnet | any device (full fidelity JIS-NB) |
| Admin_Guy | [roles/admin_guy.md](roles/admin_guy.md) | Backlog intake, operator decisions record, and machine hygiene | Haiku 5.5 | any device, any login |
| Lab_Guy | [roles/lab_guy.md](roles/lab_guy.md) | Quality owner of Claude-to-lab flow, revalidates results across models | Sonnet | any device (JIS-NUC lab) |
| Pipeliner | [roles/pipeliner.md](roles/pipeliner.md) | Routes desk work and allocates machines, logins and lab lanes | Sonnet | any device (trunk lease) |
| Session_Planner | [roles/session_planner.md](roles/session_planner.md) | Refines raw cards to ready, dispatch ranking, cleanup | Sonnet medium | coordinator-embedded |
| Supervisor | [roles/supervisor.md](roles/supervisor.md) | Runs super session, dispatches workers as role sessions | Sonnet / Opus | any device, weekly headroom |
| Builder | [roles/builder.md](roles/builder.md) | Implements scoped build cards with fail-first tests | Sonnet | coordinator-embedded |

## Rules for every role
- Work in the worktree `sync.py start <slug>` prints; never work in the live tree. Share only through `sync.py ship`. Cross-machine messages only through `mts_signal.py send` (one line); long requests are a desk task, the signal points to it.
- Opus only as in WORKERS.md rule 6. Scoped sub-work goes to Haiku Agents (rule 3a, at most 5 at a time).
- No compaction (operator 2026-10-18): a role session runs under the turn budget in WORKERS.md rule 5 and is replaced by its one-line start prompt when it is over it.
- Roles report; they do not trade, deploy, restart, touch HALT files or read `.secrets/`.
