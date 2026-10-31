# R4 Multi-LLM plan for fractal detection and testing (review/design only, no code, nothing run)
Author: Lab_Guy review, 2026-10-31. Status: PROPOSAL, OURS (every threshold below is OURS until Fable validation signs it).
Operator ask: use all available models across LLMs to detect and test fractals, only if there is value, logic and edge-seeking.

## 0. Verdict first
- The coded detector is the ground truth producer. LLMs are second readers and reviewers, never the source of a trade claim.
- LLMs earn a place only by passing a value gate on DEV (section 3.4). Default if the gate is not run or fails: LLMs do code, extraction and adversarial review only; no chart labelling.
- Prior evidence argues for a hard gate: the one project blind-read test (Argon low, 7 frames, 28 fields) gave 16 match / 1 mismatch / 5 correct-null / 4 invented numbers / 2 unverified (research/layer_lab/argon_blind_read/results_argon-low.json, descriptive_counts_7_frames). 4 of 28 fields were invented numbers: that failure mode is to be measured, not assumed away.
- Operator rejected candle-only blind TAKE/SKIP marking (system/OPERATOR_DECISIONS.md:1551, d-tom-btc-no-human-reader; STATUS.md:39-42 "G3 blind marks dropped"). This plan therefore asks LLMs to label geometry (is there a fractal pivot, at which candle index), never TAKE/SKIP, and asks the operator at most to confirm indicator readings.

## 1. Inventory (what is actually available; cite file:line)
| Model / lane | Where it runs | Cost / budget notes | Source |
|---|---|---|---|
| Claude Sonnet 5.5 | any Claude machine, 3 logins (A, B, C); one-use background Agents, max 4 at once | default worker; ~802k input-equivalent tokens per ship (Sonnet session); Agent and session cost the same at the same length; limit in turns (30 turns ~ 100k) | WORKERS.md:7-13, 38; HOW_MTS_RUNS.md:21-25 |
| Claude Haiku | one-use Agents, max 5 per session | scoped work only (named files, exact change, done check); stop at 15 turns | WORKERS.md:23-29 |
| Claude Opus | only if the operator names it, or card lane OPUS with approved_by + crucial | ~2.5x Sonnet tokens per ship (1,970k vs 802k eq) before the price multiplier | WORKERS.md:13, 34-37 |
| Fable | named only in the memory index ("Fable run" = the self-healing handover session); no routing row, no cost line in the docs | budget UNVERIFIED: read get_usage before use. This plan treats it as the validator (section 4 step 1) | memory MEMORY.md "Fable pilot", "Self-healing handover session"; absent from WORKERS.md |
| GPT (gpt-6-luna; Sol 6.1 / Astra) via Codex lab | JIS-NUC, `F:\MTS\mts-codex-lab`, lane CODEX cards, `codex_run.py tick` run by the coordinator on wake | luna medium for audit/build, low for run; Astra only for `crucial` cards at low effort; Plus-plan 5-h window + weekly cap; tick idles at 85% of either; spend guard 10 runs/window, 1 Astra/window, lab share 50 pts/window and 60 pts/week, 20 min gap | LAYER_LAB.md:24-29, 77-90; CODEX_START.md:5; ROUTING.md:55, 70 |
| Gemini 3.8 Flash | JIS-NUC via `gemini_queue.py run <card>:<effort>`; throwaway worktree `F:/MTS/gq/<id>`; a Claude session reviews the branch and ships | routine audits/tests/first-pass review; own quota pool (weekly + 5-h); effort always low (operator 10-28) | ROUTING.md:53; GEMINI_START.md:17-20, 22; memory "Gemini always low effort" |
| Gemini 4 Argon | same queue, or `agy.exe --print --model gemini-4-argon-{low,medium,high}` | weekly-only quota; keep for hard cards (C2/C3 cross-review, blind setup discovery) | GEMINI_START.md:13, 17, 19-20, 22; ROUTING.md:71, 93 |
| Claude Opus 5.5 / Sonnet 5.5 and GPT-OSS 120B inside Antigravity | Google AI Pro login, pool 2 shared | included in the Google plan, not the Anthropic account; Opus there operator-approved 2026-10-18; GPT-OSS = skip | GEMINI_START.md:17-20 |
| DeepSeek (DSA, DSA-NB, DSA-NUC) | AIBridge, chat.deepseek.com | CLOSED by operator hold; no new rows; exact-command run-and-report, not vision | ROUTING.md:8-9, 37; AIBRIDGE_LANE.md:33 |
| Local model | faster-whisper ASR only (JIS-NB `asr_transcribe.py`); no local text or vision LLM found in the docs | n/a | ROUTING.md:73 |

Vision caveat: image input is evidenced for Gemini (Argon frame blind-read ran; pilot dir research/lab_guy/pilots/2026-10-18_gemini_frame_read) and Claude (Eagle_Eyes + shot.py, ROUTING.md:65). GPT vision through `codex exec` is UNVERIFIED: a 10-image smoke test is step S1.

## 2. What each is good for in fractal work
| Task | Best lane | Why / limit |
|---|---|---|
| Numeric code: fractal pivot detector (n-bar variants), DTW / matrix profile / shape match, fee-net forward outcome, pre-registered tests | Claude Sonnet Builder card, DEV data on JIS-NUC | CI + FORMULAS.md independent expected numbers; Sonnet is the repo's tested builder (WORKERS.md:34) |
| Independent re-derivation of detector and outcome table | GPT luna medium via Codex lab (kind=audit or build), different vendor from the producer | producer != reviewer (ROUTING.md:71; GEMINI_START.md:34) |
| Vision labelling of rendered windows | Gemini Flash (cheap volume), Argon (second opinion), Claude Sonnet Agent reading PNGs, GPT only after S1 | prior test shows invented numbers, so labels are index-only (candle number, direction), never prices; numbers come from the detector |
| Extraction of trader fractal methods from captions | Sonnet via `cbp_run.py` for known channels; Gemini only for open-ended video search | ROUTING.md:73-74; `verify_extract_quotes.py` must exit 0; saturated Tom/Fabio/TA101 scraping stays halted |
| Adversarial review of the pre-reg | Argon + GPT luna (neither authored it); Opus only if the operator names it | ROUTING.md:71, 93; WORKERS.md:34-37 |
| Bulk counts on existing CSV | Haiku Agent (DSA on hold) | WORKERS.md:23-29 |

## 3. Protocol
### 3.1 Roles
- Truth producer: coded detector D (Builder, Sonnet). Output per bar: pivot yes/no and confirmation bar index. Point-in-time: a fractal of order n is knowable only n bars after the pivot, so label time = confirmation bar, never the pivot bar.
- LLM labellers L1..Lk read rendered windows and answer a fixed JSON schema.
- Checker: Lab_Guy plus an independent re-derivation (different vendor) of kappa and lift numbers.

### 3.2 Window set (blind, point-in-time)
- DEV data only (holdout never read by the lab, LAYER_LAB.md:58-61). Instruments and timeframes fixed in the pre-reg before any rendering.
- Render N bars ending at candidate confirmation bar t, nothing after t. Strip dates and symbol; price axis rebased to window close = 100; random window order and hashed ids (key stays with the Checker). 50% decoy windows (non-candidates matched on volatility) so "yes" is not a free default.
- Leak tests before any model sees a window: (a) pixel/text scan for dates and price digits; (b) future-shuffle control: replace bars after t with noise (there should be none in the image, so test the renderer) and a shape-shuffle control: labels must collapse on shuffled shapes; (c) null set from shuffled returns to calibrate the false-positive rate.
- Schema (index-only): {"pivot_present": bool, "pivot_bar_index": int|null, "direction": "high"|"low"|null, "confidence": 1-5}. No prices, no TAKE/SKIP, no forecast.

### 3.3 Measures
1. Inter-model agreement: Fleiss kappa across all LLMs on pivot_present; pairwise Cohen kappa; index match within +-1 bar among those both saying yes.
2. Agreement with detector D: Cohen kappa and precision/recall per LLM vs D on the same windows; list LLM-vs-D disagreements (the only place an LLM could add anything: pivots D misses).
3. Outcome: fee-net forward return at fixed horizons for label sources (D alone; D AND consensus; D OR consensus; consensus alone), rules fixed in the pre-reg; block-bootstrap CI on mean fee-net R; DEV only; every variant a row in research/layer_lab/TRIALS.md (LAYER_LAB.md:61).
4. Cost per label (tokens, quota points) in the same table.

### 3.4 Value gate (thresholds OURS, frozen in the pre-reg before rendering)
- Gate A, reliability: pooled Fleiss kappa among kept LLMs on pivot_present >= 0.60 AND each kept LLM vs D Cohen kappa >= 0.50 on the 200-window pilot. Below that, stop LLM labelling.
- Gate B, honesty: invalid labels (index outside window, pivot at a bar the schema forbids, labels that survive the shape-shuffle control) <= 5% per model, else that model is dropped. (Argon-low had 4 invented of 28 fields = 14%, so this gate has teeth.)
- Gate C, value: on DEV, "D AND consensus" or "D OR consensus" must beat "D alone" in fee-net mean R with the 95% bootstrap CI of the difference excluding 0, at n >= 100 events, Holm-corrected over the 3 label variants. No lift = stop and keep D only. A lift is never reported without its trial count.
- Gate D, cost: the whole LLM stage may use at most 10% of a login's weekly allowance (OURS default; Coordinator may change).
- A failed gate stops that stage; later stages do not run.

### 3.5 Sizes and cost estimate per 100 windows
Pilot 200 windows per model (100 candidate + 100 decoy); full set 1,000 only if A and B pass. All figures OURS and UNVERIFIED: measure the first 20 windows per model and replace them. Basis: one image in plus ~150 tokens of JSON out per window, 5 windows batched per call.
| Model | Per 100 windows (est.) | Lane / runner | Budget check |
|---|---|---|---|
| Gemini 3.8 Flash low | ~20 calls, small, inside its own pool | `gemini_queue.py run <card>:low`, JIS-NUC | View Usage first; skip if 5-h < 30% or week < 25% (GEMINI_START.md:21) |
| Gemini 4 Argon low | same call count; a few percent of its weekly-only pool | queue or `agy.exe --print --model gemini-4-argon-low` | only after Flash passes the S1 smoke |
| Claude Sonnet 5.5 (Agent reading PNGs) | 1-2 Agents of <= 30 turns, roughly 0.4-0.8M eq tokens | one-use Agent, files in scratchpad | WORKERS.md rule 3; get_usage first |
| GPT luna low | only if S1 vision passes; one `run` card, a few percent of the 5-h window | `codex_run.py` CODEX card, kind=run | spend guard LAYER_LAB.md:86-90 |
| Haiku | not used for labelling (judgment/vision); rendering chores only | Agent | WORKERS.md:23-29 |
| DeepSeek, Opus, local | not used | n/a | held / operator-named only / none exist |

### 3.6 Who runs what
| Stage | Who | Where |
|---|---|---|
| Pre-reg draft (definitions, windows, gates, thresholds, trial count) | Sonnet Builder | any Claude machine |
| Pre-reg adversarial review | Argon + GPT luna (not the author); Fable validates | NUC lanes + Fable |
| Detector D, renderer, leak tests, kappa script, outcome table | Sonnet Builder cards, size S/M, est_turns set (WORKERS.md rule 1) | work tree, DEV data on JIS-NUC (`F:/MTS/data`, LAYER_LAB.md:62) |
| Independent re-derivation of D and kappa | GPT luna audit card | Codex lab |
| LLM labelling pilot | Flash, then Argon, then Sonnet Agent, GPT if S1 passes | NUC queue and Agents |
| Gate decision + report | Lab_Guy, one number spot-checked by a Claude session | research/fractals_2026-10-31/ |
Operator is not needed, except an optional confirm of indicator readings (never candle-only calls) if a few windows stay ambiguous.

## 4. Order of work (nothing runs before the review gate and Fable validation)
0. Review gate: reviews R1..R4 filed; Lab_Guy ACCEPT on this plan; pre-reg draft committed with gates and thresholds frozen. No rendering, no model calls before this.
1. Fable validation: Fable reads the pre-reg and this plan, checks definitions, leak tests and gates, signs or sends changes (read get_usage first). Nothing below starts without the sign-off.
2. S0, zero LLM cost: Builder codes D, renderer, leak tests, kappa and outcome scripts (fail-first tests); GPT luna re-derives D independently; log the DEV fee-net outcome of "D alone" as the trial to beat. If D alone has no edge on DEV, stop: LLMs cannot rescue a non-edge and no labelling budget is spent.
3. S1 smoke (~10 windows): confirm the image path per vendor, run leak tests, measure real tokens/quota per window and replace section 3.5.
4. S2 pilot (200 windows per model): Flash, Argon, Sonnet, GPT (if S1 passed). Compute Gates A and B. Fail = stop, one-page report.
5. S3 outcome test: Gate C on DEV with trials logged and Holm correction; second-vendor re-derivation of the lift.
6. S4 only if C passes: extend to 1,000 windows; any holdout read goes through the pre-registered card by Fable/operator decision, never the lab.
7. Parallel and cheap, allowed after step 1: caption extraction of fractal methods (`cbp_run.py`, Gemini search only for open-ended search), each extract passing `verify_extract_quotes.py` exit 0; extracted rules reach D only through the pre-reg, each parameter labelled SOURCED (quote + file:line) or OURS.

## 5. Risks and controls
- Chart-reading theatre: decoys, shape-shuffle control, index-only schema, and Gate C (outcome lift, not agreement alone).
- Multiple comparisons: every model x variant is a trial; correction in Gate C.
- Common-mode error: models may agree and be wrong together, so LLM-LLM kappa is not evidence of truth; only agreement with D plus outcome lift count.
- Quota: the Codex lab shares the operator's allowance (LAYER_LAB.md:75-85); Gemini pools are separate; read before each batch; one heavy card at a time.
- Look-ahead: windows end at t; a renderer test asserts no bar after t reaches the image.

Noticed: (1) No doc gives Fable a cost/quota line or routing row; WORKERS.md covers only Haiku/Sonnet/Opus. (2) GPT and Claude image input through the queue/Codex paths is UNVERIFIED; S1 settles it. (3) I did not re-read the 2026-10-18 Gemini frame-read pilot; its reference is marked UNVERIFIED in the Argon result.
