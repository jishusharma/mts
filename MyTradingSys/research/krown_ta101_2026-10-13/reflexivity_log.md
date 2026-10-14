# Krown reflexivity log (extraction.md SAFEGUARD 4: after each extraction batch, what surprised us)

## Batch 1: 8 videos (extracted 2026-10-12/13 on JIS-NUC, commit 8930cabd; reviewed 2026-10-14)
Unexpected codes
- TA 101 is a foundations series, not a strategy series: 0 stop rules, 0 targets (one heuristic: range height), 0 position sizes
  in 7 TA videos. Entries are "wait for the close, volume and retest", never a price/stop pair.
- Several of his rules are stated with numbers that are testable on our data: 20-period volume SMA, 2x spike, 3-5 zones,
  >3 tests breaks a level, 21/55 EMA + 200 SMA, 50/200 cross, 5 EMA leash (his stats: 5,284 candles, 476 disconnects, 82 % reconnect
  within 2 candles, longest 7 closes), 200-week SMA (his claim: 26 years, 6 assets, 80 touches).
- Two of his rules disagree with each other or with our house rules: more touches weaken a level (SNR-18) vs three touches make a
  trend line (TRL-08); wait for the retest (SNR-15) vs the best breakouts do not retest (RNG-21); "I do not like stop losses" (SNR-21)
  vs our rule that a protective stop must exist; plain 2x volume (VOL-09) vs our lesson that plain relative volume is a clock for BTC.
Pre-conceptions challenged
- Assumed the playlist was 28 videos with 10 left. It is 37 entries, 19 reachable, 11 left. Counts now come from MANIFEST.csv.
- Assumed the extraction format could be shown to workers by pointing at a finished extract. That breaks the clean-slate rule: template added.
- One of the 8 (HhV4HI9p5Uw) is a referral promo about Coinbase fees with no TA; it is kept but not counted as a TA video.
Assumptions that need revision
- Saturation (20 videos) cannot be reached on this playlist; either waive for a descriptive layer or add Krown's other content.
- The extracts record what he says, not what the chart showed. Zones he calls "obvious" are eye calls: DISCRETIONARY until a detector is
  shown to agree with a human reader on a blind set (as planned for Tom: eye read).
Process notes
- The extract of ep7 (RNG-13) contains one aside from the MA episode (20-period MA); the number gate flags it. Left as is.
- Caption retrieval is the bottleneck, not extraction: 429 on two machines over two days.

## Batch 2: 7 videos (extracted 2026-10-14 by 7 fresh single-video workers, clean slate; verified by this session)
Unexpected codes
- The 7 are an EARLIER series (Mar-Apr 2026) plus a tops video (Jun 2026); the Aug-Oct "TA Foundations" episodes of batch 1 are largely a re-teach.
  Rules that appear in both series (zones = wick to close, close beyond the zone breaks it, 21/55 EMA + 200, daily over lower timeframes) are now
  backed by two independent passes: fewer PROVISIONAL rows on the core.
- Stops and exits DO exist: the volatility video gives a structural stop (far side of the compression zone) and a volatility exit (BBWP peak);
  the tops video gives a scale-out range (20-85 %). The batch-1 summary "no stop anywhere" was true for episodes 1-7 only.
- A fully sourced regime tool appeared: BBWP with his settings (basis 7, lookback 100) and thresholds (85 high, about 25 low, 50 confirm).
- His RSI zones (40 and 60) coincide with the Malkan 40/60 layer already in the repo.
Pre-conceptions challenged
- Assumed the 11 pending videos were blocked by YouTube. Only 4 are: I misread a log mid-run (it was still going) and wrote "blocked" into
  STATE, PROTOCOL, the cards and a decision; corrected the same day. Lesson: read a background log to its end marker before concluding.
- Assumed the number gate was final. Worker kcMnnQr1VFg reported it false-flagged ordinals ("50th", "93rd") and rewrote its text in words to pass.
  Real checker defect (my regex); fixed, and the worker's wording is acceptable but note the gate shaped the extract.
- Assumed worker logs would let me audit clean-slate compliance. The logs are empty (0 bytes). Compliance is evidenced only by the template/brief,
  each worker's own report, and the output side: none of the 7 extracts mentions another video's id.
- Opening a YouTube watch page in the in-app browser autoplays audio (operator heard it); not used again.
Assumptions that need revision
- Saturation: the last 5 extractions added whole new families (volatility, RSI, tops), so the "<5 % new codes" condition is clearly NOT met;
  four reachable videos are still unread. The waiver decision (q-krown-saturation) stays open and covers descriptive work only.
- Two orders of priority (volatility before or after structure) are stated in the same video; no resolution possible from the text.
Process notes
- Both gates passed on the first run for all 7; workers' stated concept counts (30, 31, 42, 41, 50, 53, 78) match the heading counts.
- Spot check of the highest-impact numbers against the raw transcripts (BBWP settings and thresholds, 2x of the 30-day volume average, 3 of 4 top
  signals, 377/700 EMA, the 80-95 % claim): all matched.
