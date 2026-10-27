"""Fee sweep: for each sim-desk study at its DEFAULT settings, how much of the result is fees.

Fable review (REVIEW_FABLE_2026-10-25.md, 'One screen', paragraph 2): fees are the whole result. This reads each
study's cached default run (desk._raw: cache only, never study.run via run_setting, so no new ledger row is written
and no result file is touched), keeps FILLED trades only, and prints mean gross R, fee R, net R at fee multiples
x0 / x0.5 / x1 / x2, and the break-even fee multiple (mean gross R / mean fee R) per study.

Fees include the 0.02 % slippage on market and stop fills (OURS: studies/_bars.py SLIP_DEFAULT) -- these numbers
are after that slippage, not fee-schedule-only.

    python MyTradingSys/research/sim_desk/fee_sweep.py

A missing klines folder (this host) prints NOT_IN_DATA for that study instead of raising.
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import desk  # noqa: E402

FEE_MULTS = (0.0, 0.5, 1.0, 2.0)


def sweep(gross, fees, filled):
    """Mean gross/fee R over FILLED trades only, net R at each fee multiple in FEE_MULTS, and the break-even fee
    multiple (mean_gross / mean_fee). gross <= 0 can never break even by cutting fees alone -> break_even 0.0.
    Zero mean fee makes the ratio undefined -> break_even None. `gross`/`fees`/`filled` are same-length sequences
    over ALL ideas (never-filled ones are excluded here, not before calling)."""
    gross = np.asarray(gross, dtype=float)
    fees = np.asarray(fees, dtype=float)
    filled = np.asarray(filled, dtype=bool)
    g, f = gross[filled], fees[filled]
    n = int(g.size)
    mean_gross = float(g.mean()) if n else 0.0
    mean_fee = float(f.mean()) if n else 0.0
    nets = {m: mean_gross - m * mean_fee for m in FEE_MULTS}
    if mean_fee == 0.0:
        break_even = None
    elif mean_gross <= 0.0:
        break_even = 0.0
    else:
        break_even = mean_gross / mean_fee
    return {'n': n, 'mean_gross': mean_gross, 'mean_fee': mean_fee,
            'net_x0': nets[0.0], 'net_x0_5': nets[0.5], 'net_x1': nets[1.0], 'net_x2': nets[2.0],
            'break_even': break_even}


def _study_sweep(study, cache_dir=desk.CACHE, progress=lambda s: None):
    """sweep() for one study at its DEFAULT settings, via the cached default run only (desk._raw; no run_setting,
    no ledger row, no result file). Returns None if the price data isn't on this machine (NOT_IN_DATA)."""
    q = study.normalize({})
    try:
        res, _cached = desk._raw(study, q, cache_dir, progress)
    except FileNotFoundError:
        return None
    filled = res.get('filled', np.ones(len(res['gross']), dtype=bool))
    return sweep(res['gross'], res['fees'], filled)


def _sentence(sid, out):
    be = out['break_even']
    if be is None:
        tail = 'today\'s fees are already zero'
    else:
        tail = f'fees would have to fall to {be:.2f}x of today\'s level to break even'
    return (f"{sid}: before fees {out['mean_gross']:+.3f} R, fees -{out['mean_fee']:.3f} R, "
            f"after fees {out['net_x1']:+.3f} R; {tail}")


def main():
    print('Fee sweep over cached default runs (filled trades only). Fees include the 0.02 % slippage on market '
          'and stop fills (OURS); these numbers are after that slippage, not fee-schedule-only.')
    header = f"{'study':<10} {'n':>5} {'gross R':>8} {'fee R':>7} {'net x0':>8} {'net x0.5':>9} {'net x1':>8} {'net x2':>8} {'break-even':>10}"
    print(header)
    for sid, study in desk.STUDIES.items():
        out = _study_sweep(study)
        if out is None:
            print(f'{sid:<10} NOT_IN_DATA')
            continue
        be = 'none' if out['break_even'] is None else f"{out['break_even']:.2f}x"
        print(f"{sid:<10} {out['n']:>5} {out['mean_gross']:>8.3f} {out['mean_fee']:>7.3f} "
              f"{out['net_x0']:>8.3f} {out['net_x0_5']:>9.3f} {out['net_x1']:>8.3f} {out['net_x2']:>8.3f} {be:>10}")
    print()
    for sid, study in desk.STUDIES.items():
        out = _study_sweep(study)
        print(f'{sid}: NOT_IN_DATA' if out is None else _sentence(sid, out))


if __name__ == '__main__':
    main()
