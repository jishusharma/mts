# Tom / Fabio extraction redo: plan (2026-11-13)

Owner: coding session `tf-extract-plan`. Operator order 11-13: gap list, then what we have, then what to download, then the final extraction list; Gemini for YouTube, cheap reviewers, coding session does the heavy part.
Files here: `ANSWERS_FROM_DISK.md` (done now, 24 quotes, gate exit 0), `HAVE_LIST.md` (118 videos), `BRIEF_GAP_EXTRACT.md` (rules every card follows), cards `tf-*` in `MyTradingSys/system/tasks/`.
Labels: SOURCED = trader's own words; OURS = our number; NOT_SEEN = looked for, not there.

## Headline

- Of 12 gaps that a trader's words could settle, 4 are already answered from what we hold (Q2, Q3, Q4 partly, Q14 partly). The answers matter: **no bar count exists for acceptance (our 6 is OURS), "speed" is tape speed not a bar count, "70%" is three different claims, and Tom's "closing-price count" (PbD) is named in 116 transcripts but never given as a number.** That last one is the biggest hole: it is his trend-vs-balance read and no code uses it.
- Most remaining gaps sit in videos we already hold and extracted badly (V1 fresh, catalog-only). They need a gap-driven re-read, not a download. New downloads are capped at about 16 ids.
- The Tom feed of 60 is not ranked by id here: titles are not stored and no YouTube/Invidious call was made this turn (captions locked to 02:53Z). Card `tf-g2` lists, triages by a fixed title rubric, then fetches at most 12.

## 1. GAP LIST (what a trader's own words could settle)

| Q | Question | What we use now | Status today | Likely answered by (id) | Who |
|---|---|---|---|---|---|
| Q1 | How does Tom read trend vs balance ("counting closing prices", P/B/D structures)? Any number? | SMA20 / VWAP-CVD slope (OURS) | NOT_SEEN as a number in 116 transcripts; he says "clear rules" exist (m3IMdc7QwN4, jXR1afMy-3o, 3o1VVsfBmmU) | PbD set: Ly62G168MkQ, jXR1afMy-3o, m3IMdc7QwN4, 6BAzqewtPUk, uFxYcpiaOpw, Sy-x5AQ9-Pk, K8qtT2_axPo; new Tom uploads titled PbD | x3 now, g2 after unlock |
| Q2 | What is "70%": value area, time in balance, or return to value? | 70% return tested (E6: 57% vs placebo 47%) | SETTLED as 3 claims (a) VA 68.2/70% (b) balance 60-70%+ of time, one video says 30% trend (c) 30% run / 70% come back (BB3c8visnkI). Open: which profile period and market for (c) | BB3c8visnkI, aursfDVYzUk, Fj4FDZQxw0I, VOiy8mAALWA, K8qtT2_axPo | done (disk); x4 for the period |
| Q3 | Acceptance: how many bars/closes? | 6 x 5m (OURS, once mislabelled SOURCED) | SETTLED: no count; "closing price + sideways phase", "real acceptance, not quick spikes" | Ly62G168MkQ, qLnQan0KGmQ, VxN5IxTwpbE, WQ_OAdz-PJ8 | done; x3 for the build-up wording |
| Q4 | "Speed" of rejection: what is it measured on? | reclaim <= 3 bars (OURS) | PARTIAL: market/tape speed, third pillar with footprint and price acceptance; relative to the product; no bar count | -dMWA_bbm3o, G0CiJcuXCRs, 4P5WAxyPCis (guest), k0zm5NYn0IQ; Fabio Is1HvdfQm5c | x5, x1 |
| Q5 | Stop: exact placement and buffer (Tom "below last liquidity / sideways phase"; Fabio "super small, above the area") | sweep extreme + 5 bps (OURS buffer); v3 floor 0.3-0.5% | PARTIAL: structural rule SOURCED, no buffer or tick count; Fabio NQ 1-6 bps measured | kXhIAug0Gh8, QClPWDJ-BrU, WSCIURybK3U, T6hDJcHrVBM; Fabio Is1HvdfQm5c, 8CWKfoSJu3c | x2, x1 |
| Q6 | Adds, trail, break-even, partials: rules? | none coded (no engine adds) | PARTIAL: add at breakout while pace holds, partials, BE fast (Fabio); no distances | 4MoNjEQ2Dd8, e83njGZFrPw, UOBgXV20yCM; Fabio fZlNGWvd2Ko, 0jM5Y31YJak, 8CWKfoSJu3c | x2, x1 |
| Q7 | Session window and open handling (Tom DAX hours, lunch; Fabio NY, IB 30 min); what carries to a 24/7 market | UTC blocks (OURS); v3 NY 13:30/14:30 + 390 min | PARTIAL: lunch dead (wPMiyJXL0zU), NY only (Pz8f0wWW12M), IB 30 min (LQvv5xgy_ik); exact hours not stated in held extracts | wPMiyJXL0zU, 5Ljfwvtktek, Pz8f0wWW12M, cUTsoU-15Tc, jasv3L-d8ZE, fZlNGWvd2Ko | x4, x1 |
| Q8 | Profile anchor: cash session vs day vs week vs composite vs "last major high to low"; what he does on markets with no cash session | UTC day (OURS) | PARTIAL: cash session, prior day, weekly 70%; pivot profile in sQ_biBKhPVU; no 24/7 statement | BB3c8visnkI, sQ_biBKhPVU, uFxYcpiaOpw, HySZZSjMxF8, -dMWA_bbm3o, Pz8f0wWW12M | x4 |
| Q9 | Absorption: how little price result counts as "almost zero"; big-trade size; what he reads on footprint | big trade = 99th pct (OURS); z-score grid (OURS) | PARTIAL: Fabio "UNDEFINED (almost zero)"; filter by big-trade bubbles exists in his words but no size | Is1HvdfQm5c (18k words), cUTsoU-15Tc, 06R-ebyOhDI, o-w5Gxss6T0, fZlNGWvd2Ko; new VHhvg96W6lc; Tom y67l86cSqb8, oa8kxSLLkAo | x1, x5, g1 |
| Q10 | Target: node-to-node, "a few points short", partial at POC | nearest node, 1R in census (OURS) | PARTIAL: next high-volume price SOURCED; offset size NOT_SEEN | qLnQan0KGmQ, l8RZrBfzvp4, UOBgXV20yCM, zQTbdEweG3c, M7ompiwv5co | x2, x1 |
| Q11 | What counts as "proof" before entry; how many (Tom: "many, many parameters") | 3 WATCH / 5 SETUP (OURS) | open | -dMWA_bbm3o, 3o1VVsfBmmU, y67l86cSqb8, usho6UVLqkE; new O5s9zWI0n2s (4-step framework) | x5, g1 |
| Q12 | Risk per trade, size rule, daily loss, claimed hit rate / R / yearly return | fixed R (OURS) | PARTIAL: size = % of wealth, no value in held line; 30-40% at R>3 SOURCED; "triple-digit returns" claim unread | hQ8sOq67x5o, UrZ4vpHJ97g, WSCIURybK3U, gWjHq5UMisY, yRvMW6lgN1o ("risk $250 to earn $1,212"), dh-ysRR8f-M | x2 |
| Q13 | Who speaks in 9IliXww64uM (Fabio or Andrea Cimi)? | counted as Fabio | UNSETTLED: caption header says Fabio; speaker names a "Cimi ES" template | channel/title metadata only (one fetch) | g1 |
| Q14 | Do the traders trade or read BTC? Any rules? | all rules transferred from index futures | PARTIAL: Tom draws P/B/D on Bitcoin and uses BTC as risk-on/off lead for index trades; no BTC entry/stop/target | Kg6sYKgtkrY, T6hDJcHrVBM, M7ompiwv5co, 0CrkbfuIhkc; Tom feed titles with Bitcoin | x3, gemini-yt, g2 |

Contradictions found while doing this, each goes into the answer ledger: (1) Tom gives balance as 60%, 65-70%, "well over 70%", and in Fj4FDZQxw0I trend 30% / balance 70% vs hQ8sOq67x5o "70% not 30%": the same number, but the base (time, markets, sessions) is not stated. (2) The "70% return" our test E6 measured was claim (c), and the near-band placebo already ate its edge. (3) Held notes quote "acceptance via closing price" in some places and "6 bars" in code. (4) 9IliXww64uM speaker.

## 2. HAVE LIST (high level)

Full per-id table: `HAVE_LIST.md`. Totals from the 11-12 census, 118 ids with transcript or id on file:

| Group | Ids | Transcript | Extract passes gate | Failing / none | Relevant to a gap |
|---|---|---|---|---|---|
| Tom | 88 | 87 | 43 | 26 per-video fail (19 V1-fresh only, 7 V2 thirds-tag), 16 catalog-only, 2 none | see below |
| Tom guests (Hoffmann, Nill) | 13 | 13 | 7 | 5 never extracted, 1 fail | Q4, Q9 |
| Fabio | 17 | 16 | 16 | 1 (DD73wDVvObI, no transcript) | Q4-Q10, Q13 |

HAVE_LIST tiers (keyword-density prior, then read): **RELEVANT-NOW 30** (no passing extract, and a gap hit or Tom), **RELEVANT-READ 51** (extracted, but a top-8 hit for a gap: re-read for the answer), **LOW 37**. Gap-driven re-read replaces per-video re-extraction.

Methods that work: V2 + Source GPS gate, order-flow extracts (247 rules, all exit 0), Gemini concept extract with real captions (M7ompiwv5co 15/15). Methods dead: V1 fresh (no Source GPS, cannot pass), Gemini "watch the video" notes (invented quotes), DSA bridge.

Newly seen this pass (not in older summaries): the PbD videos (Ly62G168MkQ, jXR1afMy-3o, m3IMdc7QwN4) carry Tom's whole trend/balance logic and are CATALOG-ONLY or no-extract; Kg6sYKgtkrY (no extract) is a Bitcoin B-structure read.

## 3. DOWNLOAD LIST (new videos, ranked by gap value, cap about 16)

Nothing is fetched from this desktop before 02:53Z (NUC 13:58Z). Gemini fetches via the guarded fetcher after unlock; the first 429 stops the batch.

| Rank | Video | Why | Gaps |
|---|---|---|---|
| 1 | Tom O5s9zWI0n2s "How to Finally Become a Profitable Trader (4-Step Framework)" | a stated framework = proof count, risk, size in one video; returned NOT_IN_DATA on lock | Q11 Q12 Q1 |
| 2 | Fabio VHhvg96W6lc "If I Had to Start from Zero, I'd Focus on This" | his own priority list, new, never in repo | Q9 Q11 Q12 |
| 3 | Fabio 5 shorts already on F: (_xEhztnK2g0, 3GwHv2FF4Hw, 5H1MCBG87YI, FDrHnl7StOM, 3JZH06L28us) | transcripts exist, no fetch needed, one claim each | Q5 Q6 Q9 |
| 4 | Tom feed, newest 60: triage by title, fetch top 12 only. Rubric: HIGH = title names PbD / counting / closing price / Bitcoin / swing / a live trade with entry-stop-target / risk-reward; SKIP = gear, interviews, news, mindset, and any re-upload with the same title as a held id. Dates 2026-04..11; none of the 60 ids is held | covers the PbD counting number if it is ever said | Q1 Q14 Q5 Q6 |
| 5 | Fabio partner videos agjftXPkLUE, cLgdXZnLL_0, feV6CATGUqo, pZai3k1e-Jg (take 2 after the listing) | Gemini notes exist but failed the gate; real captions let them be rechecked | Q9 Q13 |
| 6 | Fabio 8 other shorts | one-liners only; skip unless budget is left | Q5 Q6 |

Not downloaded on purpose: any id we already hold, third-party DD73wDVvObI / HUYBdYnXUNc / xUyqIjCfZzg (low), the rest of the Tom channel beyond the 60.

## 4. FINAL EXTRACTION LIST and job design

Wave A runs today on held transcripts (no fetch): Sonnet extracts, Haiku reviews. Wave B runs after unlock on Gemini. Order = value to the gaps. Every output answers Q-ids with SOURCED / NOT_SEEN, gate = `verify_extract_quotes.py` exit 0 with at least 1 quote (rules: `BRIEF_GAP_EXTRACT.md`).

| # | Card | Extractor | Reviewer | Ids | Gaps | When |
|---|---|---|---|---|---|---|
| 0 | (done here) `ANSWERS_FROM_DISK.md` | Sonnet coding session | Haiku r1 | 14 ids | Q1-Q4 Q6 Q12 Q14 | done |
| 1 | `tf-x3-tom-pbd-balance-1113` | Sonnet | Haiku r1 | Ly62G168MkQ, jXR1afMy-3o, m3IMdc7QwN4, 6BAzqewtPUk, uFxYcpiaOpw, Sy-x5AQ9-Pk, K8qtT2_axPo, 1utSjHs_Mq8, 0CrkbfuIhkc, VumVuGnCcFM, YkclL6xgu-s | Q1 Q3 Q8 Q14 | now |
| 2 | `tf-x1-fabio-orderflow-gaps-1113` | Sonnet | Haiku r1 | Is1HvdfQm5c, cUTsoU-15Tc, 06R-ebyOhDI, o-w5Gxss6T0, fZlNGWvd2Ko, 0jM5Y31YJak, 8CWKfoSJu3c, Pz8f0wWW12M | Q4 Q5 Q6 Q7 Q9 Q10 | now |
| 3 | `tf-x2-tom-risk-stop-adds-1113` | Sonnet | Haiku r1 | kXhIAug0Gh8, QClPWDJ-BrU, WSCIURybK3U, UrZ4vpHJ97g, hQ8sOq67x5o, gWjHq5UMisY, zQTbdEweG3c, UOBgXV20yCM, G0CiJcuXCRs, 4MoNjEQ2Dd8, e83njGZFrPw, yRvMW6lgN1o, dh-ysRR8f-M, T6hDJcHrVBM | Q5 Q6 Q10 Q12 | now |
| 4 | `tf-x4-tom-session-profile-1113` | Sonnet | Haiku r1 | 5Ljfwvtktek, wPMiyJXL0zU, BB3c8visnkI, VxN5IxTwpbE, HySZZSjMxF8, sQ_biBKhPVU, -dMWA_bbm3o, YopZ5ZDmMFw | Q2 Q7 Q8 | now |
| 5 | `tf-x5-tom-speed-proof-1113` | Sonnet | Haiku r1 | -dMWA_bbm3o, G0CiJcuXCRs, 3o1VVsfBmmU, y67l86cSqb8, oa8kxSLLkAo, usho6UVLqkE, vl01TiVTuoQ, OUM9LYwL8eA, k0zm5NYn0IQ; guests 4P5WAxyPCis, rFPCtOcfUMI | Q4 Q9 Q11 | now |
| 6 | `tf-r1-review-wave-a-1113` | Haiku | none (gate) | outputs of cards 1-5 | all | after 1-5 |
| 7 | `tf-g1-prime-captions-1113` | Gemini `gemini_queue.py run tf-g1-prime-captions-1113:low` | Haiku r2 | O5s9zWI0n2s, VHhvg96W6lc, plus channel/title check of 9IliXww64uM | Q9 Q11 Q12 Q13 | after 02:53Z desktop / 13:58Z NUC |
| 8 | `tf-g2-tom-feed-triage-1113` | Gemini | Haiku r2 | Tom newest 60: title triage, fetch top 12 | Q1 Q14 Q5 Q6 | after unlock |
| 9 | `tf-g3-fabio-shorts-partners-1113` | Gemini | Haiku r2 | 5 F: shorts (local), 2 partner videos, then other shorts if budget | Q5 Q6 Q9 | after unlock |
| 10 | `tf-r2-review-wave-b-1113` | Haiku | none (gate) | outputs of 7-9 | all | after 7-9 |
| 11 | `tf-s1-answer-ledger-1113` | Sonnet (coding session) | Haiku spot check | all ANSWERS.md + ANSWERS_FROM_DISK.md | all | after 6 and 10 |

Output folders: Sonnet/Haiku cards write `tf_extraction_plan_1113/out/<card-id>/`; Gemini (CODEX) cards must write under `MyTradingSys/research/layer_lab/tf_extract_1113/<card-id>/` (card lint rule). All 11 cards are `ready` and pass `tasks.py check`; `tasks.py lint` OK.

Card 11 builds `ANSWER_LEDGER.md`: one row per OURS parameter now in code (acceptance 6 bars, reclaim 3 bars, stop buffer, LVN fraction, big-trade percentile, session blocks, proof counts) with the trader's value or NOT_SEEN, and a short list of rules that stay OURS. No code changes and no new backtest until that ledger is shipped and the operator agrees on what to test.

## 5. Order for the gemini-yt queue (sent to local_dd69f68a)

1. Fix the 7 V2 thirds-tag fails first (quotes exist, cheap, pass count rises).
2. The 5 Fabio shorts from F: (local, Q5 Q6 Q9).
3. Kg6sYKgtkrY (Q14, Q1), then kKZCJui4S9U.
4. The 19 V1-fresh redo, but only these 8 first: UOBgXV20yCM, zQTbdEweG3c, T6hDJcHrVBM, VumVuGnCcFM, vl01TiVTuoQ, yRvMW6lgN1o, dh-ysRR8f-M, wPMiyJXL0zU. The other 11 (9eHZMVXilgc, C9n_d91Uitc, Fj4FDZQxw0I, KEe_CWHyuSg, OUM9LYwL8eA, e6Gm1n2h05M, l8RZrBfzvp4, rrHj24GSR6M, sQ_biBKhPVU, v5EuDl9c0iI, vk0mkNPuhDc) after cards tf-g1..g3.
5. After unlock: O5s9zWI0n2s and VHhvg96W6lc first (cards tf-g1), then tf-g2, tf-g3. Guest videos (5 never extracted) last.
Note the overlap: cards x1-x5 re-read held transcripts for gap answers; they do not replace the per-video Source GPS extracts gemini-yt is fixing, which stay the base for rule catalogs.

## 6. Notes

- Verified here: `ANSWERS_FROM_DISK.md` gate exit 0 (24 quotes). Keyword density in HAVE_LIST is a ranking prior, not a read.
- Not verified: the Tom feed contents and titles, anything about the NUC disk, whether yt_transcript_sites works for listing before unlock (not tried).
- Public repo: no account data in these files.
