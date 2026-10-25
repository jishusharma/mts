# Layer Fact Sheet: guidance (Tom/Fabio cross-guidance)

Fact sheet compiled per ANTIGRAVITY_LAPTOP.md item C from repo files only.
No verdict on keeping, dropping, demoting, or parking a layer.

---

## Layer: `bb_lvn_triggers`

### 1. ORIGIN
- Analyst / Indicator: Tom (order flow / volume profile) and Fabio (order flow / book sweeps), with indicator concepts from Bollinger Bands (John Bollinger) and RSI (J. Welles Wilder / Malkan).
- Quoted source (S1 - Tom on LVN bounce):
  > "these price areas are zones with very low volume for the respective time frame we're looking at. And the market often bounces off these areas."
  — [SOURCED_RULES.md:14](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md#L14) citing `YmygDgtoxO8_raw.txt:19 [TOM-210]`
- Quoted source (S2 - Tom on filling LVN liquidity):
  > "we're in the low volume area. That means it's doing nothing other than filling this empty price area with liquidity now."
  — [SOURCED_RULES.md:15](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md#L15) citing `4MoNjEQ2Dd8_raw.txt:19 [TOM-211]`
- Quoted source (S3 - Tom on Fair Value Gap space):
  > "This creates a space where the market was ultimately traded quickly and aggressively."
  — [SOURCED_RULES.md:16](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md#L16) citing `Fj4FDZQxw0I_raw.txt:19`
- Quoted source (S4 - Tom on single prints):
  > "single print areas are in reality nothing more than specific price ranges where the market never actually retraced within this particular move"
  — [SOURCED_RULES.md:17](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md#L17) citing `Fj4FDZQxw0I_raw.txt:19 [TOM-202]`
- Quoted source (S5 - Tom on FVG support/resistance and trend stability):
  > "fair value gaps are great support resistance levels. They are, but only if the market has trend stability." / "volatile fair value gap in a sideways phase. And if liquidity up here isn't high, then there's a good chance it'll just be traded through."
  — [SOURCED_RULES.md:18](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md#L18) citing `Fj4FDZQxw0I_raw.txt:8 and :19 [TOM-204, 209]`
- Quoted source (S6 - Tom on unhealthy trends returning to liquidity):
  > "this trend isn't entirely healthy." / "there was simply no liquidity left here and the liquidity was down here. That means low volume."
  — [SOURCED_RULES.md:19](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md#L19) citing `zQTbdEweG3c_raw.txt:19 [TOM-056, 140]`
- Quoted source (S7 - Tom on Bollinger Bands outside moves and volume surge):
  > "we gain an advantage because this allows us to see whether a market is supported by volume. Only then does it make sense to trade in that direction." / "But now trading volumes are surging outward" / "then the market certainly won't return to that Ballinger band range quickly and definitely not within the same day."
  — [SOURCED_RULES.md:20](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md#L20) citing `4VXpUjhKG2U_raw.txt:7`
- Quoted source (S8 - Tom on method order: location, context, order flow):
  > "how we connect the dynamic context and then use the order flow to get the timing right."
  — [SOURCED_RULES.md:21](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md#L21) citing `-dMWA_bbm3o_raw.txt:7`
- Quoted source (S9 - Tom on opening range compression):
  > "if something is very narrow, but liquidity is the same as in the previous days, then the probability at a later point in time is much greater that the market will trend."
  — [SOURCED_RULES.md:22](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md#L22) citing `Ld1dhjGdTCA_raw.txt:19 [TOM-212]`
- Quoted source (S10 - Tom on VWAP side setting bias):
  > "they're initially more bearishly inclined" (price below VWAP)
  — [SOURCED_RULES.md:23](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md#L23) citing `43JaKHRvxHk_raw.txt:19 [TOM-049]`
- Quoted source (S11 - Fabio on fast move after book sweep into empty level):
  > "If they squeeze this one on the top and they reach this one, probably, with high probability, they will go for a fast move all the way up because, as you can see, this level is pretty empty"
  — [SOURCED_RULES.md:24](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md#L24) citing `FawPrRUGNpk_raw.txt:770-776`
- Quoted source (S12 - Fabio on fast sweeps near extremes):
  > "when you have a book sweeping, a fast movement."
  — [SOURCED_RULES.md:25](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md#L25) citing `FawPrRUGNpk_raw.txt:253`
- Quoted source (S13 - Fabio on CVD direction and VAL target):
  > "see what the CVD is telling us" / "reaching the value area low"
  — [SOURCED_RULES.md:26](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md#L26) citing `FawPrRUGNpk_raw.txt:1048; 8CWKfoSJu3c_raw.txt:141`
- Quoted source (S14 - Fabio on hidden pressure inside balance):
  > "see what the CVD is telling us" / effort vs result
  — [SOURCED_RULES.md:27](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md#L27) citing `FawPrRUGNpk_raw.txt:724-738`
- Negative origin clarification ("saffron story"):
  > "'Price moves fast through prices where nobody wants to trade' is the narrator's sentence in research/TOM_FABIO_STORY_2026-10-05.md:13-16. It paraphrases balance/imbalance [TOM-030]. Neither trader says it."
  — [SOURCED_RULES.md:6-8](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md#L6-L8)

---

### 2. PARAMETERS
- SOURCED: VWAP anchor at 00:00 UTC for bias evaluation (S10) — [FAST_MOVE_CATALOGUE.md:46](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/FAST_MOVE_CATALOGUE.md#L46); [SOURCED_RULES.md:23](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md#L23)
- SOURCED: Weekly volume profile POC migration sign `sign(POC_thisweek - POC_lastweek)` (S9 / TOM-196 concept) — [FAST_MOVE_CATALOGUE.md:46](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/FAST_MOVE_CATALOGUE.md#L46)
- SOURCED: LVN bounce vs traverse concepts (S1 bounce, S2 fill liquidity) — [SOURCED_RULES.md:14-15](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md#L14-L15)
- OURS: Evaluation timeframe resampled to 15m closed bars from 1m Binance klines — [PRE_REG_Q33.md:8,19](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md#L8-L19); [matrix_q33.py:31-34](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/matrix_q33.py#L31-L34)
- OURS: Forward evaluation horizons H = 1, 4, 16 bars (15m, 60m, 240m), with primary horizon H = 4 (60 min) — [PRE_REG_Q33.md:19](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md#L19); [matrix_q33.py:18-19](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/matrix_q33.py#L18-L19)
- OURS: Cooldown of 4 bars (60 min) per trigger variant and direction — [PRE_REG_Q33.md:20](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md#L20); [matrix_q33.py:20](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/matrix_q33.py#L20)
- OURS: T1 Bollinger Bands BB(20, 2) on 15m close using population standard deviation; event triggers on crossing upper or lower band when previous close was inside — [PRE_REG_Q33.md:21](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md#L21); [FAST_MOVE_CATALOGUE.md:19](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/FAST_MOVE_CATALOGUE.md#L19); [matrix_q33.py:44-48,59-60](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/matrix_q33.py#L44-L60)
- OURS: T2/T2b LVN daily profile bin width fixed at `ATR(14, 1h)/10` approximated by `2.0 * ATR(14, 15m) / 10`, 3-bin smoothing — [PRE_REG_Q33.md:21](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md#L21); [MATRIX_REPORT.md:39](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md#L39); [matrix_q33.py:66-68](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/matrix_q33.py#L66-L68)
- OURS: T2 HVN defined as local max with volume >= median of non-empty bins; LVN defined as contiguous bins between two HVNs with smoothed volume <= 0.5 * median — [PRE_REG_Q33.md:21](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md#L21); [matrix_q33.py:16-28](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/matrix_q33.py#L16-L28)
- OURS: T2 traverse defined as crossing LVN band within <= 2 bars of 15m closes; T2b reject defined as wicking >= 1 bin into band and closing back outside on entry side — [PRE_REG_Q33.md:21](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md#L21); [matrix_q33.py:58-65](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/matrix_q33.py#L58-L65)
- OURS: T3/T3b 15m 3-bar Fair Value Gap (FVG), active for up to 96 bars until closed through; T3 first test (hold), T3b second test (breakthrough) — [PRE_REG_Q33.md:22](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md#L22); [matrix_q33.py:1-19](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/matrix_q33.py#L1-L19)
- OURS: T4 sweep-void breakout of prior 16-bar (240 min) high/low, closing beyond, with next prior-day HVN in move direction >= 1.0 * ATR(14, 15m) away, and CVD agreement — [PRE_REG_Q33.md:23](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md#L23); [matrix_q33.py:21-35](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/matrix_q33.py#L21-L35)
- OURS: F1 HTF trend filter combining 3 votes: close vs UTC VWAP, weekly POC migration direction, and EMA20(4h) slope over 6 4h bars (24h) — [PRE_REG_Q33.md:24](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md#L24); [matrix_q33.py:6-35](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/matrix_q33.py#L6-L35)
- OURS: F2 RSI(14) Wilder on 15m close partitioned at <40 (bear), 40-60 (neutral), >60 (bull) — [PRE_REG_Q33.md:24](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md#L24); [matrix_q33.py:43-48](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/matrix_q33.py#L43-L48)
- OURS: F3 2-bar CVD delta/volume z-score vs trailing 30 days (2880 15m bars), threshold at +/- 1.0 — [PRE_REG_Q33.md:24](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md#L24); [matrix_q33.py:37-41](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/matrix_q33.py#L37-L41)
- OURS: F7 Bollinger Band width percentile rank over trailing 672 bars (7 days), squeeze <= 20, expanded >= 80 — [PRE_REG_Q33.md:24](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md#L24); [matrix_q33.py:50-57](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/matrix_q33.py#L50-L57)
- OURS: F8 relative volume vs same time-of-day median over prior 20 days >= 1.5 with CVD agreement — [PRE_REG_Q33.md:24](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md#L24); [matrix_q33.py:59-63,24-26](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/matrix_q33.py#L59-L26)
- NOT_IN_DATA: Parameters for F4 (open interest change), F5 (long/short ratio), F6 (funding rate) because data was not available on machine — [PRE_REG_Q33.md:8](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md#L8); [MATRIX_REPORT.md:35](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md#L35)

---

### 3. BACKTESTS
- Report path: `MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md` — [LAYERS.md:78](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/system/LAYERS.md#L78); [layer_index.json:161](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/system/layer_index.json#L161); [MATRIX_REPORT.md:1](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md#L1)
- Underlying runner / cell data: `matrix_q33.py`, `MATRIX_CELLS.csv`, `MATRIX_SUMMARY.json` — [MATRIX_REPORT.md:3](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md#L3)
- Fee-net status: Fee-net tested. Cost model `FEES_ALL_TAKER` (0.05% entry + 0.05% timeout exit = 0.10% round turn taker) — [PRE_REG_Q33.md:10](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md#L10); [MATRIX_REPORT.md:5](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md#L5); [matrix_q33.py:16](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/matrix_q33.py#L16)
- In-sample / Out-of-sample breakdown: Pure event study across 2022-01-01 to 2026-10-11 (2,512,800 1m bars); no holdout held out. Split into first-half (2022-2024) and second-half (2025-2026) for temporal stability checking (survivor required same sign in both halves) — [PRE_REG_Q33.md:15](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md#L15); [MATRIX_REPORT.md:4,9-10](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md#L4-L10); [matrix_q33.py:6,38-39](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/matrix_q33.py#L6-L39)
- Number of trades (n):
  - Total cells generated: 336 cells — [MATRIX_REPORT.md:8](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md#L8)
  - Tested cells at primary horizon (n >= 300): 186 cells — [MATRIX_REPORT.md:8](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md#L8)
  - Underpowered cells (n 20 to 299): 89 cells — [MATRIX_REPORT.md:8-9](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md#L8-L9)
  - Sparse cells (n < 20): 61 cells (336 - 186 - 89) — [MATRIX_REPORT.md:8-9](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md#L8-L9)
  - Event counts per baseline trigger:
    - T1 BB-outside continuation: n = 8,689 events — [MATRIX_REPORT.md:14](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md#L14)
    - T1 BB-outside fade: n = 8,689 events — [MATRIX_REPORT.md:15](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md#L15)
    - T2 LVN traverse continuation: n = 1,491 events — [MATRIX_REPORT.md:16](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md#L16)
    - T2b LVN reject fade: n = 1,275 events — [MATRIX_REPORT.md:17](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md#L17)
    - T3 FVG first test hold: n = 19,282 events — [MATRIX_REPORT.md:18](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md#L18)
    - T3b FVG second test breakthrough: n = 8,427 events — [MATRIX_REPORT.md:19](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md#L19)
    - T4 sweep-void continuation: n = 1,870 events — [MATRIX_REPORT.md:20](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md#L20)
  - Headline outcome numbers:
    - Median gross edge across 186 tested cells at 60 min: +0.0003% — [MATRIX_REPORT.md:22](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md#L22)
    - Surviving cells (n >= 300, BH-FDR q <= 0.05 on placebo p, net mean > 0, same sign in both halves): 0 — [MATRIX_REPORT.md:9-10](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md#L9-L10)
    - Smallest FDR q-value observed: 0.62 — [MATRIX_REPORT.md:10,24](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md#L10-L24); [LAYERS.md:78](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/system/LAYERS.md#L78)
    - Positive net mean cells at 60 min: 0 of 186 cells — [MATRIX_REPORT.md:23](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md#L23)
    - Positive net mean cells at 240 min: 3 cells (best +0.039% on `T3b_through short F1=UP`, p=0.038, q=0.62, first half -0.034%, second half -0.071%) — [MATRIX_REPORT.md:23-25](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md#L23-L25)

---

### 4. KNOWN BUGS
- Ruling B172: OPEN, HIGH severity (opened 2026-10-10):
  "operator: the Sonnet ritual (relay/dispatcher sessions) uses a lot of tokens; investigate latest guidance and optimise session tokens + automatic accurate prompt creation"
  — Output of `python scripts/dev/lab_query.py rulings guidance`; [RULINGS.md](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/system/RULINGS.md)
- Ruling B105: WONTFIX, LOW severity (opened 2026-10-04):
  "Unit inconsistency in external PyPI package deflated-sharpe; guidance is to use per-period SR only"
  — Output of `python scripts/dev/lab_query.py rulings guidance`; [RULINGS.md](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/system/RULINGS.md)
- Known study shortcut / approximation: 1h ATR for LVN bin width was approximated as `2.0 * ATR(14, 15m)` rather than computed directly from 1h bars — [MATRIX_REPORT.md:39](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md#L39); [matrix_q33.py:67-68](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/matrix_q33.py#L67-L68)
- Known data exclusions in run: F4 (OI), F5 (L/S ratio), and F6 (funding) were NOT_IN_DATA on the machine and omitted from matrix execution — [PRE_REG_Q33.md:8](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md#L8); [MATRIX_REPORT.md:35](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md#L35)
- Known variant omissions in run: T4b (sweep reject) and T5/T6 (frozen Tom / Fabio events) were not run in the Q33 matrix — [PRE_REG_Q33.md:23](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md#L23); [MATRIX_REPORT.md:36](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md#L36)

---

### 5. CONFLUENCE
- Designed confluence relationship: Tom/Fabio cross-guidance was designed to test whether Bollinger Bands, LVN traversals/rejects, FVGs, and regime filters (VWAP, weekly POC, 4h EMA, RSI, CVD, BB squeeze, relative volume) could guide, filter, or confirm trades between Tom and Fabio — [layer_index.json:149,166](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/system/layer_index.json#L149-L166); [FAST_MOVE_CATALOGUE.md:1-4](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/FAST_MOVE_CATALOGUE.md#L1-L4)
- Live code isolation audit: Tom core and Fabio are completely isolated in live execution; they do not read or gate each other's state — [GUIDANCE_AUDIT.md:3-12](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/GUIDANCE_AUDIT.md#L3-L12)
  - Fabio v3 imports only stdlib, `orderflow_bars`, and its own siblings; does not import Tom or execution (`tests/test_b127_fabio_v3_isolation.py:1-8`) — [GUIDANCE_AUDIT.md:7](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/GUIDANCE_AUDIT.md#L7)
  - Tom core is Java (`SetupCandidatesBuilder.java`, `MarketDataSnapshot.java`) and does not read layer alerts — [GUIDANCE_AUDIT.md:8](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/GUIDANCE_AUDIT.md#L8)
  - Architectural boundary test specifies: "Layers are alert-only; Tom core is never filtered by layers" — [test_layer_boundaries.py:7](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/backtest/layers/test_layer_boundaries.py#L7); [GUIDANCE_AUDIT.md:10](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/GUIDANCE_AUDIT.md#L10)
  - Confluence hook `backtest/layers/consensus/` is observation-only; never gates, vetoes, or delays core — [GUIDANCE_AUDIT.md:9](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/GUIDANCE_AUDIT.md#L9)
  - `fabio_tag` in `backtest/tom_bt.py:280-290` is descriptive only and never a filter — [GUIDANCE_AUDIT.md:11](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/GUIDANCE_AUDIT.md#L11)
- Backtest confluence result: Because no cell survived in Q33 (smallest q 0.62), cross-guidance wiring was skipped (Q34 skipped) and no confluence gating was implemented — [LAYERS.md:74,78](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/system/LAYERS.md#L74-L78); [layer_index.json:150](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/system/layer_index.json#L150); [MATRIX_REPORT.md:44-46](file:///F:/MTS/gq/lf-guidance-gemini-facts/MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md#L44-L46)
