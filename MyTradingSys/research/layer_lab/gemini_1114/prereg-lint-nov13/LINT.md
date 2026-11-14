12 files, 12 with at least one gap.

Template: `MyTradingSys/research/gross_effect_screen_2026-10-15/PRE_REG.md`
File list command: `git log --since=2026-11-11 --name-only --format= -- 'MyTradingSys/research/*/PRE_REG.md' | sort -u`
Lint command: `python scripts/dev/prereg_context_lint.py` -> exit code `0` (`prereg context lint: 57 new PRE_REG checked, 0 offender(s), 0 stale allow row(s)`).

| File | On Disk | `verdicts.py` check paste | `m` value | `prereg_gate.py` line | Rule frozen before RESULT | `SOURCED`/`OURS` labels | `prereg_context_lint.py` exit | Missing items |
|---|---|---|---|---|---|---|---|---|
| `MyTradingSys/research/adx_1d_through25_2026-11-13/PRE_REG.md` | yes | no | none | no | N/A (no `RESULT.md`) | yes | 0 | `verdicts.py` paste, `m` value, `prereg_gate.py` line |
| `MyTradingSys/research/edge_oi_flush_2026-11-13/PRE_REG.md` | no | - | - | - | - | - | 0 | missing on disk (deleted/moved since 2026-11-11) |
| `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/PRE_REG.md` | yes | no | none | no | N/A (no `RESULT.md`) | yes | 0 | `verdicts.py` paste, `m` value, `prereg_gate.py` line |
| `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/PRE_REG.md` | yes | no | none | no | N/A (no `RESULT.md`) | yes | 0 | `verdicts.py` paste, `m` value, `prereg_gate.py` line |
| `MyTradingSys/research/extreme_confirm_template_2026-11/PRE_REG.md` | no | - | - | - | - | - | 0 | missing on disk (deleted/moved since 2026-11-11) |
| `MyTradingSys/research/live_aid_flags_full_2026-11-13/PRE_REG.md` | no | - | - | - | - | - | 0 | missing on disk (deleted/moved since 2026-11-11) |
| `MyTradingSys/research/malkan_divergence_r03_r04_2026-11-13/PRE_REG.md` | no | - | - | - | - | - | 0 | missing on disk (deleted/moved since 2026-11-11) |
| `MyTradingSys/research/rsi_confirm_layers_2026-11-13/PRE_REG.md` | yes | no | none | no | `RESULT.md` exists | yes | 0 | `verdicts.py` paste, `m` value, `prereg_gate.py` line |
| `MyTradingSys/research/rsi_extreme_confirm_2026-11-13/PRE_REG.md` | yes | no | none | no | `RESULT.md` exists | yes | 0 | `verdicts.py` paste, `m` value, `prereg_gate.py` line |
| `MyTradingSys/research/rsi_htf_extreme_2026-11-13/PRE_REG.md` | yes | no | none | no | `RESULT.md` exists | yes | 0 | `verdicts.py` paste, `m` value, `prereg_gate.py` line |
| `MyTradingSys/research/rsi_range_census_2026-11-13/PRE_REG.md` | yes | no | none | no | N/A (no `RESULT.md`) | yes | 0 | `verdicts.py` paste, `m` value, `prereg_gate.py` line |
| `MyTradingSys/research/with_trend_session_2026-11-11/PRE_REG.md` | yes | no | `m = 2` | no | N/A (no `RESULT.md`) | yes | 0 | `verdicts.py` paste, `prereg_gate.py` line |
