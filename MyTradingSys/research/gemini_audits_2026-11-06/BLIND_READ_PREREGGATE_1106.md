# Blind Read Audit: `scripts/dev/prereg_gate.py` (2026-11-06)

- **Card**: `gemini-blind-read-of-scripts-dev-prereg-` (SOURCED: `MyTradingSys/system/tasks/gemini-blind-read-of-scripts-dev-prereg-.json:262`)
- **Target**: `scripts/dev/prereg_gate.py` (`71` lines, SOURCED: `scripts/dev/prereg_gate.py:1-71`)
- **Commit audited**: `e6f36eb61268` (`prereg_gate --m auto counts TRIAL_LEDGER (REGATE_AUDIT fix 1) + eur_low kill scope (fix 4)`, SOURCED: `MyTradingSys/system/tasks/gemini-blind-read-of-scripts-dev-prereg-.json:269-271`)
- **Method**: Read `scripts/dev/prereg_gate.py:1-71`, verified the mathematical formulas and input guards, and independently recomputed `z_holm`, `MDE`, `MDE + cost`, `n needed`, and gate verdict by hand using the standard normal quantile $\Phi^{-1}(1 - 0.05 / (2m))$ across 5 `(n, sd, m)` triples before comparing with the script's CLI output. Read-only on `scripts/dev/prereg_gate.py`; no `VALIDATION` or `HOLDOUT` data read.

## 1. Formula & Guard Verification (`scripts/dev/prereg_gate.py:1-71`)

1. **Two-sided Holm normal quantile (`scripts/dev/prereg_gate.py:25-26`)**:
   $$z_{\text{holm}}(m) = \Phi^{-1}\!\left(1 - \frac{0.05}{2m}\right)$$
   Implemented via `NormalDist().inv_cdf(1 - 0.05 / (2 * m))` (`:26`).
2. **Minimum Detectable Effect (`scripts/dev/prereg_gate.py:29-30`)**:
   $$\text{MDE}(n, \text{sd}, m) = \frac{(z_{\text{holm}}(m) + 0.84) \cdot \text{sd}}{\sqrt{n}}$$
   where `POWER_Z = 0.84` ($80\%$ power one-sided normal quantile $\Phi^{-1}(0.80) \approx 0.8416$, labeled `OURS` at `:6, 22`).
3. **Gate Rule & Required Sample Size (`scripts/dev/prereg_gate.py:21, 62-67`)**:
   - `MAX_PLAUSIBLE_GROSS = 0.30` R (labeled `OURS` at `:6, 21`).
   - Passes (`ok = True`, exit `0`, prints `PASS: may freeze`) iff $\text{MDE} + \text{cost} \le \text{max\_gross}$; otherwise exits `1` (`BLOCK: do not freeze`).
   - Required independent units $n_{\text{needed}} = \left(\frac{(z_{\text{holm}}(m) + 0.84)\cdot \text{sd}}{\text{max\_gross} - \text{cost}}\right)^2$ when $\text{max\_gross} > \text{cost}$, else $\infty$ (`:62`).
4. **Input Validation & Repo-Wide `--m auto` (`scripts/dev/prereg_gate.py:45-60`)**:
   - `--m auto` calls `verdicts.count_with_ledger(a.verdicts_csv, a.ledger_csv, "DEV")` and adds `a.new_cells` (`:45-47`), counting both `VERDICTS.csv` and `TRIAL_LEDGER.csv` DEV rows.
   - Rejects `n <= 0 or sd <= 0 or m < 1 or cost < 0` with exit code `2` (`:54-56`).
   - Rejects unmeasured placeholder `sd <= 1` unless `--sd-source <file:line>` is non-empty, with exit code `2` (`:57-60`).

## 2. Hand Recomputation vs Script Output for 5 `(n, sd, m)` Triples (at `--cost 0.05`)

| # | Triple `(n, sd, m)` | Hand $z_{\text{holm}} = \Phi^{-1}(1 - \frac{0.025}{m})$ (OURS) | Hand $\text{MDE} = \frac{(z_{\text{holm}} + 0.84)\,\text{sd}}{\sqrt{n}}$ (OURS) | Hand $\text{MDE} + 0.05$ / $n_{\text{needed}}$ (OURS) | `prereg_gate.py` Output (`scripts/dev/prereg_gate.py:64-67`) | Status |
|---|---|---|---|---|---|---|
| 1 | `(100, 1.5, 1)` | `1.959964` (`1.960`) | `(1.959964 + 0.84) * 1.5 / 10 = 0.419995` (`0.420 R`) | `0.470 R` / `282.23` (`282`), `BLOCK` (rc `1`) | `n 100 sd 1.5 m 1 z_holm 1.960 MDE 0.420 R + cost 0.05 = 0.470 vs max plausible gross 0.3; n needed 282` (`BLOCK`, rc `1`) | MATCH |
| 2 | `(250, 2.0, 5)` | `2.575829` (`2.576`) | `(2.575829 + 0.84) * 2.0 / 15.811388 = 0.432072` (`0.432 R`) | `0.482 R` / `746.74` (`747`), `BLOCK` (rc `1`) | `n 250 sd 2 m 5 z_holm 2.576 MDE 0.432 R + cost 0.05 = 0.482 vs max plausible gross 0.3; n needed 747` (`BLOCK`, rc `1`) | MATCH |
| 3 | `(500, 1.8, 12)` | `2.865260` (`2.865`) | `(2.865260 + 0.84) * 1.8 / 22.360680 = 0.298268` (`0.298 R`) | `0.348 R` / `711.71` (`712`), `BLOCK` (rc `1`) | `n 500 sd 1.8 m 12 z_holm 2.865 MDE 0.298 R + cost 0.05 = 0.348 vs max plausible gross 0.3; n needed 712` (`BLOCK`, rc `1`) | MATCH |
| 4 | `(909, 1.4, 2)` | `2.241403` (`2.241`) | `(2.241403 + 0.84) * 1.4 / 30.149627 = 0.143085` (`0.143 R`) | `0.193 R` / `297.76` (`298`), `PASS` (rc `0`) | `n 909 sd 1.4 m 2 z_holm 2.241 MDE 0.143 R + cost 0.05 = 0.193 vs max plausible gross 0.3; n needed 298` (`PASS`, rc `0`) | MATCH |
| 5 | `(1500, 3.5, 20)` | `3.023341` (`3.023`) | `(3.023341 + 0.84) * 3.5 / 38.729833 = 0.349129` (`0.349 R`) | `0.399 R` / `2925.38` (`2925`), `BLOCK` (rc `1`) | `n 1500 sd 3.5 m 20 z_holm 3.023 MDE 0.349 R + cost 0.05 = 0.399 vs max plausible gross 0.3; n needed 2925` (`BLOCK`, rc `1`) | MATCH |

## 3. Additional Claim Table (`scripts/dev/prereg_gate.py`)

| # | Claim (`scripts/dev/prereg_gate.py`) | Recomputed Value / Code Check (`file:line`) | Status |
|---|---|---|---|
| 6 | Docstring `:5-6`: `MAX_PLAUSIBLE_GROSS = 0.30 R (OURS)`, `POWER_Z = 0.84 (OURS)` | Defined at `scripts/dev/prereg_gate.py:21-22` with `# R, OURS` and `# 80 % power, OURS`. | MATCH |
| 7 | Docstring `:7-8`: `sd <= 1` exits `2` unless `--sd-source <file:line>` is provided | Enforced at `scripts/dev/prereg_gate.py:57-60` (`if a.sd <= 1 and not a.sd_source.strip(): return 2`). | MATCH |
| 8 | Docstring `:9-10`: `--m auto` sums DEV verdicts + `TRIAL_LEDGER.csv` + `--new-cells N` | Enforced at `scripts/dev/prereg_gate.py:45-47` via `verdicts.count_with_ledger(a.verdicts_csv, a.ledger_csv, "DEV")`. | MATCH |

## 4. Defects List

None (`0` defects found; all 5 hand-computed triples and all 3 code/guard claims match `scripts/dev/prereg_gate.py` exactly).

VERDICT: MATCH

