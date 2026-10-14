# How MTS runs

One page for the operator: where to go, what runs on which machine, and what could be cut. It is shown on the MTS Layers page
(tab "How MTS runs"). Written 2026-10-13 from DEVICES.md, RELAY.md, PARALLEL.md, LAYER_LAB.md, DEPLOY_RUNBOOK.md, CLOUD_ACCOUNTS.md,
CONTROL_ROOM.md and relay_prompts/TWO_HOST.md. When one of those changes, change this page in the same commit.

## Where to go for what
| You want to | Go to |
|---|---|
| Tell the project something, or ask it a question | Control Room, Inbox (pinned page, jishu.awgp account) |
| Answer a question the project has for you | Control Room, Decisions (the open ones are also listed on the MTS Layers page, tab "Waiting on you") |
| See each layer's progress, what is stuck, the roadmap and what is missing | MTS Layers page (this page) |
| Start work | Nothing to do: on each machine the dispatcher starts the next session every 30 minutes when a task is ready. To start one by hand, open the Claude app on JIS-NUC and give it the block in NEXT_SESSION.md |
| Check the live testnet system | JIS-NB: `mts status` |

## What runs where today
| Machine | Claude account | Runs by itself | You use it for |
|---|---|---|---|
| JIS-NB (desktop) | jishu.sharma | the live testnet system (auto_trader, position_manager, daily_loss_monitor, live_runner_cli, order-flow and context feeds, 2 Java feeds); MTS-Supervisor (at logon); MTS-AutoDeploy (every 15 min); MTS-Backup (every 15 min); MTS-DailyHygiene (06:30); mts-dispatcher (hourly 07-23, night task 00-06) | your trading screen and charts |
| JIS-NB or JIS-NUC | jishusharma1985 (third, Max, 2026-10-14) | nothing of its own yet: routines are per login (CLOUD_ACCOUNTS.md "Account C") | any session from the queue; read-only Control Room mirror |
| JIS-NUC | jishu.awgp | backtests and data (`F:\MTS\data`); MTS-CodexLab (GPT lab, every 30 min); mts-dispatcher (every 30 min); DSA desk worker | research sessions; Control Room Inbox owner |
| Laptop (DESKTOP-F7IU69N) | either | nothing | travel; remote desktop into the other two |
| Cloud (claude.ai/code) | either | nothing | reviews and research; its changes arrive as pull requests into fast-track |
| GitHub | - | CI on every push (Ubuntu and Windows); auto-merge of cloud pull requests when green; moves `green/fast-track` | - |

## Who does the work
| Worker | Model | Does | Where |
|---|---|---|---|
| Claude sessions | Sonnet by default, Opus only when you name it | build, research, refine cards | either machine, or cloud |
| Codex lab | GPT (gpt-6-astra, gpt-6-luna) | audits and scoped builds from lane CODEX cards | JIS-NUC (MTS-CodexLab) |
| DSA | DeepSeek chat through AIBridge | run-and-report jobs (`desk.py`) | a chat window on JIS-NB or JIS-NUC |

## Why it feels like too much (counted 2026-10-13)
- **Work sits in five lists:** NEXT_SESSION.md tasks, task cards (`system/tasks`), the DSA desk queue, the Codex lab queue
  and the Control Room backlog. On top of those come the BUGS.md registry rows and the claims.
- **Three ways to hand over:**
  - the relay (NEXT_SESSION.md plus the dispatcher);
  - `sync.py ship` from the machines;
  - pull requests from cloud sessions.
- **Bookkeeping crowds out research.** 1,246 commits landed on fast-track between 10-01 and 10-13. By commit subject, about
  44 % are bookkeeping (claim, release, lane health, relay, sync) and about 20 % are research or backtests.
- **Two accounts take the same queue,** so "which window should I open?" has no fixed answer.

## Proposals to make it simpler (decision q17; nothing is applied until you answer)
| # | Change | What you notice |
|---|---|---|
| P1 | One account per job. jishu.awgp (NUC and cloud) does all research and building. jishu.sharma (desktop) only runs and watches the live testnet system. | One answer to "which window": research on the NUC, trading on the desktop |
| P2 | One machine starts sessions. The relay dispatcher runs on JIS-NUC only. The desktop keeps only the live-system tasks (Supervisor, AutoDeploy, Backup, DailyHygiene). | No more sessions popping up on the desktop |
| P3 | One work list: task cards. NEXT_SESSION.md shrinks to "run `tasks.py next`" plus host notes. Desk and Codex jobs are cards with a lane (most already are). | One place shows all work. The MTS Layers page reads it. |
| P4 | Bookkeeping leaves the commit history. Claim, release and lane-health records move to one state file that is not committed per change. This is a Sonnet card. | Commit history shows real work |
| P5 | Three MTS pages. Control Room (talk to the project), MTS Layers (see each layer), Tom/Fabio deck (reference). CBP pages stay with the CBP project. | Fewer pins |
