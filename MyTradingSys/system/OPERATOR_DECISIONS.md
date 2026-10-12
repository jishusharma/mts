# OPERATOR DECISIONS: repo record of the Control Room questions

The Control Room db holds the live copy (collection `decisions`, one doc per question). This file is the durable copy:
a session that adds a question appends it here; the pickup that applies an answer writes the answer and the note here,
word for word (CONTROL_ROOM.md step 4). Seed a wiped or second db from the JSON blocks below.

## q1-one-control-room | asked 2026-10-13 | Process

Which Control Room page holds your questions and Inbox?

Recommended: This page is the one place
Answer: (none yet)
Operator note (verbatim): (none yet)
Applied: (not yet)

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
Answer: (none yet)
Operator note (verbatim): (none yet)
Applied: (not yet)

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
Answer: (none yet)
Operator note (verbatim): (none yet)
Applied: (not yet)

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
Answer: (none yet)
Operator note (verbatim): (none yet)
Applied: (not yet)

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
Answer: (none yet)
Operator note (verbatim): (none yet)
Applied: (not yet)

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
Answer: (none yet)
Operator note (verbatim): (none yet)
Applied: (not yet)

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
Answer: (none yet)
Operator note (verbatim): (none yet)
Applied: (not yet)

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
Answer: (none yet)
Operator note (verbatim): (none yet)
Applied: (not yet)

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
Answer: (none yet)
Operator note (verbatim): (none yet)
Applied: (not yet)

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
