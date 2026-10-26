# W3 KAPPA REPORT 2026-10-01 - session MTS-2026-10-01-1900Z-CLD-ANA-w3-kappa

branch_alias: claude/serene-hamilton-loxx49. Usage: 85 assumed (no header readable). No subagents.

## 1. Method
- Read the 74-row blind packet (W3_BLIND_PACKET_2026-10-01.md) and decided one verdict per row with the packet's four definitions only.
- Evidence came from raw_transcripts_canonical/*_raw.txt via regex searches (value area, R:R, stop/swing, targets, VWAP, CVD, absorption, volume spike, speed, order book, shapes, funding, confluence) plus full reads of UrZ4vpHJ97g, and targeted reads of kXhIAug0Gh8, 43JaKHRvxHk, BVpYGKz9PBU, qLnQan0KGmQ. Citations are file:line, where line = the transcript's paragraph line (most files have 6-19 long lines).
- Reader CSV committed (77003ff) before the first reader's verdicts were opened. FIRST CSV then built by parsing the verdict column of PROVENANCE_AUDIT_TOM.md section 2-6 (74 rows, exactly one verdict each).
- Command: `python scripts/dev/kappa_check.py MyTradingSys/research/_archive/loose_2026-10/W3_KAPPA_FIRST_2026-10-01.csv MyTradingSys/research/_archive/loose_2026-10/W3_KAPPA_READER_2026-10-01.csv`

## 2. Blindness status
Held. None of the five barred files was opened before the reader CSV was committed; no extracts/ file was read. CLOUD_INBOX.md had one note (from 1604Z-CLD-ANA-revalidate-tom-fabio), not addressed to this session; not edited.
Limits of this read (flag, not smoothing): (a) search-based, not a full read of 1.7 MB of transcripts; a quote missed by my regexes would turn a CONCEPT-ONLY/SOURCED into NO-SOURCE. (b) I did not identify speakers per file; I used World-Champion-titled files and did not treat FawPrRUGNpk, 8CWKfoSJu3c, Wvq1TZh8aF0 or cQ-y1oULkBw (other speakers by title/content) as Tom. (c) The packet has no code, so rows were judged from their descriptions only. (d) The claimed-source column (CE:...) was used as rule text only, not as evidence.

## 3. Kappa
n=74 observed agreement=0.662 expected=0.390 kappa=0.446 (threshold 0.6): BELOW threshold.
Binary view (NO-SOURCE vs not), computed by hand from the confusion table: both NO-SOURCE 22, first only 14, reader only 8, neither 30; observed 0.703, kappa 0.403.

## 4. Confusion table (first reader = rows, this reader = columns)
```
  first=DATA-PLUMBING second=DATA-PLUMBING: 3
  first=NO-SOURCE second=DATA-PLUMBING: 5
  first=NO-SOURCE second=NO-SOURCE: 22
  first=NO-SOURCE second=TOM-CONCEPT-ONLY: 9
  first=TOM-CONCEPT-ONLY second=DATA-PLUMBING: 1
  first=TOM-CONCEPT-ONLY second=NO-SOURCE: 8
  first=TOM-CONCEPT-ONLY second=TOM-CONCEPT-ONLY: 22
  first=TOM-CONCEPT-ONLY second=TOM-SOURCED: 2
  first=TOM-SOURCED second=TOM-SOURCED: 2
```
Verdict totals: first = NO-SOURCE 36, TOM-CONCEPT-ONLY 33, TOM-SOURCED 2, DATA-PLUMBING 3. Reader = NO-SOURCE 30, TOM-CONCEPT-ONLY 31, TOM-SOURCED 4, DATA-PLUMBING 9.

## 5. Disagreeing rows (25 of 74; first -> reader)
| id | first | reader |
|---|---|---|
| A05 | TOM-CONCEPT-ONLY | TOM-SOURCED |
| A07 | TOM-CONCEPT-ONLY | TOM-SOURCED |
| A11 | NO-SOURCE | TOM-CONCEPT-ONLY |
| A12 | TOM-CONCEPT-ONLY | NO-SOURCE |
| A13 | NO-SOURCE | TOM-CONCEPT-ONLY |
| A16 | TOM-CONCEPT-ONLY | NO-SOURCE |
| A18 | NO-SOURCE | TOM-CONCEPT-ONLY |
| A21 | NO-SOURCE | TOM-CONCEPT-ONLY |
| A24 | NO-SOURCE | TOM-CONCEPT-ONLY |
| A25 | TOM-CONCEPT-ONLY | NO-SOURCE |
| A26 | TOM-CONCEPT-ONLY | NO-SOURCE |
| A28 | TOM-CONCEPT-ONLY | NO-SOURCE |
| B03 | TOM-CONCEPT-ONLY | NO-SOURCE |
| M02 | TOM-CONCEPT-ONLY | DATA-PLUMBING |
| M03 | NO-SOURCE | TOM-CONCEPT-ONLY |
| M04 | NO-SOURCE | TOM-CONCEPT-ONLY |
| M07 | TOM-CONCEPT-ONLY | NO-SOURCE |
| M09 | NO-SOURCE | DATA-PLUMBING |
| M12 | NO-SOURCE | TOM-CONCEPT-ONLY |
| P09 | NO-SOURCE | TOM-CONCEPT-ONLY |
| P10 | TOM-CONCEPT-ONLY | NO-SOURCE |
| V06 | NO-SOURCE | DATA-PLUMBING |
| V08 | NO-SOURCE | DATA-PLUMBING |
| V09 | NO-SOURCE | DATA-PLUMBING |
| V12 | NO-SOURCE | DATA-PLUMBING |

Where they split:
- First NO-SOURCE, reader CONCEPT-ONLY (9): A11, A13, A18, A21, A24, M03, M04, M12, P09. Tom names the idea (minimum usable R:R from hit rate; wait for price at the area; counter and breakout trades outside value; double distribution/P shape; reading the order book) and the number is ours. The first reader failed these because the idea was not quoted at the specific role; I passed them because the definition says CONCEPT-ONLY covers "number is ours".
- First CONCEPT-ONLY, reader NO-SOURCE (8): A12, A16, A25, A26, A28, M07, P10, B03. Mostly where the code gives the idea a role or table Tom does not (state blocks, rank table, FVG no-setup against Tom's gap-close trades, sigma bands, 7-point count). My A12 (friction 0.75) is NO-SOURCE because no transcript mentions slippage or friction; the first reader found fee mention in Q06 which my searches did not surface.
- DATA-PLUMBING boundary (5 with first NO-SOURCE: M09, V06, V08, V09, V12; plus M02 first CONCEPT-ONLY): alert, display and unit rows. This is a definition gap: "no trading meaning" vs "no Tom idea".
- Source-level: A05 and A07 (reader SOURCED, first CONCEPT-ONLY). My reading: Tom states stop below the last swing low (kXhIAug0Gh8:19, UrZ4vpHJ97g:7) and targets at value areas/naked POCs/VWAP (ODdF0Bn_KSc:7); the first reader noted the short side contradicts. The packet gives no long/short split.

## 6. One-line verdict on the 36 NO-SOURCE count
kappa 0.446 < 0.6, so the headline 36 is reader-dependent: only 22 rows are NO-SOURCE under both readers (a floor), this reader finds 30, and 14 of the 36 flip on definition boundaries (CONCEPT-ONLY vs NO-SOURCE, NO-SOURCE vs DATA-PLUMBING) rather than on missing evidence.

## 7. Per-row verdict and citation (this reader)
| id | verdict | transcript file:line, or 'no quote found' |
|---|---|---|
| A01 | TOM-SOURCED | K8qtT2_axPo:7; 1utSjHs_Mq8:19 (70% of trading activity) |
| A02 | TOM-CONCEPT-ONLY | YmygDgtoxO8:19; VOiy8mAALWA:7 (overlap levels); 0.3% ours |
| A03 | NO-SOURCE | no quote found |
| A04 | NO-SOURCE | no quote found |
| A05 | TOM-SOURCED | kXhIAug0Gh8:19; UrZ4vpHJ97g:7; 4MoNjEQ2Dd8:19 (stop below last swing low) |
| A06 | TOM-CONCEPT-ONLY | kXhIAug0Gh8:19 (last swing low); per-zone TF map ours |
| A07 | TOM-SOURCED | ODdF0Bn_KSc:7 (value areas, naked POCs); VumVuGnCcFM:19 (VWAP as target); aursfDVYzUk:7 |
| A08 | NO-SOURCE | no quote found (UrZ4vpHJ97g:7 and 43JaKHRvxHk:19 tie min R:R to hit rate, no fixed 2.0) |
| A09 | NO-SOURCE | no quote found |
| A10 | NO-SOURCE | no quote found |
| A11 | TOM-CONCEPT-ONLY | 43JaKHRvxHk:19 (minimum usable R:R from hit rate); 1.5 ours |
| A12 | NO-SOURCE | no quote found (no slippage/friction mention in any transcript) |
| A13 | TOM-CONCEPT-ONLY | 43JaKHRvxHk:19; 3JqMyzE8jIQ:13 (2:1 example only, hit rate needed); qLnQan0KGmQ has no 2:1; net gate 2.0 ours |
| A14 | NO-SOURCE | no quote found |
| A15 | NO-SOURCE | no quote found |
| A16 | NO-SOURCE | no quote found |
| A17 | DATA-PLUMBING | no quote found (output cap and minimum bar count) |
| A18 | TOM-CONCEPT-ONLY | ODdF0Bn_KSc:7 (wait for market to activate the area); 0.1% ours |
| A19 | NO-SOURCE | no quote found (per-zone-type distance caps) |
| A20 | TOM-CONCEPT-ONLY | 43JaKHRvxHk:19 (balance: shorts upper, longs lower); C9n_d91Uitc:13 (return to equilibrium); POC split by proxy |
| A21 | TOM-CONCEPT-ONLY | aursfDVYzUk:7 (above VA: counter trades and breakouts both) |
| A22 | NO-SOURCE | BVpYGKz9PBU:19 has short trades below yesterday VAL; no long-only rule |
| A23 | TOM-CONCEPT-ONLY | 43JaKHRvxHk:19 (VWAP sideways = balance); CVD-flat conjunction ours |
| A24 | TOM-CONCEPT-ONLY | VumVuGnCcFM:19 (far outside value = trend continuation likely); YmygDgtoxO8:19 |
| A25 | NO-SOURCE | no quote found (unreachable states; blocking roles never given) |
| A26 | NO-SOURCE | no quote found |
| A27 | TOM-CONCEPT-ONLY | 43JaKHRvxHk:19 (VWAP scalps both ways in balance; trend continuation); bands not Tom |
| A28 | NO-SOURCE | 96iPFDpXEcU:7; 3JqMyzE8jIQ:13; Fj4FDZQxw0I:19 Tom trades FVG closes; "no setup" contradicts |
| A29 | TOM-CONCEPT-ONLY | YmygDgtoxO8:19; ODdF0Bn_KSc:7; 3JqMyzE8jIQ:13; sigma bands and 5m/15m swings not quoted |
| P01 | TOM-CONCEPT-ONLY | 1utSjHs_Mq8:19 (rejection at balance areas, profile sense); no candle-wick rule |
| P02 | NO-SOURCE | no quote found |
| P03 | TOM-CONCEPT-ONLY | 4P5WAxyPCis:13; 4MoNjEQ2Dd8:19 (absorption); numbers ours |
| P04 | TOM-CONCEPT-ONLY | oa8kxSLLkAo:19 (zero on one side = no interest); numbers ours |
| P05 | TOM-CONCEPT-ONLY | rFPCtOcfUMI:13 (delta drops with aggressive sellers = reversal entry); numbers ours |
| P06 | TOM-CONCEPT-ONLY | KEe_CWHyuSg:13; HySZZSjMxF8:12 (volume spike / exhaustion); 2.0x/240 ours |
| P07 | TOM-CONCEPT-ONLY | 3o1VVsfBmmU:19; -dMWA_bbm3o:7 (market speed); formula ours |
| P08 | TOM-CONCEPT-ONLY | ODdF0Bn_KSc:7; rFPCtOcfUMI:13 (cumulative delta); alignment rule ours |
| P09 | TOM-CONCEPT-ONLY | 4MoNjEQ2Dd8:19 (read big orders in book); 1.5/0.67 ours |
| P10 | NO-SOURCE | no quote found (equal-weight 7-point count) |
| M01 | DATA-PLUMBING | no quote found |
| M02 | DATA-PLUMBING | VumVuGnCcFM:19 (VWAP session-based) only; UTC windows are plumbing |
| M03 | TOM-CONCEPT-ONLY | K8qtT2_axPo:7 (double distribution); 0.6 ours |
| M04 | TOM-CONCEPT-ONLY | gFJBg8Bsw68:7 (P-shape); 0.8/1.2 ours |
| M05 | TOM-CONCEPT-ONLY | YmygDgtoxO8:19 (volume nodes); 4P5WAxyPCis:13 (low-volume area); smoothing ours |
| M06 | TOM-CONCEPT-ONLY | 43JaKHRvxHk:19 (VWAP sideways/lower); VumVuGnCcFM:19; 0.05% ours |
| M07 | NO-SOURCE | no quote found (Tom rejects bands: 4VXpUjhKG2U:7 is Bollinger) |
| M08 | TOM-CONCEPT-ONLY | rFPCtOcfUMI:13 (delta drops/rises); 2% and 20/20 ours |
| M09 | DATA-PLUMBING | no quote found |
| M10 | TOM-CONCEPT-ONLY | kXhIAug0Gh8:19 (last swing low); lookbacks ours |
| M11 | NO-SOURCE | no quote found |
| M12 | TOM-CONCEPT-ONLY | 4MoNjEQ2Dd8:19 (order book big orders); +-1%/100 levels ours |
| M13 | TOM-CONCEPT-ONLY | YmygDgtoxO8:19 (above VAH/below VAL unfair); derived location |
| M14 | TOM-CONCEPT-ONLY | 3o1VVsfBmmU:19 (speed); KEe_CWHyuSg:13 (volume spike); numbers ours |
| B01 | NO-SOURCE | no quote found |
| B02 | NO-SOURCE | no quote found |
| B03 | NO-SOURCE | oa8kxSLLkAo:19 uses finished auction as signal, not a veto |
| B04 | NO-SOURCE | no quote found |
| B05 | TOM-CONCEPT-ONLY | kXhIAug0Gh8:19 (swing stop); ODdF0Bn_KSc:7 (targets) |
| B06 | TOM-CONCEPT-ONLY | ODdF0Bn_KSc:7; aursfDVYzUk:7 (counter vs breakout at areas); 0.1% ours |
| B07 | NO-SOURCE | 43JaKHRvxHk:19 supports VWAP-sideways only; funding gate: no quote found |
| V01 | NO-SOURCE | no quote found |
| V02 | NO-SOURCE | no quote found |
| V03 | NO-SOURCE | no quote found |
| V04 | TOM-CONCEPT-ONLY | VumVuGnCcFM:19; YkclL6xgu-s:7 (below value, trend continuation likely) |
| V05 | NO-SOURCE | no quote found |
| V06 | DATA-PLUMBING | no quote found (display only) |
| V07 | NO-SOURCE | no quote found |
| V08 | DATA-PLUMBING | no quote found (alert hysteresis/cooldown) |
| V09 | DATA-PLUMBING | no quote found (popup logic) |
| V10 | NO-SOURCE | no quote found |
| V11 | DATA-PLUMBING | no quote found (staleness timers) |
| V12 | DATA-PLUMBING | no quote found (labels) |
| K01 | TOM-SOURCED | BVpYGKz9PBU:19 (secure initial profits at precisely 3:1) |
| K02 | NO-SOURCE | 43JaKHRvxHk:19 and UrZ4vpHJ97g:7 tie minimum R:R to hit rate; no quote for "never lowers" |
