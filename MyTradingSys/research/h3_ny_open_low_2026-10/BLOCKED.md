# H3 (NY open+180 min new day low that holds): BLOCKED before freeze

Card ask-p0-47-h3-ny-open-low-prereg. No PRE_REG frozen, no result read, no strategy run.

- DECISION (OURS): the card window 2020-01..2021-12 is stale. splits.py (DEV 2022-01-01..2024-06-30) is the only DEV;
  2020-2021 is PRE_DEV and 1m perp klines before 2020-01 do not exist. Used splits.py DEV.
- Event count only (no prices of outcomes read): 650 NY trading days (day_gates.ny_open_utc), event = day low over
  [00:00 UTC, open+180) set at open+120..open+150 (held >= 30 min) -> n = 35 (OURS definition).
- verdicts.py check "ny open low hold": no matching H3 row; nearest priors are unrelated opr/wlow FAILs.
- prereg_gate.py --n 35 --sd 1.5 --cost 0.14 --m auto (sd two-point, OURS): m 106, MDE 1.10 R + cost 0.14 vs max
  plausible gross 0.30 -> exit 1 BLOCK. Even sd 0.5 gives MDE 0.37 R (n needed 184). At sd 1.5 needs n ~1650 events; DEV has 35.
- Verdict: INCONCLUSIVE by power; do not freeze, do not test. Reopen only with a wider event definition (more
  events, e.g. other sessions or alts) pre-registered as a new card, or the 2020-2021 window opened by an operator
  split decision.
