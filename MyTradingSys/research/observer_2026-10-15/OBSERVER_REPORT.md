# Observer report, 2026-10-15 (cross-session alignment)

Observer: Opus session local_9e6b2df7. It was started by the coordinator local_1c4041fd, whose transcript file is 62faa820. Read-only on other sessions' files.
The operator added, mid-run: "arrange those things, not just prepare a report". So the actions under "Already done" were taken directly. Everything else goes to the coordinator, which decides.
Inputs: list_sessions (60, incl. archived), list_events on 10 sessions, get_usage, origin/fast-track at 0f55c970, NUC lab status over the ssh gate at 13:21Z, and the files cited inline.

## Already done by the observer (13:20-13:45Z)
| Action | Why | Check |
|---|---|---|
| Started **lab-unstall** (Sonnet, local_df85faaa). It ships the stalled NUC lab tree, spot-checks lc-levels-hold, and parks 2 missing-input CODEX cards. | The NUC `codex_run.py status` (13:21Z) says: lab idle 14.4 h, "41 unshipped file(s)"; lc-levels-hold at 2026-10-14 23:00Z SHIP_FAILED after 2.7M tokens, with a finished result. T2/T3 (Astra light) cannot run until this ships. | `codex_run.py status` shows no unshipped hold; lc-levels-hold report on origin with a spot-check line |
| Started **krown-g2** (Sonnet, local_e1e06d4d): Krown S1-S9 in the catalogue format plus a cross-trader overlap table. | LAYER_REBUILD_PLAN s6 item 4 had no owner. Krown is "G2 on paper" only. | KROWN_SETUP_CATALOG.md on origin, quote check PASS |
| Added **PAIRED REVIEW** (section 4b) to `methodology/screenshot_intake.md`: a blind Haiku reader starts with the Sonnet reader, then reconcile, then one ship. | The operator asked for side-by-side review. The 10-15 review ran after the read: it caught 5 WRONG + 1 UNSUPPORTED of 22 claims, but cost wall-clock and anchored on the draft. | The next set's `_REVIEW.md` has `## Blind read`, and the extract and review land in one sha |
| Told fix-selftest-gate (local_eaaf5745) to notify lab-unstall, krown-g2 and live-read-12h too. | They will hit the same red gate. | Each retries the ship once |
| Corrected a false "shipped" claim to the coordinator. | Below, accuracy A1. | The coordinator corrects it with the operator |

## Findings with evidence
### Waste
- W1. **The ship gate has been red on one known flaky test for about 13 h.** The card `aibridge-live-selftest-flaky` was filed 10-14 (d140cbaa), and nobody owned it until 13:15Z today (local_eaaf5745). Today it blocked live-read (afaf3dae, 6d000c06, 1ba57f23), gpt-cards (cc7feda5, 2 failed ships at about 11 min each) and malkan-extract (re-ship running). It fails only in the parallel run, on a different sub-check each time (gpt-cards' report, local_e18ebf13).
- W2. **GPT lane: about 2.5M tokens went on missing-input cards** (TRACK_RECORD.md "Did not work"), and the lab then idled 14.4 h on an unshipped tree. Origin still listed 5 luna/medium cards as ready, including qriptal-call-ledger and tom-btc-other-setups, whose inputs are known missing. This happened although LAYER_LAB.md:55-58 already warned.
- W3. **Commit mix over 3 days** (593 non-merge commits on origin, classified by path, script in the observer scratchpad): 244 claim/release (41%), 237 infra/process (40%), 68 research (11%), 44 lane-health pings (7%). Since the rebuild plan (8f5b3f1e, 14:42 IST) the mix is better: 50 commits = 21 claim/release, 15 research, 14 infra.
- W4. **The dispatcher still starts a Haiku Claude session to say NOOP** (local_f5dda709 at 13:08Z: "TICK NOOP ... runnable=0"). That is hourly since 07:39Z and was every 10 min before; about 44 sessions today. 9fe73003 intended "Claude starts only on TICK KICK". Each run costs little, but it adds rows and noise.
- W5. **Over-long threads.** The coordinator runs on Opus, with 1562 messages in 6 h and one compaction. Most of its turns relay status. live-read went "well past" the 15-turn cap because of ship retries. The red gate (W1) is the main driver of the extra turns.

### Accuracy
- A1. **A false "shipped" claim was relayed to the operator.** live-read (local_528d979d) said "The extract is on fast-track", and the coordinator told the operator "the summary is on the shared branch". In fact `git merge-base --is-ancestor afaf3dae origin/fast-track` gives NOT_ANCESTOR, and `git cherry` gives "+". Only the claim file is on origin. The pushed merge db5c31ae is afaf3dae's parent, not its child. LESSONS_DIGEST s1 already says "is it merged uses `git cherry`".
- A2. **The live-read engine has two field defects that are not fixed yet.** `state_code.json` session_cvd is 370-400 BTC off the 1m archive. `session.vwap_anchor_utc` reads 13:30Z, but the value fits a 00:00Z anchor (live-read report; card `audit-state-code-cvd-and-vwap-anchor`, still raw). Every live read, and every FAB-* setup that uses session CVD or VWAP, inherits them.
- A3. **Fabio's "holdout FAIL" is a mislabel.** LAYERS.md:60 says "v3 tried 2026-10-04, holdout FAIL". But P2_FABIO_V3_HOLDOUT_STATUS.md (the B147 correction) says the 2026-06-26.. holdout was NOT read for Fabio v3: the FAIL is model C's OOS read, and A, B and D were not evaluable. The holdout is burned for Tom (read twice), not for Fabio. This settles plan item 5, and it matters for the A7 holdout decision.
- A4. **Spot-checks that passed:**
  - SETUP_CATALOG.md: `verify_extract_quotes.py` PASS, 0 problems; TOM-1..16 and FAB-1..8 are present.
  - Malkan SETUP_SUMMARY.md: PASS. The 7-star rule is now in his words (SETUP_SUMMARY.md:538), with no chartink source.
  - gpt-cards: T2/T3 are on astra-low (tasks.py:49-50, per the coordinator's grep).
  - The catalogue labels 26 OURS and 74 NOT STATED, so it follows the SOURCED/OURS rule.
- A5. **Reviewers:**
  - The Haiku live review caught real errors (retrace 102% vs 94%, 1m CVD pixel reads, wrong FAB citations).
  - The GPT audits caught real defects before (B144, profile-shape T2 0.500 vs 0.200; TRACK_RECORD.md "Worked"), but none has returned SOUND, and none has touched the new catalogue yet. T2 is that check.
  - No reviewer covers coordinator-to-operator relays (A1).

### Alignment (gates G0-G6)
| Layer | Gate now | Moving? |
|---|---|---|
| Tom | G2: 16 setups, 26 unread videos read (103b65c3), V1 re-extracts (c5457597) | yes, today |
| Fabio | G1-G2: 8 setups; V2 extracts of 7 of 8 raw transcripts (114b74fc). Plan s3 lists 13 staged and 3 long sessions; coverage against that list is not checked | partly |
| Malkan | G1 for 6 videos, 19 setups (a7ac506a) | yes |
| Krown | G1 done (15/15); G2 not in catalogue format | krown-g2 started |
| Any | G3 (blind marks): 0 marks; `tom-btc-eye-read` claim and release in the same minute (43f0ce7f, 6daa1fbc) | **no: the real bottleneck to any G5 number** |

- Drift: NEXT_SESSION.md (the relay queue) still lists Krown Q66-Q69 detectors, code and backtest. LAYER_REBUILD_PLAN s3 says those "wait until G2-G3". The only thing stopping a Sonnet KICK on Q66 is that Q65 sits on the DSA lane.

### Missed (repeat mistakes)
1. "Shipped" or "merged" stated without `git cherry` (A1; LESSONS s1).
2. Missing-input GPT cards issued again (W2; LAYER_LAB.md:55-58).
3. A known red test with no owner for about 13 h (W1).
4. YouTube 429 again: caption-fetch was rate-limited on every request (local_ce8e2fac). LESSONS s6 caps fetches at about 5 per session.
5. Infra share above research (W3), which STATE_OF_PLAY s4 already named.

### New
- N1. **Fee arithmetic favours higher-timeframe setups.** BTC fees force stops of at least 0.40% taker (STATE_OF_PLAY s4), which can sink Tom's small-stop intraday fades. Malkan's weekly/monthly RSI and Krown's daily setups have stops many times wider, so fees are a small fraction of R. They are cheap to test first, but have fewer events: print the MDE line with the gap-g1 helper (f01208e7).
- N2. **Cross-trader agreement as a prior.** A chart event that 2 or more independent traders describe (krown-g2 overlap table) is a better first G3/G5 candidate than a single-trader row.
- N3. **Live reads as a data-quality probe.** Each set found engine defects (A2; earlier 13 mismatches, screenshot_intake.md:11). The MISMATCH count is the cheapest live-path audit we have.

## Recommendations (ranked by expected value per cost; at most 12)
### Do now (today, cheap)
| # | Change | Who | Evidence | Worked when |
|---|---|---|---|---|
| 1 | Finish the gate fix. Then a standing rule: when 2 sessions report the same failing gate test, the coordinator spawns a Sonnet fixer within the hour. | fix-selftest-gate (running); coordinator owns the rule | W1 | No SHIP_FAILED on the same test twice in a day |
| 2 | Ship the stalled lab tree and park missing-input cards; then T2 (catalogue NOT STATED audit) runs before A3. | lab-unstall (running) | W2 | T2's CATALOG_AUDIT.md is on origin before 10-20 |
| 3 | A "shipped" claim quotes an empty `git cherry origin/fast-track <sha>`. The coordinator checks before telling the operator. Add one line to every brief. | coordinator | A1 | Zero corrections to operator reports |
| 4 | Park Q66-Q69 in NEXT_SESSION.md ("PARKED until Krown G2+G3, LAYER_REBUILD_PLAN s3"). Point the relay queue at plan s6 items only. Turn the hourly NOOP dispatcher session off when the T0 gate already says NOOP. | coordinator (one edit + relay handoff); dispatcher schedule by the session that owns 9fe73003 | Drift, W4 | The dispatcher only KICKs plan items; no NOOP sessions |
| 5 | Fix A2 (session_cvd, VWAP anchor): refine the card, then a Sonnet live-path fix with restart/reset tests. Deploy only via AutoDeploy. | Sonnet builder | A2 | The next live read's engine JSON matches the 1m archive on both fields |
| 6 | Paired blind review for live reads (screenshot_intake 4b, this commit). Coordinator briefs say "follow 4b". | live-read sessions | A5 and the operator's ask | REVIEW has a blind section; same-sha ship; WRONG rate tracked |
| 7 | Correct the Fabio holdout label at the LAYERS.md source ("OOS FAIL model C; holdout unread"). Feed this into the A7 decision. | Haiku (one edit) | A3 | LAYERS.md no longer says "holdout FAIL" |
| 8 | **Gate board, the standing mechanism.** make_status.py prints one line per layer: gate now, proof file, hours since it moved, and "non-gate commits 24h: x%". If no gate moved in 24 h, the coordinator's next spawn must target a gate. | Sonnet (T0 script, about 1 h) | W3, Drift | STATUS.md shows the board; the infra share stays under 30% |

### Decide at the 10-20 Fable A3 audit
| # | Question | Evidence | Input A3 needs |
|---|---|---|---|
| 9 | G3 first: which layer and setups get blind marks. Proposed rule: score = BTC-visible Y x stop CLEAR x number of traders who agree (N2). Then build a phone-friendly marking page for the operator plus one blind second reader. | G3 = 0 marks; tom-btc-event-study BLOCKED twice for no marks | the krown-g2 overlap table, T2 audit |
| 10 | First G5 order: higher-timeframe (Malkan, Krown) before intraday Tom, by fee arithmetic, with a power line (N1) | STATE_OF_PLAY s4-s5 | catalogue stop classes, MDE helper |
| 11 | GPT lane after T2/T3: keep it only if T2 finds at least 1 catalogue error that Claude confirms; otherwise end before the 11-11 trial end | TRACK_RECORD | T2/T3 reports, astra-low token cost |
| 12 | Fabio G1 coverage: are the 13 staged and 3 long sessions all extracted? If not, run a targeted extraction from A3's findings, as plan s6 item 7 says | Fabio row above | A3's list of missing concepts |

## How to tell the whole thing is working (daily, about 5 min, Haiku)
Read the gate board line in STATUS.md, the SHIP_FAILED count (`git log --grep SHIP_FAILED --since=1.day`) and the shots line. The day is on track if one gate moved, there were 0 repeated ship failures, and no operator report needed correcting. If not, the coordinator gets one line naming the stuck gate.
