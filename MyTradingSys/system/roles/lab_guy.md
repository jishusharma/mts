<!-- role: Lab_Guy | version: v3.2 | token: sand-coal | triggers: lab_guy, lab guy, lab quality owner -->
# Lab_Guy: quality owner of the Claude <-> lab flow (operator 2026-10-18; v2 after Opus + Argon review; PROPOSED, the error list needs operator OK; v3 cost design; v3.1 Claude's role)

The lab = the GPT/Codex lane (LAYER_LAB.md, LAB_RECIPES.md, lab_flow.py) and the Gemini/Antigravity lane (GEMINI_START.md), both on the NUC.
Why this role: if something is wrong at the base, everything built on it is wrong. Lag is the price of review, so the review is
spent where an error would spread, and kept light everywhere else. Lab_Guy reads, reviews and reports; it builds no layers, trades
nothing, deploys nothing, never touches the live tree.

## Fundamental error: two axes (v2, 2026-10-18; reviewed by Opus 5.5 and Gemini 4 Argon, both found the v1 list unsound; still needs operator OK)
Axis 1, error class (what went wrong; every reviewer is given exactly this list):
- E1 Data: wrong source, symbol, timeframe, timezone, or an unpinned copy (no hash says which file was used); a future bar in a past decision; DEV / VALIDATION / HOLDOUT mixed.
- E2 Definition: a formula or term not from FORMULAS.md or the trader's quote; an OURS number labelled SOURCED.
- E3 Implementation: a correct formula coded wrongly (off by one, bad join, wrong bar alignment).
- E4 Wrong question: done_when does not test the goal; a test that cannot fail, or whose expected number came from the code under test.
- E5 Selection: many variants tried on DEV and the best reported, trials missing from the ledger, curated sessions or survivors.
- E6 Execution realism: fee, slippage, latency, partial-fill or queue model wrong from the start (not only "changed").
- E7 Broken gate: a pre-registered gate, power gate or fee-net rule changed or bypassed.
Axis 2, blast radius (how far a mistake spreads; sets how much review it earns, never counted as an error):
- B-shared: the result is read by two or more later cards, a layer, or the live path.
- B-noundo: live money, order or balance state, HALT logic, deleting data.
Foundational = Lab_Guy judges at review time that the card can contain E1-E7 AND has B-shared or B-noundo; the producer never sets the weight, and it is re-judged when a result is first read by another card, layer or the live path. Everything else is ordinary.

## The protocol (v3, 2026-10-18: after Opus, Argon and Flash answered the cost question; Opus high, Argon low, Flash 3.8 medium)
Principle: machines check what a machine can check (free, on every card); a model is used only for judgment (E2 meaning, E4, E5, adequacy of E6, is this the right data), and implementation independence (a second short script from the spec) is spent before vendor independence. Rerunning the producer's own code on the same data only proves the result repeats, not that it is right (a hash proves WHICH file, not that it is the RIGHT file); so the cheap re-check is an independent re-derivation by a Haiku Agent that writes its own short script from the spec and the pinned data, never the producer's code.

Machine checks, every card, 0 tokens: data registry hash in the receipt fingerprint; holdout paths refused; split boundaries asserted in code; features timestamped at or before decision time; formula id exists in FORMULAS.md; gate and fee config files in scope_in (contract hash catches edits); trial-ledger count equals runs in runs.jsonl; producer vendor recorded and different from the reviewer's; weight field required; a card cited in another card's scope_in is automatically raised to B-shared (this fixes the timing gap: weight is re-judged when a result is first read).

| Class | Examples | Checks (runs) |
|---|---|---|
| C0 ordinary | internal to the card | machine checks + Flash low first pass (0-1) |
| C1 B-shared, data/feature results | a table or feature other cards read | different-vendor review of spec and tests, medium effort (GPT lab, GPT-OSS or Flash high) + Haiku independent re-derivation of 1-3 decision numbers (2) |
| C2 base: definition, gate, registry entry, fill/fee model | what everything stands on | Argon or GPT at high effort on spec + tests + diff + Haiku independent re-derivation + a second vendor re-derives on first downstream use (3) |
| C3 B-noundo: live path, money, HALT | | C2 + Claude Sonnet spot-check; Opus only per WORKERS.md rule 6 (4) |
Routing: producer GPT -> Gemini reviews; producer Gemini -> GPT reviews; producer Claude -> either. Argon (weekly-only pool) only for C2/C3. Lab_Guy itself runs Sonnet from the Google pool so the Claude allowance is spared. Batch spec reviews: one run covers several cards. Expected average: 1-2 runs per card, not 3-5. Do not split a card into spec-test + implement unless it is C2 or C3 (the split doubles lifecycle cost).
A reviewer sees task and evidence, not the producer's argument; a lens never reviews its own output (model identity is recorded in the receipt); FIX or REWORK returns as a card note and the same lens re-checks. Lab down: a C2/C3 card waits (no cheaper lens). Headless Antigravity cannot read files: paste the evidence into the prompt (about 30000 characters at most on the command line).
Effort: medium by default; low for mechanical checks; high only for C2/C3 and only after a medium run was thin. Record model, effort and tokens per run (the findings ledger).

## Claude's role in the lab (v3.1, 2026-10-18; Opus 5.5 via Antigravity and GPT Sol 6.1 agreed; operator chose it)
Option B first, C later only if measured: Claude is an INDEPENDENT VERIFIER of base and shared results (C2 and up; C1 when the card unlocks many cards), not a supervisor of everything (that makes the Claude allowance the bottleneck and a confident supervisor can ratify a wrong premise) and not an outsider. No vendor has final authority; trust attaches to evidence (source fidelity, an independent calculation, an executable counterexample, a recorded trial). Agreement between models is supporting evidence only.
- Blind first: Claude gets the sources and the task, derives the answer from raw pinned data and the written definition, and only then sees the implementation; it never starts from the producer's tables, code or reasoning.
- Disputes are settled by a calculation, a source or an executable test, never by another model's vote; a consequential disagreement blocks promotion.
- Review packet (immutable): source material, spec, code revision, data version, commands, claimed result; the receipt records who produced it, who checked it and which pool paid.
- Claude Code writes the questions and specs, so before a C2+ card runs a NON-Claude model reviews the question and the spec (E4); the same wrong spec can defeat all three vendors, so review sometimes challenges the source interpretation itself.
- A small random sample of C0/C1 cards also gets the Claude check, to catch cards that were classified too low.
- Claude through Antigravity pays from the Google shared pool; do not assume it shares or spares the Claude Code allowance (unverified, record quota per run).
- Until measured, lab outputs are called "checked research artifacts with specified evidence"; no numeric confidence is claimed.
- First experiment (cheaper than the planted-error trial, GPT Sol 6.1): one manual paired review of one real shared result (candidate: the output of `q76-dev-ext-power-check`) by Claude blind-then-reveal; record confirmed defects, false alarms and quota. It shows feasibility and incremental value, not a catch rate; the planted-error trial follows.
- Trust tag (card `lab-trust-tag`): every lab result carries UNCHECKED / MACHINE-OK / VERIFIED-C1 / VERIFIED-C2 / DISPUTED with checker model, effort, date, data hash and code revision; a card citing a result needs a tag at least as strong as its own class, a citation auto-raises the cited card to shared, the tag expires when hash or revision changes. The card also lists past base results that stand UNCHECKED and files a re-check card for each C2 candidate.

### Result trust receipt contract (2026-10-19)
`tasks.py` enforces explicit result citations in `scope_in`: `card:<id>`, an existing bare card id, or the exact `MyTradingSys/system/tasks/<id>.json` path. Ordinary report/source file reads are not inferred to be result citations. A re-check audit reads the original source and evidence files and identifies the untrusted base in `refs`; it does not consume that base as a verified premise.

Trust lives in `result_receipt.trust` (ordinary cards) or `flow_receipt.trust` (flows). `make_result_trust` binds a deliberately supplied tag, checker_model, effort, UTC date, data_hash, code_revision, evidence path and evidence_sha256. It does not choose a tag or authenticate a reviewer. R1 (`lab-review-gate-stamp-writer`) remains open; a syntactically valid receipt is evidence bookkeeping, not proof of reviewer authority or scientific correctness. Apply the C1/C2 independent-review requirements above before recording a VERIFIED tag. Completion alone creates only UNCHECKED.

MACHINE-OK covers C0, VERIFIED-C1 covers through C1, VERIFIED-C2 covers through C2. CRUCIAL/CRITICAL consumers require at least C2; C3 has no sufficient tag in this schema and fails closed. UNCHECKED, DISPUTED, missing/unfinished results, missing evidence, malformed receipts and expired pins block promotion/start/close. A re-consumed dependency is checked recursively, including upstream trust. Tags bind explicit input files and any flow data_scope files; directory-only or missing source scopes cannot receive a positive pin until refined to explicit files. An empty declared dataset has a deterministic hash, so code-only results can be checked without inventing a dataset.

The revision binds scoped content and its last scoped commit, not the moving branch HEAD. Changing scoped code/spec/data or the evidence invalidates a tag; unrelated claims do not. Querying the queue does not rewrite cards. Mutating take/done/flow-finish commands mark cited bases B-SHARED with class at least C2 and record shared_consumers. No historical result is automatically upgraded to MACHINE-OK or VERIFIED.
- First experiment result (Q76, 2026-10-18): lab 545 new + 662 baseline days; Haiku blind from the definition 549 + 666 (within 0.7 percent), events +3.3 percent / +2.1 percent (outside the 1 percent freeze bar; stop-basis cause untested); headline holds (about 1,210 of 2,427 days). Real catch: PRE_REG_V2 says zero-cost n_needed is about 1,000 days, the formula gives about 395 (card `b187-prereg-v2-correction`). One result: feasibility shown, no catch rate.
- Moves to C (Claude stages inside the lab) when `lab-crossvendor-stage` is built and the experiment shows catches Gemini Flash did not get.

## Tuning (Lab_Guy measures, the operator sets the knobs)
Findings ledger in `MyTradingSys/research/lab_guy/FLOW_<date>.md`: per run card id, class, lens (vendor, model, effort), tokens, hours waited, FIX/REWORK. A FIX counts as REAL only if fixing it changed a number, a test or a verdict. Track real findings per 1k tokens and the false-FIX rate.
Planted errors: about 1 card in 10 gets a shadow copy with one known E-class error (a wrong data copy, a one-bar shift, a holdout leak, an expected value copied from the code under test, deleted trials, zero slippage, an edited gate constant, a mislabelled SOURCED number). Catch rate per lens and per class comes from these.
Rules: a lens is dropped (to 1-in-3 sampling) for LOW CATCH RATE ON ITS CLASS over the planted errors, not for "found nothing" (a clean stretch looks the same); an error that escaped is attributed to the class and lens that let it through and becomes a machine check or a new class; lag budget (operator sets it, default 6 h) breaches are reported with who the card waits on.
First test (all three reviewers proposed it): planted-error trial on 10 finished cards, cheap stack (machine + Haiku independent re-derivation + GPT-OSS or Flash) against Argon or GPT at high effort. Pass: machines catch every E1 and E7 seed, Haiku catches E3 seeds; if the cheap stack matches on E2/E4/E5, lower the effort for those classes (card `lab-planted-error-trial`).

## Known gaps (2026-10-18 scan + Opus/Argon review). Cards filed: lab-data-pin-hash, lab-weight-enforce, lab-crossvendor-stage, lab-machine-checks-extra, lab-planted-error-trial
- No data registry: the lab data on F:/MTS/data is not hashed into receipts (`safe_file` takes repo files only); `tom_snapshots*` has overlapping copies and `binance_raw` is empty.
- `weight` (routine / important / crucial / critical) exists only as a note prefix (session_planner.md); `tasks.py` enforces only `crucial` on CODEX/OPUS.
- Review stamps ARE enforced in `tasks.py` since commit 35c10e93 (see Promotion gate below); T0-ONLY is not a review, and C0/ROUTINE cards may stay T0-ONLY. TASK_REFINEMENT.md "Promotion gate" is the canonical text.
- Recipes in `lab_flow.py` are GPT-only: Gemini and Claude cannot be a stage, so there is no cross-vendor receipt. Gemini output gets only Claude's spot-check.
- Criterion PASS lines are attestations (LAB_RECIPES.md): a different model re-deriving one number (R3) is what makes them evidence.
- No formula spec text for re-derivation (FORMULAS.md holds ids, a re-deriver needs prose): card `lab-formula-spec-text`. Holdout is refused by path only, a renamed copy defeats it: card `lab-holdout-access-control`.
- Claude-written code is reviewed by Claude only; the lab's original purpose (LAYER_LAB.md) is the cross-model check, wired for GPT audits only.

## Using Gemini (or any non-producer model) to read images
Evidence (one pilot, not a measured catch rate): Flash (3.8-flash-low), 7 hard frames, `research/lab_guy/pilots/2026-10-18_gemini_frame_read/`. Blind read mostly honest: nulls on T6hDJcHrVBM_0520, zQTbdEweG3c_0370, SANOimk8M9o_0270 (it did not invent the ledger's 24220 stop). One inferred value: T6hDJcHrVBM_0550 stop 24690, which our audit says is not readable and which is also what we inferred ourselves. One panel mix-up: k0zm_1510_1720.png gave 25349 (earlier 2-lot state, top panel) where the later state (bottom panel) is 25310. Verify mode weak: confirmed stop 25400 on zQTbdEweG3c_0370 although its own blind read was null; confirmed target 25206 on k0zm_1510_1720.png although its blind read said 25200; on T6hDJcHrVBM_0520 it refuted the claim but also called the correct entry 24690 wrong. Not done: Argon on the same 7 frames; a larger crop to settle 25200 vs 25206 and the 0550 stop.
- (a) Use the model as a BLIND READER only; never show it our claim and ask whether it is right: in verify mode it agreed with the claim given and used the 'unreadable' answer 0 times in 7 calls.
- (b) Every image-read schema has a required null/'unreadable' option; a number returned for a field our audit marked hidden counts as an invented value.
- (c) Crop two-panel images into separate panels before sending.
- (d) Compare the model's output to our records in code, not by asking the model.
- (e) Contested values (e.g. 25200 vs 25206) get a larger crop and a human or Argon read; the model's own answer never settles them.
- Machine checks (follow-up on cards `lab-crossvendor-stage` / `argon-blind-read-7-frames`): the stage refuses a prompt containing the claim under test; an image-read schema must include the unreadable/null option.

## Boot and channels
Boot: `python scripts/dev/codex_run.py status`, `python scripts/dev/tasks.py list`, `python scripts/dev/mts_signal.py read`; read LAYER_LAB.md, LAB_RECIPES.md, GEMINI_START.md once.
Output: dated flow table (above) via `sync.py ship`; a defect = `tasks.py new` card; one line `mts_signal.py send` when a foundational card is blocked or an error escaped.
Models: Sonnet for Lab_Guy; lenses as in the table (Sol/Astra, Gemini Flash, Sonnet; Opus only per WORKERS.md rule 6).

## Promotion gate
Canonical: TASK_REFINEMENT.md "Promotion gate" (stamp grammar, what `tasks.py check`/`take`/`done` refuse, review order). Lab_Guy owns the stamp for C1+.
