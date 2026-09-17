# TOM VERBATIM INDEX
# Purpose: single source of verbatim Tom quotes for rule citations.
# Authority: raw_transcripts_canonical/*.txt are canonical. This file points. Does not duplicate.
# Rule: every derived rule in MyTradingSys/mts/conditions/ carries [TOM-NNN] or [SCREENER].
# Rule: SCREENER means "our invention". Must not be presented as Tom.
# Verifier: scripts/tools/verify_rule_citations.ps1

## QUOTES

| quote_id | transcript | position | excerpt | topic |
|---|---|---|---|---|
| TOM-001 | BVpYGKz9PBU | L19 | "here is a B profile and that shows me that there is weakness in the market" | B profile = weakness |
| TOM-002 | OUM9LYwL8eA | L19 | "if you understand the B profile, you will understand that we know in the top we will go back um to the lower of this price" | B profile = top, return lower |
| TOM-003 | rFPCtOcfUMI | L13 | "such a B profile is always the first sign for me that there has definitely been strong and aggressive selling here" | B profile = aggressive selling |
| TOM-004 | tS6ZEiHj8gQ | L19 | "you have a real setup, in this case, a B structure that shows you it is really time now" | B = setup confirmation |
| TOM-005 | vk0mkNPuhDc | L13 | "There was aggressive selling here, and the market is now accepting lower prices" | B = accepting lower |
| TOM-006 | 3o1VVsfBmmU | [BEGINNING] | "The first thing I generally do is I give myself what I always call a quick watch of the current price trend" | Quick watch first |
| TOM-007 | BVpYGKz9PBU | [BEGINNING] | "The first thing we always do is look at the trend structure and the major trend structure" | Weekly structure first |
| TOM-008 | Ld1dhjGdTCA | [MIDDLE] | "Where are we in balance or are we currently in an active aggressive trend?" | Balance vs trend |
| TOM-009 | Ld1dhjGdTCA | [MIDDLE] | "Whether it is trend or balance because I have to use different setups there and that is absolutely crucial." | State to setup match |
| TOM-010 | BVpYGKz9PBU | [MIDDLE] | "you absolutely have to divide your setups that are suitable for short trades into counter trend continuation or breakout" | Setup split |

## SCREENER PROXIES (ours, not Tom)

| proxy_id | what | where | status |
|---|---|---|---|
| SCREEN-001 | profile shape letters TWOPEAK / D / P | MarketDataSnapshot.java L484, L553, L561 | rename candidate, I40 |
| SCREEN-002 | distance caps 0.005 / 0.004 / 0.003 / 0.002 | SetupCandidatesBuilder.java L416-425; mts_math.py L25-40 | screener-invented, no condition-file support |
| SCREEN-003 | book imbalance 0.4 / 0.6 thresholds | SetupCandidatesBuilder.java L541 | screener-invented, no condition-file support |
| SCREEN-004 | scalp_short / scalp_long split | SetupCandidatesBuilder.java L448 | condition files define scalp as concept, no direction split |

## PENDING

- Populate one row per rule in each condition file. Mechanical pass, one file per session.
- Every rule in conditions/ gains [TOM-NNN] or [SCREENER]. Then verifier runs.

# END
