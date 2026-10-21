# Simulator desk: review so far, why the data is small, roadmap, 2-hour session plan (2026-10-21)

Read this first. Sources: INPUTS.md, DESIGN.md, REVIEW_FABLE.md, PLUGIN.md, questions.json (all in this folder), layer_lab/TRIALS.md.

## 1. What has happened (commits on trunk)
| Step | Commit | Result |
|---|---|---|
| Desk v1 | ab5f42d1e | One local page: settings, Run, verdict, 3 numbers, 6 example trade charts, trial ledger, date lock (DEV only). Levels study only. |
| Independent review (Fable) | 46c596a40 | Numbers reproduce exactly. Two things misleading: 517 of 772 "trades" never filled; the "not enough data" verdict rested on a model the zeros break. Advice: park the levels idea. |
| Review fixes | 3c262f8b3 | Counts filled trades only (255), sample-spread verdict, dated charts. |
| Plug-in seam + Questions panel | 5f2c69939 | A study is one file in `studies/`; the page shows open questions with defaults (`questions.json`). |
| RSI 40/60 and WaveTrend | 2b80ef52b | Two more studies on the desk. |
Findings: levels idea loses about 0.12 R per filled trade after fees (255 filled, range wide, so NOT ENOUGH DATA, default = park). RSI on the daily chart gave 5 setups, 2 filled, both lost; 4-hour gives 20 trades, 1-hour 75, both about 0 R after fees, still NOT ENOUGH DATA.

## 2. Why the test data is small (checked, not guessed)
1. **On purpose, three sealed windows.** Data on disk: BTCUSDT 1-minute bars, 2022-01 to 2026-09 (89 files, F:/MTS/data/tom_raw/klines). The desk may only run the DEV window 2022-04-01..2024-06-30 (27 months, "Q79" in TRIALS.md). VALIDATION 2024-07..2025-06 and HOLDOUT 2025-07+ are sealed and read once each, so the strategy search cannot be fitted to them. Roughly 30 percent of the months are usable for hit-and-try.
2. **One asset, one bar size.** Only BTC 1m was fetched. No ETH or other coins, no 5m/1h files of their own (built from 1m).
3. **Rare signals.** The rule decides the trade count, not the data: daily RSI fires about twice in 27 months; levels touched often but only 255 of 772 ideas filled.
4. **Order-flow data starts December 2024**, after DEV ends, so Fabio-style layers cannot be tested on DEV at all.
5. **Every extra try makes a lucky result likelier**, so more tries on the same small window do not fix it; more months, more assets or a second sealed check do.
Options to get more data (cost low to high): fetch ETH/SOL 1m for the same DEV months (public data, DSA-NUC desk row; the desk code takes a symbol only if the study allows it: check); extend DEV back before 2022 (pre-2022 BTC 1m, public; changes the lock, needs the operator's OK); use VALIDATION once per finished idea (already the plan).

## 3. Roadmap, in order (what is built when)
- R1 (now, 0-30 min): verify v1 + review fixes are live and tests pass (`python -m pytest MyTradingSys/research/sim_desk -q`); answer the three open questions with their defaults (park levels; plug nothing new until chosen; RSI 4h/1h as logged tries only).
- R2 (30-90 min): data breadth. ETH 1m for DEV months, then the desk gets a symbol box (one study first: RSI, since it is bar-only). Goal: 2x to 3x the trades per idea without touching sealed windows.
- R3 (90-120 min): the first real second-layer decision: CryptoCred wrapper (exists, setups failed once) or Tom v2 wrapper once v2 rules are written. Default: nothing new plugged until the operator picks.
- R4 (next sessions): validation run, once, for any idea that PASSES on DEV with the wider data; Fabio only after order-flow history exists for a DEV-like window.
- R5: the one-page dashboard polish (typical no-fill and day-end examples, plain verdict wording) only after R2 shows the desk gets used.

## 4. Session planner for 2 hours (login C main, A and B share; GPT and Gemini lanes on the NUC)
Rule: economical. One thinker, at most 2 workers at once on C, 1 lab card at a time on the NUC. No session is run to exhaustion: reuse by budget, then hand over. Budget stop: each login stays inside `supervisor.py plan` mode (NORMAL / THROTTLE).
| Minute | Login C (notebook, simulator) | Login B (NUC) | Login A (later) |
|---|---|---|---|
| 0-10 | Boot: `supervisor.py plan`, Session_Planner Agent (Sonnet) refines the cards below; Thinker (Opus, named by operator) reviews ROADMAP.md choices | `supervisor.py plan`; GPT lab status (`codex_run.py status`); fetch card for ETH 1m via DSA-NUC | not started |
| 10-60 | Worker 1 (Sonnet): R1 verify + symbol box design note; Worker 2 (Haiku): data checks on fetched files | GPT card: independent re-derivation of the desk's frozen numbers (255 / -0.119 R); Gemini card: public-data fetch + cross-review of the RSI study spec (different vendor from the producer) | |
| 60-110 | Worker 1: add symbol box + RSI on ETH, tests that fail on old code; Thinker re-judges verdicts | GPT: second re-derivation of ETH trade counts; Lab_Guy stamp for C1 if cards need it | |
| 110-120 | Hand-over: NEXT_SESSION block, `sync.py ship`, `git cherry` empty, Supervisor log line | same | |

## 5. Hard limits for every session here
Testnet only; no secrets; DEV window only on the desk; VALIDATION/HOLDOUT never read unless a card says so; repo is public (no price data committed); no live tree; ship only through `sync.py ship`; one writer per file set; typed operator prompts are never blocked and sessions never tell him about caps or compaction.
