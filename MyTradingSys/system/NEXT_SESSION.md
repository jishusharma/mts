# NEXT_SESSION

Older blocks (2026-10-18/19): `MyTradingSys/system/handoff_history/2026-10-21_next_session_trim.md`. A session reads only its own block.

## Simulator desk R2: ETH 1m + symbol box (hand-over, Supervisor C, 2026-10-21)
Run with zero operator input; defaults for open questions (park levels; keep RSI daily default; plug nothing new). Plan: `MyTradingSys/research/sim_desk/ROADMAP.md` (now on trunk).
- Verified: desk tests 41 passed / 3 skipped on trunk code. Nothing built yet (supervisor read budget ran out right after the planner).
- Step 1 (public data, Sonnet or Haiku): fetch ETHUSDT 1m 2022-01..2024-06 (30 files, warm-up included) into F:/MTS/data/tom_raw/klines; do not commit CSVs: `python -c "import sys; sys.argv=['f','--start','2022-01-01','--end','2024-06-30','--datasets','klines','--out','F:/MTS/data/tom_raw']; import MyTradingSys.backtest.fetch_binance_archive as f; f.SYM='ETHUSDT'; sys.exit(f.main())"`; expect `{'ok': 30}`.
- Card B1 (Sonnet; owns `backtest/fetch_binance_archive.py` add `--symbol`, `studies/_bars.py`, `test_studies.py`): `load_1m(symbol='BTCUSDT')`, `data_ready(symbol)`, symbol-keyed `.npy` cache and `_ALL` (today keyed `'a'`: ETH would silently read BTC). Test: tmp BTC and ETH CSVs with different prices, `load_1m('ETHUSDT')` after BTC returns ETH; red on old code.
- Card B2 (Sonnet, after B1; owns `desk.py`, `studies/rsi.py`, `page.html`, `test_desk.py`): `symbol` param (BTCUSDT, ETHUSDT) in rsi `params/normalize/label/run`; TRIALS row carries symbol for non-BTC, BTC label/row byte-identical; bump `RESULT_VERSION` to 3; levels refuses non-BTC; dropdown in page. Test: fake bars both symbols, ETH row has `ETHUSDT`, BTC run after ETH not served from ETH cache; frozen BTC levels row (n 772 / -0.039) unchanged.
- DEV window only. Thinker session `sim-thinker` (local_05060ea8-b8b6-4e9d-8024-03062ef8c643) is on standby, model not yet set to Opus (set_session_model was blocked); stop it or set Opus then send it the roadmap-judging task.
- Login B (NUC): GPT card re-derive 255 / -0.119 R; Gemini card cross-review of RSI spec. Not posted this session.

## Live host move JIS-NB -> DESKTOP-F7IU69N: STAGED 2026-10-21, cutover NOT run (hand-over, Opus, Lenovo)
Run with zero operator input; defaults for open questions. Plan and checklists: `MyTradingSys/system/LIVE_HOST_MOVE.md`; DEVICES.md s1/3/6/7/8/9 and DEPLOY_RUNBOOK.md ("Live host cutover") point to it. Nothing was deployed, started, stopped or shared.
- Result: laptop facts captured (2 batteries, Balanced plan, Wi-Fi only, Update active hours 22-16, IPv4 192.168.29.157 DHCP); laptop Wi-Fi baseline 2026-10-20 21:34Z median per new HTTPS call: Binance ~200 ms, Deribit testnet ~320 ms. JIS-NB numbers for the comparison NOT taken.
- Next, builder session (Sonnet, any host, not the live tree), cards in this order, each with tests that fail on old code: (1) `live_mirror.py` root/publisher not tied to the JIS-NB hostname (env/config per host; LIVE_HOST_MOVE s6); (2) `mts.ps1:348` auto-trader Python path resolved like the other launch lines, fail closed if missing (live path: restart + error tests); (3) `supervisor.py` lane rules know the laptop as the live host. File them with `tasks.py` if they are not cards yet.
- Next, operator (10 min, laptop): LIVE_HOST_MOVE s3 items 1-6 (charge threshold 60-80 % both batteries, Energy saver off, sleep/hibernate on AC never, NIC power saving off, Update restart notify, data SIM in the laptop LTE modem (replaces Ethernet; probe must pass over the SIM)), install `gh` and log in; NUC: create shares MTS-Data (read-only), MTS-Live, MTS-Mirror, MTS-Backup (s5); UPS USB link; router + ONT mini-UPS (s7).
- Next, a session on JIS-NB: run the s3 item 9 probe on JIS-NB and on the laptop in the same 15 min, record both in LIVE_HOST_MOVE s1, pass/fail per the OURS rule there.
- Cutover (s4): only the operator or a coordinator the operator names, in a window the operator chooses; none set (default: no move until named). Builders never run it. Defaults: q-live-autostart NO (manual `mts start` after any reboot), alerts stay on the laptop and are read on JIS-NB via the mirror, trips cut back to JIS-NB first.
- CI: STATUS showed `CI green:` RED (oldest ungreen 22.7 h) and `gh` is missing on the laptop, so CI was not checked here; a host with `gh` checks the pinned `ci-<sha>` card first.
- Do not add gates, lints or rule docs for this.

## Simulator desk: RSI and WaveTrend studies shipped 2026-10-21 (hand-over, Opus lead)
Run with zero operator input; defaults for open questions. Start: `python MyTradingSys/research/sim_desk/desk.py`, http://127.0.0.1:8765, pick the study at the top.
- `studies/rsi.py` (Malkan 40/60 via rsi_core + malkan_40_60) and `studies/wavetrend.py` (LazyBear cross via wavetrend.py) share `studies/_bars.py` (1m bars cached in cache/bars, resample, one trade on 1m bars). Every on-screen choice says (trader) or (ours); sources are in each file header.
- On screen (DEV, fee-net, filled trades): RSI daily (trader default) 2 trades, -1.04 R, NOT ENOUGH DATA (under 30 trades); RSI 4h 20 trades / 1h 75 trades, about 0 R, NOT ENOUGH DATA. WaveTrend 1h default 369 trades, -0.158 R, range -0.288 to -0.023, FAILED.
- Desk verdict now: under 30 filled trades = NOT ENOUGH DATA; whole range below zero = FAILED. New question `rsi-timeframe` on the page (default: keep daily).

## Simulator desk: plug-in seam + Questions panel shipped 2026-10-21 (hand-over, Opus lead)
Run with zero operator input; defaults for open questions.
- A new layer is one file in `MyTradingSys/research/sim_desk/studies/` (levels moved to `studies/levels.py`); the desk finds it at start, no desk.py edit; a study picker appears once there are two. Contract and per-layer verdicts: `sim_desk/PLUGIN.md`. Nothing fits as-is today; Tom, CryptoCred and RSI need a small adapter; Fabio does not fit (order-flow bars start 2024-12-02, after the DEV window). No layer was ported.
- Questions panel at the bottom of the desk page: questions live in `sim_desk/questions.json`, the operator's answers append to `sim_desk/cache/answers.jsonl` (local, gitignored). FIRST STEP of the next desk session: read that file (latest row per id wins). No answer = default: `first-layers` -> wait for Tom v2 rules, then wrap Tom first; `levels-park` -> parked.
- Ask the operator new desk questions by adding them to questions.json, not in chat. 32 tests (6 new, red before).

## Simulator desk fixes shipped 2026-10-21 (hand-over, Opus lead; Fable review C1-C3 + E)
Run with zero operator input; defaults for open questions. Start: `python MyTradingSys/research/sim_desk/desk.py`, http://127.0.0.1:8765 (first Run builds a local cache once, ~77 s; then ~7 s per Run; needs the 1m bars at F:/MTS/data/tom_raw/klines).
- Now: only filled trades count (screen shows "255 trades (517 ideas never filled)"); verdict from the spread of the real trades, the two-point power model is off the screen; every chart caption has date/time UTC, R, long/short and outcome, and the level the entry filled at is drawn; plain error messages; "already tried" is keyed on TRIALS.md rows, so another tree does not log the same setting twice; the target box greys out unless the exit is "chosen multiple"; labels "Which touches" / "How to enter". 26 tests (10 new, red before).
- Frozen setup on screen: NOT ENOUGH DATA, 255 filled trades, -0.119 R per trade, 95 % range -0.369 to +0.148 R, worst losing streak 15. The review expected FAILED; on filled trades the spread is wide (sd 1.57 R, power for +0.10 R 17 %), so +0.10 R is not ruled out. FAILED in the review came from the 517 zero rows.
- Levels strategy: PARKED (coordinator, operator pre-approved). No validation run; card lc-validation stays unrun. Reason: no positive fee-net edge on DEV in any of 240 variants, filled trades average -0.119 R.
- Open from the review, only if the operator asks after using it: C4 (one no-fill and one day-end example when common), C5 (study 2 = Fabio, check its data first). The study's 240-variant ranking counted no-fills as 0 R trades; nobody should re-rank it (strategy parked).
- Do not add gates or rule docs for this.

## LC3 ladder simulator (lc-ladder-dev) shipped 2026-10-21 (hand-over, Fable; data run on JIS-NB)
Run with zero operator input; defaults for open questions. Card lc-ladder-dev is done; report `research/levels_confluence_2026-10-14/ladder_dev.md`, rule `frozen_rule.json`, 243 rows in `layer_lab/TRIALS.md`, 9 tests in `test_ladder.py` (red before the code existed).
- Result on standard DEV (5976 first touches of the 8 KEEP levels, 2022-04..2024-06, VALIDATION/HOLDOUT unread): no variant of the 240 (3 entry filters x 4 scale-ins x 5 stops x 4 exits) has a lower 95 % CI above zero. Frozen rule E1 S2 K5 X0_2R: mean net R -0.039 [-0.123, +0.048], n 772. Verdict: INCONCLUSIVE by the card rule (power_mde.py two-point power 31 % < 50 %), FAIL by sample-sd power (87 % for +0.10 R). Arm P (METHOD.md ladder sizing): -0.130 R, 0 liquidations, max leverage 1.4x; it beats a random-entry control by +0.115 R and the naive S0 K1 X1 by +0.333 R, so the level and the capped adds help, but not enough to pay fees (mean fee 0.11 R per idea; break-even needs gross +0.11 R, the rule makes +0.07 R).
- Decision for the operator (default given): card `lc-validation` (LC4, refined, depends on lc-ladder-dev) reads VALIDATION once only on a DEV PASS. Default: do NOT run it; park LC4 and the levels-confluence layer (fee-net evidence says no edge at the first touch with these exits). If the operator wants one more DEV iteration, the cheapest unexplored direction is the K0 finding: winners travel 1.27 % against before T1 (90th pct) while the tested stops sit at 0.2-0.7 %, i.e. every stop arm cuts most winners; a wide-stop/small-size arm was not pre-registered and would be a new trial.
- Known contamination: E1/E4 filters were chosen on the stale VALIDATION-window separation.md (kept as pre-registered); event_table.csv was not used.
- Do not add gates or rule docs for this.


## Gate tiers by path: shipped 2026-10-20 (hand-over, Sonnet)
Run with zero operator input; defaults for open questions. gate-tiers-by-path is on trunk (ba46d25c7); measured on JIS-NB after it: non-live code ship (smoke gate, 11 steps) 71 s wall; docs-only ship (this hand-over) 11 s wall, no local step.
- Claims now live on the side branch `claims`: `sync.py claim/release` add no trunk commits; `relay_board.py` reads it (b1bb04ff3).
- Follow-up, one small card: `desk.py` (trunk_claims), `trace.py` (open_claims), `make_layers_board.py` and `scripts/sched/relay.py` (live path: needs the restart/error tests) still read claim files from the trunk folder; point them at `origin/claims`.
- A duplicate copy of this task sits unshipped on branch claude/vigilant-chatelet-c1366c (mid-merge, 10 conflicts); leave it, the operator decides on deleting it.
- Second ship from one tree within 10 min is refused; `--again` overrides (trunk implementation).
- Do not add gates, lints or rule docs for this.

## Thinker hand-over 2026-10-20 (v1 plan written; nothing else changed)
Run with zero operator input; defaults for open questions. The v1 plan is in `MyTradingSys/research/v1_plan_2026-10-20/` (README.md indexes D1-D9 and DECISIONS_PROPOSED.md). Nothing in it changed code, cards, config or the live tree.
- Pipeliner / coordinator: post the seven questions in `DECISIONS_PROPOSED.md` on the decision page (OPERATOR_DECISIONS.md format, defaults given). Until the operator answers, apply only the defaults that cost nothing: release the 3 stale claims, 35-41 h with no commit (D1 section 4), ship the unjam branch `claude/traffic-unjam-77aa8e` after a rule-11 review (2 commits not on trunk: 958c0d05, 8d3dc4d0), run `tasks-sweep-closed-cards`.
- Operator (ten minutes): read `D2_V1_SPEC.md` then `D7_ROADMAP.md`; answer yes / no / change per question. q-v1-config-1023 is due before 2026-10-23 (27 grandfathered sources).
- Do not start new layers, lanes, pages or rule docs: D7 freeze is proposed and the default is yes.
- Operator note 2026-10-20 (minimum work, lean, no gates that do not belong): `D10_OPERATOR_STYLE_TUNING.md` adds q-v1-gate-tiers, q-v1-claims-off-git, q-v1-turn-caps (defaults yes). First S0 card after the answer: gate tiers in `gate_select` + `sync.py` with tests that fail on old code.

## NB tandem coordinator 2026-10-18 hand-over (NB at 81% weekly on 2026-10-18 ~13:00 IST, 5-hour 33%; weekly cap 78% passed: NB does shipping only until the 2026-10-20 reset)
Shipped to trunk (git cherry empty): outcome-labeler incremental fix + 9 tests (SLOW exit 3 is discarded by `start-trading-day.ps1:546`, log it there: follow-up), krown-recall-check, state-machine vwap/cvd audit, RV02 R1+R2 (REVIEWED stamps), Fabio date-match + Tom ctlong audit, planner batch 3.
Not on NB: a Tom fade paths ship (`tom-encode-fade-entry-paths`, branch claude/eloquent-shannon-345adc, REVIEWED APPROVE; NUC claimed the same card at 0628Z: look in the trunk history first) and eu-low-sweep (branch claude/quirky-volhard-b457c7): both sessions were told to ship and stop.
For the NUC / Gemini (Flash medium or high; `agy` cannot run from NB, it says sign in over the SSH gate): `tom-probe-prereg`, `rv05-h2-position-line-evidence`, `rv-dsa-ledger-mechanical`, planner raw cards. Stay Claude (CRUCIAL, diff-only review Agent first): RV02 R3 `rv02-fix-dax-full-dev-authorization`, R4 `rv02-fix-dax-producer-data-binding`, `tom-dax-backtest`. Hold `gap-g2-dax-ask-candles` (A-20261018-6) and new consumers of unchecked lab bases (A-20261018-5). Live tree not at trunk (blocked by a live BUGS.md edit); BUGS rows B190-B193, java-popups desk check and the JIS-NB fetch row for gap-g2 are still open.
Ship tips: run ships detached (`nohup python -u sync.py ship > log 2>&1 &`), the 2 gate slots queue for hours when 6+ sessions ship; a red from `Java insufficient memory` is load, rerun once.

