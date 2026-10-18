# NEXT_SESSION

Task: finish card fabio-session-date-price-match (claimed by the fabio-dating-1018 session; test passes 4/4).
State: script + test shipped in research/fabio_date_match_2026-10-18/. Spoken day 2025-10-15 already scores 1.0 (F6 entry 13:47 UTC, CFD price 24752.033 = futures basis about -162). Full scan 2025-09-15..2025-12-19 is rate-limited (~1 day/min); raw bi5 cache at F:/MTS/data/nq_raw resumes.
Steps (zero operator input): 1) `python -I MyTradingSys/research/fabio_date_match_2026-10-18/date_match.py > run.log` until it prints `verdict` (cached days are instant). 2) Write DATE_MATCH.md: top-5 table (score, day, entry minute, price), verdict MATCH/AMBIGUOUS, CFD-vs-futures caveat, thresholds labelled SOURCED/OURS (see script header). 3) `sync.py ship --release fabio-session-date-price-match`, git cherry empty, `tasks.py done fabio-session-date-price-match --result "..."`.
Do not edit the ledger. Card tom-ctlong-below-zone-cvd-aligned-audit is done (shipped); new cards tom-cvd-aligned-direction-blind, tom-ctlong-zone-lost-state need `tasks.py check` + refinement.
