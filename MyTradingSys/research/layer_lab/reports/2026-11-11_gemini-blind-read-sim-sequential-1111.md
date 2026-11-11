COUNTS: CONSISTENT=6 CONTRADICTION=0 NOT_IN_DATA=0

# Independent Gemini Blind Read: sim_sequential.py Promote/Kill Rule Against Docstring

- **Card**: `gemini-blind-read-sim-sequential-1111`
- **Lane**: CODEX
- **Date**: 2026-11-11 UTC
- **Reader**: Gemini (`gemini-3.8-flash-low`, JIS-NUC throwaway worktree `gemini-q/gemini-blind-read-sim-sequential-1111`)
- **Scope In (read-only)**:
  - `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-f1-testnet-design/sim_sequential.py` (read)
  - `MyTradingSys/research/edge_hunt_2026-11-09/results/eh-f1-testnet-design/test_sim_sequential.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-blind-read-sim-sequential-1111.md` (new)
- **Scope Out Respected**:
  - No edit to source files; no live-tree edit; no deploy; no `.secrets` or `.env` read; read-only audit.
  - Zero push; no `sync.py ship`.
- **Audit Mandate**:
  - Independent blind read of `sim_sequential.py` against its module docstring rule:
    1. E+ formula: lambda-grid mean of prod(1 + lambda*(x - mu0)) with mu0 = 0
    2. E- formula: grid mean of prod(1 - lambda*(x - delta))
    3. lambda ranges / upper bounds respect the bounds: lambda in (0, 1/(mu0 - a)] for E+, lambda in (0, 1/(b - delta)] for E-
    4. Promote threshold and n_min: PROMOTE at E+ >= 1/alpha after n_min_promote
    5. Kill threshold and n_min: KILL at E- >= 1/beta after n_min_kill
    6. Retire at n_max: RETIRE at n_max (undecided)

---

## 1. Executive Summary

- Total clauses audited: **6**
- Counts: **CONSISTENT = 6, CONTRADICTION = 0, NOT_IN_DATA = 0** (sum 6)
- The implementation in `sim_sequential.py` (`e_promote`, `e_kill`, `decide`, and default module constants / `RuleCfg`) strictly and faithfully implements every mathematical formula, bound, stopping time threshold, and minimum observation gate specified in its module docstring.
- All 12 unit tests in `test_sim_sequential.py` pass cleanly and independently verify the hand values, boundary checks, Ville supermartingale bound, and decision logic.

---

## 2. Clause Audit Table

| # | Clause Description | Docstring Specification | Implementation & Test Evidence | Status |
|---|---|---|---|---|
| 1 | E+ formula | SOURCED (`sim_sequential.py:7-8`): `"PROMOTE process E+_n = mean over lambda in a grid of prod_i (1 + lambda * (x_i - mu0)), mu0 = 0 R"` | SOURCED (`sim_sequential.py:38,46,137,146-147`): `MU0 = 0.0`; `LAMBDA_FRACS = (1 / 16, 1 / 8, 1 / 4, 1 / 2, 3 / 4)`; `e_promote()` calculates `np.stack([np.cumsum(np.log1p(f * lam_max * (x - mu0)), axis=1) for f in fracs])` followed by `_log_mixture()` returning `np.exp(...)` which computes the exact arithmetic mean of `prod(1 + lambda * (x - mu0))` across the grid via log-sum-exp. Verified by hand calculation in `test_sim_sequential.py:27-34`. | CONSISTENT |
| 2 | E- formula | SOURCED (`sim_sequential.py:10-11`): `"KILL process E-_n = mean over the grid of prod_i (1 - lambda * (x_i - delta)), delta = the smallest edge worth a slot"` | SOURCED (`sim_sequential.py:40,46,150,158-160`): `DELTA_KILL = 0.25`; `e_kill()` calculates `np.stack([np.cumsum(np.log1p(-f * lam_max * (x - delta)), axis=1) for f in fracs])` followed by `_log_mixture()` returning `np.exp(...)` which computes the arithmetic mean of `prod(1 - lambda * (x - delta))` across the grid. Verified by hand calculation in `test_sim_sequential.py:36-43`. | CONSISTENT |
| 3 | lambda upper bounds | SOURCED (`sim_sequential.py:8,11`): `"lambda in (0, 1/(mu0 - a)]"` and `"lambda in (0, 1/(b - delta)]"` | SOURCED (`sim_sequential.py:46,145-146,158-159`): `lam_max = 1.0 / (mu0 - a)` for promote, `lam_max = 1.0 / (b - delta)` for kill; grid values are `f * lam_max` where `f in (1/16, 1/8, 1/4, 1/2, 3/4)`. Because `0 < f < 1`, every lambda is strictly in `(0, lam_max]`. Bounds `x >= a` and `x <= b` enforced with `ValueError` (`sim_sequential.py:143-144,156-157`), tested in `test_sim_sequential.py:45-50`. | CONSISTENT |
| 4 | Promote threshold & n_min | SOURCED (`sim_sequential.py:13`): `"PROMOTE at the first n >= n_min_promote with E+_n >= 1/alpha_slot"` | SOURCED (`sim_sequential.py:41,43,165,167,187,189,197-199`): `ALPHA_SLOT = 0.05 / 4`; `N_MIN_PROMOTE = 30`; `promote_ok = (ep >= 1.0 / cfg.alpha) & (idx >= cfg.n_min_promote)`; `first_p = np.where(promote_ok.any(axis=1), promote_ok.argmax(axis=1) + 1, n + 1)`; code set to `1` at `first_p`. Tested in `test_sim_sequential.py:52-59,69-74`. | CONSISTENT |
| 5 | Kill threshold & n_min | SOURCED (`sim_sequential.py:14`): `"KILL at the first n >= n_min_kill with E-_n >= 1/beta"` | SOURCED (`sim_sequential.py:42,44,166,168,188,190,194-196`): `BETA_KILL = 0.10`; `N_MIN_KILL = 10`; `kill_ok = (ek >= 1.0 / cfg.beta) & (idx >= cfg.n_min_kill)`; `first_k = np.where(kill_ok.any(axis=1), kill_ok.argmax(axis=1) + 1, n + 1)`; code set to `-1` at `first_k` (with tie-break `kill_first = first_k <= first_p`). Tested in `test_sim_sequential.py:61-67,75-81`. | CONSISTENT |
| 6 | Retire at n_max | SOURCED (`sim_sequential.py:15`): `"RETIRE at n_max (undecided: neither a proven edge nor a proven loser; the slot is freed)"` | SOURCED (`sim_sequential.py:45,169,182,191-192,195,198`): `N_MAX = 150`; `x = x[:, : cfg.n_max]`; initial `code = np.zeros(paths, dtype=int)` (where `0 = RETIRE at n_max`, `sim_sequential.py:178`); paths where neither promote nor kill fires before `n_max` retain code `0` and decision trade `n_dec = n` (`cfg.n_max`). Tested in `test_sim_sequential.py:82-86`. | CONSISTENT |
