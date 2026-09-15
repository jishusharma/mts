# VALIDATION REQUEST — GPT (OpenAI)
## Role: Risk Auditor / Quantitative Methodology Reviewer
## Context: Real-time crypto trading system (BTCUSDT perpetual futures)
## Your Job: Audit the methodology, identify statistical flaws, and design the validation path.

---

## WHAT WE BUILT

A session-aware trading rule set for BTC that claims:
1. **BTC has session seasonality despite 24/7 trading** — volatility peaks during US equity hours (14:30–21:00 UTC), compresses during Asian session (00:00–08:00 UTC)
2. **US equity open (14:30 UTC) is the single most important structural event** — volume and volatility both spike
3. **BTC–NASDAQ correlation ~0.30 and rising** — BTC behaves as a risk asset during US hours
4. **10 session-aware negative rules** should filter trade setups by UTC time window

## THE 10 RULES WE WANT TO IMPLEMENT

| ID | Rule | UTC Window | Setup | Action |
|----|------|------------|-------|--------|
| SR-001 | Avoid CT in first 15 min of US open | 14:30–14:45 | CT | ABORT |
| SR-002 | Boost BO during US–Europe overlap | 14:30–16:30 | BO | BOOST |
| SR-003 | Avoid scalps during Asian session | 00:00–08:00 | Scalp | ABORT |
| SR-004 | Wait for US open range before directional bets | 14:30–15:00 | Swing | HOLD |
| SR-005 | Avoid BO during Asian session | 00:00–08:00 | BO | ABORT |
| SR-006 | Avoid new swing positions during After Hours | 21:00–00:00 | Swing | ABORT |
| SR-007 | Avoid all entries within 5 min of funding resets | 00:00/08:00/16:00 ±5m | All | ABORT |
| SR-008 | Reduce size 50% during US Pre-Market | 13:00–14:30 | All | MODIFY |
| SR-009 | Avoid CT during US–Europe overlap | 14:30–16:30 | CT | ABORT |
| SR-010 | Boost CT during After Hours | 21:00–00:00 | CT | BOOST |

## EVIDENCE WE CITED

### S-Level (Strong Authority)
- **Block Scholes Research (Feb 2025):** "Volatility tends to peak during Western open market hours... BTC typically experiences significantly lower levels of volatility over the weekend."
- **S&P Global (Mar 2026):** "Rolling correlation between Nasdaq-100 and BTC daily price returns has a positive trend." Correlation ~0.30.
- **Coinbase Institutional (2024):** Hourly volume data — institutional flow concentrated during US equity hours.
- **Glassnode:** Weekend on-chain activity materially lower.

### A-Level (Academic / High-Quality Practitioner)
- **Coin Bureau (Jul 2024):** 90-day rolling BTC-NASDAQ correlation fluctuates 0.20 to -0.30, trending positive.
- **Kaiko Research (2024–2025):** Hourly volume/volatility patterns — US overlap dominates.
- **CryptoQuant (2024–2025):** Volume profile by session, funding rate impact.

### B-Level (Platform / Practitioner)
- **ATAS Platform (Aug 2026):** US session (13:30–20:00 UTC) shows increased activity. US session POC can act as support in subsequent Asian session.
- **CoinSwitch (May 2025):** Europe+US overlap (13:00–16:30 UTC) = highest volume window.
- **SGT Markets (Apr 2025):** American session (13:00–21:00 UTC) = most volatile due to overlaps.
- **CoinGlass (2024–2025):** Funding resets at 00:00/08:00/16:00 UTC, liquidation clusters near resets.
- **Binance Research (2024):** Volume distribution — US hours dominate exchange flow.

## WHAT WE ADMIT WE DO NOT KNOW (Gaps)

1. **Exact hourly volatility %** — no tick-data study available
2. **BTC-SPX intraday correlation** — all studies use daily returns only
3. **Crypto "Initial Balance"** — no study validates if first 30m of US open establishes reliable daily range
4. **Funding reset magnitude** — no quantified volatility spike data
5. **US session POC transfer reliability** — ATAS claims it, no statistical backtest
6. **Lunch lull in crypto** — does not exist; low volume is Asian session, not midday

## THE OLD (WRONG) ASSUMPTION WE'RE REPLACING

> "Crypto trades 24/7. Tom's session-based timing does not apply directly. Adaptation: Replace session timing with UTC 00:00 as 'daily open'."

We now believe this is FALSE. Empirical evidence confirms session-bound behavior.

---

## YOUR TASK — AUDIT EVERYTHING

We need you to act as a risk manager reviewing a proposed strategy before capital deployment. Be thorough, conservative, and methodical.

### 1. METHODOLOGY AUDIT

Evaluate the research methodology:
- **Sample bias:** Are 12 sources (4 S, 3 A, 5 B) sufficient to support 10 trading rules?
- **Recency bias:** All sources are 2024–2026. Is this appropriate for a strategy that must work across market regimes (bull, bear, sideways)?
- **Survivorship bias:** Are we only seeing sources that confirmed the hypothesis? What about sources that found NO session effect?
- **Correlation ≠ causation:** The BTC-NASDAQ correlation is daily, not intraday. Can we really infer that US equity open drives BTC volatility?
- **Aggregation bias:** All correlation studies use daily returns. Does a 0.30 daily correlation imply anything about 15-minute windows?

### 2. STATISTICAL RIGOR AUDIT

For each of the 10 SR rules, evaluate:
- **What is the null hypothesis?** (e.g., "CT entries during 14:30–14:45 UTC have the same win rate as CT entries during other hours")
- **What data would falsify this rule?** Be specific about the test design.
- **What is the minimum sample size needed** to validate each rule with 95% confidence?
- **What is the statistical power** of the evidence we currently have?
- **Which rules are testable with available data** (1-minute BTC spot price, 12+ months) and which require data we don't have?

### 3. IMPLEMENTATION RISK AUDIT

- **False positive rate:** How many valid setups would these rules incorrectly abort?
- **False negative rate:** How many bad setups would these rules fail to catch?
- **Opportunity cost:** What is the expected value of trades we would miss due to these rules?
- **Interaction effects:** Do these rules interact dangerously with existing rules? (e.g., SR-001 + existing "no proof" rule = double abort during best setups)
- **Regime dependency:** Which rules work in bull markets but fail in bear markets? Vice versa?
- **Parameter sensitivity:** How sensitive is each rule to the exact UTC window? (e.g., would 14:30–14:50 instead of 14:30–14:45 change the outcome?)

### 4. BACKTEST DESIGN

Design a specific backtest for each rule:
- **Data requirements:** exact fields, granularity, period
- **Test statistic:** what exactly are we measuring? (win rate, Sharpe, max drawdown, slippage)
- **Control group:** what is the baseline for comparison?
- **Significance threshold:** what p-value or effect size would convince you the rule is valid?
- **Out-of-sample validation:** how do we prevent overfitting to the test period?

### 5. PHASED DEPLOYMENT RECOMMENDATION

Assuming we want to implement these rules, design a phased rollout:
- **Phase 1 (Week 1):** Which 2–3 rules should we implement FIRST? Why?
- **Phase 2 (Month 1):** Which rules need paper trading before live deployment?
- **Phase 3 (Month 3):** Which rules require custom data collection before implementation?
- **Kill switch:** Under what conditions do we ABANDON a rule entirely?

### 6. ALTERNATIVE FRAMEWORKS

Are there better ways to achieve the same goal?
- Instead of hard UTC windows, should we use **real-time volatility filters** (e.g., "abort if 15m ATR > 2x daily average")?
- Instead of session labels, should we use **volume percentile filters** (e.g., "abort if current 1h volume < 30th percentile of 24h")?
- Should we combine session timing with **market regime detection** (trending vs. ranging)?
- What would a professional quant fund do differently?

---

## OUTPUT FORMAT

Be structured and specific. Use tables where possible. We need actionable recommendations, not general advice.

```
## OVERALL VERDICT: [APPROVE / CONDITIONAL APPROVAL / REJECT]
## CONFIDENCE: [High / Medium / Low]
## STATISTICAL SUFFICIENCY: [Sufficient / Insufficient / Borderline]
## BIGGEST METHODOLOGY FLAW: [one sentence]
## RULE WITH STRONGEST EVIDENCE: [SR-XXX]
## RULE WITH WEAKEST EVIDENCE: [SR-XXX]
```

Then give us:
1. **Methodology Assessment Table** — rule by rule
2. **Backtest Design Table** — rule by rule
3. **Phased Deployment Plan** — week by week
4. **Alternative Framework Comparison** — pros/cons
5. **Final Recommendation** — what to do, in what order, with what data
