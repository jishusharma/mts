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
Answer: (none yet)
Operator note (verbatim): (none yet)
Applied: (not yet)

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
Answer: (none yet)
Operator note (verbatim): (none yet)
Applied: (not yet)

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
