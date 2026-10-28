# ANGLE: ELICITATION / METHOD SCIENCE - from spoken expert walkthroughs to testable rules (research worker, 2026-09-30)

Scope: how to turn Tom Vorwald / Fabio Valentini walkthroughs into codified, testable rules, and why rule-list extraction fails.
Context read: playbook.md Part I; MISSING_PIECES_2026-09-30.md sections 0-3. No repo file edited except this one.

## 0. Evidence status (read first, honest)
**No source could be OPENED.** Every WebFetch call (semanticscholar, sagepub, eric, philpapers, arxiv, mlr.press, wikipedia,
springer, ncbi, dtic, acritch, scispace, macrocognition, gary-klein.com, research.bond.edu.au) returned EGRESS_BLOCKED from the
agent proxy. Only WebSearch worked, and it returns bibliographic records plus search-engine summaries. Playbook Part I step 3a
requires opening a source and matching title/authors/venue/year; abstract-only access is allowed only if the page was opened.
So strictly NO source below passes the citation check. Per Part I I do not use them to justify any rule. They are listed as
"search-record match" (title, authors, venue, year agreed across >=1 search result) and used only to rank what to TEST first.
Every finding is therefore capped at Confidence L/M and tagged "UNVERIFIED (not opened)". Re-verify when egress allows
(suggested hosts: doi.org, arxiv.org, proceedings.mlr.press). Recommendation R1-R10 below stand on our own design logic and
data, which our own tests decide (Part I step 3e), not on these citations.

## 1. Method note (Part I step 1)
What would settle the question "does codifying a discretionary expert's talk give rules that reproduce his trades?": a held-out
set of the expert's own labeled trades/days (timestamped entries, exits, skipped setups) never used to write the rules;
engine output on the same bars; a confusion matrix at the trade and day level; then P&L of engine vs expert on the same days
with fees + funding + slippage; out-of-sample period; trial count logged (DSR/PBO via verdict.py). The elicitation literature
itself offers no P&L test; it is "unvalidated domain" for the trading-specific claim, so external papers only shape the
record format. Sample period/size: see section 5 (own binomial arithmetic, not a citation).

## 2. Findings by topic (all tagged Tier | Method quality | Confidence; all UNVERIFIED - not opened)
### 2.1 Knowledge elicitation
F1. Critical Decision Method = critical incident technique plus probes for cues, perceptual and conceptual discriminations,
typicality and alternatives, run on ONE real incident retold in sweeps (timeline, deepening, "what if" probes).
Source: Klein, Calderwood, MacGregor (1989), "Critical decision method for eliciting knowledge", IEEE Trans. Systems, Man,
Cybernetics 19(3):462-472. Search-record match only. Tier T1 (peer-reviewed) if verified | method: qualitative, no OOS | Conf M.
Use: the unit of elicitation is an incident with a timeline, not a rule. Our extractions do the reverse.

F2. Recognition-primed decision (RPD): recognising a situation as typical brings with it four things: plausible goals, cues to
monitor, expectancies (what should happen next), and a typical action; mental simulation then checks the action; violated
expectancies signal an anomaly and trigger reassessment. Source: Klein (1993) "A recognition-primed decision (RPD) model of
rapid decision making" in Klein, Orasanu, Calderwood, Zsambok (eds), Decision Making in Action: Models and Methods, Ablex.
Search-record match only. Tier T1/T2 (book chapter; derived from fireground interviews) | method: field interviews, no OOS | Conf M.
Use: a trade record must carry cues, expectancy, goal, action and the anomaly that would abort (this is exactly what Tom's
"doesn't belong above the high" and Fabio's "not the day to trade trend following" are: expectancy/anomaly statements).

F3. Knowledge-elicitation techniques fall in three families: analysis of tasks experts actually do, interviews, and contrived
tasks that reveal reasoning without asking about it; techniques differ in efficiency and yield, so use several. Source: Hoffman,
Shadbolt, Burton, Klein (1995), "Eliciting knowledge from experts: a methodological analysis", Organizational Behavior and
Human Decision Processes 62(2):129-158. Search-record match only (abstract via search summary). Tier T1 | method: review plus
comparative studies | Conf M. Use: combine incident retelling (CDM), limited-information / contrived tasks (show the expert a
chart cut at time t, ask what he does), and task observation (his actual trade log).

F4. Think-aloud data: concurrent verbalisation of what is in short-term memory is valid data and does not change the process;
retrospective or explanatory ("why") reports are the unsafe kind. Source: Ericsson & Simon (1980), "Verbal reports as data",
Psychological Review 87(3):215-251. Search-record match only. Tier T1 | method: theoretical plus review | Conf M.
Use: a live-session walkthrough (the expert narrating as he trades, before outcome) is better evidence than a later
explanation. Fabio's "live session" videos are closer to concurrent protocol than a polished lecture; rank them higher.

F5. People often cannot report the real causes of their own choices and produce plausible theories instead. Source: Nisbett &
Wilson (1977), "Telling more than we can know: verbal reports on mental processes", Psychological Review 84(3):231-259.
Search-record match only. Tier T1 | method: review of experiments | Conf M. Use: stated rules are not the policy. The stated
reason for a trade is a hypothesis to test against what he actually did.

F6. Expert intuition is trustworthy only where the environment is regular and the expert had practice with timely feedback;
judge the expert's claims by those two conditions. Source: Kahneman & Klein (2009), "Conditions for intuitive expertise: a
failure to disagree", American Psychologist 64(6):515-526. Search-record match only. Tier T1 | method: position paper | Conf M.
Use: markets are low-validity; a trader's narrated confidence says nothing about edge. Hence our own backtest decides.

F7. Hindsight: knowing the outcome raises the judged likelihood of the outcome and changes which cues seem relevant.
Source: Fischhoff (1975), "Hindsight is not equal to foresight", J. Exp. Psychology: Human Perception and Performance
1(3):288-299. Search-record match only. Tier T1 | method: 3 experiments, 479 students | Conf M (replication record exists in
search results, not opened). Use: post-trade commentary over-explains the winner. Anything said after the outcome is known
must be flagged; pre-outcome statements (entry narration, placed orders) carry more weight.

### 2.2 Codifying discretionary trading / imitation
F8. Behavioral cloning trains a supervised model to predict expert action from state; on its own state distribution the learner
errs, and errors compound with horizon, so pure cloning from logs needs interaction or recovery data. Source: Ross, Gordon,
Bagnell (2011), "A reduction of imitation learning and structured prediction to no-regret online learning", AISTATS (PMLR 15).
Search-record match only (summary states error grows with horizon squared for plain cloning). Tier T1 | method: theory +
robotics/games experiments, NOT trading, no costs | Conf M for the mechanism, L for transfer to trading.
Use: the engine's own path differs from the expert's (engine flat while expert is long, etc.); per-bar agreement overstates
fidelity. Evaluate at event (trade) level and day level, and feed disagreements back to the expert (his "DAgger" step).

F9. Selection bias / multiple testing: without counting trials, reported performance is inflated; the Deflated Sharpe Ratio
adjusts for it. Source: Bailey & Lopez de Prado (2014), "The Deflated Sharpe Ratio...", J. Portfolio Management 40(5):94-107.
Search-record match only. Tier T1 | method: analytic | Conf M. Use: every rule variant tried against expert trades is a
trial; log the count. Already required by verdict.py/PBO; apply it to the codification loop too.

F10. No validated evidence found (by this search) for: (a) academic work that converts a named human discretionary trader's
talk into rules and then tests reproduction of his trades; (b) sample sizes for learning a trader's policy from labeled trades.
The trading imitation papers that surfaced (AAAI-20 iRDPG on futures; arXiv 2110.01325 on simulated double-auction agents)
imitate synthetic or oracle "experts", not human discretionary traders, and were snippet-only (see discards).
Per Part I 3d I do not lower the bar; section 5 gives our own arithmetic instead.

## 3. Why rule-list extractions fail (mapped to MISSING_PIECES section 3, inference from F1-F7 plus our repo evidence)
1. **Wrong unit.** CDM and RPD both treat a bounded incident (situation, cues, expectancy, action, outcome) as the unit. A rule
   row cuts the incident apart; the sequence (stop streak, then one 1:20 trade) and management (risk to zero, then add) vanish.
2. **Stated rule is not the policy** (F5): "stop above the high" vs his actual inside-the-range stop; FAB-jasv3L-d8ZE-R5 was
   probably inverted by a caption slip. A single quote with no behavior check corrupts the rule.
3. **Hindsight narration** (F7): commentary on a won trade explains the winner; losses and skipped setups are rarely narrated.
   Published walkthroughs are selected (best sessions, one-trade videos): selection bias in the examples, survivorship of
   the setups he chose to show.
4. **Missing negatives.** RPD anomalies and "does NOT" statements, and every non-trade bar inside the day, are needed to
   estimate precision. Rules extracted from positives only can never be falsified by the engine's false positives.
5. **State is implicit.** Day type (compression vs trend, long gamma) is the expert's first recognition step (F2); rules that omit
   it apply the trend model every day; engine produced only shorts in 4.7 years, consistent with a missing state gate.
6. **Verbatim check is the wrong gate.** verify_extract_quotes.py proves the quote exists; it cannot prove the rule means what
   he did. Quote fidelity is necessary, behavioral fidelity is the real test.
7. **Transfer blindness.** Instrument, tick size, cost ratio (12 ticks ES ~0.044%) are dropped, so BTC portability is never checked.

## 4. Recommendations for our pipeline
### 4.1 What an extraction record must contain (one record per INCIDENT, not per rule)
Fields (extends methodology/extraction.md; keep verbatim quotes and GPS):
- incident_id, source video id, [m:ss] span, speaker, channel.
- narration_mode: LIVE (concurrent, before outcome) | RETRO (after outcome) | LECTURE (generic). Weight LIVE > RETRO > LECTURE.
- instrument, tick size, session/time zone, timeframe of decision, size/risk in money and ticks.
- state: day type, weekly/daily context, gamma/inside day (as stated; measurable proxy to be defined separately, else UNKNOWN).
- cues: each cue he names, with whether it is observable in our data (Y/N/proxy).
- expectancy: what should happen next if the setup is valid; anomaly: what he says would invalidate it.
- goal and action: entry (order type, resting vs reactive, level), stop (place and reason), target, management (BE, adds with or
  against the move, partial), exit, session stop.
- outcome as stated, timestamp of outcome statement (for hindsight flag), P&L in R and money.
- negatives: skipped setups, "I do not trade this when", losing trades on the same day, stop streaks.
- sequence: ordered list of actions with clock times; day P&L path.
- confidence tags per field: STATED | SHOWN_ON_SCREEN | INFERRED (inference must say "interpolation - requires validation").
- conflict log: numbers that disagree within the video (e.g. 2,330 vs 10,000) kept, not reconciled.

### 4.2 How to validate an extraction against the source
V1. Quote gate as now (verbatim + GPS). V2. Incident read-back: a second reader (different model or human) reconstructs the
incident timeline from the record alone, without the transcript; diff against the transcript; unresolved diffs go to the conflict
log. V3. Inversion check: for every rule, list the actions he took in the same video; flag a rule whose word direction
contradicts his action (would have caught R5). V4. Consistency across videos: same rule in >=2 independent incidents, else
mark SINGLE-INCIDENT. V5. Screen check: where chart frames exist, confirm stated levels against the screenshot (chart_read_protocol.md).
V6. Live vs retro weighting (F4, F7). V7. Expert probe: send the compiled rule plus 3 counter-cases back to the expert if reachable
(Tom/Fabio are not interviewable; substitute V2-V5, label "no expert confirmation").

### 4.3 Testing whether a codified rule reproduces the expert (labeled-trade ground truth)
Build a LABELED SET: every trade the expert shows (entry time, side, price, stop, target, exit) from chart replays in the videos,
plus the sessions' skipped opportunities where stated. Split by video/day (not by trade) into a rule-writing set and a held-out
set. Then run the engine, unmodified, on the same bars and compute at the TRADE level:
- Match rule: engine entry counts as the same trade if same side, entry within tolerance (e.g. +/- N minutes or +/- x*ATR; fix
  tolerance before looking), and the expert's setup window. One-to-one matching.
- Confusion matrix cells: TP (both), FN (expert traded, engine silent), FP (engine traded, expert did not in a day he was
  shown trading), TN is not defined per bar; use DAY level: day types {expert traded, expert skipped, expert stopped after
  recovery} vs engine {traded, silent}. Report precision = TP/(TP+FP), recall = TP/(TP+FN), by side (longs separately: the
  shorts-only result is a recall failure on longs) and by day type.
- Geometry check: for TP, compare stop distance, target distance, R:R, order type, management sequence; the matched trade
  must also match in management, not only in entry.
- Outcome check: P&L in R of engine on matched vs unmatched days; the expert's day-level distribution (stop streak then fat
  winner) vs engine's; judge the RIGHT-TAIL capture, not win rate.
- FP caveat: expert silence on a bar is not proof he would not trade; FP is an upper bound. Sample FPs and have the video
  re-read for a stated skip.
- Report the trial count and do not tune rules against the held-out set (one look; then it becomes rule-writing data).
- Failing result is informative: list FN causes by cue (missing state, missing level type, late entry), which drives the next extraction.

### 4.4 Ordered recommendations
R1. Change the extraction unit from rule to incident record (4.1). Rules are derived from >=2 incidents.
R2. Record negatives and sequence: stop streaks, skipped setups, session-stop after recovery, management order.
R3. Tag narration mode LIVE/RETRO/LECTURE and outcome-statement time; down-weight post-outcome explanation.
R4. Add inversion and read-back checks (V2, V3) to the gate beside verify_extract_quotes.py.
R5. Build the LABELED SET of expert trades from chart replays and score the engine by confusion matrix (4.3) per side and
    day type BEFORE any P&L backtest; a rule that cannot find his trades is not his rule.
R6. Make day-type state a measurable field (even crude) and evaluate on day-level P&L, not per-trade win rate.
R7. Stamp instrument, tick size and cost ratio on every incident; flag portability to BTC at extraction time.
R8. Treat one-video quotes as hypotheses (SINGLE-INCIDENT) and track trials (DSR/PBO) through the codification loop.
R9. Pick videos to cover losing days and skipped setups, not only best sessions (selection bias).
R10. Re-run this note's citation check when egress opens; until then F1-F9 guide design only.

## 5. Sample sizes (own arithmetic, not a citation; "No validated evidence found" for external numbers)
- Precision or recall as a proportion with 95% CI half-width d: n ~= 1.96^2 * p(1-p) / d^2. p=0.5, d=0.10 -> n ~= 96 trades per
  cell; d=0.15 -> ~43. So 95 labeled trades per side are needed for +/-10 points; we likely hold far fewer (Tom ~20 verbatim trades).
- Zero misses: upper 95% bound on miss rate ~= 3/n ("rule of three"); 10 trades all found still allows 30% misses.
- Edge itself is a separate question: with win rate ~20% and payoff 8R, expectancy per trade is noisy; R-multiple SD ~ 2.5R means
  ~ (1.96*2.5/0.5)^2 ~ 96 trades to resolve +/-0.5R mean. Expert P&L from videos cannot settle edge; only our OOS backtest can.
- Therefore at current sample sizes the confusion matrix is a DIAGNOSTIC (find FN causes, catch gross failures like no longs), not
  a proof of fidelity. Report intervals, not bare rates, and pool across Tom and Fabio only for method checks, never for rules.

## 6. Discarded sources (Part I step 3c; do not re-research)
- Every opened-attempt of a primary page: blocked, so nothing "used" under the citation gate (see section 0). Not a rejection of the papers.
- medium.com Balaena Quant "Deflated Sharpe Ratio" post: secondary blog, no method check.
- yukaichou.com "Hindsight Bias: S-Tier Behavioral Designer's Guide": marketing/gamification site.
- apple podcast page on Ross et al. DAgger: audio summary, no method.
- arXiv 2110.01325 "Learning to Classify and Imitate Trading Agents in Continuous Double Auction Markets": simulated agents, not humans; snippet-only.
- AAAI-20 Yang, Liu "iRDPG" (futures, oracle demonstrations): demonstrations generated by an oracle, not a discretionary human; snippet-only.
- arXiv 2407.15007 "Is Behavior Cloning All You Need? Understanding Horizon in Imitation Learning": snippet-only, not matched to a claim I rely on.
- arXiv results with implausible future ids (2609.07946, 2605.04004, 2607.06117, 2606.09025) and "Structural Limits of OHLCV..." etc.: not opened, unverifiable, off-topic.
- Wikipedia pages (RPD, Klein): tertiary.
- Sagepub "Features of Problem Detection" (1999) and Hoffman/Crandall/Shadbolt 1998 CDM case study: surfaced, not opened, not needed for a claim.

## 7. Counts
Distinct sources cited as search-record matches: 9 (Klein-Calderwood-MacGregor 1989; Klein 1993 RPD; Hoffman et al. 1995;
Ericsson & Simon 1980; Nisbett & Wilson 1977; Kahneman & Klein 2009; Fischhoff 1975; Ross-Gordon-Bagnell 2011; Bailey &
Lopez de Prado 2014). Verified by opening: 0. Discarded/unused: 9 groups listed in section 6.
