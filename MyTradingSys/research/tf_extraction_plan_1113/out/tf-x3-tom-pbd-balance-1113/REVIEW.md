# REVIEW tf-x3 Tom PbD / balance (reviewer: Haiku, 2026-11-13)

Gate: `python scripts/dev/verify_extract_quotes.py ANSWERS.md` exit 0, 33 quotes OK, PASS: 0 problems.
Blocks checked: Q1, Q3, Q8, Q14 (all 4 blocks; quotes read in transcript context).

| block | quote supports claim Y/N | note |
|---|---|---|
| Q1 | Y | P/B/D meanings (m3IM) Y. "closing-price count" named, never numbered (jXR1, Ly62) Y. "round about 30% of markets ... The other 70%" (jXR1) supports the 30/70 split. "about 70% balance" (Ly62 "sideways phases make up about 70% of the market") Y. |
| Q3 | Y for the acceptance wording; N for one quote | Ly62 "ideally at the closing price" and Sy-x5 "more time above or below" support the build-up read. The 0CrkB quote "as long as the market remains above the 325 level based on the closing price" is about an unnamed chart level; it supports closing-price language, not an acceptance form. Weak, replace. |
| Q8 | Y except the TPO term | 1utS quotes support "30 minute" blocks and "I haven't summed up these 30 minute bars into a single profile" Y. "TPO" is not in 1utS; it is in K8qtT2 ("TPO time price opportunity"). The verdict cites 1utS for TPO, so cite K8qt or drop TPO. VWAP session-based and "not useful" Y. |
| Q14 | Y | "examine a market like Bitcoin" (m3IM) Y. "perfect B structure twice" (0CrkB) Y. "acceptance again below 72,000" Y. Header of 0CrkbfuIhkc shows Published 2026-05-15 Y. "S&P 500, Nasdaq, and Bitcoin" in 0CrkB Y. |

NOT_SEEN grep (keyword pairs, 10 ids):
- Q1 closing-count number (closes / times / candles near "closing price"): 0 hits. Consistent.
- Q3 acceptance + bars/closes: 0 hits. Consistent.
- Q14 Bitcoin + stop/target/entry: 0 hits. Consistent.
- Q8 no-cash market (weekend, crypto, 24h) near "profile": 0 hits. Consistent.

SOURCED numbers not in a quote: none beyond the 70% and 30% which are quoted; 72,000 quoted.
GUEST check: no guest speaks. Patrick, Christopher, and others are mentioned as students only. Header speakers differ by intro name (ASR); not a guest issue.

Verdict: FIX

Exact lines to fix:
1. Q8 verdict: replace "30-minute TPO block as the profile unit" with "30-minute blocks as the profile unit" (the cited 1utS quotes do not say TPO), or add the K8qtT2 "TPO time price opportunity" quote to the block.
2. Q3 block: delete the quote "as long as the market remains above the 325 level based on the closing price." (0CrkbfuIhkc), or keep it only with the verdict stating it is an unnamed level, not an acceptance form.

Fixes applied 2026-11-13 by extractor; re-check by tf-r1.
