# B058 - FLOOR-REACTION MODE MISSING

Register row: MyTradingSys/research/BUGS.md B058.
Convention: one item, one doc. Verbatim ask at top when available. Updates appended chronologically, newest last.

## VERBATIM ASK

No verbatim ask on record (opened 2026-09-20, before items/ convention on 2026-09-22). Row title and evidence transcribed below from BUGS.md.

Title: Verdict path has no floor-reaction mode; net_rr gate blocks every daily VAL long; alerts churn without firing.

Evidence (2026-09-20 apparatus_log.txt 08:00-09:40Z): four ct_long@daily_val 80211.29 cycles rejected as WAIT_RR (net_rr 1.55 < 2.0); twelve+ ct_short@daily_vah 80582.56 cycles rejected as WAIT_RR (net_rr 1.54 < 2.0); price ran 80161 to 80524 (+363 pts) with zero fires; 670 alerts; HSTOP long-block flag flips True at the exact low.

## STATE

2026-09-22 OPEN. Parts A+B landed (hash A3140FD5 -> D32180A4): mode field + net_rr suspension for floor/ceiling within 0.15 pct.
Parts C (contradiction suppression) and D (per-zone cooldown) still OPEN.
Part D needs live tape: same-zone repeat WATCH or SETUP_FORMING.

## UPDATES (chronological, newest last)

### 2026-09-22T18:00Z - coordinator, session MTS-2026-09-22-1737Z

Item doc created during T039 functionality-doc sweep.
