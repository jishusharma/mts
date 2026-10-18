# RESEARCH SPECIFICATION: PITCHFORK LAYER (NEW LAYER FAMILY)
## Systematic Median Line & Structural Geometry for Bitcoin Swing Trading

---

### 1. Motivation and Context

In the MyTradingSys (MTS) architecture, prior order-flow and technical layers (e.g. Tom fade, Fabio NYC open, RSI divergence, CVD absorption) often struggled with two primary impediments:
1. **Low-Timeframe Fee Drag:** Strategies evaluated on 1-minute to 15-minute horizons frequently generated gross alpha of $+0.05\%$ to $+0.08\%$ that was completely eliminated by the $0.10\%$ round-trip exchange taker fee hurdle (`FABIO_OF_REPORT.md`, `MATRIX_REPORT.md`).
2. **Lack of Dynamic Location Anchors:** Fixed indicator levels (such as horizontal support/resistance or fixed moving averages) fail to accommodate Bitcoin's accelerating volatility and non-linear trend expansion.

The **Pitchfork Layer Family** (`pitchfork`) solves both limitations:
- **Wide Stop & Target Space:** By operating on 4-Hour and Daily swing structures, typical targets span $+3.5\%$ to $+8.0\%$ with stops of $1.2\%$ to $2.0\%$, reducing exchange fee friction to under $5\%$ of gross trade expectancy.
- **Dynamic Equilibrium:** The Median Line provides a time-and-price adaptive equilibrium vector derived from natural market swings ($P_0, P_1, P_2$).

---

### 2. Sourced Master Principles & Formal Rules

Every parameter and rule in this layer is directly sourced from canonical literature:

#### Rule P-01: Anchor Confirmation (Mikula 2002:42; Morge 2002:18)
- **Source:** [SOURCED: Patrick Mikula, *The Best Trendline Methods of Alan Andrews*, p. 42; Timothy Morge, *Trading with Median Lines*, p. 18]
- Pivots $P_0, P_1, P_2$ must be confirmed swing extrema with a minimum clearance of $N \ge 3$ bars on each side and a swing amplitude exceeding $k \ge 2.5 \times \text{ATR}_{14}$.
- Pitchfork evaluation begins only after $P_2$ is confirmed (no lookahead bias).

#### Rule P-02: Slope Normalization / Schiff Switch (Schiff; Dologa 2007:65)
- **Source:** [SOURCED: Jerome Schiff; Mircea Dologa, *Integrated Pitchfork Analysis*, Vol 1, p. 65]
- If the median line angle $|\theta| > 55^\circ$, the standard Andrews Pitchfork is rejected and the **Modified Schiff Pitchfork** is deployed:
  $$P_{0,\text{ModSchiff}} = \left(t_0, \, \frac{p_0 + p_1}{2}\right)$$
- If $|\theta| > 75^\circ$, the structure is invalidated as an uncontained vertical climax.

#### Rule P-03: The 80% Median Line Target (Andrews 1965:12)
- **Source:** [SOURCED: Alan H. Andrews, *The Babson Action-Reaction Course*, Section 2, p. 12]
- Following the completion of Pivot 2, price has a high probability (~$75\%-80\%$) of reaching the Median Line ($ML$).
- In an ascending pitchfork, a confirmed bounce at the Lower Median Line ($LML$) initiates a Long trade targeting $ML$.

#### Rule P-04: Hagopian Momentum Failure (Andrews 1965:28; Morge 2002:74)
- **Source:** [SOURCED: Alan H. Andrews, Section 4; Timothy Morge, p. 74]
- If price rallies from $P_2$ but stalls before reaching the Median Line ($ML$), reverses, and closes beyond the $LML$, a **Hagopian Failure** is triggered.
- Direction: Short breakout.
- Target: Measured move equal to the channel width $W = |p_{UML} - p_{ML}|$.

---

### 3. Layer Setups

```
+-----------+------------------------+-------------------+--------------------+--------------------+
| Setup ID  | Name                   | Entry Trigger     | Target             | Stop-Loss          |
+-----------+------------------------+-------------------+--------------------+--------------------+
| PF-REV-L  | LML Bounce Long        | Reversal at LML   | Median Line (ML)   | 1.0 ATR below P2   |
| PF-REV-S  | UML Bounce Short       | Reversal at UML   | Median Line (ML)   | 1.0 ATR above P2   |
| PF-HAG-S  | Hagopian Failure Short | Close below LML   | ML - Channel Width | Above local fail   |
| PF-HAG-L  | Hagopian Failure Long  | Close above UML   | ML + Channel Width | Below local fail   |
| PF-WRN-L  | WL1 Breakout Long      | Close above UML   | Warning Line 1     | Prior UML          |
+-----------+------------------------+-------------------+--------------------+--------------------+
```

---

### 4. Integration with MTS Order Flow & Proof Gates

When a Pitchfork setup triggers at Layer 1 (Geometry), it must pass the MTS microstructural proof gates in `SetupCandidatesBuilder.java`:
1. **Absorption Proof (`proof_absorption`):**
   At $LML$, volume on the 5-minute bar must exceed the 80th percentile with negative Delta, but price closes in the upper half of the bar (passive buy absorption).
2. **CVD Alignment Proof (`proof_cvd_aligned`):**
   At the point of bounce, Cumulative Volume Delta must not be diverging downward against the direction of the trade.
3. **Delta Flip Proof (`proof_delta_flip`):**
   Confirmation bar following the tine touch exhibits positive Delta on an up-close.

---

### 5. Validation Plan & Milestones

- **Phase 1: Detector & Unit Verification (NOW):**
  - Implement `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py`.
  - Comprehensive unit test suite `test_pitchfork_detector.py` covering all geometric forms, slope thresholds, and Hagopian conditions.
- **Phase 2: Historical Event Study on BTC (PLANNED):**
  - Run pitchfork detection across Binance BTCUSDT 4H and 1D klines (2020–2026).
  - Measure empirical ML reach percentage, average duration to ML, and Hagopian payout ratios.
- **Phase 3: Order Flow Confluence & Backtest (PLANNED):**
  - Backtest with Deribit/Binance taker/maker fee models.
