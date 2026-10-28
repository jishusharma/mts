# ANGLE: external source of truth on Tom Vorwald and Fabio (2026-09-30)
# Playbook Part I applied. RESULT: NO PAGE COULD BE OPENED. Read section 0 before anything else.

## 0. Method note (Step 1) and outcome
- Question: what do Tom's and Fabio's own published words say about long entries, stops, targets, IVB/first 30 min,
  day type, adds, big-trade thresholds, balance vs imbalance, that our extractions missed?
- Evidence that settles it: the trader's own verbatim words (T3, primary) from an opened page or transcript. No statistical
  test applies; adoption still needs our own OOS backtest (Part I 3e).
- OUTCOME: every WebFetch failed with EGRESS_BLOCKED (network allowlist proxy; not a login wall, not a paywall, nothing
  worked around). Blocked hosts: www.youtube.com, tradethetraders.com, get.tradethetraders.com, podcasts.apple.com,
  www.podcast.de, open.spotify.com, www.kagels-trading.de, www.tradezella.com, www.chartacademy.com, videohighlight.com,
  youtubesummary.com, www.forex.in.rs.
- WebSearch returned only title+URL lists and a model-written summary of them. A search summary is NOT an opened page.
  Under Part I 3a ("cannot open = REJECT") NOTHING below may be cited as evidence. Section 2 lists the search-summary
  claims as LEADS (vocabulary only, tagged "unopened"), so a session with open internet can verify them in minutes.
- Consequence: "No validated evidence found" for every question asked, for both traders. No new rule is proposed.

## 1. Sources opened and matched
NONE (0 of 12 attempted). Local repo files were read (playbook, TOM_VERBATIM_INDEX head, PROJECT_VISION, conditions/*.md
greps, FABIO_BTC_RESEARCH sections 0/1/5, FABIO_V3_SPEC greps); those are our own corpus, not external sources.

## 2. LEADS from search summaries (unopened; T3-vendor at best | no method | L; vocabulary only)
Tom Vorwald (URLs that appeared in results; none opened):
- L1 Identity: founder/mentor of Trade The Traders (TTT), trading office Switzerland / Reutlingen / Cyprus; "over 20 years",
  "trained over 2,000 traders", "+500% in 4 years", mentor of two-time Trading World Cup winner Patrick Nill; "PbD-Methode"
  and "Trader-DNA". Source listed: tradethetraders.com/tom-vorwald, get.tradethetraders.com/mentors/tom-vorwald. Marketing
  bio: credentials and return claims are unaudited and are not evidence. Identity confirmation only.
- L2 Instruments: DAX, US index futures, commodity futures. Methods named: orderflow/footprint for timing, volume profile and
  market profile for "business zones" and "opportunity zones", counter / breakout / swing strategies.
- L3 Podcasts (Insider Trading podcast, two episodes: "Footprint Trading erklaert vom Trading-Weltmeister Coach"; "Trading-
  Weltmeister Coach verraet alles"): listed on apple/spotify/podcast.de. Content unknown (no description or transcript read).
- L4 YouTube channel youtube.com/@TomVorwald appears in results; the repo already holds his transcripts (TOM_VERBATIM_INDEX
  cites IDs such as l8RZrBfzvp4, BVpYGKz9PBU, 4MoNjEQ2Dd8, qLnQan0KGmQ, 43JaKHRvxHk). Channel description not read.
- L5 No book found by search (an Amazon "Volume Profile: The insider's guide" is by Trader Dale, a different author; discard).
Fabio Valentini (generic summary of unopened pages, all vendor/clone material):
- L6 "Direction, Location, Aggression" three-step process; balance vs imbalance each traded differently.
- L7 First 30 min of NY open used as initial range for VAL/VAH/POC; scale in only as absorption confirms; routine partials.
- L8 "Volume multiplier 2.0, max price move 0.3 ATR" absorption numbers: these came from the PickMyTrade TradingView clone
  (already REJECTED in FABIO_BTC_RESEARCH section 5). Not Fabio's words. REJECT again.

## 3. Comparison with our rules (status is about the LEAD, not a verified source)
Tag: every row = unopened search summary | T3-vendor | L. None can move a rule.
| Lead | Our rules | Status | Where |
|---|---|---|---|
| Tom trades futures incl. DAX + US index (L2) | DAX, counter, swing occur in all six conditions files | CONFIRMED (scope) | conditions/*.md; TOM_VERBATIM_INDEX |
| Tom splits counter-trend vs breakout vs swing (L2) | Setups split into counter-trend continuation or breakout (Tom quote) | CONFIRMED | conditions/setup_type_rules.md:20, :142, :384 |
| Tom "business zones" from volume/market profile (L2) | Business zones have a section | CONFIRMED | zone_identification_rules.md:27, :259 |
| "PbD" as a named method (L1) | PBD logic cited (TOM-148, lower balance after rejection) | CONFIRMED (term only; "PbD" expansion unknown to us) | setup_type_rules.md:42, :236 |
| Footprint used for timing/entries (L2) | Footprint used for stop placement and entries | CONFIRMED | risk_protocol.md 2.5; entry_timing_triggers.md |
| "Opportunity zones" (L2) | No such term in conditions | MISSING (vocabulary; unknown whether distinct from business zone) | grep 2026-09-30, 0 hits |
| Commodity futures (L2) | Not mentioned in conditions | MISSING (scope only; irrelevant to BTC) | grep, 0 hits |
| Fabio Direction/Location/Aggression (L6) | Appears only in SUPERVISOR_LOG.md, not in FABIO_V3_SPEC | MISSING from spec (framing; spec has S3 control, S7 premium/discount, S4 big_push which map to it) | SUPERVISOR_LOG.md; FABIO_V3_SPEC S3-S7 |
| Fabio IVB / first 30 min (L7) | Model C IVB, m {5,15}, one trade per day | CONFIRMED | FABIO_V3_SPEC.md:114-119 |
| Fabio scales in only after confirmation (L7) | Adds only after risk is zero, max 3 | CONFIRMED (stricter) | FABIO_V3_SPEC.md:137-141 |
| Fabio takes partial profits routinely (L7) | "partial" appears 0 times in V3_SPEC (BE, trail, S8 exit instead) | MISSING (unverified; TOM has partial exits: risk_protocol 4MoNjEQ2Dd8 row) | grep count 0 |
| Absorption 2.0x / 0.3 ATR (L8) | Spec uses prior-30d 99th / 99.9th percentile big trades | CONTRADICTED only by a REJECTED source; ignore | FABIO_V3_SPEC.md:19-23 |
Nothing is CONTRADICTED by a usable source. Nothing tagged MISSING is backed by anything stronger than a search summary.

## 4. The specific questions asked: how Tom takes longs, stops, targets
No validated evidence found from any external page. The only evidence is our own extraction of his transcripts (not an
independent check). For reference, what our files already say, so a later verifier knows what to check against:
- Stop: "my stop loss belongs below the last liquidity" (risk_protocol 2.1); below last swing low on re-entry (2.2); below
  last low (2.3); not inside VPOC/VA (2.13); trail to last significant volume level (2.11).
- Target: next structural level / high-volume area (5.1; TOM-018); VWAP for counter-trades (5.2).
- Longs are not a separate set in our files; rules are mirrored. No external page confirms or contradicts this.
Fabio day-type selection, big-trade thresholds and balance vs imbalance judgement: No validated evidence found (nothing new
beyond FABIO_BTC_RESEARCH sections 1 and 5).

## 5. Discarded (Part I 3c; do not re-search blindly)
- All 12 blocked hosts in section 0: unopened, REJECT as evidence. Retry only with open internet and read the page itself.
- PickMyTrade TradingView script / blog / Scribd (L8 numbers): marketing clone, already REJECTED upstream.
- Amazon "Trader Dale" book: different author.
- kagels-trading.de "Trade The Traders Erfahrungen": review site, likely affiliate; unopened.
- apple/spotify/podcast.de listings, TikTok: descriptions unread; transcript would be needed (T3 primary) - not obtained.
- Generic volume-profile blogs from results (trading.de, traivend, tradingsim, topstep, masterytraderacademy, quantum-algo,
  journalplus, trade-ideas): generic HVN/VA advice, not Tom's or Fabio's words; no method; REJECT.
- The search-summary credentials (+500%, 2,000 traders, World Cup wins): marketing; REJECT as evidence.

## 6. Recommended next step (for a session with open egress)
Open, in order: (1) youtube.com/@TomVorwald About text; (2) the two Insider Trading podcast episode pages plus any transcript;
(3) tradethetraders.com/tom-vorwald and /manifesto; (4) TradeZella LVN playbook and the Fabio pickscribd transcript already
used upstream. Then verify verbatim and match against risk_protocol 2.x/5.x and FABIO_V3_SPEC S3-S7, Model C. Until then the
answer to "what did our extractions miss" is: unknown; no evidence of a miss.
