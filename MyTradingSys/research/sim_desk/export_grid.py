"""Run a fixed grid of desk settings for one study and export each run as results/desk-<study>-<hash>.json with the desk's example-trade charts.

Usage: python export_grid.py tom_vp|fabio_v3 [--results DIR]
A setting already in layer_lab/TRIALS.md adds no ledger row (the desk rule); a new one adds one. DEV window only (the desk locks it).
Prints one line per run: id, filled trades, ideas never filled, verdict, mean net R, charts exported.
"""
import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import desk  # noqa: E402

GRIDS = {
    # the 12 settings of the 2026-10-31 tom_vp grid (TRIALS.md rows 'sim-desk tom_vp ...')
    'tom_vp': [{'anchor': 'prior_day', 'setup': 'RETURN', 'accept_n': 0},
               {'anchor': 'prior_day', 'setup': 'RETURN', 'accept_n': 6},
               {'anchor': 'prior_day', 'setup': 'RETURN', 'accept_n': 6, 'shift': 'WITH'},
               {'anchor': 'prior_day', 'setup': 'RETURN', 'accept_n': 6, 'target': 'R', 'target_r': 2.0},
               {'anchor': 'prior_day', 'setup': 'FADE', 'accept_n': 0},
               {'anchor': 'prior_day', 'setup': 'FADE', 'accept_n': 6, 'shift': 'WITH'},
               {'anchor': 'prior_day', 'setup': 'ACCEPT', 'accept_n': 3},
               {'anchor': 'prior_day', 'setup': 'ACCEPT', 'accept_n': 6},
               {'anchor': 'prior_day', 'setup': 'ACCEPT', 'accept_n': 12},
               {'anchor': 'prior_day', 'setup': 'ACCEPT', 'accept_n': 6, 'shift': 'WITH'},
               {'anchor': 'prior_week', 'setup': 'RETURN', 'accept_n': 6},
               {'anchor': 'prior_week', 'setup': 'ACCEPT', 'accept_n': 6}],
    # first small Fabio grid: Model C x push x floor x exit, Model B x balance window x floor x exit
    'fabio_v3': [{'model': 'C', 'push': 'OFF', 'm': 15, 'f_pct': 0.5},
                 {'model': 'C', 'push': 'OFF', 'm': 15, 'f_pct': 0.3},
                 {'model': 'C', 'push': 'CANDLES', 'm': 5, 'f_pct': 0.5},
                 {'model': 'C', 'push': 'CANDLES', 'm': 15, 'f_pct': 0.5},
                 {'model': 'C', 'push': 'OFF', 'm': 15, 'f_pct': 0.5, 'exit': 'R', 'target_r': 2.0},
                 {'model': 'B', 'n_bal': 60, 'f_pct': 0.5},
                 {'model': 'B', 'n_bal': 120, 'f_pct': 0.5},
                 {'model': 'B', 'n_bal': 240, 'f_pct': 0.5},
                 {'model': 'B', 'n_bal': 120, 'f_pct': 0.3},
                 {'model': 'B', 'n_bal': 120, 'f_pct': 0.5, 'exit': 'R', 'target_r': 2.0}],
}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('study', choices=sorted(GRIDS))
    ap.add_argument('--results', default=str(desk.RESULTS))
    a = ap.parse_args(argv)
    study = desk.load_studies()[a.study]
    rows = []
    for p in GRIDS[a.study]:
        out = desk.run_setting(study, p, charts=True, progress=lambda m: None)
        rid = desk.export_result(out, study, results_dir=a.results)
        n_ch = len(out['charts'])
        rows.append((rid, out['n'], out['nofill'], out['verdict'], out['mean'], n_ch))
        print(f"{rid} filled={out['n']} nofill={out['nofill']} {out['verdict']} mean={out['mean']:+.3f} charts={n_ch}  [{out['label']}]", flush=True)
    return rows


if __name__ == '__main__':
    main()
