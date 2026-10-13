# Alignment review, 2026-10-13 (Opus, JIS-NUC): are we moving in the right direction?

Operator ask (Jis, thread "Non-core layer audit handoff", 2026-10-12 19:11Z): look back 24 hours across layers, sessions and
machines; check direction, duplication, wasted effort; learn from the backtests; make blockers visible as Control Room questions;
show what each session did; keep CI/CD and token cost in view. Blanket go: decide with the recommended option, record it.

Window read: 2026-10-11 13:30Z to 2026-10-12 19:00Z. Sources: `git log origin/fast-track` (334 commits), `session_log.py` (new),
`system/relay_runs.jsonl`, `tasks.py list`, `sync.py claims/health`, `lane_health.py status`, ROADMAP.md, BACKTEST_FAILURES_RESEARCH.md,
observations/2026-10-12_layer_observations.md, revalidation/VERDICTS.md, TOKEN_AUDIT_2026-10-12.md, the Control Room db (this account),
the project thread list (40 threads). Not read: the JIS-NB live tree (mirror is 23 h old), the other account's Control Room db (no access).

## 1. Answer
**The direction is right. The pace on the one chain that matters is not.** The road map of 2026-10-11 (redefine Tom and Fabio from
their own trades, stop re-testing the old encodings) is sound and every finding since supports it. But in the 30 hours after it was
written, about 80 sessions ran and the chain that leads to a Tom answer advanced by one step (ledger repairs). It then stopped at two points
nobody was watching:
1. `tom-layer-v2-spec` (Opus) was waiting for you to name Opus. You did at 19:11Z. It is now ready, priority 1.
2. `tom-holdout-clean-split` (priority 1) sat under a JIS-NB claim for 30 hours with no commit. Released; it runs on any machine.

Everything else that ran was real work, mostly useful, but it was work *around* the chain: tooling, audits, maps, relay plumbing.

## 2. The chain (what actually leads to "does Tom's method work")
| Step | Card | State now | Blocked by |
|---|---|---|---|
| Ground truth | tom-trade-ledger | done: 37 rows, 12 trade groups | - |
| Repairs | tom-ledger-* (4) | done 10-12 | - |
| Second look | rv01, rv-fix-tom-ledger-date-column | ready | date cells of T5-T7, T9-T11 are assumed or prose (VERDICTS D4) |
| Clean holdout + design/check split | tom-holdout-clean-split | ready (was a dead claim) | needs the date fix first: the split is computed from dates (dependency added today) |
| Spec A: families + sourced rules | tom-layer-v2-spec (Opus) | **ready, p1** | nothing |
| Spec B: cost, stop-width transfer | tom-layer-v2-cost (Opus) | blocked | spec A |
| Encode spike fade | tom-encode-spike-fade | refined | spec B, clean holdout |
| Home-market test | tom-dax-backtest | built; harness H1-H8 fixed by GPT | rv02 deep audit of those fixes; spike fade |
| Transfer to BTC | tom-probe-prereg | refined | all above |

Fabio is one stage behind Tom and should stay there: ledger audit is FIX-FIRST (3 HIGH, 4 MED), 8 usable entries against a goal of 20,
no minute timestamps (frames can only be cut on JIS-NB). `fabio-layer-v2-spec` was "ready"; a spec written on that ledger would repeat
the mistake Tom's ledger repairs just avoided. Put on hold today until the `fabio-ledger-*` fixes land.

## 3. Aligned, and not
| Work in the window | Verdict | Why |
|---|---|---|
| Tom ledger repairs, canonical groups, time/instrument/management provenance | Aligned (on the chain) | - |
| GPT lab: DAX harness fixes H1-H8, ledger frame audits | Aligned | protects the one holdout we cannot re-read |
| Second-eyes revalidation (9 defects, 2 HIGH in `sync.py tidy`) | Aligned | found a tool that deleted live work; lost klines had to be re-fetched |
| Fabio ledger video windows | Aligned in goal, **wasteful in method** | 32 window reads in 60 h, one 250-second window per session; 17 found no trade. Each paid a full session start |
| Q32/Q33 cross-guidance matrix (336 cells, 0 survive) | Off the road map | new BTC test of trigger-plus-fixed-horizon while the STOP list was in force; result only re-proved "no edge". Useful once, do not extend (no Q33b) |
| Alpha SMA200 daily backtest | Off the road map, operator-requested | NO-SOURCE chatbot spec; best variant 20.5 % CAGR against buy-and-hold 43.8 %. Parked |
| Non-core layer audit + evidence register + identity table | Aligned as preparation | it is the readiness work for the later home-fit audits; no new backtests |
| Layer index, layer map, Layer Board, relay board, artifact registry | Useful, but four views of one thing in two days | see section 5 |
| Relay plumbing: two-host standby, lane health, GPT failover, tidy, AIBridge autostart | Necessary, large share | 54 % of all commits are bookkeeping (179 of 334) |
| Live reads 8h/30m/15m + observations | Aligned | produced the three concrete engine gaps in section 4 |

## 4. What the backtests and the live screenshots taught (keep these, they cost a lot to learn)
1. **A backtest tests our encoding, not the trader.** Coded Tom fired on 0 of 7 of his own DAX trades. Every trader-derived layer
   (Tom, Fabio, Malkan, CryptoCred, positioning) was tested off its home market, timeframe or exits. Their "no edge" is ours.
2. **The fair negatives are real and stay parked:** volume (553 trials, 0 survive), candles, MA, session momentum, RSI divergence
   (92 cells, 0 candidates). Gross return is about zero before fees, so cheaper fees or other horizons will not rescue them.
3. **Frames, not transcripts.** Transcript price "18,258", chart 24,257. Every trade fact needs a frame.
4. **Stops sized for DAX do not transfer.** Tom's 20-63 point stops sit inside BTC 1-minute noise (ranges 90-154 points on 10-12)
   and cost about 2.8 R in fees per loss. The live read saw the same thing the backtest diagnosed.
5. **Live screenshots exposed engine gaps no backtest could:** Tom core cannot emit a short below value (rule reads the wrong value
   area); "healthy trend" is coded as "outside value" only; the state machine's VWAP/CVD disagree with the klines; Bollinger bands and
   the RSI 40/60 regime that are on every chart you read are computed nowhere in code. These are cards; the first two belong in spec A.
6. **A pass bar can be gamed.** Recall of 4 of 7 can be met by firing on every spike; it needs a fire-rate limit and held-back trades.
7. **Our own tools need second eyes.** Green tests asserted the bug (`tidy` deleting a just-started worktree). The package I shipped
   yesterday failed the gate on its own scripts. Revalidation by a different model found 9 defects in one pass.
8. **Unsourced numbers hide in "sourced" files.** Live RSI tolerance 0.5 is the edge of an in-sample grid; CryptoCred's 1.5R is the
   trader's minimum, used as a fixed target.

## 5. Duplication and waste found (numbers from the session log)
| Finding | Evidence | Action |
|---|---|---|
| 12 closed sessions of about 75 shipped nothing | `session_log.py 30`: most are GPT lab retries every 30 min into a spent allowance (`lab-dax-readiness-gate`, `lab-dax-unavailable-flow`), 2 are `cryptocred-home-fit-audit` started twice while blocked | lab retries fixed 10-12 23:33 (window rule); the blocked card now stays blocked until Tom spec B |
| One video window per session | 32 Fabio window reads in 60 h, 17 with no trade in the window | Control Room question Q3: pre-screen windows with a script, read only windows that show an order ticket |
| Start-up cost paid about 80 times | every session loads 63-73k tokens before working; 82 % of a relay session's tokens are that prefix re-read (TOKEN_AUDIT) | `b172-trim`, `b172-template` raised to priority 1 |
| Four overlapping views of layers | LAYERS.md, Layer Map page, Layer Board, evidence register | keep all four only because each is generated from files; rule: no fifth view, new facts go into `layer_index.json` |
| Two Control Room databases | one per account; this account's page had 0 questions and 41 "restored" Inbox rows with no replies | Q1: one page owns questions and Inbox |
| Same message filed twice | Setup Beta spec twice; one OBI research text under two names (Inbox) | no action; counted once in B163 |
| Task ids reused (Q43-Q47) by three threads | VERDICTS D9 | lint now refuses a repeated id |
| JIS-NB dark since about 13:00Z 10-12 | 3 open claims (8 h, 8 h, 30 h), live mirror 23 h old, testnet HALT uncleared since 09:46Z | Q2 |

## 6. Who does what, and the fallbacks (as it works today)
| Lane | Does | Falls back to | Works? |
|---|---|---|---|
| Sonnet relay, JIS-NUC (primary) | build, audit, docs, one card per session | JIS-NB dispatcher after 90 quiet minutes | yes: 23 of 24 hand-overs in 24 h were NUC |
| Opus | the four spec cards only, when you name it | none (by design) | was the silent blocker; one line from you unblocks |
| GPT / Codex lab, JIS-NUC | audits, DAX harness, second eyes | Sonnet or DSA when the allowance window is spent | yes since 10-12 23:33 |
| DSA + AIBridge | run-and-report rows | Sonnet after 24 h | **no worker heartbeat**; 4 rows wait for you to open a DSA chat (Q5) |
| JIS-NB | live testnet stack, frames (cv2), live mirror | nothing: only that machine can do these | **dark**; see Q2 |
| CI/CD | gate on every push, auto-deploy the green commit | nothing deploys when red | green at 385320d (10-12 18:11Z), 6 commits behind the tip while CI runs |

## 7. Session switching: is it working?
- **Scope: yes.** Sessions are one card each; no 272-turn session since 10-09.
- **Hand-over: yes.** 24 recorded relay hand-overs in 24 h (`relay_runs.jsonl`), each leaves NEXT_SESSION.md and a commit.
- **Cost: only partly.** A relay session spends about 1.7 M cached tokens to produce about 10k tokens of work, because the fixed
  prefix is re-read on each of about 21 turns. Short sessions cap the damage of long ones, but each switch buys the prefix again.
  The saving arrives only when the prefix shrinks (`b172-trim`) and empty starts stop (section 5).
- **Visibility: was missing.** The record existed only as `sync.py news` in a terminal. The Control Room now has a
  "Sessions: what each one did" section (results newest first, then every session with its machine and whether it shipped anything).
  The chats themselves are in the app sidebar under the project (one thread per task) and under Routines for the relay sessions.

## 8. Decisions taken under your blanket go (each is a Control Room question you can overrule)
| # | Question | Taken |
|---|---|---|
| Q1 | Which Control Room page owns questions and Inbox | this account's page (the relay runs here); the other becomes a view |
| Q2 | JIS-NB dark: HALT, mirror, three stale claims | needs you at that machine; one stale claim released, the other two left |
| Q3 | Fabio video reading method | pre-screen first; no more one-window sessions until then |
| Q4 | Fabio spec now or after ledger fixes | after |
| Q5 | DSA rows | wait 24 h for a DSA chat, then move to Sonnet |
| Q6 | Frame libraries on JIS-NUC | **not taken**: a package install needs your word |
| Q7 | Delete stale pages (CBP Dashboard 10-07 and five old ones) | **not taken**: deletion cannot be undone |
| Q8 | Cross-guidance Q33b | no |
| Q9 | Republish pages after every build | yes, rule added |

## 9. Next three sessions (in order)
1. Opus: `tom-layer-v2-spec` part A (include live gaps G2, G3 from the 10-12 read as questions the spec must answer).
2. Sonnet: `rv-fix-tom-ledger-date-column`, then `tom-holdout-clean-split`.
3. Sonnet: `b172-trim` (measure before and after).
Do not start: new layers, Q33b, more BTC runs of old encodings, a fifth layer view.
