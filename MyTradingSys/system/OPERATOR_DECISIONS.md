# OPERATOR DECISIONS: repo record of the Control Room questions

The Control Room db holds the live copy (collection `decisions`, one doc per question). This file is the durable copy:
a session that adds a question appends it here; the pickup that applies an answer writes the answer and the note here,
word for word (CONTROL_ROOM.md step 4). Seed a wiped or second db from the JSON blocks below.

## q1-one-control-room | asked 2026-10-13 | Process

Which Control Room page holds your questions and Inbox?

Recommended: This page is the one place
Answer: This page is the one place
Operator note (verbatim): (none)
Applied: 2026-10-13: this page (NUC account) is the one place; already treated so since the answer.

```json
{
 "order": 1,
 "stage": "Process",
 "refs": "artifact registry",
 "title": "Which Control Room page holds your questions and Inbox?",
 "why": "There are two copies of this page, one per Claude account, and each has its own store. An answer typed on one is invisible on the other. That is why this page showed no questions: the old questions and your replies live on the other account's page, which sessions on this machine cannot read. Almost all work now runs on this account (23 of the last 24 session hand-overs). Under your go I am treating THIS page as the one place for questions and Inbox from today, and the other page becomes a view with a link here. Your old replies on the other page are not lost; they need one session on JIS-NB to copy them into the repo.",
 "options": [
  "This page is the one place",
  "The other account's page is the one place",
  "Keep both and copy between them"
 ],
 "recommended": "This page is the one place"
}
```

## q2-jis-nb-dark | asked 2026-10-13 | Live testnet

JIS-NB looks dark: trading halted, live view 23 hours old. Can you open Claude there?

Recommended: I will open Claude on JIS-NB; find the cause, then clear the halt
Answer: I will open Claude on JIS-NB; find the cause, then clear the halt
Operator note (verbatim): 
> Loot at this - 
> 
> Sync to the latest. And uh, see why the loop is down. Make everything tick. The work is mostly going on on Nuke. Check what you have to do on your sides. That is it. Do everything end to end.
> 
> Ran 2 commands
> Many worktrees. Use mts-push (reuse) for work; first update it and run sync start there.
> 
> Ran 7 commands
> Status: the machine rebooted at 10:09 today, so the stack was down overnight and is now back. I’m checking the Java feed and why CI hasn’t run since last night.
> 
> Ran 6 commands
> Cause found: docs-only commits don’t trigger CI (path filter), so the “green” marker never advances and STATUS falsely says RED. I’m fixing that line to ignore commits that touch no gated paths.
> 
> Ran 6 commands
> Q31 is already done (applied 10-12), so I’m moving to Q43, the worktree tidy. It also helps with the C: space complaint.
> 
> Ran 6 commands (1 blocked)
> I’m still on the tidy fix. That command was blocked, so I’ll make the test edit with the Edit tool instead.
> 
> Edited test_sync.py, ran 4 commands (1 blocked)
> Shipped. Next I’ll run a dry run of the tidy to see exactly what it would delete.
> 
> Ran 3 commands
> The loop isn’t down now. It was down overnight because the PC was off, and everything restarted by itself at logon.
> 
> Why it was down
> 
> The PC was off from about 01:53 to 10:26 IST, and the last reboot was 10:09. Per the project’s own rule, the stack stays down while the machine is off and isn’t caught up afterwards.
> The supervisor restarted everything at 10:29. The wrapper, Java feed, auto_trader, live_runner_cli, orderflow_live and daily_loss_monitor are all running.
> Snapshot age is about 30 s and the supervisor log reads “ok”.
> Fixed and shipped
> 
> False “CI RED”:
> STATUS.md was saying CI was red and auto-deploy idle. Nothing had actually failed.
> CI only runs on pushes that touch code paths, so docs-only commits never move the green marker.
> get_ci_line in scripts/dev/make_status.py now ignores docs-only commits, with a new test.
> sync.py tidy: it was keeping about 60 id
Applied: 2026-10-13: queued as card exec-halt-entry-10031 (host=JIS-NB, p1): operator opens Claude on JIS-NB, finds the cause of the 10031 reject, then clears the halt. Not touched from the NUC.

```json
{
 "order": 2,
 "stage": "Live testnet",
 "refs": "exec-halt-entry-10031, live-mirror-stale",
 "title": "JIS-NB looks dark: trading halted, live view 23 hours old. Can you open Claude there?",
 "why": "Testnet trading has been halted since 12 Oct 09:46Z. The exchange rejected one turn-of-candle entry (code 10031, invalid arguments) and the safety rule stopped the whole stack; 9 later signals were skipped, including shorts during the sell-off. Nothing has traded since. The live mirror from JIS-NB was last published 11 Oct 20:09Z, and three task claims from that machine have had no commit for 8 to 30 hours. Only a session on JIS-NB may look at the halt, clear it and publish the mirror; sessions here are not allowed to touch the live stack. What I did: released the 30-hour claim so its task can run here, left the other two, and kept the halt card at top priority for JIS-NB. What I need: the Claude app open on JIS-NB with the relay routine running.",
 "options": [
  "I will open Claude on JIS-NB; find the cause, then clear the halt",
  "Clear the halt first, investigate after",
  "Leave testnet halted until Tom v2 is ready"
 ],
 "recommended": "I will open Claude on JIS-NB; find the cause, then clear the halt"
}
```

## q3-fabio-video-method | asked 2026-10-13 | Fabio

Fabio's videos: keep reading one 250-second window per session?

Recommended: Pre-screen windows with a script, read only those with a trade
Answer: Pre-screen windows with a script, read only those with a trade
Operator note (verbatim): (none)
Applied: 2026-10-13: card fabio-video-prescreen refined to ready (Sonnet, M, p2, any host; NUC has Pillow+opencv). Q3 one-window reads stay stopped until its flagged-window list exists.

```json
{
 "order": 3,
 "stage": "Fabio",
 "refs": "fabio-trade-ledger, Q3/Q18",
 "title": "Fabio's videos: keep reading one 250-second window per session?",
 "why": "In 60 hours there were 32 window reads, one session each. 17 found no trade in the window. Every one of those sessions paid the full start-up cost (about 65 thousand tokens before any work) to report 'flat, no trade'. The ledger still has 8 usable trades against a goal of 20. A cheap first pass can look at the frames for an order ticket or a position line and list only the windows worth reading. What I did under your go: no more one-window sessions are queued until the pre-screen exists.",
 "options": [
  "Pre-screen windows with a script, read only those with a trade",
  "Keep one window per session",
  "Stop reading videos; work with the trades already found"
 ],
 "recommended": "Pre-screen windows with a script, read only those with a trade"
}
```

## q4-fabio-spec-timing | asked 2026-10-13 | Fabio

Write the Fabio v2 spec now, or after his trade ledger is fixed?

Recommended: After the ledger fixes
Answer: After the ledger fixes
Operator note (verbatim): (none)
Applied: 2026-10-13: Fabio spec stays on hold (fabio-layer-v2-spec blocked) until the fabio-ledger-* fixes land.

```json
{
 "order": 4,
 "stage": "Fabio",
 "refs": "fabio-layer-v2-spec, lab-audit-fabio-ledger-frames",
 "title": "Write the Fabio v2 spec now, or after his trade ledger is fixed?",
 "why": "GPT's audit of the Fabio ledger says fix first: 3 high and 4 medium problems (entries not matching the order label, an outcome that does not match the stop, dates assumed, no minute timestamps), and only 8 usable trades. Tom's spec waited for the same kind of repairs, and those repairs changed 76 rows. A spec written on the current ledger would be built on numbers we already know are wrong. What I did under your go: put the Fabio spec on hold. Tom's spec (Opus) is ready and first in the queue, since you named Opus.",
 "options": [
  "After the ledger fixes",
  "Now, on the 8 trades we have",
  "Drop Fabio until Tom v2 has a result"
 ],
 "recommended": "After the ledger fixes"
}
```

## q5-dsa-chat | asked 2026-10-13 | Process

Four run-and-report rows wait for a DSA chat. Will you open one on the NUC?

Recommended: I will open a DSA chat on the NUC
Answer: I will open a DSA chat on the NUC
Operator note (verbatim): 
> Today this was done -
> 
> Sync to the latest. And uh, see why the loop is down. Make everything tick. The work is mostly going on on Nuke. Check what you have to do on your sides. That is it. Do everything end to end.
> 
> Ran 2 commands
> Many worktrees. Use mts-push (reuse) for work; first update it and run sync start there.
> 
> Ran 7 commands
> Status: the machine rebooted at 10:09 today, so the stack was down overnight and is now back. I’m checking the Java feed and why CI hasn’t run since last night.
> 
> Ran 6 commands
> Cause found: docs-only commits don’t trigger CI (path filter), so the “green” marker never advances and STATUS falsely says RED. I’m fixing that line to ignore commits that touch no gated paths.
> 
> Ran 6 commands
> Q31 is already done (applied 10-12), so I’m moving to Q43, the worktree tidy. It also helps with the C: space complaint.
> 
> Ran 6 commands (1 blocked)
> I’m still on the tidy fix. That command was blocked, so I’ll make the test edit with the Edit tool instead.
> 
> Edited test_sync.py, ran 4 commands (1 blocked)
> Shipped. Next I’ll run a dry run of the tidy to see exactly what it would delete.
> 
> Ran 3 commands
> The loop isn’t down now. It was down overnight because the PC was off, and everything restarted by itself at logon.
> 
> Why it was down
> 
> The PC was off from about 01:53 to 10:26 IST, and the last reboot was 10:09. Per the project’s own rule, the stack stays down while the machine is off and isn’t caught up afterwards.
> The supervisor restarted everything at 10:29. The wrapper, Java feed, auto_trader, live_runner_cli, orderflow_live and daily_loss_monitor are all running.
> Snapshot age is about 30 s and the supervisor log reads “ok”.
> Fixed and shipped
> 
> False “CI RED”:
> STATUS.md was saying CI was red and auto-deploy idle. Nothing had actually failed.
> CI only runs on pushes that touch code paths, so docs-only commits never move the green marker.
> get_ci_line in scripts/dev/make_status.py now ignores docs-only commits, with a new test.
> sync.py tidy: it was keeping about
Applied: 2026-10-13: operator will open a DSA chat on the NUC; nothing to do from a builder session. Rows stay posted for DSA.

```json
{
 "order": 5,
 "stage": "Process",
 "refs": "rv-dsa-ledger-mechanical, rv-dsa-q33-rerun, rv-dsa-test-sweep, rv02",
 "title": "Four run-and-report rows wait for a DSA chat. Will you open one on the NUC?",
 "why": "The second-eyes checks you asked for include four rows that need no judgement (re-run tests, re-run the Q33 numbers, check the Tom ledger mechanically, check the DAX harness fixes). They are posted for DSA with the bridge, which is the cheapest way to run them. The DSA worker has no heartbeat: nobody has a DSA chat open with the bridge on this machine. What I did under your go: left them for DSA for 24 hours; after that they move to Sonnet so the checks still happen.",
 "options": [
  "I will open a DSA chat on the NUC",
  "Move them to Sonnet now",
  "Drop the mechanical re-runs"
 ],
 "recommended": "I will open a DSA chat on the NUC"
}
```

## q6-frame-libraries-nuc | asked 2026-10-13 | Process

Install the image libraries on JIS-NUC so frame work can run here?

Recommended: Yes, install Pillow and opencv-python on JIS-NUC
Answer: Yes, install Pillow and opencv-python on JIS-NUC
Operator note (verbatim): In future do not ask such question s- just download
Applied: 2026-10-13: Pillow 12.3.0 and opencv-python 5.0.0 installed on JIS-NUC. Standing rule from the note: package installs for operator-approved work are done, not asked.

```json
{
 "order": 6,
 "stage": "Process",
 "refs": "Q29, rv01, rv05, fabio-ledger-minute-timestamps",
 "title": "Install the image libraries on JIS-NUC so frame work can run here?",
 "why": "The videos and frame sheets are on this machine's F: drive, but its Python cannot open or cut an image (no Pillow, no OpenCV, no ffmpeg). So every task that needs a frame waits for JIS-NB, which is dark: Fabio minute timestamps, the frame pass of the Tom ledger check, the Fabio frame pass. Installing two Python packages (Pillow and opencv-python) on JIS-NUC would let the primary machine do this work. I have NOT done this: installing software needs your word.",
 "options": [
  "Yes, install Pillow and opencv-python on JIS-NUC",
  "No, keep frame work on JIS-NB only"
 ],
 "recommended": "Yes, install Pillow and opencv-python on JIS-NUC"
}
```

## q7-delete-stale-pages | asked 2026-10-13 | Process

Delete the stale pages so each app shows one clean list?

Recommended: Delete all six pages and the leftover branch
Answer: Delete all six pages and the leftover branch
Operator note (verbatim): Deleted all sx
Applied: 2026-10-13: the six pages are already gone from the account list (operator deleted them). Branch shots-inbox/2026-10-12-1532 NOT deleted: its two CoinGlass PNGs are not in the repo or the screenshot store (shot.py ingest failed: store path resolves wrong on this git). Kept until they are landed.

```json
{
 "order": 7,
 "stage": "Process",
 "refs": "system/artifacts/registry.json",
 "title": "Delete the stale pages so each app shows one clean list?",
 "why": "On this account: 'CBP Dashboard' is a one-off snapshot from 7 Oct, replaced by CBP Desk and CBP Consensus Desk, and there are five old unpinned pages from 5 and 6 Oct (Binance Perp Backtesting Guide, MTS Field Guide, MTS Research Follow-through Audit, MTS Research Agenda, BACKTEST_PIPELINE). The registry in the repo already lists which page is the real one for each purpose. Deleting a page cannot be undone and breaks its link, so I have NOT done it. Also for your word: the leftover git branch shots-inbox/2026-10-12-1532 (delete once its screenshots are confirmed in the store).",
 "options": [
  "Delete all six pages and the leftover branch",
  "Unpin CBP Dashboard only, keep everything",
  "Keep as is"
 ],
 "recommended": "Delete all six pages and the leftover branch"
}
```

## q8-cross-guidance | asked 2026-10-13 | Layers

Tom/Fabio cross-guidance: run a second matrix with trader-style exits?

Recommended: No second matrix; revisit after the v2 specs
Answer: No second matrix; revisit after the v2 specs
Operator note (verbatim): (none)
Applied: 2026-10-13: closed; no second matrix. Revisit after the v2 specs.

```json
{
 "order": 8,
 "stage": "Layers",
 "refs": "Q33, Q34, MATRIX_REPORT.md",
 "title": "Tom/Fabio cross-guidance: run a second matrix with trader-style exits?",
 "why": "The first matrix tested 336 combinations of trigger and context on BTC with a fixed holding time and fees. None survived (best result +0.039 %, far from significant). A second run with exits closer to how the traders manage is possible, but it would again test the old encodings on BTC, which the road map says to stop until the v2 specs exist. What I did under your go: closed it. No wiring between layers, no second matrix.",
 "options": [
  "No second matrix; revisit after the v2 specs",
  "Run the second matrix now"
 ],
 "recommended": "No second matrix; revisit after the v2 specs"
}
```

## q9-republish-rule | asked 2026-10-13 | Process

Pages are republished at the end of every session that shipped something. OK?

Recommended: Yes, every session that shipped
Answer: Yes, every session that shipped
Operator note (verbatim): (none)
Applied: 2026-10-13: rule stands; this session republishes the Control Room at hand-over.

```json
{
 "order": 9,
 "stage": "Process",
 "refs": "CLAUDE.md, artifacts.py",
 "title": "Pages are republished at the end of every session that shipped something. OK?",
 "why": "You said every page must be updated after every build. The rule is now in the session instructions: at hand-over a session rebuilds the Control Room and the Layer Map from the repo and republishes them over the same link when their content changed (a rebuild costs no tokens; a republish is one step). CBP pages are built by the CBP routine, not by MTS sessions, so they follow the CBP schedule. Pages on the other account update only when a session runs on that account.",
 "options": [
  "Yes, every session that shipped",
  "Only once a day",
  "Only when I ask"
 ],
 "recommended": "Yes, every session that shipped"
}
```

## q-pub-trend-holdout | asked 2026-10-13 | Research

Spend the sealed 2025-07..2026-09 BTC holdout once on the short-lookback trend family (30-100 d)?

Recommended: Yes, once, one pooled pre-registered hypothesis
Answer: Yes, once, one pooled pre-registered hypothesis (Control Room db, 2026-10-14/15)
Operator note (verbatim): (none)
Applied: 2026-10-15 card pooled-short-lookback-trend-tsmom-30d-sm noted: pre-register one pooled hypothesis (gate 0a-0f), then read the 2025-07..2026-09 holdout once. Not run in this pickup.

```json
{
 "order": 2,
 "stage": "Research",
 "refs": "research/published_strats_2026-10-13/RESULTS.md, volume report A7",
 "title": "Spend the sealed 2025-07..2026-09 BTC holdout once on the short-lookback trend family (30-100 d)?",
 "why": "62 published rules were tested at 0.10 % per side plus funding; none survived correction on 2021-01..2023-06. Short-lookback trend (TSMOM 30 d, price above SMA50/100) leans positive (Sharpe about 0.5, uncorrected p about 0.13) and is the only family worth a single look. The sealed holdout is the only clean data left for BTC, so it should be used once, on one pooled rule, or not at all.",
 "options": [
  "Yes, once, one pooled pre-registered hypothesis",
  "No, keep it sealed for Tom or Fabio",
  "Fetch ETH first and test there"
 ],
 "recommended": "Yes, once, one pooled pre-registered hypothesis"
}
```

## q10-tom-v2-after-design-fail | asked 2026-10-13 | Tom v2

Tom v2 failed its first test on DAX. What next?

Recommended: Add the profile arm, then re-run recall as a new trial
Answer: Add the profile arm, then re-run recall as a new trial
Operator note (verbatim): (none)
Applied: 2026-10-13 (JIS-NUC): answered 14:27Z. Card tom-profile-shape-parity is now lane CODEX kind build (GPT luna lab, Pillow on JIS-NUC); then tom-encode-fade-profile-proofs, then recall re-run as a NEW trial row. k=0 not adopted; Tom v2 not parked.


## q11-fdax-orderflow-recall | asked 2026-10-13 | Tom v2

Buy Eurex FDAX trade data with aggressor side (buyer or seller crossed the spread) for Tom's 7 ledger sessions plus seeded random days, to test whether his named order-flow proofs mark his entries?

Recommended: Yes, buy the 7 sessions + seeded controls; run before the CFD profile arm
Answer: No FDAX data. Apply Tom's core idea on BTC charts and BTC data with our own judgement (operator chat 2026-10-13; none of the four options fits word for word: it is not "park Tom")
Operator note (verbatim): "I agree with you! I just have a feeling that orde-flow trading is real and Tom is not lying. 'Tom has never passed that test' yes because we have never applied Tom correctly.  We do not need tp prove anything abt Tom here. Orderflow is real and works on all markets." ... "so let us apply the core idea on the chart and uh, see how it needs to be adjusted in order to make profitable trades. Focus on that"
Applied: 2026-10-13 (cloud, flow-audit session): plan research/tom_btc_2026-10-13/TOM_ON_BTC.md; DAX-only Tom cards held (tasks.py apply-op hold, note q11); Tom-on-BTC cards tom-btc-* created.

```json
{
 "order": 3,
 "stage": "Research",
 "refs": "research/tom_dax_what_is_proven_2026-10-13/REPORT.md; backtest/dax_data.py:100-106; tom_transfer_2026-10-11/RECALL_DAX_V2.md:24-31",
 "title": "Buy FDAX aggressor-side trade data to test Tom's order-flow proofs at his entries?",
 "why": "Every DAX test so far ran on CFD candles where delta is forced to 0, so Tom's own proofs (footprint absorption, delta surplus; k0zm5NYn0IQ_raw.txt:19) could never fire. Recall with the idea alone was 4 of 5 (random 0.3 %) but the idea fires on 46 % of days; at 1+ proof it fell to 2 of 5 (random 15.7 %). Real FDAX order flow is the one input missing that Tom says picks his entries. PASS (>= 4 of 5 sessions within one stop-width, random <= 5 %, both check sessions hold) funds the full FDAX P&L run; FAIL parks the coded Tom layer as discretionary.",
 "options": [
  "Yes, buy the 7 sessions + seeded controls; run before the CFD profile arm",
  "Yes, but after the CFD profile arm (q10) finishes",
  "No, park Tom as discretionary now",
  "No, keep the current CFD-only plan"
 ],
 "recommended": "Yes, buy the 7 sessions + seeded controls; run before the CFD profile arm"
}
```

Audit note (2026-10-14, supersedes the 2026-10-13 flow-audit recommendation to park Tom): operator direction is that Tom's ideas are tested on BTC and no DAX/FDAX data is bought. Nothing is parked; see q11 Applied line above.


## q12-requeue-crypto-first | asked 2026-10-13 | Process | NO AUTO-APPLY

Re-order the queue: crypto-native sources first?

Recommended: Qriptal scoring (B162) and cryptocred-home-fit-audit to priority 1; pause the Tom v2 and Fabio v2 home-market chains
Answer: Qriptal scoring (B162) and cryptocred-home-fit-audit to priority 1; pause the Tom v2 and Fabio v2 home-market chains (Control Room db, 2026-10-14/15)
Operator note (verbatim): (none)
Applied: 2026-10-15 cryptocred-home-fit-audit p4 -> p1 (qriptal-score-binance already p1); paused at p5: fabio-layer-v2-markets, fabio-layer-v2-spec, tom-v2-btc-min-stop-width, tom-v2-dax-dev-backtest (done Tom v2 cards untouched).

```json
{
 "order": 4,
 "stage": "Process",
 "refs": "research/mts_flow_audit_2026-10-13/REPORT.md section 5",
 "title": "Re-order the queue: crypto-native sources first?",
 "why": "Audit d2. The audit found the crypto-native sources (Qriptal posts entry, stop and target; CryptoCred is BTC) sit at the back of the queue while a machine-translated DAX trader is priority 1. Qriptal needs only free Binance candles. DIRECTION CHANGE: needs Jis's explicit answer; must NOT auto-apply after 24h.",
 "options": [
  "Qriptal scoring (B162) and cryptocred-home-fit-audit to priority 1; pause the Tom v2 and Fabio v2 home-market chains",
  "Keep the current order",
  "Qriptal and CryptoCred first, but let the running Tom v2 cards finish"
 ],
 "recommended": "Qriptal scoring (B162) and cryptocred-home-fit-audit to priority 1; pause the Tom v2 and Fabio v2 home-market chains",
 "no_auto_apply": true
}
```


## q13-six-line-gate | asked 2026-10-13 | Process | NO AUTO-APPLY

Adopt the six-line pre-build gate as items 0a-0f of PRE_REG_TEMPLATE?

Recommended: Yes
Answer: Yes (Control Room db, 2026-10-14/15)
Operator note (verbatim): be flexible
Applied: 2026-10-15 items 0a-0f added ahead of item 1 in backtest/PRE_REG_TEMPLATE.md; "be flexible": a "no" stops the build unless the pre-registration states why it is waived.

```json
{
 "order": 4,
 "stage": "Process",
 "refs": "research/mts_flow_audit_2026-10-13/REPORT.md section 5",
 "title": "Adopt the six-line pre-build gate as items 0a-0f of PRE_REG_TEMPLATE?",
 "why": "Audit d3. Six questions answered before anything is built (is the track record verified, do we have the data he reads, do fees allow his stop, and so on); see REPORT.md section 3. DIRECTION CHANGE: needs Jis's explicit answer; must NOT auto-apply after 24h.",
 "options": [
  "Yes",
  "No",
  "Yes, but as advice, not a gate"
 ],
 "recommended": "Yes",
 "no_auto_apply": true
}
```


## q14-doctrine-tom-core | asked 2026-10-13 | Process | NO AUTO-APPLY

Doctrine: your 09-23 'Tom is core' vs the 10-10 'promotion to core uses the S3 bar, never opinion'

Recommended: Let S3 decide what is core
Answer: No fixed core: remove "Tom is core" and the hard layer rules; flexible system (operator chat 2026-10-13)
Operator note (verbatim): "WRT “Tom is core, non-negotiable” - It was a long time ago when we started - now it makes no sense to have anything like this. We need flexible system now that can adapt to whatever change we need to bring. So we have to remove all those uh, hard rules about layers and everything."
Applied: 2026-10-14 JIS-NB on Jis's OK in chat ("Yes - go ahead from me - do not be afraid to change what makes sense to change!"), commit "rules rewrite q14 applied" (script deleted after use). Was: rule text staged 2026-10-13: scripts/dev/staged/apply_rules_2026_10_13.py, task system/cli_tasks/2026-10-13_rules_rewrite.md. The cloud session could not apply it (its permission check blocks edits to agent instruction files); a local session runs it on Jis's OK.

```json
{
 "order": 4,
 "stage": "Process",
 "refs": "research/mts_flow_audit_2026-10-13/REPORT.md section 5",
 "title": "Doctrine: your 09-23 'Tom is core' vs the 10-10 'promotion to core uses the S3 bar, never opinion'",
 "why": "Audit d4. The two rules contradict each other and Tom has never passed S3. Changing the doctrine is the operator's edit only (VISION change rule), so a session will not edit it from this answer alone. DIRECTION CHANGE: needs Jis's explicit answer; must NOT auto-apply after 24h.",
 "options": [
  "Let S3 decide what is core",
  "Keep Tom core by decree",
  "Decide per layer later"
 ],
 "recommended": "Let S3 decide what is core",
 "no_auto_apply": true
}
```


## q15-merge-translation-postmortem | asked 2026-10-13 | Process | NO AUTO-APPLY

Merge TRANSLATION_POSTMORTEM_2026-10-12.md into fast-track?

Recommended: Yes
Answer: Yes (Control Room db, 2026-10-14/15)
Operator note (verbatim): (none)
Applied: 2026-10-15 research/TRANSLATION_POSTMORTEM_2026-10-12.md taken from origin/claude/sharp-carson-3xkd36 (commit 45fa300e) into fast-track.

```json
{
 "order": 4,
 "stage": "Process",
 "refs": "research/mts_flow_audit_2026-10-13/REPORT.md section 5",
 "title": "Merge TRANSLATION_POSTMORTEM_2026-10-12.md into fast-track?",
 "why": "Audit d5. It is the only review that carries the simulator-validation list. DIRECTION CHANGE: needs Jis's explicit answer; must NOT auto-apply after 24h.",
 "options": [
  "Yes",
  "No, leave it on its branch"
 ],
 "recommended": "Yes",
 "no_auto_apply": true
}
```


## q16-simulator-validation-card | asked 2026-10-13 | Process | NO AUTO-APPLY

File the simulator-validation card: planted edge in tom_bt/sim, a null that includes fees, a trade-list diff?

Recommended: Yes
Answer: Yes (Control Room db, 2026-10-14/15)
Operator note (verbatim): (none)
Applied: 2026-10-15 card simulator-validation-planted-edge filed (raw) for the refiner.

```json
{
 "order": 4,
 "stage": "Process",
 "refs": "research/mts_flow_audit_2026-10-13/REPORT.md section 5",
 "title": "File the simulator-validation card: planted edge in tom_bt/sim, a null that includes fees, a trade-list diff?",
 "why": "Audit d6. None of the backtest engines has been shown to find a planted edge, so every FAIL so far is unvalidated. DIRECTION CHANGE: needs Jis's explicit answer; must NOT auto-apply after 24h.",
 "options": [
  "Yes",
  "No"
 ],
 "recommended": "Yes",
 "no_auto_apply": true
}
```


## q17-simplify-operations | asked 2026-10-13 | Process | NO AUTO-APPLY

Simplify how MTS runs: apply proposals P1-P5 in system/HOW_MTS_RUNS.md (one account per job, one machine starts sessions, one work list, bookkeeping out of git history, three pages)?

Recommended: Yes, all five
Answer: Yes, all five (Control Room db, 2026-10-14/15)
Operator note (verbatim): I will add one more a/c in future. I need flexibility to run any a/c on any machine. 
Applied: 2026-10-15 HOW_MTS_RUNS.md proposals marked adopted with the operator note: P1/P2 are defaults, not locks (any account runs on any machine, a third account is expected). Cards filed for P3, P4, P5 and P1-P2 config (raw, for the refiner); nothing structural changed in this pickup.

```json
{
 "order": 5,
 "stage": "Process",
 "refs": "system/HOW_MTS_RUNS.md section 'Proposals to make it simpler'",
 "title": "Simplify how MTS runs: apply P1-P5 (one account per job, one machine starts sessions, one work list, bookkeeping out of git, three pages)?",
 "why": "Operator 2026-10-13: 'my head is actually spinning the project is growing uh, too big for me to handle it'. Work sits in five lists, hand-over runs three ways, two accounts take one queue, and about 44 % of 1,246 commits since 10-01 are bookkeeping. DIRECTION CHANGE: needs Jis's explicit answer; must NOT auto-apply after 24h.",
 "options": [
  "Yes, all five",
  "Yes, but only the ones I name in the note",
  "Not now"
 ],
 "recommended": "Yes, all five",
 "no_auto_apply": true
}
```

## q-gap-a-underpowered-fail | asked 2026-10-14 | Research

Is an underpowered FAIL on the DAX dev run INCONCLUSIVE (sample extended) instead of final STOP?

Recommended: Keep the frozen bar, add an MDE line
Answer: Keep the frozen bar, add an MDE line (Control Room db, 2026-10-14/15)
Operator note (verbatim): (none)
Applied: 2026-10-15 no change to the stop rule; the frozen bar stays. power_mde.py (card gap-g1-power-mde-helper, done) prints the MDE line.

```json
{
 "order": 10,
 "stage": "Research",
 "refs": "research/backtest_gap_review_2026-10-13/REPORT.md",
 "title": "Is an underpowered FAIL on the DAX dev run INCONCLUSIVE (sample extended) instead of final STOP?",
 "why": "REPORT.md G1: at Tom's own numbers the frozen bar has 7-35 % power at 100-150 trades, so a FAIL is mostly a miss. Changing the stop rule is a protocol change, so the default keeps the bar and only prints the MDE (card gap-g1-power-mde-helper).",
 "options": [
  "Keep the frozen bar, add an MDE line",
  "Yes: INCONCLUSIVE when power at the claimed edge < 80 %, extend the sample"
 ],
 "recommended": "Keep the frozen bar, add an MDE line"
}
```
## q-gap-b-go-live-shadow-fills | asked 2026-10-14 | Research

Should GO_LIVE_BAR count shadow fills from the real tape instead of testnet fills?

Recommended: No change, report both
Answer: No change, report both (Control Room db, 2026-10-14/15)
Operator note (verbatim): (none)
Applied: 2026-10-15 GO_LIVE_BAR unchanged; card gap-g3-shadow-fills reports shadow-fill and testnet numbers side by side.

```json
{
 "order": 11,
 "stage": "Research",
 "refs": "research/backtest_gap_review_2026-10-13/REPORT.md",
 "title": "Should GO_LIVE_BAR count shadow fills from the real tape instead of testnet fills?",
 "why": "REPORT.md G3: Deribit says testnet liquidity is synthetic (support article could not be opened from the NUC, so this stays a search snippet). Changing the go-live bar is yours; default leaves it and reports both numbers (card gap-g3-shadow-fills).",
 "options": [
  "No change, report both",
  "Yes: shadow fills decide, testnet is a plumbing check"
 ],
 "recommended": "No change, report both"
}
```
## q-gap-c-deribit-public-mainnet | asked 2026-10-14 | Research

May sessions read Deribit public mainnet candles (no account) for a venue-parity check?

Recommended: No
Answer: Yes, public market data only (Control Room db, 2026-10-14/15)
Operator note (verbatim): What is this check and why it is needed? i do not know why this exists ->  'never mainnet' is a standing rule, so default is No. -  do what makes sence to achive your goals. we will do trading on mainnet so what is the confusion?
Applied: 2026-10-15 CLAUDE.md testnet rule now allows public mainnet market data (no account, no orders); card gap-g8-deribit-parity unblocked. Why the check exists: backtests use Binance prices, execution is Deribit, so parity tells whether Binance results transfer.

```json
{
 "order": 12,
 "stage": "Research",
 "refs": "research/backtest_gap_review_2026-10-13/REPORT.md",
 "title": "May sessions read Deribit public mainnet candles (no account) for a venue-parity check?",
 "why": "REPORT.md G8: backtests use Binance prices, execution is Deribit. A parity check needs BTC-PERPETUAL 1m candles from the public endpoint. 'Never mainnet' is a standing rule, so the default is No (card gap-g8-deribit-parity).",
 "options": [
  "No",
  "Yes, public market data only"
 ],
 "recommended": "No"
}
```
## q-krown-captions | asked 2026-10-14 | Research

How do we get the captions for the 4 unextracted Krown TA 101 videos?

Recommended: Retry once a day for 3 days, then ask me
Answer: Retry once a day for 3 days, then ask me (2026-10-15)
Operator note (verbatim): Queue the Krown/Malkan caption fetch and the Malkan extraction of the two on-disk transcripts.
Applied: 2026-10-15 card krown-ta101-extract-remaining-10 set ready (no cookies)

```json
{
 "order": 13,
 "stage": "Research",
 "refs": "research/krown_ta101_2026-10-13/STATE.md",
 "title": "How do we get the captions for the 4 unextracted Krown TA 101 videos?",
 "why": "YouTube returned HTTP 429 to JIS-NUC on 2026-10-13 and, for 4 of 11 videos, to JIS-NB on 2026-10-14 (the other 7 came through and are extracted). Rules say stop on a bot check, no workarounds. The 4 missing are about top-down method order, chart patterns, building a system and beginners adding indicators (card krown-ta101-extract-remaining-10, STATE.md).",
 "options": [
  "Retry once a day for 3 days, then ask me",
  "I will paste the 4 transcripts",
  "Skip them: build on the 14 TA videos"
 ],
 "recommended": "Retry once a day for 3 days, then ask me"
}
```
## q-krown-saturation | asked 2026-10-14 | Research

Waive the 20-video saturation gate for a descriptive Krown layer?

Recommended: Yes: detectors and a DEV study only, no engine setup file
Answer: Yes: detectors and a DEV study only, no engine setup file
Operator note (verbatim): (none)
Applied: 2026-10-17: waiver recorded. Cards krown-layer-v0-detectors and krown-recall-check unparked (state raw, the refiner re-scopes them) and krown-dev-event-study follows them. Scope stays descriptive detectors, recall and a DEV event study; no engine setup file, nothing reaches the engine or live without you. q-pause-krown-detectors no longer holds these cards.

```json
{
 "order": 14,
 "stage": "Research",
 "refs": "research/krown_ta101_2026-10-13/STATE.md",
 "title": "Waive the 20-video saturation gate for a descriptive Krown layer?",
 "why": "extraction.md SAFEGUARD 3 wants 20 videos and 5 consecutive saturated extractions before a setup file is built. Only 19 videos are reachable (14 TA extracted so far, and the last 5 extractions still added whole new rule families). The waiver covers descriptive detectors, recall and a DEV event study; nothing reaches the engine or live without you.",
 "options": [
  "Yes: detectors and a DEV study only, no engine setup file",
  "No: wait for more Krown content"
 ],
 "recommended": "Yes: detectors and a DEV study only, no engine setup file",
 "answer": "Yes: detectors and a DEV study only, no engine setup file"
}
```
## q-krown-stop | asked 2026-10-14 | Research

May any live Krown use run without a resting protective stop (his style)?

Recommended: No: a protective stop always; his close-based exit is a backtest arm only
Answer: Yes, on the testnet only
Operator note (verbatim): (none)
Applied: 2026-10-17: recorded. A Krown use on the testnet may run without a resting protective stop (his close-based exit, KR-X01); the house rule (protective stop on every position) stays for anything beyond the testnet. No Krown layer is in the engine yet, so no code changed; the detector and event-study cards carry the close-based exit as a testnet arm.

```json
{
 "order": 15,
 "stage": "Research",
 "refs": "research/krown_ta101_2026-10-13/STATE.md",
 "title": "May any live Krown use run without a resting protective stop (his style)?",
 "why": "He says he does not like stop losses and exits himself when a zone breaks on a close (KR-X01). MTS rules require a protective stop on every live position. The default keeps the house rule (conflict C3 in KROWN_CONSOLIDATED.md).",
 "options": [
  "No: a protective stop always; his close-based exit is a backtest arm only",
  "Yes, on the testnet only"
 ],
 "recommended": "No: a protective stop always; his close-based exit is a backtest arm only",
 "answer": "Yes, on the testnet only"
}
```
## q-krown-volume-venue | asked 2026-10-14 | Research

Which volume series counts for Krown's volume rules?

Recommended: Test both: Binance and Coinbase daily volume
Answer: Test both: Binance and Coinbase daily volume
Operator note (verbatim): Include CME
Applied: 2026-10-17: Binance and Coinbase BTC-USD daily are already on F: (krown-data-daily-majors, done). CME added as a third arm: card krown-data-cme-btc-volume (DSA, public data only, NOT AVAILABLE if no free source).

```json
{
 "order": 16,
 "stage": "Research",
 "refs": "research/krown_ta101_2026-10-13/STATE.md",
 "title": "Which volume series counts for Krown's volume rules?",
 "why": "He says crypto volume can be faked and reads Coinbase, the TradingView index or CME. Our data is Binance. Coinbase BTC-USD daily candles are public market data (no account, no trading). Card krown-data-daily-majors fetches them only if you agree (conflict C6).",
 "options": [
  "Test both: Binance and Coinbase daily volume",
  "Binance only"
 ],
 "recommended": "Test both: Binance and Coinbase daily volume",
 "answer": "Test both: Binance and Coinbase daily volume"
}
```
## q-host-worktree-tidy | asked 2026-10-15 | Process | NO AUTO-APPLY

Remove 39 finished worktrees on JIS-NB (about 750 MB) and repair 23 broken ones?

Recommended: Yes: fix tidy's idle clock, protect mts-control-room, remove the 39 finished trees, repair the 23 broken HEADs
Answer: Yes (chat 2026-10-15: "clean everything, do not leave anything behind")
Operator note (verbatim): Commit all your changes and clean everything. Do not leave anything behind.
Applied: 2026-10-15 on JIS-NB: 23 broken HEADs repaired, 34 finished trees retired by tidy, 30 more swept with copies in F:/MTS_backup.git (LEFTOVERS_2026-10-15.md)
Page db: not yet a doc (asked from the jishusharma1985 login, which cannot write the jishu.awgp db); the next jishu.awgp pickup creates it from the JSON below. Apply on JIS-NB only.

```json
{
 "order": 17,
 "stage": "Process",
 "refs": "system/HOST_WORKTREES_2026-10-15.md",
 "title": "Remove 39 finished worktrees on JIS-NB (about 750 MB) and repair 23 broken ones?",
 "why": "`sync.py tidy --all` (dry run, 2026-10-15) checked 101 worktrees on JIS-NB and would remove only 2. A git cleanup at 03:07 today rewrote every tree's history file, so tidy thinks 32 more finished trees were used 5 h ago; they are clean, fully on origin and idle 32-140 h (18 old relay trees, 13 App trees, mts-sup). 5 App trees with a detached HEAD are clean with nothing unshipped. 23 trees are broken: HEAD names jis-nb/x but the branch is JIS-NB/x, so git shows every file as new; after a one-line repair 17 of them are clean and shipped. Kept whatever you answer: 12 trees with uncommitted work, 8 with unshipped commits (incl. BinanceDataFeed.registry, which MTS-Live-Health runs from), 14 used in the last 24 h, 4 named lanes, and mts-control-room (the mts-control-room routine works there). The tree-by-tree list is in the refs file.",
 "options": [
  "Yes: fix tidy's idle clock, protect mts-control-room, remove the 39 finished trees, repair the 23 broken HEADs",
  "Only the 2 trees tidy removes today",
  "Not now"
 ],
 "recommended": "Yes: fix tidy's idle clock, protect mts-control-room, remove the 39 finished trees, repair the 23 broken HEADs"
}
```
## q-host-sched-tasks | asked 2026-10-15 | Process | NO AUTO-APPLY

Retire 4 legacy Windows tasks on JIS-NB and re-point MTS-Live-Health?

Recommended: Yes: disable Tick and both Audit tasks (unregister after 7 quiet days), unregister Monitor_4h, point Live-Health at the live tree, fix MTS-Backup
Answer: Yes: disable Tick and both Audit tasks (unregister after 7 quiet days), unregister Monitor_4h, point Live-Health at the live tree, fix MTS-Backup
Operator note (verbatim): remove comnpletely - no mure schedulars in any device - no routines - we have super sessions now.. they run for the drfined timelines.. 
Applied: (not yet; waits for Jis's explicit answer, no 24h default)
Page db: not yet a doc (asked from the jishusharma1985 login, which cannot write the jishu.awgp db); the next jishu.awgp pickup creates it from the JSON below. Apply on JIS-NB only.

```json
{
 "order": 18,
 "stage": "Process",
 "refs": "system/HOST_TASKS_2026-10.md",
 "title": "Retire 4 legacy Windows tasks on JIS-NB and re-point MTS-Live-Health?",
 "why": "21 MTS tasks run on JIS-NB. MTS-Scheduler-Tick still runs the old tick.py clock every 15 min; only the retired NUC worker read its reports. MTS_Monitor_4h points at a script that no longer exists. MTS-Audit-Digest and MTS-Audit-Rotation were built for the NUC Qwen queue retired on 2026-10-01. MTS-Live-Health runs its checker from BinanceDataFeed.registry, a checkout 1621 commits behind (the checker file itself is current). MTS-Backup failed at 08:22 (exit 1). Nothing was changed or unregistered.",
 "options": [
  "Yes: disable Tick and both Audit tasks (unregister after 7 quiet days), unregister Monitor_4h, point Live-Health at the live tree, fix MTS-Backup",
  "Only unregister MTS_Monitor_4h",
  "Not now"
 ],
 "recommended": "Yes: disable Tick and both Audit tasks (unregister after 7 quiet days), unregister Monitor_4h, point Live-Health at the live tree, fix MTS-Backup",
 "answer": "Yes: disable Tick and both Audit tasks (unregister after 7 quiet days), unregister Monitor_4h, point Live-Health at the live tree, fix MTS-Backup"
}
```

## q-context-baseline | asked 2026-10-15 | Process

Switch off the add-ons MTS sessions never use?

Recommended: Yes, switch them off on all three logins
Answer: Yes, switch them off on all three logins
Operator note (verbatim): (none)
Applied: 2026-10-17: decided. The four switches in CONTEXT_BASELINE.md (computer use, Claude in Chrome, Claude Docs and visualize connectors, 9 file skills) are app settings that only you can change, once per login; then run token_audit.py --days 7 to re-measure.

```json
{
 "order": 19,
 "stage": "Process",
 "refs": "system/CONTEXT_BASELINE.md",
 "title": "Switch off the add-ons MTS sessions never use?",
 "why": "Every MTS session starts at about 65k tokens before reading a file (median of 160 Sonnet sessions, 7 days, JIS-NB). About 5.9k of that describes add-ons no MTS session used in those 7 days: computer use, Claude in Chrome, the Claude Docs and visualize connectors, and 9 file-format skills (docx, pptx, xlsx, pdf ...). Switched off, every turn of every session is about 9% lighter. Nothing is deleted and each one switches back on with the same click. The built-in browser stays (YouTube trader videos). Clicks: CONTEXT_BASELINE.md.",
 "options": [
  "Yes, switch them off on all three logins",
  "Only computer use and Claude in Chrome",
  "No, keep everything"
 ],
 "recommended": "Yes, switch them off on all three logins",
 "answer": "Yes, switch them off on all three logins"
}
```

## q20-persistent-worktrees | asked 2026-10-15 | Process

One long-lived worktree per machine/lane, a branch per task?

Recommended: Yes, adopt it
Answer: Yes, adopt it (chat 2026-10-15)
Operator note (verbatim): decide as per the goals of the task from where this question originates (no stale trees left behind, lower cost, same performance)
Applied: 2026-10-15 sync.py start <slug> in a lane tree (mts-app/mts-relay/mts-dsa) switches to <host>/<slug>; claims block only on overlapping --area; SHORT SESSIONS 10 operator / 40 tool turns (CLAUDE.md, turn_meter.py, RELAY.md); tidy keeps mts-app; PARALLEL.md

```json
{
 "order": 20,
 "stage": "Process",
 "refs": "system/PARALLEL.md, scripts/dev/stop_guard.py",
 "title": "One long-lived worktree per machine/lane, a branch per task?",
 "why": "26 stale worktrees piled up on JIS-NB because every session makes its own tree and ends before shipping. Data is already safe: the MTS-Backup task snapshots every tree every 15 min to the private F:/MTS_backup.git. The cause is still one tree per session. Proposal: one persistent worktree per machine and lane (JIS-NB: app, relay, dsa; NUC: relay), a fresh branch per task inside it (sync.py start <slug> switches to host/<slug> off origin/fast-track), claims only when the claimed areas overlap with an open claim (health already reports overlaps), and the session cap raised from 5 operator / 15 tool turns to 10 / 40 for one task. CLAUDE.md rules 'work only in the printed WORKTREE' and 'SHORT SESSIONS' would change; nothing is changed until you answer.",
 "options": [
  "Yes, adopt it",
  "Only the longer session cap",
  "No, keep one tree per session"
 ],
 "recommended": "Yes, adopt it",
 "answer": "Yes, adopt it"
}
```

## q21-artifacts-on-sharma | asked 2026-10-15 | Process

Which login owns the Control Room page and its Inbox/decisions database?

Recommended: jishu.sharma (the account with the GitHub identity)
Answer: jishu.sharma (chat 2026-10-15)
Operator note (verbatim): there is no 1 place for me to record decisons? i need all artifacts to be associated with the jishu.sharma a/c - it is the main a/c that has my GitHub.
Operator 2026-10-15 (chat): do not wait for or copy answers still in the jishu.awgp db; seed from the repo only, ask later if something was missed.
Applied: 2026-10-15 (JIS-NUC, session signed in as jishu.sharma@gmail.com): no move was needed. Artifact list on this login shows it already owns
the Control Room Ep6gA5 (and the other pages the repo filed under jishu.awgp), and it cannot read EoHi2q: the repo had the two logins' names swapped.
Ep6gA5 stays the one Control Room (a new page would split the Inbox again). Its db was seeded from the repo only: the 11 decisions and 1 Inbox item
in OPERATOR_DECISIONS.md / OPERATOR_INBOX.md that it lacked were added; nothing was overwritten or deleted. Registry keys, CONTROL_ROOM.md,
CLOUD_ACCOUNTS.md, HOW_MTS_RUNS.md, ACCOUNT_SYNC.md, INSTALL.md and mts-control-room.SKILL.md now name jishu.sharma. q1-one-control-room is superseded.
Closed 2026-10-15: the 9 answers were copied and applied (Control Room pickup, JIS-NUC).

```json
{
 "order": 21,
 "stage": "Process",
 "refs": "system/CONTROL_ROOM.md, system/artifacts/registry.json, system/CLOUD_ACCOUNTS.md",
 "title": "Control Room, Inbox and decisions on the jishu.sharma account",
 "why": "Operator 2026-10-15: one place for decisions, and every artifact under jishu.sharma. A session cannot move a page between logins or read another login's page or db, so the move is: a session signed in as jishu.sharma (1) runs artifacts.py build, (2) publishes the Control Room with capabilities db + user to the jishu.sharma url (or a new url), (3) seeds decisions/<id> from OPERATOR_DECISIONS.md json blocks and feedback/<id> from OPERATOR_INBOX.md, answers included, (4) updates registry.json, CONTROL_ROOM.md, CLOUD_ACCOUNTS.md and HOW_MTS_RUNS.md, republishes the other pages under jishu.sharma, and the jishu.awgp and jishusharma1985 pages become read-only copies or are retired by the operator. The repo files are the durable record; answers still in the old jishu.awgp db that are not in OPERATOR_DECISIONS.md must be copied over first by a session on that login.",
 "options": [
  "jishu.sharma",
  "Keep jishu.awgp"
 ],
 "recommended": "jishu.sharma",
 "answer": "jishu.sharma"
}
```
## q-pause-krown-detectors | asked 2026-10-15 | Research

Pause the Krown detector queue (NEXT_SESSION Q65-Q69) until Krown setups pass G2 and G3?

Recommended: Yes: park Q65-Q69 until G2-G3
Answer: Yes: park Q65-Q69 until G2-G3 (decided by coordinator on operator's behalf 2026-10-15 per operator rule 'decide toward goals'; reopens when krown-g2 catalogue rows pass G3)
Operator note (verbatim): (none: coordinator decision under the operator's standing rule)
Applied: 2026-10-15 observer commit: NEXT_SESSION.md PARKED block; cards krown-data-daily-majors, krown-layer-v0-detectors, krown-recall-check on hold.
Page db: not yet a doc; the next Control Room pickup creates it from the JSON below.

```json
{
 "order": 22,
 "stage": "Research",
 "refs": "research/layer_rebuild_2026-10-15/LAYER_REBUILD_PLAN_2026-10-15.md s3",
 "title": "Pause the Krown detector queue (NEXT_SESSION Q65-Q69) until Krown setups pass G2 and G3?",
 "why": "The claude-side audit (research/layer_lab/reports/2026-10-15_claude-side-audit.md, question 2) asked whether to pause the Krown detector queue Q65-Q69. LAYER_REBUILD_PLAN_2026-10-15 s3 says no detectors or backtests before a setup passes G2 and G3; Krown is G1 with its G2 catalogue in progress (krown-g2).",
 "options": [
  "Yes: park Q65-Q69 until G2-G3",
  "No: keep building Krown detectors now"
 ],
 "recommended": "Yes: park Q65-Q69 until G2-G3"
}
```

## q-fabio-asr-d2 | asked 2026-10-16 | Research

Speech-to-text on Fabio's two long uncaptioned sessions (Is1HvdfQm5c 2.5 h, xUyqIjCfZzg 3.8 h)?

Recommended: NO for now (Fable 5.1 default D2, research/fable_audit_2026-10-16/CATALOGUE_AUDIT.md s6: frames-only cards stay parked)
Answer: YES: local open-source transcriber on JIS-NB, low priority, then extract both (operator 2026-10-16; flips D2)
Operator note (verbatim): Yes: install a local open-source transcriber on JIS-NB, run it at low priority on Fabio's two long sessions (Is1HvdfQm5c, xUyqIjCfZzg), and extract them.
Applied: 2026-10-16 session fabio-transcribe: faster-whisper small.en in a venv outside the repo (F:/MTS/tools/asr-venv), BELOW_NORMAL, 4 threads, one video at a time. DECISION (OURS) model = small.en: medium.en beam 5 projects to 11.0 h for the 6.29 h of audio (> the 8 h gate), medium.en greedy is faster but drops speech. Figures and limits: research/fabio_asr_2026-10-16/ASR_RUN.md. Extraction and card updates follow in the same session (research/fabio_asr_2026-10-16/ASR_RUN.md s5 lists the shipped result).

```json
{
 "order": 23,
 "stage": "Research",
 "refs": "research/fabio_asr_2026-10-16/ASR_RUN.md, research/fable_audit_2026-10-16/CATALOGUE_AUDIT.md s6 D2",
 "title": "Speech-to-text on Fabio's two long uncaptioned sessions (Is1HvdfQm5c 2.5 h, xUyqIjCfZzg 3.8 h)?",
 "why": "Both videos were downloaded video-only (f398), so they had no words at all: Fable's catalogue audit (D2) left them frames-only because a local transcription run was not available. The operator approved a local open-source transcriber on JIS-NB at low priority. Result: machine transcripts (ASR, small.en) in raw_transcripts_canonical, fresh single-video extractions, and catalogue rows or quotes for Fabio's setups.",
 "options": [
  "YES: local open-source transcriber on JIS-NB, low priority, then extract both",
  "NO for now: keep them frames-only"
 ],
 "recommended": "NO for now: keep them frames-only",
 "answer": "YES: local open-source transcriber on JIS-NB, low priority, then extract both"
}
```

## D3-dev-ext | asked 2026-10-16 | Research

Add 2020-2021 BTCUSDT 1m data to DEV as a separate DEV_EXT segment so single context factors become testable?

Recommended: Yes, as a separate segment read only by DEV-stage work
Answer: Yes, as a separate segment read only by DEV-stage work (DECISION (OURS), operator may overrule)
Operator note (verbatim): (none; free public market data is pre-approved, defaults chosen without asking)
Applied: 2026-10-16 session d3-dev-ext. DECISION (OURS): segment DEV_EXT = Binance USD-M BTCUSDT 1m klines, bar open 2020-01-01 .. 2021-12-31 (731 days, 1,052,640 minutes, 24 monthly zips, SHA256 matches the .CHECKSUM files, 0 duplicate minutes, 0 gaps, all UTC-aligned, OHLC sane). The REPORT.md D3 proposal said 2019-09; the public perp 1m archive starts 2019-12-31 (daily) and 2020-01 (monthly), so 2019 is NOT filled, and 2019 spot is NOT mixed in (different venue, basis). Stored outside the repo: F:/MTS/data/dev_ext_2019_2021/ (klines, funding, zips). DEV (2022-01-01..2024-06-30), VALIDATION (2024-07-01..2025-06-30) and HOLDOUT are unchanged. Loader: research/context_factors_2026-10-16/dev_ext.py, OFF unless include_dev_ext=True, never returns a bar at/after 2024-07-01 (test_dev_ext.py). Only DEV-stage reads may use it. Counts: research/context_factors_2026-10-16/COUNTS_DEV_EXT.md.

```json
{
 "order": 24,
 "stage": "Research",
 "refs": "research/context_factors_2026-10-16/REPORT.md D3, research/context_factors_2026-10-16/COUNTS_DEV_EXT.md",
 "title": "Add 2020-2021 BTCUSDT 1m data to DEV as a separate DEV_EXT segment so single context factors become testable?",
 "why": "The context-factors study found only the composite is powered on 821 DEV days. Free public Binance USD-M data for 2020-2021 adds 731 days. It is kept as its own segment (DEV_EXT) that only DEV-stage reads may use, so VALIDATION and HOLDOUT are never touched.",
 "options": [
  "Yes, as a separate segment read only by DEV-stage work",
  "No: keep DEV at 2022-01-01 .. 2024-06-30"
 ],
 "recommended": "Yes, as a separate segment read only by DEV-stage work",
 "answer": "Yes, as a separate segment read only by DEV-stage work (DECISION (OURS), operator may overrule)"
}
```

## D6-two-context-engines | asked 2026-10-16 | Research

Two independent context-factor engines exist (Opus and Fable, same prompt). Adopt day units + Holm + the realised-MDE rule for the Fable study and run its cross-engine agreement count before any outcome read?

Recommended: Yes: PRE_REG_V2 (day units, m = 59, realised-MDE rule), audit card first, cross-engine count first, then one read of the 14 cells
Answer: Yes: PRE_REG_V2 (day units, m = 59, realised-MDE rule), audit card first, cross-engine count first, then one read of the 14 cells (DECISION (OURS), operator may overrule)
Operator note (verbatim): (none; routine research default, logged without asking)
Applied: 2026-10-16 Fable session context-factors: PRE_REG_V2.md written, card context-factors-one-run rescoped to it, card context-factors-pit-audit added, queue Q87/Q88.

```json
{
 "order": 25,
 "stage": "Research",
 "refs": "research/context_factors_pit_2026-10-16/COMPARISON.md, research/context_factors_pit_2026-10-16/PRE_REG_V2.md, research/context_factors_2026-10-16/REPORT.md D4",
 "title": "Two independent context-factor engines exist (Opus and Fable, same prompt). Adopt day units + Holm + the realised-MDE rule for the Fable study and run its cross-engine agreement count before any outcome read?",
 "why": "The same prompt ran twice on 2026-10-16 (research/context_factors_2026-10-16 on Opus, research/context_factors_pit_2026-10-16 on Fable). Their PRE_REGs count power in different units (days vs episodes), so the Fable claim '9 of 14 cells powered' becomes '4 of 14' under the trunk's day convention (Opus D4, both AUDIT_BEFORE_RUN files). Two conventions in VERDICTS.csv would make verdict words incomparable. The comparison itself is new evidence: factors where the two engines disagree (band veto 2 % vs 26 % of events, phase object, ladder width) are definition-fragile and any verdict on them is a verdict on the definition. Defaults taken in the Fable study, now logged: W = 2.5 % of price, target 1.5 R, PRIOR_RULE last_closed, K_ZONE 0.5 x ATR14(4h), plausible 0.15 R for a cost-free filter contrast. Also logged here because it was never recorded: Opus D4 (units = distinct UTC days, Holm) is applied de facto by both audits.",
 "options": [
  "Yes: PRE_REG_V2 (day units, m = 59, realised-MDE rule), audit card first, cross-engine count first, then one read of the 14 cells",
  "No: run the Fable PRE_REG.md as written (episode units, 9 of 14 cells)",
  "Park the Fable card; keep only the Opus composite chain"
 ],
 "recommended": "Yes: PRE_REG_V2 (day units, m = 59, realised-MDE rule), audit card first, cross-engine count first, then one read of the 14 cells",
 "answer": "Yes: PRE_REG_V2 (day units, m = 59, realised-MDE rule), audit card first, cross-engine count first, then one read of the 14 cells (DECISION (OURS), operator may overrule)"
}
```

## D7-context-opus-defaults | asked 2026-10-17 | Research

Log the five operator decisions of the Opus context-factors REPORT (D1-D5) with the default each one took?

Recommended: Yes: D1 ran, D2 walk veto kept, D3 applied, D4 days + Holm, D5 no flag
Answer: Yes: D1 ran, D2 walk veto kept, D3 applied, D4 days + Holm, D5 no flag (DECISION (OURS), operator may overrule)
Operator note (verbatim): (none; operator 2026-10-17: "do everything end to end ... do not wait for any further input")
Applied: 2026-10-17 session context-compare-close. D1: card context-composite-dev-read ran once (RESULT.md: INCONCLUSIVE, 241 of 1,010 C events matched, 164 days < 387). D2: the 1h band-walk veto stays in the frozen composite; the operator's 'dance' reading (any close at/below the lower band in the last 2 bars) is a variant only, and COMPARISON.md shows the veto is definition-fragile (2 % of Opus events, 26 % of Fable short episodes). D3: applied 2026-10-16 (D3-dev-ext). D4: every PRE_REG counts power in distinct UTC days with Holm-adjusted z (already enforced by both AUDIT_BEFORE_RUN files and by D6). D5: no 'undone by the partial candle' flag until a candle factor gets a powered test.

```json
{
 "order": 26,
 "stage": "Research",
 "refs": "research/context_factors_2026-10-16/REPORT.md s.4, research/context_factors_2026-10-16/RESULT.md, research/context_factors_pit_2026-10-16/COMPARISON.md s.3 and s.5",
 "title": "Log the five operator decisions of the Opus context-factors REPORT (D1-D5) with the default each one took?",
 "why": "The Opus REPORT listed D1-D5 with defaults, but only D3 reached this log; COMPARISON.md s.5 found D1, D2, D4 and D5 recorded nowhere but the REPORT. A default that is not logged is a habit, not a record, so the next study cannot cite it.",
 "options": [
  "Yes: D1 ran, D2 walk veto kept, D3 applied, D4 days + Holm, D5 no flag",
  "No: leave them in REPORT.md only"
 ],
 "recommended": "Yes: D1 ran, D2 walk veto kept, D3 applied, D4 days + Holm, D5 no flag",
 "answer": "Yes: D1 ran, D2 walk veto kept, D3 applied, D4 days + Holm, D5 no flag (DECISION (OURS), operator may overrule)"
}
```

## D8-context-composite-hold | asked 2026-10-17 | Research

Hold card context-composite-v2-dev-read, since under its audit's two fixes the only reachable verdict is INCONCLUSIVE?

Recommended: Yes: hold the card; the composite stays INCONCLUSIVE on DEV; no further composite read until new data or a new design
Answer: Yes: hold the card; the composite stays INCONCLUSIVE on DEV; no further composite read until new data or a new design (DECISION (OURS), operator may overrule)
Operator note (verbatim): (none; operator 2026-10-17: "do everything end to end ... do not wait for any further input")
Applied: 2026-10-17 session context-compare-close: card state blocked (tasks.py apply-op hold), NEXT_SESSION Q86 updated, counts in research/context_factors_2026-10-16/counts_v3.py and REPORT.md s.6.

```json
{
 "order": 27,
 "stage": "Research",
 "refs": "research/context_factors_2026-10-16/AUDIT_BEFORE_RUN.md items 1-2, layer_lab/context_fix1_stop_strata and context_fix2_mde_rule PRE_REG_V3_ADDENDUM_DRAFT.md, research/context_factors_2026-10-16/counts_v3.py, REPORT.md s.6",
 "title": "Hold card context-composite-v2-dev-read, since under its audit's two fixes the only reachable verdict is INCONCLUSIVE?",
 "why": "Counts only, no outcome read. PASS cannot happen: PRE_REG_V2 keeps the gate 'mean net_R of C > 0' and V1 already printed -0.137 R on the same 1,010 trades. FAIL cannot happen: the audit fix forbids FAIL when C and control stops differ by > 25 % relative; the matched V2 controls have median stop 1.560 % vs C 2.086 % (long, 25.2 %) and 1.670 vs 2.165 % (short, 22.9 %), the pool medians 22.5 % / 25.1 % (fix-1 draft), so the bound is crossed on one side either way. Matching controls on stop width (each within 1/1.25 .. 1.25 x the C stop) makes the R units comparable (gap 4.7 % / 6.5 %) but leaves 241 matched events on 165 days, below the 393-day gate. So every DEV design tried so far returns INCONCLUSIVE, and running the card spends an M card for a known word.",
 "options": [
  "Yes: hold the card; the composite stays INCONCLUSIVE on DEV; no further composite read until new data or a new design",
  "No: run PRE_REG_V2 as written (audit said FIX-FIRST)",
  "Assemble PRE_REG_V3 from the two drafts and run it (expected word: INCONCLUSIVE)"
 ],
 "recommended": "Yes: hold the card; the composite stays INCONCLUSIVE on DEV; no further composite read until new data or a new design",
 "answer": "Yes: hold the card; the composite stays INCONCLUSIVE on DEV; no further composite read until new data or a new design (DECISION (OURS), operator may overrule)"
}
```

## blind-monitor-halt-recovery | asked 2026-10-17 | Process

Blind-monitor HALT_DAILY_LOSS on testnet: may the monitor clear its own blind halt?

Recommended: Monitor clears only its own blind halt after the account reads cleanly for 30 minutes
Answer: Monitor clears only its own blind halt after the account reads cleanly for 30 minutes
Operator note (verbatim): For now - see what should be done for future - the correct impellentatin and then adopt that pilicy 
Applied: 2026-10-17: 30 minutes is the interim rule. A session designs the correct long-term rule from the halt history (3 blind halts in 7 days), then adopts it, tests first; a real daily-loss halt is never auto-cleared and mainnet stays fail-closed. Builders still never touch HALT files by hand.

```json
{
 "order": 28,
 "stage": "Process",
 "refs": "blind-monitor-halt-recovery",
 "title": "Blind-monitor HALT_DAILY_LOSS on testnet: may the monitor clear its own blind halt?",
 "why": "Three blind halts in 7 days (10-06 Deribit 502, 10-07, 10-12; 20 consecutive read failures, last HTTP 502). Testnet only. A real daily-loss halt is never auto-cleared and mainnet stays fail-closed.",
 "options": [
  "Monitor clears only its own blind halt after the account reads cleanly for 30 minutes",
  "Monitor clears it after 10 minutes of clean reads",
  "I clear every one myself (no auto-recovery)"
 ],
 "recommended": "Monitor clears only its own blind halt after the account reads cleanly for 30 minutes",
 "answer": "Monitor clears only its own blind halt after the account reads cleanly for 30 minutes"
}
```

## q-sched-scope | asked 2026-10-17 | Process | NO AUTO-APPLY

Your note on q-host-sched-tasks said "no more schedulers in any device, no routines, super sessions now". How far does that go?

Recommended: Remove the legacy tasks now; keep AutoDeploy, Supervisor and the dispatcher until a super-session replacement for each is built and tested
Answer: Remove every scheduled task on every device now (deploys, revival and the relay stop until super sessions cover them)
Operator note (verbatim): "q-sched-scope: remove every scheduled task on every device now, accepting that deploys, revival and the relay stop."
Applied: 2026-10-17: JIS-NUC: MTS-CodexLab, MTS-DailyHygiene, MTS-DispatchGate unregistered (XML backups in F:/MTS/backups/sched_tasks_2026-10-17_NUC; re-register with Register-ScheduledTask -Xml); MTS-NUC-Worker is disabled and refused deletion (access denied), left disabled. JIS-NB: card host-legacy-tasks-unregister widened to every MTS task there (export first). Stopped by this: auto-deploy, process revival, relay dispatch, the Codex lab runner.

```json
{
 "order": 29,
 "stage": "Process",
 "refs": "system/HOST_TASKS_2026-10.md, q-host-sched-tasks",
 "title": "How far does 'no more schedulers' go?",
 "why": "Four legacy tasks go now (Tick, Audit-Digest, Audit-Rotation, Monitor_4h). The rest are not legacy: AutoDeploy is the only thing that changes the live tree, the Supervisor revives dead processes, the dispatcher starts the next relay session, Live-Health and Backup watch and save the live system. Removing them with nothing in their place stops deploys, revival and backups.",
 "options": [
  "Remove the legacy tasks now; keep AutoDeploy, Supervisor and the dispatcher until a super-session replacement for each is built and tested",
  "Remove the legacy tasks and Live-Health and Backup too; keep only AutoDeploy, Supervisor and the dispatcher",
  "Remove every scheduled task on every device now (deploys, revival and the relay stop until super sessions cover them)"
 ],
 "recommended": "Remove the legacy tasks now; keep AutoDeploy, Supervisor and the dispatcher until a super-session replacement for each is built and tested",
 "answer": "Remove every scheduled task on every device now (deploys, revival and the relay stop until super sessions cover them)"
}
```

## q-pit-power-gate | asked 2026-10-17 | Research

Q76 PIT price-level study (pit-prior-va-failed-auction-dev): overrule the power gate and run underpowered, or keep it BLOCKED?

Recommended: Keep BLOCKED; get the data from a trusted source first
Answer: Get the data from a trusted source where it can be had; if it cannot, keep it blocked or remove it, so it does not come back. Other sessions work on it.
Operator note (verbatim): "This is also a data related question. It must also be answered in the same way. Uh, get the data from where you can get it, the source that you can trust. And if you cannot do it, then uh, keep it blocked, or better to remove it, so that uh, you do not uh, come back here. We need to close things." Then: "We do not need to do anything right now. Just record my decision and uh, let other sessions work on it."
Applied: 2026-10-17: recorded only. No overrule written; the card stays BLOCKED (BLOCKED.md). Data path for other sessions: data.binance.vision serves the monthly BTCUSDT 1m klines and aggTrades zips (HTTP 200 for 2021-01 when checked 2026-10-17). Public market data only, no account. If no trusted source closes the gap, remove the card and B187 instead of re-asking.

```json
{
 "order": 30,
 "stage": "Research",
 "refs": "research/pit_levels_2026-10-16/BLOCKED.md, research/pit_levels_2026-10-16/PRE_REG_V2.md, research/BUGS.md B187, research/pit_levels_2026-10-16/bug_b187_evidence.txt",
 "title": "Q76 PIT power gate: overrule and run underpowered, or keep it BLOCKED?",
 "why": "The PIT study fails its frozen power gate: MDE plus cost 0.411 R against a plausible 0.30 R, and 662 feasible DEV days against 2,427 needed. Only a written overrule lets it run. The operator asked for trusted data first, and if none closes the gap, to keep it blocked or remove it so it does not come back.",
 "options": [
  "Get the data from a trusted source where it can be had; if it cannot, keep it blocked or remove it. Other sessions work on it.",
  "Overrule the plausible effect and run it underpowered",
  "Keep BLOCKED with no further data work"
 ],
 "recommended": "Keep BLOCKED; get the data from a trusted source first",
 "answer": "Get the data from a trusted source where it can be had; if it cannot, keep it blocked or remove it, so it does not come back. Other sessions work on it.",
 "no_auto_apply": true
}
```

## q-v1-gate-tiers | asked 2026-10-20 | Process

Local ship gate by path: none for docs, targeted tests for code, quick gate for the live path? (research/v1_plan_2026-10-20/D10_OPERATOR_STYLE_TUNING.md)

Recommended: Docs/research/cards/pages: no local gate (CI is the gate); code outside the live path: targeted tests only, 240 s cap; live path: quick gate unchanged; lint and doc caps only on files in the diff
Answer: Docs/research/cards/pages: no local gate (CI is the gate); code outside the live path: targeted tests only, 240 s cap; live path: quick gate unchanged; lint and doc caps only on files in the diff
Operator note (verbatim): "Yes: apply q-v1-gate-tiers, q-v1-claims-off-git and q-v1-turn-caps with their defaults. File the S0 card for gate tiers in gate_select and sync.py with tests that fail on old code."
Applied: 2026-10-20: recorded; card gate-tiers-by-path filed (SONNET, prio 1) for gate_select.py, run_all_tests.py, sync.py with tests that fail on the old code. No code changed by this pickup.

```json
{
 "order": 31,
 "stage": "Process",
 "refs": "research/v1_plan_2026-10-20/D10_OPERATOR_STYLE_TUNING.md, q-v1-gate-tiers",
 "title": "Local ship gate by path: none for docs, targeted tests for code, quick gate for the live path",
 "why": "Measured 2026-10-20: a docs-only ship took 17, 17 and 39 min; step 4t (targeted pytest) 870-2150 s on tests that never read the changed files; card lint 2 min on a change with no card. CI runs the full suite behind every push and green/fast-track is the deploy pointer, so the local gate duplicates CI everywhere except the live path.",
 "options": [
  "Keep the gate as it is",
  "Docs/research/cards/pages: no local gate (CI is the gate); code outside the live path: targeted tests only, 240 s cap; live path: quick gate unchanged; lint and doc caps only on files in the diff"
 ],
 "recommended": "Docs/research/cards/pages: no local gate (CI is the gate); code outside the live path: targeted tests only, 240 s cap; live path: quick gate unchanged; lint and doc caps only on files in the diff",
 "answer": "Docs/research/cards/pages: no local gate (CI is the gate); code outside the live path: targeted tests only, 240 s cap; live path: quick gate unchanged; lint and doc caps only on files in the diff"
}
```

## q-v1-claims-off-git | asked 2026-10-20 | Process

Claims leave trunk: side branch or skipped for new-file work; one ship per task enforced? (research/v1_plan_2026-10-20/D10_OPERATOR_STYLE_TUNING.md)

Recommended: Claims on a side branch (B17 mechanism) or skipped for new-file work (B16); no claim or release commit on trunk; a second ship from the same tree within 10 min is refused
Answer: Claims on a side branch (B17 mechanism) or skipped for new-file work (B16); no claim or release commit on trunk; a second ship from the same tree within 10 min is refused
Operator note (verbatim): "Yes: apply q-v1-gate-tiers, q-v1-claims-off-git and q-v1-turn-caps with their defaults. File the S0 card for gate tiers in gate_select and sync.py with tests that fail on old code."
Applied: 2026-10-20: recorded; implemented by the same card gate-tiers-by-path (sync.py part).

```json
{
 "order": 32,
 "stage": "Process",
 "refs": "research/v1_plan_2026-10-20/D10_OPERATOR_STYLE_TUNING.md, q-v1-claims-off-git",
 "title": "Claims leave trunk: side branch or skipped for new-file work; one ship per task enforced",
 "why": "3,772 trunk commits since 2026-10-13: claim 538 (14 %), release 477 (13 %), merge 1,239 (33 %). Claim and release commits race every ship into a merge commit. The lane heartbeat already lives on a side branch (TRAFFIC_BUSTERS B17).",
 "options": [
  "Keep claims on trunk",
  "Claims on a side branch (B17 mechanism) or skipped for new-file work (B16); no claim or release commit on trunk; a second ship from the same tree within 10 min is refused"
 ],
 "recommended": "Claims on a side branch (B17 mechanism) or skipped for new-file work (B16); no claim or release commit on trunk; a second ship from the same tree within 10 min is refused",
 "answer": "Claims on a side branch (B17 mechanism) or skipped for new-file work (B16); no claim or release commit on trunk; a second ship from the same tree within 10 min is refused"
}
```

## q-v1-turn-caps | asked 2026-10-20 | Process

Turn caps apply to unattended workers only? (research/v1_plan_2026-10-20/D10_OPERATOR_STYLE_TUNING.md)

Recommended: Caps for unattended workers only; a session the operator is driving ends on his word
Answer: Caps for unattended workers only; a session the operator is driving ends on his word
Operator note (verbatim): "Yes: apply q-v1-gate-tiers, q-v1-claims-off-git and q-v1-turn-caps with their defaults. File the S0 card for gate tiers in gate_select and sync.py with tests that fail on old code."
Applied: 2026-10-20: WORKERS.md rule 5 and CLAUDE.md step 5 say so; turn_meter.py unchanged (its message already allows "unless the operator said to keep going here").

```json
{
 "order": 33,
 "stage": "Process",
 "refs": "research/v1_plan_2026-10-20/D10_OPERATOR_STYLE_TUNING.md, q-v1-turn-caps",
 "title": "Turn caps apply to unattended workers only",
 "why": "The turn meter nagged an operator-driven session 10 times while the operator was giving instructions. Caps exist to bound unattended cost; the operator bounds his own session.",
 "options": [
  "Caps for every session",
  "Caps for unattended workers only; a session the operator is driving ends on his word"
 ],
 "recommended": "Caps for unattended workers only; a session the operator is driving ends on his word",
 "answer": "Caps for unattended workers only; a session the operator is driving ends on his word"
}
```

## q-go-private-on-edge | asked 2026-10-22 | Process

When does the public repo go private? (Admin_Guy chat 2026-10-22; repo public since 2026-10-11, CLAUDE.md "go private before mainnet")

Recommended: Go private when the first layer passes its fee-net out-of-sample gate (a promoted setup), not only before mainnet; a check notifies the operator at that threshold
Answer: Go private when the first layer passes its fee-net out-of-sample gate (a promoted setup), not only before mainnet; a check notifies the operator at that threshold
Operator note (verbatim): "Why don't you put word about this MTS files? So that when we have some edge, there is a hook that triggers a threshold when I am notified that okay, maybe it's time to go private. So going private is not a problem, we were actually just not sure what to do. And I also agree with you that some strategies are worth protecting, because they stop working if enough people know about it."
Applied: 2026-10-22: CLAUDE.md hard rule names both triggers; card go-private-trigger-notify-operator-when- (SONNET, raw) builds the notification with a fail-first test. Going private stays the operator's own action.

```json
{
 "order": 34,
 "stage": "Process",
 "refs": "CLAUDE.md Hard rules (Repo is PUBLIC), MyTradingSys/execution/promoted_setups.json, q-go-private-on-edge",
 "title": "Go private when the first layer shows an out-of-sample edge; notify the operator",
 "why": "A strategy stops working once enough people trade it. Today no layer has an edge (promoted_setups.json has 0 entries, 2026-10-21), so public costs little; the day one passes, its rules and parameters are in the open.",
 "options": [
  "Go private only before mainnet",
  "Go private when the first layer passes its fee-net out-of-sample gate (a promoted setup), not only before mainnet; a check notifies the operator at that threshold"
 ],
 "recommended": "Go private when the first layer passes its fee-net out-of-sample gate (a promoted setup), not only before mainnet; a check notifies the operator at that threshold",
 "answer": "Go private when the first layer passes its fee-net out-of-sample gate (a promoted setup), not only before mainnet; a check notifies the operator at that threshold"
}
```

## q-ci-speed-fixes | asked 2026-10-22 | Process

Build the CI speed fixes from CI_SPEED_DIAGNOSIS_2026-10-22.md items 1 and 2? (Admin_Guy chat 2026-10-22)

Recommended: Build CI speed fix 1 (one CI run per commit, green pointer only moves forward) and fix 2 version 1 (Windows tests split into parallel shards, same tests)
Answer: Build CI speed fix 1 (one CI run per commit, green pointer only moves forward) and fix 2 version 1 (Windows tests split into parallel shards, same tests)
Operator note (verbatim): "What do you mean fixes number 1 and number 2 are still waiting on my board? I am waiting for these fixes to be available already"
Applied: 2026-10-22: cards ci-one-run-per-commit-on-fast-track-gree and ci-split-the-windows-test-leg-into-paral (SONNET, prio 1, raw). Fix 2 version 2 (Linux-only full gate) was not asked for and stays off.

```json
{
 "order": 35,
 "stage": "Process",
 "refs": "MyTradingSys/system/CI_SPEED_DIAGNOSIS_2026-10-22.md items 1-2, .github/workflows/ci.yml:28-32, q-ci-speed-fixes",
 "title": "Build CI speed fixes 1 and 2 (version 1)",
 "why": "Push-to-green measured 25 min with 11 min queued behind another run; the Windows leg takes 11-13 min against under 3 on Linux.",
 "options": [
  "Leave CI as it is",
  "Build CI speed fix 1 (one CI run per commit, green pointer only moves forward) and fix 2 version 1 (Windows tests split into parallel shards, same tests)"
 ],
 "recommended": "Build CI speed fix 1 (one CI run per commit, green pointer only moves forward) and fix 2 version 1 (Windows tests split into parallel shards, same tests)",
 "answer": "Build CI speed fix 1 (one CI run per commit, green pointer only moves forward) and fix 2 version 1 (Windows tests split into parallel shards, same tests)"
}
```

## q-no-permission-endings | asked 2026-10-22 | Process

May a session end its reply by asking the operator's leave ("say go", "want me to?") for work it can do? (Admin_Guy chat 2026-10-22)

Recommended: A Stop hook blocks replies that end by asking the operator's leave for work; sessions do the work, the operator stops them if wrong
Answer: A Stop hook blocks replies that end by asking the operator's leave for work; sessions do the work, the operator stops them if wrong
Operator note (verbatim): "There must be a hook which says that never ask such a question as if you say go and you know, you should just go and do it and if I see that you are doing something which you should not, then I will stop you. At least the work will not be lost."
Applied: 2026-10-22: scripts/dev/offer_guard.py (Stop hook, .claude/settings.json) with scripts/dev/test_offer_guard.py; OPERATOR-ONLY: lines stay allowed for real operator decisions.

```json
{
 "order": 36,
 "stage": "Process",
 "refs": "scripts/dev/offer_guard.py, q-no-permission-endings",
 "title": "No permission questions at the end of a reply: do the work",
 "why": "The operator drives three devices and does not read every reply; a closing question leaves the work undone and it is lost in the chat (CI speed fixes 1-2 sat as 'say go' with no card, 2026-10-22).",
 "options": [
  "Sessions may close with an offer or a go/no-go question",
  "A Stop hook blocks replies that end by asking the operator's leave for work; sessions do the work, the operator stops them if wrong"
 ],
 "recommended": "A Stop hook blocks replies that end by asking the operator's leave for work; sessions do the work, the operator stops them if wrong",
 "answer": "A Stop hook blocks replies that end by asking the operator's leave for work; sessions do the work, the operator stops them if wrong"
}
```

## q-light-supervisor-start (2026-10-22, Admin_Guy)
```json
{"id": "q-light-supervisor-start", "order": 37, "date": "2026-10-22", "status": "DECIDED",
 "quote": "just open all three logins ... and just hit a prompt there, start the super session. Yeah. And the super session starts with minimum workers. It picks the recently available tasks ... it actually picks the critical tasks that are blockers if there are no instructions ... So it starts a light super session, and then the operator can build on it.",
 "also": "every session that I start, starts latest.",
 "done": "supervisor.py RAMP=1 (one new worker per wake); trunk_lag.py session-start also fast-forwards fresh App worktrees and the main checkout."}
```

## q-ci-speed-build (2026-10-22, Admin_Guy)
```json
{"id": "q-ci-speed-build", "order": 38, "date": "2026-10-22", "status": "DECIDED",
 "quote": "Can you finish this task end-to-end? You have like 11 dollars left.",
 "context": "after 'tell me cool idea to reduce our ship time by half or maybe half of half?'",
 "done": "per-commit CI + forward-only mark-green; Windows leg in 3 shards; Windows temp on D: and Defender real-time off on the runner (CI_SPEED_DIAGNOSIS_2026-10-22.md)."}
```

## q-ci-under-2-min (2026-10-23 IST, Admin_Guy)
```json
{"id": "q-ci-under-2-min", "order": 39, "date": "2026-10-22", "status": "DECIDED",
 "quote": "I want everything to be under 2 minutes.",
 "context": "after the 3-shard CI went green in 5m50s push-to-green (run 39833754926 on 788790ff)",
 "done": "CI in 11 shards (Linux 3, Windows 8), file-list steps split per file, Java only on shard 1, uv installs, Defender off in the background, mark-green via the API without a checkout. Local: every shard 10-53 s. CI wall not yet measured (CI_SPEED_DIAGNOSIS_2026-10-22.md)."}
```

## d-six-slots-poll | decided 2026-10-23 | Thinker
```json
{"id": "d-six-slots-poll", "order": 40, "date": "2026-10-23", "status": "DECIDED",
 "question": "How can we utilize all 6 slots? ... constant communication between all our logins ... polling.",
 "options": {"A": "actionable wake: supervisor.py wait also exits when the last plan left a worker slot and ready cards unused (CI green, a gate free); the RAMP lifts when every gate is idle",
             "B": "a model poll every 5 min per Supervisor (~540k eq tokens/h each)",
             "C": "revive idle machines: the lane owner prints one OPERATOR line to start a Supervisor on a machine with no heartbeat, ready cards and budget",
             "D": "do nothing: gates are spare capacity, RAMP 1 per 50 min wake"},
 "recommended": "A + C",
 "answer": "go with A + C - do it here",
 "done": "supervisor.py: wait --login ACTIONABLE wake (once per plan, fail closed, off after 2 plans that started nothing), idle_hosts OPERATOR line (once per machine per 2 h). The gates-idle ramp lift was dropped after review (no gate busy = no worker mid-ship, not an idle machine): the 5 min wake does the speed-up. Plan: research/thinker/2026-10-22_six_slots.md"}
```

## DECISION NEEDED 2026-10-21 (Lab_Guy): pre_pipeline_sources review_by 2026-10-23
27 grandfathered testnet sources in auto_trader_config.json expire for review on 2026-10-23; promoted_setups.json has 0 entries. Options: (a) extend review_by 14 days (recommended, OURS default), (b) prune falsified layers (turn_of_candle, rsi_divergence, session_levels), (c) stop them. Needs an operator answer in the Control Room; no chat question.

## d-cbp-a2-end-to-end | decided 2026-10-23 | Thinker
```json
{"id": "d-cbp-a2-end-to-end", "order": 41, "date": "2026-10-23", "status": "DECIDED",
 "question": "CBP integration: A (new Extraction Core), A2 (adopt existing MTS tools) or C (do nothing)?",
 "options": {"A": "new shared Extraction Core module", "A2": "one quote checker, one fetcher, one store, actionable-6 profile, consumer proves one acked row", "C": "do nothing"},
 "recommended": "A2",
 "answer": "process earthing end to end - make sure that you do not bloat your context past 250k so better use 1 time spawned agents and plan scoped tasks. (read as: process everything end to end; dictation)",
 "done": "pending: cards cbp-one-quote-checker plus the three below, each run by its own scoped session. DEFAULT (OURS): q-v1-cbp-routine stays unanswered (stopping the Haiku routine is the operator's call). Plan: research/thinker/2026-10-23_cbp_core_vs_adopt.md"}
```

## d-supervisor-stay-to-window | decided 2026-10-23 | Thinker
```json
{"id": "d-supervisor-stay-to-window", "order": 42, "date": "2026-10-23", "status": "DECIDED",
 "question": "Supervisor C ended at 2239Z (mode=ENDED, 5h=4%, window end=02:19Z) after CI went green, with ready cards left. What now?",
 "options": {"A": "Supervisor stays up to its window end while ready cards exist (roles/supervisor.md + a handover guard)", "B": "leave as is; operator restarts by hand", "C": "Thinker flags it each 30-min check"},
 "recommended": "A",
 "answer": "A",
 "done": "pending: card supervisor-handover-refuses-before-trans. Fact: supervisor.md:53 already says transit = TRANSIT time or 5h >= 80%; the early end broke it, so the fix is a guard (handover refuses before transit while ready cards exist, --early <reason> overrides) plus one line in supervisor.md. Review: research/thinker/2026-10-22_ship_context_review.md item 3"}
```

## d-first-ask-driven | decided 2026-10-23 | Thinker
```json
{"id": "d-first-ask-driven", "order": 43, "date": "2026-10-23", "status": "DECIDED", "question": "His own first typed ask is metered as unattended (turn_meter.py:306, driven from the 2nd prompt); the NUC diagnosis was cut off half done. Fix?", "options": {"A": "his first typed prompt counts as him being there unless it is a worker brief", "B": "keep the budget but deny only writes/spend, not reads and web search", "C": "do nothing"}, "recommended": "A", "answer": "yes - do it - and revalidate eveything once done - test it - stress test it - list scenarios of edge cases - but use quota wisely now - we are 89% and reset happens on Sunday", "done": "pending: card below (builder; the Thinker's own edit was denied by the auto-mode classifier as self-modification). Spec, tests, 12 edge cases: research/thinker/2026-10-23_first_ask_driven.md"}
```
