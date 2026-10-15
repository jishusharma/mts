# Morning report - overnight 2026-10-15 evening IST -> 2026-10-16 (super-2, JIS-NB)

**Bottom line: no edge yet, pipeline ready.** Two screens ran and both are INCONCLUSIVE. Nothing is promoted (the registry is
empty). The testnet system is HALTed and deploy-blocked since yesterday, and it needs four operator steps (below) to run the
new code.

Coordinator: super-2 (Opus, worktree compassionate-herschel-52c7ce), run 2026-10-15 17:57Z to ~22:00Z. Workers were 18 Agent
subagents (Sonnet/Haiku). Full log: side-session notes `super2_log.md`.

## What you need to do (in order)
1. **Unblock deploy (one time).** AutoDeploy has been STOP_DIRTY since ~15:45Z 10-15 because a generated STATUS.md is dirty in
   the live tree, which is 209 commits behind green.
   `git -C C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed checkout -- MyTradingSys/research/STATUS.md` (plus any other
   generated file shown by `git -C C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed status --short`). The next 15-min tick
   then deploys. Tonight's allowlist fix (2913fefa) stops this from recurring.
2. **Clear the HALT.** In place since 10-15 08:00:19Z after a Deribit 10041 (settlement in progress) reject. After the
   deploy, a 10041 on a first entry no longer halts (b0cb201e).
3. **Restart the hung orderflow recorder.** PID 11468 has been alive but frozen at 2026-10-14 12:29Z, so it is about 33 h
   dead. Back up `runtime_data/.../_state.json`, then `Stop-Process -Id 11468`. The supervisor relaunches it and resumes
   from 12:30Z. From now on the new stall guard (bde4a491) exits it on its own after 15 min without progress.
4. **Confirm by 2026-10-23:** the grandfathered trading list (see Decisions, W14), including that `consensus` is now
   collection-only on testnet.
- Before the NUC ever runs the live loop, set `MTS_LIVE_OWNER_DIR` to a folder shared by both hosts (ce7e74ad). If the
  supervisor refuses to start because of an unreadable owner marker, delete that marker in `runtime_data`.
- The super-session watchdog (1e50bbf8) takes effect only after step 1 deploys. JIS-NB has no MTS-DispatchGate Windows
  task; the `mts-dispatcher` routine runs in the live tree.

## Live analysis (W1, read-only, 10-15 ~18:00Z)
- **State:** HALT present; AutoDeploy STOP_DIRTY; live HEAD 71a3c75e; orderflow recorder frozen (W7).
- **24 h:** 78 trades, net -29.20 USD, PF 0.10, 86 % time exits.
- **7 d:** 486 trades, net -40.81 USD, PF 0.38, 97 % time exits.
- **Why time exits dominate (W10):** an 8-bar time exit against a 1 % stop and a 2R target. TOC 1m, about 80 % of trades,
  holds at most 8 minutes.
- **Ledger mislabel fixed:** 17 of 24 "target" exits were really stops. The true split is 7 targets / 19 stops; net is
  unchanged. Old rows were not rewritten.
- `rsi:cross` maps only (40, down) and (60, up); other levels are rejected fail-closed (104 rejects since 10-07).
- The parked layers are not live.

## Screen verdicts
| Screen | Verdict | Numbers |
|---|---|---|
| gross-effect-screen-dev (NUC, PRE_REG'd) | INCONCLUSIVE | Arm T: n=40, mean -0.057 %. DIFF vs notF -0.050 % (t -0.37). MDE 0.365 %. Net after cost negative in every arm, so no detector work follows. |
| wlow-bounce-bbrsi60 (your 10-15 screenshot setup, DEV only) | INCONCLUSIVE | n=8 (< pre-registered min 10). Mean 4 h -0.29 % vs baseline +0.00 %; DIFF -0.30 % (t -2.05). MDE 0.41 %. A decision needs ~130 events; DEV gives ~3 a year. |

What each layer added to the weekly-low setup:
- **Net delta:** NOT_EVALUATED (one side < 10 events).
- **CVD:** NOT_EVALUATED (one side < 10 events).
- **Open interest:** NOT_IN_DATA for DEV (OI history starts 2025-09).

All three are now logged for every live occurrence (W18), so a forward sample builds.

Weekly-low setup records:
- **Pre-registration:** PRE_REG f22feae7 was committed 56 s before RESULT f0605887. Commit order holds; that no outcome was
  read first rests on the worker's word.
- **Trial ledger:** TRIAL_LEDGER.csv, 8 rows.
- **Status:** `python -m MyTradingSys.backtest.layers.wlow_bounce.status` read ACTIVE at the 10-15 19:00Z bar (RSI 56.7,
  close 0.47 % under the upper BB, prior weekly low 80,344.8).
- **Promotion:** the manifest is REJECTED by `promote.py check`, so the setup is not registered.

## What is on testnet, and in which mode
- **Promotion registry** `execution/promoted_setups.json`: **empty**. Nothing has been promoted through the new pipeline.
- **Default-deny (W14):**
  - Only sources in the registry, or in the grandfather list `auto_trader_config.json` `pre_pipeline_sources` (20 entries,
    today's trading set incl. tom), can place testnet orders.
  - Everything else is collection-only shadow: an alert with `shadow_side` and no `side`, which auto_trader rejects.
- **wlow-bounce:** collection-only shadow emitter (W18, d2be783f). Each ARMED/ACTIVE reading goes to `runtime/wlow_bounce_forward.jsonl` (gitignored) with OI, CVD and net delta. Triggers go to the 1h alerts as `collection_only` with `shadow_side=long` and no `side`, and auto_trader rejects them. It never sends orders and starts after the next deploy.
- **In practice:** nothing trades until steps 1-2 above, and the deployed code is still the 10-15 version until step 1.

## Shipped tonight (all verified `git cherry origin/fast-track <sha>` empty)
| Worker | SHA | What works now |
|---|---|---|
| W2 | bff7c423 (merge a71562cf) | Promotion pipeline: `promote.py check/register/demote/verify`; shadow gate in live_runner_cli; auto_trader rejects collection-only alerts; CI checks every registry entry; PROMOTION_PIPELINE.md. |
| W5 | 1e50bbf8 | `relay.py heartbeat`; dispatch_gate runs `relay.py watchdog`, which resumes a super-session stop whose heartbeat is older than 60 min. |
| W6 | 2913fefa | AutoDeploy backs up and restores allowlisted generated files instead of stopping STOP_DIRTY. |
| W6 | b0cb201e | Deribit 10041 on a first entry: skip, no HALT. |
| W8 | bde4a491 | Orderflow recorder logs each cycle; backoff 40-300 s; exits with code 3 after a 15-min stall. |
| W9 | 0a4b856c | A deploy that touches the orderflow recorder restarts it. |
| W10 | 8e35b31a | classify_exit fix; LEDGER_EXIT_AUDIT.md. |
| W12 | ce7e74ad | `live_owner.py` one-owner guard for the live loop. |
| W13 | b9b9f294 | live_mirror publish failure is visible (PUBLISH_FAIL.json, `brief` warns). |
| W14 | 8254ece6 | Fable H1: default-deny gate plus grandfather list. |
| W15 | 3c7dcf86 | Fable H3: stale-green fallback refuses CI red/unknown. Fable L6: live inputs restored after merge. |
| W17 | 644ca8b6 | Fable H2: demote off is enforced via trade_blocklist. M4: PRE_REG pinned. L7: shared size validator. |
| W16 | f22feae7, f0605887, 611a2a23 | wlow-bounce PRE_REG, study, detector, status CLI. |
| W18 | d2be783f | wlow-bounce collection-only emitter with OI/CVD/delta per event. |
| coord | 9644d77a | SUPER_SESSION.md learning loop, Boot facts, Agent-worker rules. |

Closed with no code change:
- **W4 queue health:** 18 READY cards; RELAY.md was over its cap, already fixed by 45747d28.
- **W7 orderflow diagnosis.**
- **W11 exec-halt-entry-10031:** root cause unprovable; 10031 keeps halting, fail-closed.

Shipped by other sessions tonight:
- **Pacer:** 51bee990 budget.py.
- **Gross-effect screen** on the NUC.
- **Fable review** `research/fable_audit_2026-10-16/PROMOTION_REVIEW.md`: SAFE WITH FIXES, no BLOCKER. H1, H2, H3, M4, L6
  and L7 are fixed above.
- **Open:** M5 (OOS numbers in a manifest are self-declared). It is a pipeline limitation, not a live risk while the
  registry is empty.

## Decisions (OURS, taken without asking you)
- **Workers as Agent subagents:** this coordinator was started by a session, so the app refuses `start_session`.
- **HALT and STOP_DIRTY left in place:** builders never touch HALT or the live tree. Code fixes shipped; the one-time steps
  are yours (above).
- **No new Windows scheduled task created:** the watchdog waits for the deploy.
- **Fable fixes ran in the order H1 -> H3+L6 -> H2+M4+L7:** H1 grandfathers today's trading set, so testnet behaviour did
  not change tonight. The `layer:` catch-all is NOT grandfathered, so `consensus` (no size override, no own account) is now
  collection-only (fewer trades, the safe direction). review_by 2026-10-23 is informational: enforcing it would halt testnet.
- **CI fallback is stricter than the review asked:** unknown CI state now refuses as well.
- **10031 and unknown Deribit codes keep halting** (fail closed).
- **Your weekly-low request:**
  - "Live tracking" of an unvalidated setup means observation only, no orders.
  - Your direct request overrides the plan-s3 detector park for this one setup.
- **Not run tonight:**
  - nb-* cards: they change the live tree or scheduled tasks.
  - G5 event-study cards: parked until G2+G3.
- **Spend brake:** after W17, only W18 (your live-tracking request); then drain.
- **Queue host:** no tasks.py schema change; the card `lane` keeps carrying the host.

## Usage
| When | 5-hour | Weekly all models | Weekly Fable |
|---|---|---|---|
| Start 10-15 17:57Z | 3 % | 33 % | 2 % |
| 10-15 21:28Z | 67 % | 41 % (+8, shared with NUC + Fable on the same meter) | 7 % |
| End 10-15 22:10Z | 76 % (resets 22:40Z) | 42 % (+9) | 7 % (+5) |

Target was about +8 for this session within a +15 shared cap; +9 used on the shared meter (NUC screen and Fable review included).

## Next (NEXT_SESSION.md)
The s6 relay items come first, then the JIS-NB-lane READY cards:
- wlow-bounce forward sample: review once 10 live events are logged.
- move-live-host-generated-files-status-md.
- Fable M5: an independent OOS re-run before a registry entry.
