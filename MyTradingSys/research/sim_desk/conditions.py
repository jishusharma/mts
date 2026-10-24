"""Shared CONDITIONS for any layer: a filter applied to a study's trades before they are scored.

Every value is typed free-form and is OURS (our judgement, tuned on DEV; never the trader's). A new setting adds one
TRIALS row (desk.run_setting). Features are causal: they use only the last bar that was CLOSED before the trade's
touch time. Conditions never change the simulation, so a changed condition re-uses the cached run.

Caveat: this is a post-filter. It is exact when trades are independent (levels). A bar study that holds one
position at a time (rsi, wavetrend) could trade a different set if the condition were applied before it; the
filtered set here is a subset of the unfiltered one, not a re-run.

  side        both | long | short
  hour_from, hour_to   UTC hour window [from, to), wraps midnight when from > to; both empty = any hour
  ema_rel     off | above | below  : last closed close vs EMA(ema_len) of ema_tf-minute bars
  atr_lo, atr_hi       percentile band 0..100 of ATR(atr_len) on atr_tf-minute bars, among the last atr_win bars
  days        weekdays allowed, e.g. "mon,tue" or "0,1" (Monday=0, UTC); empty = any
  layer_b, layer_b_bars, layer_b_tf   only when study layer_b (default settings) also fired within the last
              layer_b_bars bars of layer_b_tf minutes before this trade's touch time
"""
import numpy as np

MIN = 60_000
HOUR = 3_600_000
DAY = 86_400_000
DAYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
DEFAULT = {'side': 'both', 'hour_from': None, 'hour_to': None, 'ema_rel': 'off', 'ema_tf': 60, 'ema_len': 50,
           'atr_lo': None, 'atr_hi': None, 'atr_tf': 60, 'atr_len': 14, 'atr_win': 500,
           'days': '', 'layer_b': '', 'layer_b_bars': 4, 'layer_b_tf': 60}
FIELDS = [
    {'key': 'side', 'label': 'Side', 'type': 'choice', 'choices': ['both', 'long', 'short']},
    {'key': 'hour_from', 'label': 'UTC hour from', 'type': 'int', 'min': 0, 'max': 23},
    {'key': 'hour_to', 'label': 'UTC hour to (excluded)', 'type': 'int', 'min': 0, 'max': 24},
    {'key': 'ema_rel', 'label': 'Trend: price vs EMA', 'type': 'choice', 'choices': ['off', 'above', 'below']},
    {'key': 'ema_tf', 'label': 'EMA bar minutes', 'type': 'int', 'min': 1, 'max': 1440},
    {'key': 'ema_len', 'label': 'EMA length', 'type': 'int', 'min': 2, 'max': 500},
    {'key': 'atr_lo', 'label': 'ATR percentile from', 'type': 'int', 'min': 0, 'max': 100},
    {'key': 'atr_hi', 'label': 'ATR percentile to', 'type': 'int', 'min': 0, 'max': 100},
    {'key': 'atr_tf', 'label': 'ATR bar minutes', 'type': 'int', 'min': 1, 'max': 1440},
    {'key': 'atr_len', 'label': 'ATR length', 'type': 'int', 'min': 2, 'max': 200},
    {'key': 'atr_win', 'label': 'ATR percentile look-back (bars)', 'type': 'int', 'min': 20, 'max': 5000},
    {'key': 'days', 'label': 'Weekdays (mon,tue,...)', 'type': 'text'},
    {'key': 'layer_b', 'label': 'Only if layer B also fired (study id)', 'type': 'text'},
    {'key': 'layer_b_bars', 'label': 'within N bars', 'type': 'int', 'min': 1, 'max': 1000},
    {'key': 'layer_b_tf', 'label': 'layer B bar minutes', 'type': 'int', 'min': 1, 'max': 1440},
]


def _int(c, key, lo, hi, none_ok=False):
    v = c.get(key, DEFAULT[key])
    if v in (None, ''):
        if none_ok:
            return None
        v = DEFAULT[key]
    try:
        f = float(v)
    except (TypeError, ValueError):
        raise ValueError(f'{key}: {v!r} is not a number')
    if f != int(f) or not lo <= f <= hi:
        raise ValueError(f'{key}: {v} must be a whole number {lo}..{hi}')
    return int(f)


def parse_days(s):
    if isinstance(s, (list, tuple)):
        s = ','.join(str(x) for x in s)
    out = set()
    for part in str(s or '').replace(' ', '').lower().split(','):
        if not part:
            continue
        if part[:3] in DAYS:
            out.add(DAYS.index(part[:3]))
        elif part.isdigit() and 0 <= int(part) <= 6:
            out.add(int(part))
        else:
            raise ValueError(f'days: {part!r} is not a weekday (use mon,tue,... or 0..6)')
    return sorted(out)


def normalize(c):
    """Validated canonical form holding only the ACTIVE conditions (an empty dict = no condition). ValueError on bad input."""
    c = dict(c or {})
    out = {}
    side = str(c.get('side') or 'both').lower()
    if side not in ('both', 'long', 'short'):
        raise ValueError(f'side: {side!r} must be both, long or short')
    if side != 'both':
        out['side'] = side
    hf, ht = _int(c, 'hour_from', 0, 23, True), _int(c, 'hour_to', 0, 24, True)
    if (hf is None) != (ht is None):
        raise ValueError('hour window: fill both "from" and "to", or neither')
    if hf is not None and hf != ht:
        out['hour_from'], out['hour_to'] = hf, ht
    rel = str(c.get('ema_rel') or 'off').lower()
    if rel not in ('off', 'above', 'below'):
        raise ValueError(f'ema_rel: {rel!r} must be off, above or below')
    if rel != 'off':
        out.update(ema_rel=rel, ema_tf=_int(c, 'ema_tf', 1, 1440), ema_len=_int(c, 'ema_len', 2, 500))
    lo, hi = _int(c, 'atr_lo', 0, 100, True), _int(c, 'atr_hi', 0, 100, True)
    if lo is not None or hi is not None:
        lo, hi = (0 if lo is None else lo), (100 if hi is None else hi)
        if lo > hi:
            raise ValueError(f'ATR percentile band: from {lo} is above to {hi}')
        out.update(atr_lo=lo, atr_hi=hi, atr_tf=_int(c, 'atr_tf', 1, 1440), atr_len=_int(c, 'atr_len', 2, 200),
                   atr_win=_int(c, 'atr_win', 20, 5000))
    days = parse_days(c.get('days'))
    if days and len(days) < 7:
        out['days'] = ','.join(DAYS[d] for d in days)
    b = str(c.get('layer_b') or '').strip()
    if b:
        out.update(layer_b=b, layer_b_bars=_int(c, 'layer_b_bars', 1, 1000), layer_b_tf=_int(c, 'layer_b_tf', 1, 1440))
    return out


def label(c):
    """One line for the TRIALS ledger and the page, e.g. 'long, UTC 8-16, close above EMA50 of 60m bars'. Empty if none."""
    parts = []
    if 'side' in c:
        parts.append(c['side'] + ' only')
    if 'hour_from' in c:
        parts.append(f"UTC {c['hour_from']}-{c['hour_to']}")
    if 'ema_rel' in c:
        parts.append(f"close {c['ema_rel']} EMA{c['ema_len']} of {c['ema_tf']}m bars")
    if 'atr_lo' in c:
        parts.append(f"ATR{c['atr_len']} of {c['atr_tf']}m bars at {c['atr_lo']}-{c['atr_hi']} percentile of last {c['atr_win']}")
    if 'days' in c:
        parts.append('days ' + c['days'])
    if 'layer_b' in c:
        parts.append(f"{c['layer_b']} fired within {c['layer_b_bars']}x{c['layer_b_tf']}m")
    return ', '.join(parts)


def _closed_index(bars, touch_t, tf_min):
    """Index of the last bar whose close time (open + tf) is <= touch_t; -1 if none."""
    return np.searchsorted(bars[:, 0] + tf_min * MIN, touch_t, side='right') - 1


def ema(closes, length):
    """Standard EMA, alpha 2/(length+1), seeded with the first close."""
    a = 2.0 / (length + 1)
    out = np.empty(len(closes))
    e = closes[0]
    for i, c in enumerate(closes):
        e = c if i == 0 else a * c + (1 - a) * e
        out[i] = e
    return out


def atr(bars, length):
    """Simple mean of the last `length` true ranges; NaN until enough bars."""
    h, l, c = bars[:, 2], bars[:, 3], bars[:, 4]
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    out = np.full(len(tr), np.nan)
    if len(tr) >= length:
        cs = np.cumsum(np.r_[0.0, tr])
        out[length - 1:] = (cs[length:] - cs[:-length]) / length
    return out


def mask(c, touch_t, side, minute_bars=None, b_times=None, resample=None):
    """Boolean keep-mask over trades. minute_bars: 1m array (t,o,h,l,c) needed only for ema/atr; b_times: sorted touch
    times of layer B; resample(a, tf_min) -> bars (desk passes studies._bars.resample)."""
    touch_t = np.asarray(touch_t, np.int64)
    side = np.asarray(side)
    keep = np.ones(len(touch_t), bool)
    if 'side' in c:
        keep &= side == (1 if c['side'] == 'long' else -1)
    if 'hour_from' in c:
        h = (touch_t % DAY) // HOUR
        f, t = c['hour_from'], c['hour_to']
        keep &= (h >= f) & (h < t) if f < t else (h >= f) | (h < t)
    if 'days' in c:
        wd = ((touch_t // DAY) + 3) % 7        # 1970-01-01 was a Thursday (Monday=0)
        keep &= np.isin(wd, parse_days(c['days']))
    if 'ema_rel' in c:
        bars = resample(minute_bars, c['ema_tf'])
        e = ema(bars[:, 4], c['ema_len'])
        j = _closed_index(bars, touch_t, c['ema_tf'])
        ok = j >= c['ema_len']               # warm-up: EMA needs its length in bars
        jj = np.clip(j, 0, len(bars) - 1)
        above = bars[jj, 4] > e[jj]
        keep &= ok & (above if c['ema_rel'] == 'above' else ~above)
    if 'atr_lo' in c:
        bars = resample(minute_bars, c['atr_tf'])
        a = atr(bars, c['atr_len'])
        j = _closed_index(bars, touch_t, c['atr_tf'])
        pct = np.full(len(touch_t), np.nan)
        for n, k in enumerate(j):
            if k < 0 or np.isnan(a[k]):
                continue
            w = a[max(0, k - c['atr_win'] + 1):k + 1]
            w = w[~np.isnan(w)]
            pct[n] = 100.0 * np.sum(w <= a[k]) / len(w)
        keep &= (pct >= c['atr_lo']) & (pct <= c['atr_hi'])     # NaN compares False: no history, no trade
    if 'layer_b' in c:
        bt = np.sort(np.asarray(b_times if b_times is not None else [], np.int64))
        span = c['layer_b_bars'] * c['layer_b_tf'] * MIN
        hi = np.searchsorted(bt, touch_t, side='right')       # fired at or before this trade's touch
        lo = np.searchsorted(bt, touch_t - span, side='left')
        keep &= hi > lo
    return keep


def apply(res, keep):
    """Subset a study result dict (arrays and refs) to the kept trades; all_days stays whole (it is the day universe)."""
    n = len(keep)
    out = {}
    for k, v in res.items():
        if k == 'all_days':
            out[k] = v
        elif k == 'refs':
            out[k] = [r for r, kp in zip(v, keep) if kp]
        elif hasattr(v, '__len__') and len(v) == n:
            out[k] = np.asarray(v)[keep]
        else:
            out[k] = v
    return out
