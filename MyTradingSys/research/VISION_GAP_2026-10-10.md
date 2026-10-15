# VISION GAP 2026-10-10 - is PROJECT_VISION.md current, and what is missing from it

Operator ask (Control Room inbox mpvin6sch7v345bc7zcn, verbatim): "Check is the vision doc is updated - Assing Opus to this task.
What is missing in our vision for MTS given where it is today?"
Session: Opus, worktree mts-inbox (jisnb/inbox-fix), read-only analysis. PROJECT_VISION.md NOT edited (operator approves vision changes).
Read: PROJECT_VISION.md, PROJECT_VISION_CHANGELOG.md, STATUS.md, GO_LIVE_BAR.md, DSA_DELEGATION.md, RELAY.md, DEPLOY_RUNBOOK.md,
LIVE_MIRROR.md, NEXT_SESSION.md, BUGS.md B130-B163, ARCHITECTURE_TWO_CORES_2026-10-01.md, CONSOLIDATED_ROADMAP_2026-10-09.md,
LAYER_PROVENANCE_AUDIT.md, CONTROL_ROOM.md, control_room.json, DEVICES.md, auto_trader_config.json, CLAUDE.md, git log since 2026-09-27.

## (a) Is the vision doc current? NO.

- Last real edit: commit 4f74c20, 2026-09-28 (RSI/timeframe directive). `git log -- MyTradingSys/PROJECT_VISION.md` has nothing later.
  The header still says "Rewritten: 2026-09-23" (PROJECT_VISION.md:2), so even the 09-26 and 09-28 additions are not dated in it.
- Since then: 833 commits on fast-track (`git log --since=2026-09-27 --oneline | wc -l`). None touched the vision.
- The changelog has ZERO rows (PROJECT_VISION_CHANGELOG.md:5-6) although at least 5 commits edited the vision
  (261a181, b1531f9, 87e7cef, 2195386, 4f74c20). The audit trail it promises does not exist.
- A second "corrected vision" now lives outside the vision file: CONSOLIDATED_ROADMAP_2026-10-09.md:6-14. Two direction sources.
- Stale statements inside the vision:
  - "Tom is core" as the only core (PROJECT_VISION.md:16, 94). Operator directive 2026-10-01 made TWO cores, Tom and Fabio
    (ARCHITECTURE_TWO_CORES_2026-10-01.md:5-9). Fabio is not named anywhere in PROJECT_VISION.md. CLAUDE.md:76 still says "Tom is core".
  - Three-machines table: NUC = "Ollama code builder" (PROJECT_VISION.md:131, 151). Qwen/Ollama lane decommissioned 2026-10-01 (263b13f);
    NUC is now backtest worker and proposed future live-loop host (DEVICES.md:34, 65-68); laptop is a full working machine (DEVICES.md:35).
  - Probability layer "frequency-table MVP queued (NUC 033)" (PROJECT_VISION.md:88): the NUC queue no longer exists (263b13f).
  - Session frame, tick-delta, timeframe layer listed as "design" (PROJECT_VISION.md:90, 150): code exists under
    backtest/layers/session, session_levels (T087, 71df3aa), tick/ (tick_flagger, tick_oi_extremes), timeframe/ (registry.json, T088 0aa8f56).
  - "Analyst verdicts ... distant" (PROJECT_VISION.md:80, 89): Malkan RSI extracts (e860ee9), CryptoCred live layer (B145),
    Kurisko spec (e3e1be6), Qriptal scorecard (B162, BUGS.md:275) are in progress now.
  - L170/L186 say PROJECT_VISION.md.new is "left in place": the file no longer exists in the tree (ls, 2026-10-10).
- Not mentioned at all (each verified in a file read this session):
  CI/CD auto-deploy (DEPLOY_RUNBOOK.md:3-24); relay/session switching (RELAY.md:1-28); DSA desk delegation (DSA_DELEGATION.md:1-14);
  Control Room operator page + decisions loop (CONTROL_ROOM.md:1-12); live mirror (LIVE_MIRROR.md:18-35); two-account parallel work
  (CLAUDE.md:26-27); provenance rule (CLAUDE.md:77, f23db23 2026-09-30); go-live bar (GO_LIVE_BAR.md:1-14); road S1-S5
  (control_room.json:6+); fee findings (B146, BUGS.md:257); NO-SOURCE research tests (B163, BUGS.md:276; D22 in 0fc934b);
  BT-TUNED tuning override (SUPERVISOR_LOG.md:275); options module (5006a9e, 2026-10-09); screenshot/visual evidence loop (514bb42, B157-B161).

## (b) What is MISSING from the vision given where MTS is today

1. A goal and a definition of done. The vision states architecture, not purpose. The real target now exists only in
   GO_LIVE_BAR.md:6-14 (200 trades, net > 0 after fees, PF > 1.2, time-outs < 5 %, uptime > 95 %, 30 days) and the
   five-stage road S1 Trustworthy measurements -> S2 Survive the fees -> S3 Find a real edge -> S4 Prove it on testnet -> S5 Go-live
   (control_room.json:6-90). The vision should name these stages as the project's spine.
2. An honest current-evidence statement and a "what if the core has no edge" path. Today no source shows edge after fees
   (control_room.json:5); Tom gross R -0.15 [-0.29, +0.04] before fees, holdout burned (CONSOLIDATED_ROADMAP:30-31);
   0 of 34 layer/side rows reach lift 1.15 (CONSOLIDATED_ROADMAP:27-29); exit policies rescue nothing (CONSOLIDATED_ROADMAP:76).
   The doctrine "Tom is core, non-negotiable" (PROJECT_VISION.md:16) has no clause for a core that fails S3.
3. Core count and core admission. Two cores (Tom, Fabio) since 2026-10-01 (ARCHITECTURE_TWO_CORES:5-9) vs one core in the
   vision and CLAUDE.md:76. The admission gate "until backtesting justifies promotion" (PROJECT_VISION.md:19) has no measurable bar;
   GO_LIVE_BAR.md item 1 (walk-forward OOS net R > 0, CI above 0) is the natural one.
4. Provenance as a direction-level principle, and its exceptions. Hard rule since 2026-09-30 (CLAUDE.md:77, f23db23); 30 of 81
   non-core params NO-SOURCE and no layer has a sourced exit (LAYER_PROVENANCE_AUDIT.md:29-42). Two exceptions are live but not in the
   vision: BT-TUNED tuning for big-trade capture (SUPERVISOR_LOG.md:275, CONSOLIDATED_ROADMAP:9-10) and NO-SOURCE research-only tests
   for chatbot/third-party specs (B163, BUGS.md:276; D22). The vision must say which wins when "never tune" meets "tune toward big trades".
5. Trading economics and execution. No section on fees, stop width, maker vs taker, sizing, or exits. Evidence: stops < 0.10 % are
   57 % of Tom sim trades at 3.8-7.6 R fees each (CONSOLIDATED_ROADMAP:73); B146 (BUGS.md:257); 97 % time-exits (GO_LIVE_BAR.md:12).
   Fee survival is road stage S2 (control_room.json) but absent from the vision.
6. Risk and money safety. Daily-loss monitor, kill switch, position_manager never killed, per-source testnet accounts
   (auto_trader_config.json:4; DEPLOY_RUNBOOK.md:21-23), B148/B149 (BUGS.md:259-260). The vision has no risk principle
   (fail closed, per-source capital, max daily loss) and no mainnet policy beyond GO_LIVE_BAR.md:25-27.
7. Testnet's role. Testnet currently runs as a data-collection calibration: all layers fire, sizes 20-1000 USD, blocklist parked
   (auto_trader_config.json:2, 105-110); turn_of_candle FAILED its backtest yet is 79 % of trades (CONSOLIDATED_ROADMAP:32-33).
   The vision does not say whether testnet is a proving ground (only S3-passed configs) or a sensor (everything fires). GO_LIVE_BAR.md:9 implies the former.
8. Source roster and admission of new traders/analysts. Operator wants professionals "WORTH listening to" (PROJECT_VISION.md:199);
   today: Tom, Fabio, Malkan, CryptoCred, Kurisko, Qriptal (live calls via Discord, B162), chatbot handoffs (B163). No criterion for
   who enters, how a trader's track record is scored (B162 scorecard is the first), or when a source is retired.
9. Objective function. 2026-10-09 directive: backtests exist so layers fire on big, profitable trades (CONSOLIDATED_ROADMAP:9-10;
   PROJECT_VISION.md BT-TUNED, which holds that purpose now). The vision only speaks of "independent reads" and "confluence later".
10. Confluence/consensus endpoint. Consensus row is defined (ARCHITECTURE_TWO_CORES:29-43) but the vision has no rule for when a
    confluence may influence a trade (today: never gates). Needed before S3 results can be combined.
11. Research evidence standard. Only "Rule 32: 3-snapshot proof" (PROJECT_VISION.md:99). Practice is now pre-registration,
    one holdout look, walk-forward, fees included, playbook PART I gate (ec18096, B154 BUGS.md:266, GO_LIVE_BAR.md:7-8).
    Regime/session stratification is still missing (B154 OPEN).
12. Data integrity as a principle. B136: OI/LS/taker endpoints dead 2026-09-24..10-05 with OI reported 0.0 at HIGH confidence
    (fail-open, BUGS.md:247); B141 htf balance null (BUGS.md:252); uptime ~81 % (GO_LIVE_BAR.md:23); B140 disk WHEA errors (BUGS.md:251).
    Road stage S1 exists for this; the vision has no "missing data = no signal, never 0" rule.
13. Operating model. Cost-first routing (CLAUDE.md:26), short relay sessions (RELAY.md), DSA desk (DSA_DELEGATION.md), two accounts,
    CI/CD with green SHA (DEPLOY_RUNBOOK.md:3-5), mirror (LIVE_MIRROR.md), Control Room as the only operator channel (CONTROL_ROOM.md:7-12).
    The vision's three-machine and assistant sections describe a model that was replaced (263b13f).
14. Scope. Options module (5006a9e) and multi-timeframe 1m..5d (T088) widen scope; the vision never states the universe
    (BTCUSDT perp only? options? other symbols?). Symbol scope: NOT_IN_DATA (no file read states it).
15. Visual evidence loop. Operator charts are evidence (CLAUDE.md Screenshots; shot.py engine B160, BUGS.md:273); 9 shots overdue
    (STATUS.md:63-72). Not a vision item although it is the operator's main way to test MTS.
16. Local AI assistant and tick-delta (PROJECT_VISION.md:115-163): status since 2026-09-25 is NOT_IN_DATA for the assistant
    (no items/ file mentions it; grep "assistant" in items/ hits only T040). The vision should keep, park or drop it explicitly.
17. Vision governance. Changelog empty; header undated; direction now also lives in CONSOLIDATED_ROADMAP and CLAUDE.md. Needs a
    single owner rule: vision = direction + stage + principles; roadmap = order; Control Room = status.

## (c) PROPOSED ADDENDUM - APPLIED 2026-10-10 (D23 answered 'Apply the addendum as drafted'; now in PROJECT_VISION.md, changelog row logged)

```
## DIRECTION UPDATE (DRAFT 2026-10-10, not verbatim; supersedes stale rows above where they conflict)

### Goal and stages
MTS exists to trade BTC with a proven net edge after fees, first on testnet, then real money only after the
GO-LIVE BAR (system/GO_LIVE_BAR.md, D06-gate 2026-10-09) holds for 30 days. Work follows five stages:
S1 trustworthy measurements, S2 survive the fees, S3 find a real edge (walk-forward OOS net R > 0, CI above 0),
S4 prove it on testnet, S5 go-live gate. Status today: S1-S2 in progress; no source has passed S3.

### Cores and layers
Two cores since 2026-10-01: Tom and Fabio, each compiled independently with its own verdicts, plans and ledger
source flag (research/ARCHITECTURE_TWO_CORES_2026-10-01.md). Every other system (RSI/Malkan, CryptoCred,
session, positioning, probability, tick, timeframe, options, analyst/caller feeds) is a switchable layer that
never gates a core. A core or layer that fails S3 on fixed data is parked (alerts kept for data), not tuned
into passing. Promotion to core uses the S3 bar, never opinion.

### Provenance and its two exceptions
Every parameter comes from the source trader's own words (file:line) or is NO-SOURCE. Exceptions:
(1) BT-TUNED: backtests may tune toward catching big, profitable moves; tuned values are labelled and never
written to live files without an operator decision. (2) NO-SOURCE research tests: specs with no trader
behind them (chatbot handoffs, B163) may run as labelled backtests only, never as live layers.

### Sources we listen to
A trader/analyst enters only with transcripts or a verifiable call history, scored before any trade
(Qriptal scorecard B162 is the template). Each stays an isolated layer until S3.

### Economics and risk
Every result is net of real fees and funding. Stops are wide enough that fees cost under 0.25 R.
Safety checks fail closed; missing data is reported as missing, never as 0. Per-source testnet accounts,
daily-loss monitor and kill switch guard every trade. Testnet calibration (all layers fire) counts as data,
not as S4 evidence; only S3-passed configs count toward the bar. Mainnet needs a separate signed decision.

### How the project runs
Operator speaks through the Control Room (inbox verbatim, decisions). Work is cost-routed: scripts, then DSA,
then Sonnet, Opus only when named. Sessions are short and relay automatically. Code reaches the live tree only
through CI-gated auto-deploy. Off-desktop sessions read live state through the read-only mirror.
Devices: JIS-NB live loop; JIS-NUC backtests (candidate live host); laptop for travel. Qwen/Ollama lane retired.

### Parked or open
Local AI assistant: parked (no build since 2026-09-25). Symbol scope beyond BTCUSDT perp: undecided.
Confluence may gate a trade only after each input passed S3 on its own.
```

## Verification notes
- MATCH: every count above was read from the named file this session. NOT_IN_DATA: assistant build status (16), symbol scope (14).
- Not read (out of budget, cited only via the roadmap): bigtrade FINDINGS.md, AUDIT_MAJOR_GAPS_2026-10-09.md, EXIT_POLICIES_REPORT.md.
