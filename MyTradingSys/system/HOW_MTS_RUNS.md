# How MTS runs

One page for the operator: where to go, who does what on which machine, and what could be cut. It is shown on the MTS Layers page
(tab "How MTS runs"). Updated 2026-10-15 from DEVICES.md, RELAY.md, PARALLEL.md, LAYER_LAB.md, DEPLOY_RUNBOOK.md, CLOUD_ACCOUNTS.md,
CONTROL_ROOM.md, relay_prompts/TWO_HOST.md and relay_runs.jsonl. When one of those changes, change this page in the same commit.
The table below is the one place for machine x login x lane x model x may-touch; every other doc points here. A cell that cannot be sourced says UNVERIFIED.

## Where to go for what
| You want to | Go to |
|---|---|
| Tell the project something, or ask it a question | Control Room, Inbox (pinned page, jishu.sharma login, q21) |
| Answer a question the project has for you | Control Room, Decisions (the open ones are also listed on the MTS Layers page, tab "Waiting on you") |
| See each layer's progress, what is stuck, the roadmap and what is missing | MTS Layers page (this page) |
| Start work | RETIRED 2026-10-17, see SCHEDULING_POLICY.md: no dispatcher starts sessions. A super-session coordinator starts them (SUPER_SESSION.md); to start one by hand, open the Claude app and give it the block in NEXT_SESSION.md |
| Check the live testnet system | JIS-NB: `mts status` |
| Names | New name JIS-DESKTOP = old JIS-NB (the desktop); JIS-LAPTOP = old DESKTOP-F7IU69N (the Lenovo laptop); JIS-NUC stays (the NUC). Table and aliases: `scripts/dev/hosts.py`; rename steps: MACHINE_RENAME.md |

## Who does what (machine, login, lane, model, may touch)
| Machine | Login / worker | Lane and what runs by itself | Model | May touch |
|---|---|---|---|---|
| JIS-NB (desktop) | jishu.sharma | RETIRED 2026-10-17, see SCHEDULING_POLICY.md (was: relay `mts-dispatcher` every 10 min (`*/10`, waits for a peer host 90 min); KICK sessions from NEXT_SESSION.md); your trading screen | dispatcher Haiku (App setting; UNVERIFIED from the repo); builders Sonnet; Opus only when you name it | work trees only; the live tree changes only through MTS-AutoDeploy |
| JIS-NB | Windows tasks, no model (RETIRED 2026-10-17, see SCHEDULING_POLICY.md: MTS-Supervisor, MTS-AutoDeploy, MTS-Backup, MTS-DailyHygiene are stopped/to be unregistered) | the live testnet system (auto_trader, position_manager, daily_loss_monitor, live_runner_cli, order-flow and context feeds, 2 Java feeds); MTS-Supervisor (at logon, revives processes); MTS-AutoDeploy (15 min); MTS-Backup (15 min, local bare repo only); MTS-DailyHygiene (06:30) | none | the live tree and runtime data (gitignored) |
| JIS-NB | jishusharma1985 (third login, Claude Max, 2026-10-14) | any queue task; no routines of its own yet (routines are per login, CLOUD_ACCOUNTS.md "Account C"); Control Room copy is a read-only mirror | Sonnet; Opus only when named | work trees only |
| JIS-NUC | jishu.sharma (checked 2026-10-15; CLOUD_ACCOUNTS.md) | RETIRED 2026-10-17, see SCHEDULING_POLICY.md: relay `mts-dispatcher` at `7,37 * * * *` (last relay_runs row 2026-10-13: running now is UNVERIFIED); backtests and data (`F:\MTS\data`); DSA bridge; Control Room Inbox owner | Sonnet sessions; dispatcher model UNVERIFIED | work trees (`mts-dsa`, `mts-relay`); no live tree, no live loop, no MTS-AutoDeploy |
| JIS-NUC | jishusharma1985 | any queue task | Sonnet; Opus only when named | work trees only |
| JIS-NUC | Codex (GPT; no Claude login) | lane CODEX: (RETIRED 2026-10-17, see SCHEDULING_POLICY.md: MTS-CodexLab unregistered; the coordinator runs `codex_run.py tick`) plus the hand-started Codex app project (`F:\MTS\mts-codex`) | gpt-6-luna; astra only for a card flagged `crucial`, low effort (LAYER_LAB.md) | `F:\MTS\mts-codex-lab`; audit and run cards write only `research/layer_lab/` and `system/tasks/`; never the relay, live path or a holdout |
| JIS-NUC | Gemini (Google AI Pro login, Antigravity IDE; no Claude login) | hand-started only, no scheduler: lane CODEX cards the Codex lab has not claimed (GEMINI_START.md) | Google's model, UNVERIFIED which | `F:\MTS\mts-gemini` work tree only; ask-before-write; no live path, no secrets |
| Laptop (DESKTOP-F7IU69N) | Gemini (Google AI Pro login, standalone Antigravity app; no Claude login) | hand-started only: lane CODEX cards nobody has claimed (GEMINI_START.md, Laptop section) | Google's model, UNVERIFIED which | `C:\Users\e-ngineers\IdeaProjects\mts-gemini` work tree only; ask-before-write; no live path, no secrets |
| JIS-NB and JIS-NUC | DSA (DeepSeek chat, no Claude login) | lanes DSA, DSA-NB, DSA-NUC: run-and-report jobs from the desk board (`desk.py`) through AIBridge | DeepSeek | work tree `mts-dsa`; no live path, no secrets; data on JIS-NB only for DSA-NB |
| Laptop (DESKTOP-F7IU69N) | either Claude login | nothing by itself; travel, remote desktop into the other two | per login | its own clone, committed data only |
| Cloud (claude.ai/code) | any login (which login holds the 100 USD credits, expiry 2026-11-05: UNVERIFIED) | offline research, specs and reviews; its changes arrive as pull requests into fast-track | UNVERIFIED | pushed refs only; no LAN, no gitignored files |
| GitHub | none | CI on every push (Ubuntu and Windows); auto-merge of cloud pull requests when green; moves `green/fast-track` | none | nothing else |
Card lanes (`tasks.py`): HAIKU and SONNET = relay builders, OPUS = only when you name it, DSA, DSA-NB, DSA-NUC = run-and-report, CODEX = layer lab, JIS-NB = live-host desk work.
Claims are labelled by the machine's `MTS_ACCOUNT`, not by the login that is signed in (PARALLEL.md). The Qwen lane ended 2026-10-01.

## Why it feels like too much (counted 2026-10-13)
- **Work sits in five lists:** NEXT_SESSION.md tasks, task cards (`system/tasks`), the DSA desk queue, the Codex lab queue
  and the Control Room backlog. On top of those come the BUGS.md registry rows and the claims.
- **Three ways to hand over:**
  - the relay (NEXT_SESSION.md plus the dispatcher; RETIRED 2026-10-17, see SCHEDULING_POLICY.md);
  - `sync.py ship` from the machines;
  - pull requests from cloud sessions.
- **Bookkeeping crowds out research.** 1,246 commits landed on fast-track between 10-01 and 10-13. By commit subject, about
  44 % are bookkeeping (claim, release, lane health, relay, sync) and about 20 % are research or backtests.
- **Three logins take the same queue,** so "which window should I open?" has no fixed answer.

## Proposals to make it simpler (decision q17: answered "Yes, all five" 2026-10-14; note: "I will add one more a/c in future. I need flexibility to run any a/c on any machine.")
Adopted as defaults, not locks: any account must be able to run on any machine, a third account is expected. Cards: see OPERATOR_DECISIONS.md q17 Applied.
P1 and P2 are open and conflict with your 2026-10-14 request that the relay runs every 10 minutes on the desktop; they stay pending q17 and are not the plan today.
| # | Change | What you notice |
|---|---|---|
| P1 | One machine per job. The NUC (login jishu.sharma, checked 2026-10-15) does all research and building. The desktop JIS-NB only runs and watches the live testnet system. | One answer to "which window": research on the NUC, trading on the desktop |
| P2 | RETIRED 2026-10-17, see SCHEDULING_POLICY.md. One machine starts sessions. The relay dispatcher runs on JIS-NUC only. The desktop keeps only the live-system tasks (Supervisor, AutoDeploy, Backup, DailyHygiene). | No more sessions popping up on the desktop |
| P3 | One work list: task cards. NEXT_SESSION.md shrinks to "run `tasks.py next`" plus host notes. Desk and Codex jobs are cards with a lane (most already are). | One place shows all work. The MTS Layers page reads it. |
| P4 | Bookkeeping leaves the commit history. Claim, release and lane-health records move to one state file that is not committed per change. This is a Sonnet card. | Commit history shows real work |
| P5 | Three MTS pages. Control Room (talk to the project), MTS Layers (see each layer), Tom/Fabio deck (reference). CBP pages stay with the CBP project. | Fewer pins |
