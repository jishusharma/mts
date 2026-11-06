# Layer Lab Report: `gemini-blind-read-export-trades-py-bars-`

- **Task**: `gemini-blind-read-export-trades-py-bars-`
- **Date**: `2026-11-04` (UTC)
- **Role**: Gemini blind-read auditor

## Summary of Findings

Conducted independent blind recomputation of `sim_desk` `export_trades.py` and `studies/_bars.trade_rows` across all DEV replay runs (`fabio_v3-c`, `fabio_v3-b`, `tom_vp-fade`, `tom_spike_level`, and `fabio_v3-ad` unmeasured):

1. **Parameter and Formula Audit**:
   - Fees: `maker_pct = 0.02%`, `taker_pct = 0.05%` (`SOURCED` `backtest/fees.py:1-17`).
   - Slippage: `slip_pct = 0.02%` on market/stop fills (`SOURCED` `backtest/layers/FORMULAS.md:353`, `studies/_bars.py:23-27`).
   - R normalization: `gross_r = side * (exit_px - entry_px) / risk`, `net_r = gross_r - fee_r` (`SOURCED` `FORMULAS.md:659`, `studies/_bars.py:174-178`).
   - Export ladder schema: distances signed in trade favour as percent from fill price (`OURS` `studies/_bars.py:229-247`).

2. **Recomputed Headline Numbers vs Stated Results**:
   - `fabio_v3-c`: $N = 518$ filled trades, mean $+0.062$ R (`+0.061689` R), 95% CI $[-0.135, +0.268]$, cumulative net $+31.9543$ R, win rate $31.66\%$ (164/518). Verdict: `NOT ENOUGH DATA`. `MATCH`.
   - `fabio_v3-b`: $N = 64$ filled trades, mean $-0.445$ R (`-0.445060` R), 95% CI $[-0.694, -0.186]$, cumulative net $-28.4839$ R, win rate $39.06\%$ (25/64). Verdict: `FAILED`. `MATCH`.
   - `tom_vp-fade`: $N = 2052$ filled trades, mean $-0.247$ R (`-0.246997` R), 95% CI $[-0.285, -0.211]$, cumulative net $-506.8366$ R, win rate $38.26\%$ (785/2052). Verdict: `FAILED`. `MATCH`.
   - `tom_spike_level`: $N = 1399$ filled trades, mean $-0.222$ R (`-0.222427` R), 95% CI $[-0.269, -0.176]$, cumulative net $-311.1741$ R, win rate $49.68\%$ (695/1399). Verdict: `FAILED`. `MATCH`.
   - `fabio_v3-ad`: $0$ filled trades, `NOT MEASURED` (`tone: warn`), correctly excluded on DEV window as required delta/CVD fields start 2024-12-02.

3. **Deliverables Created**:
   - `MyTradingSys/research/gemini_audits_2026-11-04/BLIND_READ_EXPORT_TRADES_1104.md` with full per-number match table and `VERDICT: MATCH`.
   - Test passing: `python -c "import pathlib; p=pathlib.Path('MyTradingSys/research/gemini_audits_2026-11-04/BLIND_READ_EXPORT_TRADES_1104.md'); assert p.exists() and 'VERDICT' in p.read_text()"`.
