# Layer Lab Report: tf-g1-prime-captions-1113

- **Date:** 2026-11-13 (UTC)
- **Task ID:** `tf-g1-prime-captions-1113`
- **Output:** [ANSWERS.md](file:///F:/MTS/gq/tf-g1-prime-captions-1113/MyTradingSys/research/layer_lab/tf_extract_1113/tf-g1-prime-captions-1113/ANSWERS.md)
- **Analyst Transcripts Checked:**
  - `raw_transcripts_canonical/O5s9zWI0n2s_raw.txt` (Tom Vorwald EN: "How to Finally Become a Profitable Trader! (4-Step Framework)")
  - `raw_transcripts_canonical/VHhvg96W6lc_raw.txt` (Fabervaale ENG: "If I Had to Start from Zero, I’d Focus on This.")
  - `raw_transcripts_canonical/9IliXww64uM_raw.txt` (Andrea Cimi: "Using Orderflow to Make $4000 in 1h")

## Verification & Gate
Executed gate command:
`python scripts/dev/verify_extract_quotes.py MyTradingSys/research/layer_lab/tf_extract_1113/tf-g1-prime-captions-1113/ANSWERS.md`
Result: PASS: 0 problem(s), 16 quotes verified.

## Gap Answers Summary

1. **Q9 (Absorption / Big-trade size / Footprint):**
   - **Verdict: PARTIAL**
   - Fabio (VHhvg96W6lc) states that absorption shows as big orders on the far side of balance or in delta profile, and trades test of big trades.
   - Exact numerical big-trade size and "almost zero" price result are **NOT_SEEN**.

2. **Q11 (Proof count / Entry confirmations):**
   - **Verdict: PARTIAL**
   - Tom (O5s9zWI0n2s) specifies a 4-step framework / 4 pieces of market information (buyers/sellers, balance profile, target zones, open gap), waiting for confirming setup (range setup on footprint, inside/outside bars, balance breakout, or PBD).
   - Numerical proof count threshold is **NOT_SEEN**.

3. **Q12 (Risk per trade / Size / Daily loss / Hit rate / R):**
   - **Verdict: PARTIAL**
   - Tom (O5s9zWI0n2s) places risk structurally below the setup or strong buyer zone.
   - Fabio (VHhvg96W6lc) details reinvesting 1/3 of floating profit into additional positions for 6-8R expansion while protecting capital.
   - Percentage size per trade, daily loss limits, and hit rates are **NOT_SEEN**.

4. **Q13 (Speaker of 9IliXww64uM):**
   - **Verdict: ANSWER**
   - Settled: Andrea Cimi.
   - Title: "Using Orderflow to Make $4000 in 1h", Channel: "Andrea Cimi" (`@AndreaCimi`), confirmed via YouTube oEmbed API and spoken reference to template "Achimi ES" in transcript.
