# Formula spec text lab — 2026-10-23

**Date:** 2026-10-23  
**Runner:** Gemini Flash (Antigravity, JIS-NUC)  
**Card:** `lab-formula-spec-text`  
**Decision source:** `MyTradingSys/system/card_specs/codex-unstick-2026-10-23.md` (builder codex-unstick: F01 decision + F18-F21 sub-id depth delegated to lab-formula-spec-recount)

---

## 1. Summary of Resolution & Deliverables

- **Resolution of F01 blocker:**
  - `F01` DEV tape example cites 15 consecutive 1h bar opens (2022-04-12 20:00 UTC through 2022-04-13 10:00 UTC) from `F:/MTS/data/bigtrade/cache/perp/klines_1h.npz` with exact Wilder RSI value `57.830163407447`% (`57.8302`%).
  - A second worked example labelled `SYNTHETIC` is retained under F01 with the classic close changes `[+56, +40, -70]` (period 3):
    - Gain mean: $(56 + 40 + 0) / 3 = 32$
    - Loss mean: $(0 + 0 + 70) / 3 = 23.333333$
    - $RS = 32 / (70 / 3) = 48 / 35$
    - $\text{RSI} = 100 - 100 / (1 + 48/35) = 4800 / 83 = 57.831325\dots\%$ (displayed as `57.8313`%, correcting the legacy erroneous `57.8125`).
- **Correction of arithmetic defects:**
  - `F11.4` and `F11.5`: average fill is `62751.9875` (corrected from `62751.992997`).
  - `F11.6`: inverse stop loss USD is `-0.399847` (corrected from `-0.400484`).
- **Header truthfulness in `FORMULAS_SPEC.md`:**
  - Line 3 and line 17 updated to explicitly document that all worked examples are derived directly from the DEV tape (`t < 1719792000000`), except the second F01 synthetic twin and self-contained sub-ID illustrations.
- **Verification test suite:**
  - `MyTradingSys/research/layer_lab/formula_spec_text/test_formula_spec.py` asserts:
    1. Every formula ID and sub-ID has a specification section and worked example matching `examples.json`.
    2. Independent mathematical re-implementation matches expected values within floating point tolerance across all tape records.
    3. The synthetic F01 twin with `57.8313`% is present in `FORMULAS_SPEC.md`.

---

## 2. Verification Commands & Outputs

1. `python -m unittest MyTradingSys/research/layer_lab/formula_spec_text/test_formula_spec.py`
   - Output: `Ran 2 tests in 0.044s. OK`
2. `python -m unittest MyTradingSys/tests/test_gate_discovery_b150.py`
   - Output: `Ran 2 tests in 0.058s. OK`
3. Registered in `scripts/dev/run_extra_tests.py` under `EXTRA` (passes as part of the 129 extra tests).
