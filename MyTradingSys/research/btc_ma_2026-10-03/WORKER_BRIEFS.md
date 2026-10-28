# Worker briefs - MTS-2026-10-03-2053Z-APP-ANA-btc-moving-averages

Three Sonnet web-research workers launched 2026-10-03 ~21:10Z. If an output file below is missing, re-run that brief
(general-purpose agent, model sonnet). Method notes + tier plan: research/_archive/loose_2026-10/BTC_MA_SETUPS_RESEARCH_2026-10-03.md sections 1-2.

Common rules (all three): playbook Part I governs (methodology/playbook.md). Fixed tiers T1/T2/T3/REJECT (SSRN/arXiv never
T1). Open every cited source (ToolSearch "select:WebSearch,WebFetch"), match title/authors/venue/year, record URL/DOI +
"verified YYYY-MM-DD" or "abstract only"; cannot open = REJECT; never cite from memory. Tag every finding
`Tier | Method quality | Confidence H/M/L`. "No validated evidence found" instead of lowering the bar. Paraphrase; <= 1 quote
per source, < 15 words. Write ONE file only, plain ASCII, no backslash-u; no git, no execution/ or runtime/ touches.
Return <= 25 lines: 5 strongest tagged findings, counts verified/abstract-only/rejected, one citation to spot-check.

| W | Output file | Question | Method note (frozen) | Leads to verify |
|---|---|---|---|---|
| sonnet-01 | Q1_standard_ma.md (<=250 lines) | Q1 standard MA setups on BTC: price-vs-MA, dual crossovers incl 50/200, VMA/FMA (BLL style), MA-ratio predictors, MA bands, intraday MA rules | OOS returns vs buy-and-hold, net of fees (+funding), snooping control (RC/SPA/Romano-Wolf/PBO), >=5y daily, subperiods pre/post Dec-2017 futures and post Jan-2024 ETF | Detzel et al 2021 Fin Mgmt; Corbet et al 2019 FRL; Hudson & Urquhart 2021 Ann OR; Gerritsen et al 2020 FRL; Grobys et al 2020 FRL; Resta et al 2020 Risks; Huang et al 2019 JFDS; Shynkevich ~2021; Zarattini et al 2025 SSRN; BLL 1992, STW 1999 (method) |
| sonnet-02 | Q2_nonstandard_ma.md (<=250 lines) | Q2 non-standard MAs: KAMA, FRAMA, MAMA/FAMA, VIDYA, Hull, ALMA, McGinley, JMA, T3, ZLEMA, DEMA/TEMA; VWMA, anchored VWAP; 200W SMA, Mayer Multiple, Pi Cycle, 2Y MA x5, 20W/21W band, Golden Ratio mult.; realized price, MVRV, STH-RP | As Q1 + head-to-head vs SMA/EMA of matched lag; cycle signals: count events, n<10 = "anecdote, n=k". T3 allowed for DEFINITIONS table (formula, params, author, year) | Ellis & Parbery 2005 RIBAF; Kaufman; Ehlers 2001/2005; Chande 1992; Tillson 1998; Hull 2005; Legoux 2009; McGinley; Mahmudov & Puell 2018; Coin Metrics 2018; Swift 2019; Mayer 2017 |
| sonnet-03 | Q3Q4_regimes_factors.md (<=280 lines) | Q3 trending vs ranging (ADX, ER, Hurst/VR, MA slope, HMM, vol regimes); Q4 other factors (vol/vol-targeting, volume, attention, funding/basis/OI, time-of-day/DOW/weekend, halving, efficiency drift 2017/2024, macro, stablecoins, decay) | Q3: returns split by EX-ANTE label, difference tested, filtered rule OOS net of costs; full-sample-fitted regime = look-ahead. Q4: conditional returns or interaction regression OOS; factor that predicts BTC alone = "separate-layer candidate" | Zakamulin & Giner 2020 QF; Zakamulin 2014 JAM; Han Yang Zhou 2013 JFQA; Detzel 2021; Liu & Tsyvinski 2021 RFS; LTW 2022 JF; Urquhart 2016 EL; Bariviera 2017 EL; Ardia et al 2019 FRL; Shynkevich; Caporale & Plastun 2019 FRL; Wen et al 2022 NAJEF; Shen et al 2022 Fin Rev; Moreira & Muir 2017 JF; He et al arXiv 2212.06888; Kosc 2019; Tzouvanas 2020; Borgards 2021; Rohrbach 2017; Gurrib 2018 |

Supervisor step after each report: re-fetch the one named citation and match it (spot-check), then fold findings into
BTC_MA_SETUPS_RESEARCH_2026-10-03.md section 3 (tagged), section 5 (answer + surface), section 6 (REJECT list).
