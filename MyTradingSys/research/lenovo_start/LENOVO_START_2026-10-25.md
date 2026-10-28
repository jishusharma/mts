# Starting work on the Lenovo (DESKTOP-F7IU69N, login A) - Thinker note 2026-10-25

Operator ask (voice, 2026-10-25): how can work start on login A on the Lenovo, can a session reach it while idle, is there a script,
and how do we avoid collisions and broken builds. Simplest fixes with ROI only. Cross-checked with Gemini (NUC job gb4-lenovo-start,
branch gemini-q/gb4-lenovo-start, `research/lenovo_start/gemini_answer.md`); the GPT job gx5-lenovo-start had not finished when this was written.

## 1. What exists already (evidence)
- Lenovo is login A today: `mts_signal.py who` (2026-10-25) prints `login A desktop-f7iu69n seen 15h ago`. Docs disagree: CLOUD_ACCOUNTS.md:9 puts A on
  JIS-NUC (2026-10-15) and LENOVO_SETUP.md:1 calls the Lenovo jishusharma1985 (login C). Fix the docs to the roll call.
- It already works as a builder: 233 commits from `e-ngineers@DESKTOP-F7IU69N` (2026-10-19..24), incl. super sessions (SUPER_SESSION.md:64,
  "full gate passes only with MTS_GATE_JOBS=2, ONE ship at a time") and 4463a42e (2026-10-24).
- Headless runner exists: `scripts/dev/mts_run.py` (restored from the Lenovo 0c91e268, 2026-10-24; design RUN_MODEL.md). A Python loop, 0 tokens:
  picks a ready SONNET/HAIKU/OPUS card, `sync.py claim`, `sync.py start`, runs `claude -p` (one card, then exit), logs to a ledger, stops on an
  ACTIVE STOP/HOLD in ANNOUNCEMENTS.md, 3 failures, the pace limit or the hour limit (mts_run.py:211-321). It finds the CLI on the Lenovo's winget path (mts_run.py:35).
- Remote start of a headless worker exists for the NUC only: `scripts/dev/nuc_wake.py` (ssh gate + a one-shot scheduled task running `claude -p`).
  SCHEDULING_POLICY.md:24 allows that one-shot task for nuc_wake.py only; no standing tasks or routines anywhere (SCHEDULING_POLICY.md:7).
- Cross-device notes: `mts_signal.py` (orphan branch `mts-signals`). Pull-only: "nothing wakes an idle session" (mts_signal.py:29). Proof:
  2026-10-24 14:50Z the Lenovo (A) signalled JIS-NB "reply with a task card id for me"; no reply came; it picked cards itself.
- Power: sleep and hibernate never, lid close does nothing, on AC and battery (DEVICES.md:133, done 2026-10-21). Wi-Fi only (DEVICES.md:131).
- Lenovo has no ssh server or gate: NOT_IN_DATA (only the NUC gate is documented, DEVICES.md:110). This app has no saved SSH connections
  (`list_start_targets`, 2026-10-25: `ssh: []`).

## 2. Ways to start a Claude session on the Lenovo
| Way | Needs | Can a JIS-NB session trigger it with no operator turn? |
|---|---|---|
| Lenovo Claude app, signed in as A, session typed by the operator | app open, operator at the Lenovo (or RDP) | No |
| Remote Control: steer a Lenovo app session from claude.ai or the phone signed in as A | that session opened once on the Lenovo with Remote Control on | No: Remote Control and SendMessage reach only the SAME login's sessions (ListAgents here shows login C only) |
| `start_session` from JIS-NB to the Lenovo | target "ssh" needs a saved SSH connection (none) and would bill login C, not A | No |
| `mts_run.py loop` started once on the Lenovo in a foreground PowerShell | machine on, Windows signed in, CLI signed in; the app need NOT run | YES, indirectly: JIS-NB writes a ready card; the loop takes it. Stop = an ANNOUNCEMENTS STOP/HOLD |
| ssh + one-shot task (nuc_wake pattern), Gemini's step 2 | OpenSSH server + key on the Lenovo, operator yes to widen SCHEDULING_POLICY s4 | Yes, but costs a new inbound door and a policy change |
| Wake-on-LAN, `claude://` deep links, GUI clicks | - | Not needed (the Lenovo never sleeps); deep links need a person at the screen |
Only knowable by trying: whether the CLI on the Lenovo uses login A (`claude -p` reads the same `~/.claude.json` as `mts_signal.login()`; run one and check
the signal's login letter); whether the Lenovo app and CLI share that sign-in; login A's weekly room (no BUDGET line for A on the signal branch).

## 3. Collisions and broken builds
| Failure | What prevents it today | Gap |
|---|---|---|
| two devices take one card | `sync.py claim` pushes a claim at once; mts_run skips claimed cards and calls `claim` (refused = skip) | none for code cards |
| same files edited at once | `--area` overlap refusal (PARALLEL.md:44); git merge on ship | cards without `--area` |
| broken trunk | smoke gate on ship; CI on push; code ship blocked while CI red (`sync.py enforce_ci`); revert within 10 min (CLAUDE.md) | none new |
| machine overload | GATE_SLOTS=2 per machine (sync.py:145); mts_run runs 1 worker by default | Lenovo needs MTS_GATE_JOBS=2 (SUPER_SESSION.md:64) |
| card needs data the Lenovo lacks (F:/MTS klines, JIS-NB live data) | lanes: such cards sit in JIS-NB / DSA-NUC / CODEX lanes, which mts_run never picks | a SONNET card that needs data fails, 3 fails stop the loop |
| idle loop never sees new cards | - | mts_run reads local cards; the empty-queue path sleeps 10 min and never fetches (mts_run.py:221-231, 307-311) |
| leftovers | `sync.py where`, stop guard | 6 Lenovo branches pushed but not merged (signal 2026-10-24 09:46Z) |

## 4. Plan (ROI order, at most 5 steps)
1. Refresh fix in mts_run.py (Builder, Sonnet, JIS-NB, ~15 turns, cost low). Before `pick_card`, fetch and fast-forward the runner tree (reuse
   `sync.py start`), so a card written on JIS-NB is seen within 10 min. New test in MyTradingSys/tests/test_mts_run.py fails on today's code.
   Benefit: the whole remote-start path works without anyone at the Lenovo. Test (<10 min): the test, plus a dry run `mts_run.py once --dry-run`.
2. One-time check at the Lenovo (OPERATOR AT THE LENOVO, 10 min): `git -C <clone> pull`, `setx MTS_GATE_JOBS 2`, then
   `python scripts/dev/mts_run.py once --dry-run --login A` and one real `once` on a tiny docs card. Pass = a claim and a ship from
   desktop-f7iu69n with login A on the signal branch. This answers the "only by trying" questions.
3. Start the loop (OPERATOR AT THE LENOVO, 1 min per day): `python scripts/dev/mts_run.py loop --hours 10 --login A` in a PowerShell window
   left open (no scheduler; it ends by itself). From then on any JIS-NB session starts Lenovo work by making a SONNET/HAIKU card `ready`,
   and stops it with an ANNOUNCEMENTS HOLD. Test (<10 min): a ready docs card is claimed by desktop-f7iu69n within one 10-min sleep.
4. Docs truth (Haiku, 10 turns): CLOUD_ACCOUNTS.md and LENOVO_SETUP.md say Lenovo = login A per the 2026-10-25 roll call; the operator
   lines in step 2-3 go into LENOVO_SETUP.md. Ship the 6 leftover Lenovo branches or delete them after a check that their content is on trunk.
5. Only if step 3 has run 3+ days and walking to the Lenovo to restart the loop is the bottleneck: the ssh route (Gemini's steps 1-2:
   OpenSSH + key on the Lenovo, a `lenovo_wake.py` from nuc_wake.py), with the operator's yes to widen SCHEDULING_POLICY s4. Cost: an inbound
   door on the laptop that becomes the live host; that is why it is last.

## What NOT to build
Wake-on-LAN (it never sleeps); deep links or GUI clicking; a new messaging bus (signals plus cards suffice); cross-login session control
(the app does not offer it); standing scheduled tasks; a Lenovo super session in the app (the CLI loop costs 0 tokens while idle).
DECISION (OURS): the CLI loop beats the ssh route on cost and risk; nothing here touches the live loop or the planned cutover (LIVE_HOST_MOVE.md).
