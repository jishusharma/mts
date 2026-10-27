"""Independent standard-library derivation of FORMULAS.md section 20.

Written before reading wavetrend.py, its tests, or its golden generator.
No repository imports. Numeric output is unmasked; events require 200 bars.
"""
import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / 'MyTradingSys/backtest/layers/wavetrend'


def derive(rows, source='hlc3', alpha_scale=1.0):
    esa = deviation = fast = None
    window = []
    previous_time = None
    strict_side = 0
    age = 0
    result = []
    for row in rows:
        stamp = int(row['open_time'])
        if previous_time is not None and stamp - previous_time != 3600000:
            esa = deviation = fast = None
            window = []
            strict_side = age = 0
        previous_time = stamp
        ap = ((float(row['high']) + float(row['low']) + float(row['close'])) / 3
              if source == 'hlc3' else float(row['close']))
        a = 2 / 11
        esa = ap if esa is None else esa + a * (ap - esa)
        distance = abs(ap - esa)
        deviation = distance if deviation is None else deviation + a * (distance - deviation)
        ci = ((ap - esa) / (0.015 * deviation)
              if deviation > 1e-9 * abs(ap) else math.nan)
        if math.isnan(ci):
            fast = None
            window = []
            strict_side = age = 0
            wt1 = wt2 = math.nan
            event = 0
        else:
            fast = ci if fast is None else fast + (2 / 22 * alpha_scale) * (ci - fast)
            wt1 = fast
            window.append(fast)
            window = window[-4:]
            wt2 = sum(window) / 4 if len(window) == 4 else math.nan
            age += 1
            event = 0
            if math.isnan(wt2):
                strict_side = 0
            else:
                side = (wt1 > wt2) - (wt1 < wt2)
                if side:
                    if strict_side and side != strict_side and age >= 200:
                        event = side
                    strict_side = side
        result.append(dict(open_time=stamp, ap=ap, esa=esa, d=deviation,
                           ci=ci, wt1=wt1, wt2=wt2, event=event))
    return result


def load_fixture():
    with (DATA / 'fixture_btcusdt_1h_dev_2022-01.csv').open(newline='') as stream:
        return list(csv.DictReader(stream))


if __name__ == '__main__':
    rows = derive(load_fixture())
    print('bars:', len(rows))
    print('first:', rows[0])
    print('second:', rows[1])
    print('last:', rows[-1])
