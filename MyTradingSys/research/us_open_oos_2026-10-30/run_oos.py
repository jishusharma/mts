"""OOS replication of session_open_study.py on 2020-01..2021-12 (DEV_EXT). Study code is reused verbatim; only the
data dirs, date range, holiday list and output path are swapped by text substitution (nothing else tuned).
2020-21 NYSE closures below are from memory (OURS, verify): 2020 Jan1 Jan20 Feb17 Apr10 May25 Jul3 Sep7 Nov26 Dec25;
2021 Jan1 Jan18 Feb15 Apr2 May31 Jul5 Sep6 Nov25 Dec24 (plus early closes 2020-11-27, 2020-12-24, 2021-11-26 not removed:
13:00 ET closes only shorten the last 3 h of a 390-min day)."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "session_sweeps" / "session_open_study.py"
s = SRC.read_text(encoding="utf-8")
s = s.replace('ROOT = Path(__file__).resolve().parents[3]', f'ROOT = Path(r"{HERE.parents[2]}")')
s = s.replace('DIRS = [ROOT / "Dumps/backtest/raw_1m_2022/klines", ROOT / "Dumps/backtest/raw/klines"]',
              'DIRS = [Path("F:/MTS/Dumps/backtest/raw_1m_2019/klines")]')
s = s.replace('OUT = Path(__file__).resolve().parent / "results_2026-10-04.json"',
              f'OUT = Path(r"{HERE}") / "results_oos_2020_2021.json"')
s = s.replace('dt.date(2022, 1, 3), dt.date(2026, 9, 25)', 'dt.date(2020, 1, 2), dt.date(2021, 12, 31)')
s = s.replace('NYSE_EXTRA = frozenset(', 'NYSE_EXTRA = frozenset(dt.date(*x) for x in ((2020,1,1),(2020,1,20),(2020,2,17),(2020,4,10),(2020,5,25),(2020,7,3),(2020,9,7),(2020,11,26),(2020,12,25),(2021,1,1),(2021,1,18),(2021,2,15),(2021,4,2),(2021,5,31),(2021,7,5),(2021,9,6),(2021,11,25),(2021,12,24))) | frozenset(', 1)
s = s.replace('if __name__ == "__main__":\n    main()', '')
exec(compile(s, str(SRC), "exec"))
main()
