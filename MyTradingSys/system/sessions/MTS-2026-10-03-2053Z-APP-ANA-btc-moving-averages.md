# MTS-2026-10-03-2053Z-APP-ANA-btc-moving-averages
surface: APP
host: JIS-NB
account: none
model: claude-opus-5-5 (Claude desktop app, Code tab)
role: ANA
branch: fast-track
branch_alias: none
predecessor: MTS-2026-10-03-2051Z-APP-ANA-btc-session-sweeps (concurrent sibling; also -2051Z-APP-ANA-btc-candle-patterns)
lanes: subagents /sonnet-01, /sonnet-02, /sonnet-03 (web research); none live
started: 2026-10-03 20:53Z
ended: 2026-10-03 ~21:30Z (operator: session limit approaching)
status: handed-off
commits: records named MTS-Session: MTS-2026-10-03-2053Z-APP-ANA-btc-moving-averages
handoff: next APP-ANA session (this record). Resume steps below.

## Done
- research/_archive/loose_2026-10/BTC_MA_SETUPS_RESEARCH_2026-10-03.md: sections 1 (method notes) + 2 (tier plan) frozen before search;
  section 4 (data coverage, event counts per setup, reuse file map, build list) complete.
- BUGS B103 filed (funding_paid silent 0 outside loaded funding; archive funding exists from 2020-01).
- research/btc_ma_2026-10-03/WORKER_BRIEFS.md: the three worker briefs, re-runnable.

## Pending (resume here)
1. Check research/btc_ma_2026-10-03/ for Q1_standard_ma.md, Q2_nonstandard_ma.md, Q3Q4_regimes_factors.md.
   Missing file = worker died with this session -> re-run its brief from WORKER_BRIEFS.md.
2. Spot-check one citation per worker file (re-fetch, match title/authors/venue/year).
3. Fill sections 3 (tagged findings), 5 (answer; surface per SURFACE_POLICY 1: build + backtest on APP desktop
   jis-nb, since Dumps/ data is gitignored and not visible to CLD), 6 (REJECT list) of the research doc; commit.
4. Event-count script (re-creatable from section 4b description) lived in the session scratchpad, not the repo.

## Task
Operator 2026-10-03 (verbatim): "What trading setups are there for BTC using the moving averages. Maybe secret
moving averages that are back-tested and works under certain market condition like trending/ranging. There could
be other diverse factors and we have to research what they could be!"

## Surface reason
APP first (SURFACE_POLICY 1b): research + file write + commit only; no Maven, no live loop, no execution/ edits.
Read-only against execution/ and layers/alerts/ (no claim taken).
