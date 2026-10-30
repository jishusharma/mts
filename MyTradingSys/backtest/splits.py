"""One definition of DEV / VALIDATION / HOLDOUT for every study, plus a guard.

Boundaries are half-open [start, end), UTC.
  DEV         2022-01-01 .. 2024-07-01   (last DEV bar 2024-06-30 23:59)
  VALIDATION  2024-07-01 .. 2025-07-01   (read once, under a PRE_REG)
  HOLDOUT     2025-07-01 ..              (sealed; read once, logged)

SOURCE: system/OPERATOR_DECISIONS.md:899 ("DEV (2022-01-01..2024-06-30),
VALIDATION (2024-07-01..2025-06-30) and HOLDOUT are unchanged") and
research/lead/BACKTEST_CONSOLIDATION_2026-10-30.md:14 (HOLDOUT 2025-07+ sealed).

DECISION (OURS): sources disagree. Desk DEV locks at 2022-04-01 (sim_desk/ROADMAP.md
section 2.1; a subset of this DEV, kept as a desk-level lock). Tom/LC use DEV
2024-12..2025-03, VAL 2025-04..06 (levels_confluence_2026-10-14/PLAN.md:68), and Tom's
own holdout starts 2026-06-26; those would place "DEV" inside this VALIDATION/HOLDOUT.
We take the most conservative rule: the earliest holdout start (2025-07-01) and the
project DEV end (2024-06-30). Any study reading past DEV_END must go through
read_holdout() / an explicit PRE_REG, not through assert_dev_only().
"""
import csv
import os
from datetime import datetime, timezone

import pandas as pd

DEV_START = pd.Timestamp('2022-01-01')
DEV_END = pd.Timestamp('2024-07-01')          # exclusive
VALIDATION_START = DEV_END
VALIDATION_END = pd.Timestamp('2025-07-01')   # exclusive
HOLDOUT_START = VALIDATION_END

HOLDOUT_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'research', 'holdout_reads.csv')
_HEADER = ['timestamp_utc', 'study', 'holdout_window', 'accessor', 'reason', 'verdict']


class SplitViolation(ValueError):
    pass


def _ts(x):
    t = pd.Timestamp(x)
    return t.tz_convert(None) if t.tzinfo is not None else t


def window_of(ts):
    t = _ts(ts)
    if t < DEV_START:
        return 'PRE_DEV'
    if t < DEV_END:
        return 'DEV'
    if t < VALIDATION_END:
        return 'VALIDATION'
    return 'HOLDOUT'


def assert_dev_only(ts_min, ts_max):
    """Raise SplitViolation unless [ts_min, ts_max] lies inside DEV."""
    lo, hi = _ts(ts_min), _ts(ts_max)
    if hi >= DEV_END:
        raise SplitViolation(f'{window_of(hi)} timestamp {hi} at/after DEV end {DEV_END}')
    if lo < DEV_START:
        raise SplitViolation(f'timestamp {lo} before DEV start {DEV_START}')


def dev_only(df):
    """Keep only rows whose DatetimeIndex lies in DEV."""
    return df[(df.index >= DEV_START) & (df.index < DEV_END)]


def read_holdout(study, accessor, reason, verdict='', log_path=None, window='2025-07..'):
    """Explicit holdout read request: append a row to holdout_reads.csv, return its window."""
    p = log_path or HOLDOUT_LOG
    new = not os.path.exists(p) or os.path.getsize(p) == 0
    with open(p, 'a', newline='\n') as f:
        w = csv.writer(f, lineterminator='\n')
        if new:
            w.writerow(_HEADER)
        w.writerow([datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), study, window, accessor, reason, verdict])
    return window
