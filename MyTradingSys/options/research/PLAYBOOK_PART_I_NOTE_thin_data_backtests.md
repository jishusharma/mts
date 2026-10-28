# Proposed playbook addition (not applied; playbook.md is shared - operator/supervisor to merge)
Part I has no step for backtests where the tradable sample is thin (here: options, 12-36% fill rate, 29-110 trades per cell).
Add: (1) report fill rate and trades per cell next to every statistic; (2) t-stats on overlapping or sparse trades are
not evidence - use block-bootstrap CI and per-year table; (3) choose the cell on IS only and quote OOS unchanged;
(4) require PBO < 0.2 AND a named stress-period slice before any "candidate" label; (5) a result with 0% drawdown is a
sample-coverage flag, not a finding.
