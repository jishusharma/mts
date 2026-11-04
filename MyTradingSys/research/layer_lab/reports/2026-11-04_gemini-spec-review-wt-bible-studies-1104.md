# Gemini Spec Review Report: WaveTrend Bible Studies Frozen Designs (2026-11-04)

- **Task**: `gemini-spec-review-wt-bible-studies-1104` [SOURCED: gemini-spec-review-wt-bible-studies-1104.json:15]
- **Audited Spec**: `MyTradingSys/research/wt_bible_studies_2026-11-04/SPEC.md` [SOURCED: SPEC.md:1-22]
- **Deliverable Review**: `MyTradingSys/research/wt_bible_studies_2026-11-04/REVIEW_GEMINI_1104.md`
- **Review Lens**: Gemini 3.8 Flash (independent cross-vendor review lens per `roles/lab_guy.md` Class C2 policy)
- **Status / Verdict**: VERDICT: FIX-FIRST (8 defects identified, OURS)

---

## 1. Summary of Defects

1. **Defect 1 [E1 Data / E7 Broken Gate] (HIGH / Blocker)**: Burned VALIDATION/HOLDOUT Data Contaminates Confirmation Gate.
   - Evidence: `SPEC.md:5` admits BTCUSDT VALIDATION and sealed HOLDOUT were counted during coordinator scratch exploratory passes (`n=1219 net -6.1 bp`, `2023-26 -12.0 bp` [SOURCED: SPEC.md:14]). Yet `SPEC.md:15` mandates that a cell PASSES only if VALIDATION confirms the sign and CI.
   - Reference: `splits.py:5-6` requires VALIDATION read once under frozen PRE_REG and HOLDOUT sealed.
   - Fix: Disallow BTCUSDT VALIDATION confirmation; require unpeeked asset or restrict to DEV exploratory findings; record holdout reads in `research/holdout_reads.csv` per `splits.py:101-110`.

2. **Defect 2 [E2 Definition / E1 Data] (MEDIUM)**: Non-Existent File Reference for Canonical Operator Rules.
   - Evidence: `SPEC.md:2` cites verbatim rules in `system/layer_bible/wavetrend.md`.
   - Command: `git ls-files "*wavetrend.md*"` returns 0 matches (OURS).
   - Fix: Update `SPEC.md:2` to cite the actual commit/session or commit the canonical file before locking the spec.

3. **Defect 3 [E5 Selection] (HIGH)**: Unbounded Multiple Testing Space ($m$) and Unfrozen Binning in Card 1.
   - Evidence: `SPEC.md:13` lists 5 feature dimensions without bin edges; `SPEC.md:14` lists 2 metrics; `SPEC.md:6` leaves $m$ open (`m = DEV variants + new cells`).
   - Fix: Freeze exact bin cutoffs, clarify 1D marginal vs factorial grid, and specify exact integer $m$ (e.g. $m=11$ for 1D slices, OURS).

4. **Defect 4 [E3 Implementation / E2 Definition] (HIGH)**: Ambiguous and Colloquial Divergence Event Definition in Card 1.
   - Evidence: `SPEC.md:11` defines event using "high around the earlier cross" and "price high since that dip", and `SPEC.md:12` uses ">= 3 down-cross waves above 0 since".
   - Fix: Define precise bar index offsets (e.g. $\pm 1$ bar around cross, OURS) and explicit wave conditions.

5. **Defect 5 [E4 Wrong Question / E3 Implementation] (HIGH)**: Mathematically Invalid "Paired Difference" in Card 2.
   - Evidence: `SPEC.md:19` specifies "paired net-bp difference nested minus baseline per TF", but nested trades are an unequal-sized subset of baseline trades with identical individual returns.
   - Fix: Reformulate as paired daily returns with explicit position sizing or two-sample difference in trade expectancies.

6. **Defect 6 [E1 Data / E3 Implementation] (MEDIUM)**: Card 3 Cycle Definition Relies on Non-Causal Lookahead.
   - Evidence: `SPEC.md:22` defines full cycle as "valid bottom up-cross to the last valid top before the next bottom", which cannot be determined causally at bar close for `layer_state.py`.
   - Fix: Define cycle boundaries from trough-to-trough or peak-to-peak, and define real-time state machine transitions causally.

7. **Defect 7 [E1 Data / E3 Implementation] (MEDIUM)**: Unspecified Multi-Timeframe Alignment for 4h Slope.
   - Evidence: `SPEC.md:13,19` cites "4h wt1 slope" without specifying closed-bar synchronization.
   - Reference: `wavetrend.py:62-70` defines `htf_index()` for closed-bar alignment.
   - Fix: Require explicit closed-bar indexing via `wavetrend.py:htf_index()`.

8. **Defect 8 [E6 Execution Realism] (LOW)**: Omission of Slippage and Execution Latency in 5m/15m Swings.
   - Evidence: `SPEC.md:3` budgets 0.14% round-trip fee with zero slippage for bar-close market entries.
   - Fix: Specify taker execution with a 1–2 bp slippage buffer per leg (OURS).

---

## 2. Verification Command

```powershell
python -c "import pathlib; assert 'VERDICT:' in pathlib.Path('MyTradingSys/research/wt_bible_studies_2026-11-04/REVIEW_GEMINI_1104.md').read_text()"
```
Output: Exit 0 (Pass).
