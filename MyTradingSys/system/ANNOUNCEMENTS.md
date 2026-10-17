# ANNOUNCEMENTS: what every session on every machine must know (operator 2026-10-18)

One durable board on trunk. Signals (`mts_signal.py`, SUPER_SESSION.md rule 10) are one-line, expire in 7 days and carry no detail; the board holds
the detail. A new announcement = one entry here, shipped, plus one signal line `ANNOUNCE <id>: <title>, read ANNOUNCEMENTS.md` so running sessions see
it within about 5 minutes. Nobody needs a scheduler for this.

**Every session, at boot:** read the ACTIVE entries below (the file stays short; expired entries move to the bottom list). If an active entry
says STOP or HOLD for the kind of work you are doing, do not start it; if you are mid-way, finish the commit, ship, and hand over.
**Posting:** coordinators and Lab_Guy/Doctor roles only; the operator can post by telling any session. An entry that stops or holds work needs the
operator's OK first (write it as PROPOSED until then). Public repo: no secrets, no account names, no runtime data.

Entry format: `### A-<yyyymmdd>-<n> <kind> <title>` with kind one of INFO, DO-NOW, CONTINUE, HOLD, STOP; then Applies to / Until / What / Why.

## ACTIVE

### A-20261018-1 INFO Lab_Guy workflow v3.1 is in force (design), enforcement is being built
- Applies to: every session that creates or refines a card, or reads a lab result.
- Until: replaced by the machine gate (card `lab-trust-tag`).
- What: new cards carry a `weight` (routine / important / crucial / critical). Risk class C0-C3 decides review depth (`roles/lab_guy.md`): ordinary cards get only the free machine checks, shared or base results get a cross-vendor review plus an independent re-derivation, live path and money get the full stack. Cards that touch no lab data, results or definitions skip it entirely. Claude is an independent verifier of base and shared results, not a supervisor of everything.
- Do now: when you cite a lab result in a card, say which result and treat it as UNCHECKED until it carries a tag.
- Why: an error at the base spreads to everything built on it; Q76 re-derivation already found a wrong sentence in a pre-registration.

### A-20261018-2 INFO Q76 / B187 power gate: current number
- Applies to: anything using the 662 / 2,427 days numbers.
- What: with `dev_ext_2019_2021` the feasible days are 1,207 (lab) or about 1,215 (Haiku blind) against 2,427 needed: still about 1,200 short; fetching more data is not a complete fix. PRE_REG_V2 sentence "about 1,000 days at zero cost" is wrong (about 395); the 2,427 is right. Card `b187-prereg-v2-correction`.

### A-20261018-3 DO-NOW GPT lab queue is idle; NUC keeps it busy
- Applies to: NUC super session.
- What: run the ready CODEX cards one at a time in this order: lab-data-pin-hash, lab-machine-checks-extra, lab-weight-enforce, lab-crossvendor-stage, lab-holdout-access-control, lab-formula-spec-text; then lab-planted-error-trial (blocked until the first two are done: `tasks.py release`). Check `codex_run.py status` each wake; the spend guard (10 runs per 5 h window) paces it.

### A-20261018-4 INFO Where each kind of work goes (two machines)
- NUC (lab, GPT/Codex, Gemini/Antigravity, F:/MTS/data): lab cards, re-derivations, planted-error trial, retro-audit of past base results.
- NB (live tree, JIS-NB lane, screenshots, deploy): live-path desk tasks (java-popups, outcome-labeler-timeout), deploys, live checks, Eagle_Eyes. Run-and-report work for the lab goes to the NUC by desk row `desk.py post --target DSA`; deploy asks go to NB by desk row `--target JIS-NB`. Plan: `research/lab_guy/TANDEM_PLAN_2026-10-18.md`.

### A-20261018-6 STOP Do not rerun `gap-g2-dax-ask-candles` as written (operator OK 2026-10-18)
- Applies to: the CODEX lane and anyone starting that card.
- Until: the card is re-scoped (its requested dates are after the DEV cutoff and the sandbox blocks the Dukascopy download; DEV-only dates and the fetch as a JIS-NB desk task).

### A-20261018-7 INFO Image reads by non-producer models (Gemini pilot 2026-10-18)
- Applies to: any session that sends images to a non-producer model (Gemini, GPT, any vendor other than the one that made the claim).
- What: (1) blind reader only, never show the model our claim and ask if it is right (it agreed with the claim given, 'unreadable' used 0 times in 7 calls); (2) every schema has a required null/'unreadable' option, a number for a hidden field is an invented value; (3) crop two-panel images into panels first; (4) compare model output to our records in code; (5) contested values (25200 vs 25206) get a larger crop and a human/Argon read.
- Detail: `MyTradingSys/system/roles/lab_guy.md` ("Using Gemini ... to read images"); pilot data `research/lab_guy/pilots/2026-10-18_gemini_frame_read/`. One pilot, not a catch rate.

## EXPIRED
### A-20261018-5 HOLD No new consumers of unchecked lab bases (operator OK 2026-10-18)
- Applies to: every session creating or starting a card that reads a lab event table, the Q76 / B187 chain or another lab result as its base.
- Until: that result carries a trust tag at or above the card's class (card `lab-trust-tag`), or the operator lifts it.
- What: running work finishes and ships. Not held: live trading operations, deploys, docs, tooling, hygiene, and the retro-audit and re-check cards themselves.
- LIFTED 2026-10-18 by the operator in chat ("remove all the holds, get the workflow going"). Results on lab bases stay labelled UNCHECKED.
