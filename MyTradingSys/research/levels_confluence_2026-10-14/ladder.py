"""LC3 ladder simulator: scale-in S0-S3 x stops K1-K5 x exits X0-X2 on first touches of KEEP levels (DEV only).

One trade idea = the first touch of a KEEP level in a UTC day (side from the previous close, Q79 rule). L1 is the
touched level, L2 the next KEEP level beyond it against the trade, T1 the first KEEP level in the trade's favour.
Full planned size = 1; R = the loss if every planned fill happens and the one stop is hit (planned average entry
minus stop). Per-leg fees from backtest/fees.py (Binance USDT-M: limit fills maker, stops and market exits taker).
Within one 1m bar the order is: pending limit fill, then stop, then target (stop before target: conservative).
The ladder (X2) reads closed 5m bars after the first target: CVD = sum(2*taker_buy - volume) per 5m bar.
All parameters are OURS unless marked SOURCED; see ladder_dev.md.
"""
import bisect
import statistics
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).parent))
from MyTradingSys.backtest import fees as feemod  # noqa: E402
import event_table as et  # noqa: E402

MAKER, TAKER = feemod.BINANCE_MAKER, feemod.BINANCE_TAKER
FEES_MAIN = {'entry': MAKER, 'add': TAKER, 'target': MAKER, 'stop': TAKER, 'market': TAKER}
FEES_TAKER = {'entry': TAKER, 'add': TAKER, 'target': TAKER, 'stop': TAKER, 'market': TAKER}
S_ARMS = {'S0': (('L1', 1.0),), 'S1': (('L1', .5), ('L2', .5)), 'S2': (('L2', 1.0),), 'S3': (('L1', 1 / 3), ('L2', 2 / 3))}
K_ARMS = ('K1', 'K2', 'K3', 'K4', 'K5')
X_ARMS = ('X0_1R', 'X0_2R', 'X1', 'X2')
MARGIN = 0.001          # OURS: 0.10 % beyond a level (K1 minimum, K2, K5)
FLAT_FRAC = 0.25        # OURS: a 5m CVD bar is flat when |delta| <= 0.25 x median |delta| of the prior 20 bars
BB_N, BB_W = 20, 2      # SOURCED: FORMULAS.md section 22 (population sd)


def _fee_floor(fees):
    """Card lc-ladder-dev step 1: stop at least 0.40 % beyond the level with taker entries, 0.20 % with maker."""
    return 0.004 if fees['entry'] > MAKER else 0.002


class DayCtx:
    """Arrays and 5m/15m buckets of one UTC day of 1m bars (shared by every idea of the day)."""

    def __init__(self, daybars):
        self.bars = daybars
        self.n = len(daybars)
        self.op = np.array([float(b['o']) for b in daybars])
        self.hi = np.array([float(b['h']) for b in daybars])
        self.lo = np.array([float(b['l']) for b in daybars])
        self.cl = np.array([float(b['c']) for b in daybars])
        self.b_end, self.b_close, self.b_delta, self.b_thr, self.b_bbpos = self._buckets(300000)
        self.f_end, self.f_close, _, _, _ = self._buckets(900000, bb=False)

    def _buckets(self, span, bb=True):
        ends, closes, deltas, thrs, bbpos = [], [], [], [], []
        cur = None; delta = 0.
        for j, b in enumerate(self.bars):
            k = int(b['t']) // span
            if cur is not None and k != cur:
                ends.append(j - 1); closes.append(float(self.bars[j - 1]['c'])); deltas.append(delta); delta = 0.
            cur = k
            delta += 2 * float(b.get('tbv', 0)) - float(b['v'])
        ends.append(self.n - 1); closes.append(float(self.bars[-1]['c'])); deltas.append(delta)
        for k in range(len(ends)):
            prior = [abs(x) for x in deltas[max(0, k - 20):k]]
            thrs.append(FLAT_FRAC * statistics.median(prior) if prior else 0.)
            bbpos.append(et.bollinger_position(closes[max(0, k - BB_N + 1):k + 1], BB_N, BB_W) if bb and k + 1 >= BB_N else None)
        return ends, closes, deltas, thrs, bbpos

    def first_adverse(self, side, x, start):
        """First bar index >= start whose low (long) / high (short) reaches x; None if never."""
        if x is None or start >= self.n:
            return None
        cond = (self.lo[start:] <= x) if side > 0 else (self.hi[start:] >= x)
        k = int(cond.argmax())
        return start + k if cond[k] else None

    def first_favorable(self, side, y, start):
        if y is None or start >= self.n:
            return None
        cond = (self.hi[start:] >= y) if side > 0 else (self.lo[start:] <= y)
        k = int(cond.argmax())
        return start + k if cond[k] else None

    def first_close15_beyond(self, side, level, start):
        """K4: first 15m bucket closing (end index >= start) strictly beyond level against the trade: (end, close)."""
        k = bisect.bisect_left(self.f_end, start)
        while k < len(self.f_end):
            c = self.f_close[k]
            if (c < level) if side > 0 else (c > level):
                return self.f_end[k], c
            k += 1
        return None, None

    def ladder(self, side, start, rem, stop_idx, stop_px, exits, flat_rule=True, t2=None, t2_px=None, q_t2=0.):
        """Step out of `rem` after the first target: closed 5m bars after bar `start`.
        Exit all on CVD against the trade or the opposite Bollinger band; with flat_rule, half of the rest once on a
        flat bar. Optional second target (arm P). The one stop keeps running. Appends (price, qty, reason)."""
        flat_done = not flat_rule
        k = bisect.bisect_right(self.b_end, start)
        t2_done = t2 is None
        while k < len(self.b_end):
            e = self.b_end[k]
            events = []
            if not t2_done and t2 is not None and t2 <= e:
                events.append((t2, 1, 'T2'))
            if stop_idx is not None and stop_idx <= e:
                events.append((stop_idx, 0, 'STOP'))
            for _, _, kind in sorted(events):
                if kind == 'STOP':
                    exits.append((stop_px, rem, 'STOP_LATE')); return
                q = min(q_t2, rem); exits.append((t2_px, q, 'T2')); rem -= q; t2_done = True
                if rem <= 1e-12:
                    return
            d = side * self.b_delta[k]; thr = self.b_thr[k]; pos = self.b_bbpos[k]
            band = pos is not None and ((pos >= 1) if side > 0 else (pos <= 0))
            if band or d < -thr:
                exits.append((self.b_close[k], rem, 'BAND' if band else 'CVD_AGAINST')); return
            if not flat_done and abs(d) <= thr:
                exits.append((self.b_close[k], rem / 2, 'CVD_FLAT')); rem /= 2; flat_done = True
            k += 1
        exits.append((float(self.cl[-1]), rem, 'TIME'))


def stop_price(ctx, i, idea, S, K, fees):
    """The one stop for the set and the planned average entry; None when the arm is undefined for this idea."""
    side, L1, L2 = idea['side'], idea['L1'], idea.get('L2')
    plan = [(L1 if lv == 'L1' else L2, w) for lv, w in S_ARMS[S]]
    if any(p is None for p, _ in plan):
        return None
    avg = sum(p * w for p, w in plan)
    deepest = plan[-1][0]
    if K == 'K1':
        stop = deepest - side * deepest * max(MARGIN, _fee_floor(fees))
    elif K == 'K2':
        stop = None if L2 is None else L2 - side * L2 * MARGIN
    elif K == 'K3':
        atr = idea.get('atr1h')
        stop = None if (L2 is None or atr is None) else L2 - side * 0.5 * atr
    elif K == 'K4':  # trigger: a 15m close beyond L2; R measured as for K2 (exit price is that close)
        stop = None if L2 is None else L2 - side * L2 * MARGIN
    elif K == 'K5':
        ext = float(ctx.lo[:i + 1].min()) if side > 0 else float(ctx.hi[:i + 1].max())
        base = min(ext, deepest) if side > 0 else max(ext, deepest)
        stop = base - side * base * MARGIN
    else:
        raise ValueError(K)
    if stop is None:
        return None
    R = side * (avg - stop)
    if R <= 0:
        return None
    return {'plan': plan, 'avg_planned': avg, 'stop': stop, 'R_price': R}


def simulate(daybars, i, idea, S, K, X, fees=FEES_MAIN, ctx=None):
    """One idea, one (S, K, X) arm. Returns None when the arm is undefined for the idea (no L2, no T1, no ATR)."""
    ctx = ctx or DayCtx(daybars)
    side = idea['side']
    sp = stop_price(ctx, i, idea, S, K, fees)
    if sp is None:
        return None
    plan, avg, stop, R = sp['plan'], sp['avg_planned'], sp['stop'], sp['R_price']
    if X == 'X0_1R':
        T = avg + side * R
    elif X == 'X0_2R':
        T = avg + side * 2 * R
    else:
        T = idea.get('T1')
    if T is None:
        return None
    L1, L2 = idea['L1'], idea.get('L2')
    fills = []  # (price, qty, bar)
    for (lv, w), (p, _) in zip(S_ARMS[S], plan):
        if lv == 'L1':
            fills.append((L1, w, i))
        else:
            f2 = ctx.first_adverse(side, L2, i)
            if f2 is not None:
                fills.append((L2, w, f2))
    if K == 'K4':
        s, stop_px = ctx.first_close15_beyond(side, L2, i)
    else:
        s, stop_px = ctx.first_adverse(side, stop, i), stop
    t = ctx.first_favorable(side, T, i + 1)
    INF = 10 ** 9
    s_t, t_t = (INF if s is None else s), (INF if t is None else t)
    exits = []
    status = 'NOT_STOPPED'
    if s_t <= t_t:
        live = [f for f in fills if f[2] <= min(s_t, ctx.n - 1)]
        qty = sum(w for _, w, _ in live)
        if qty <= 0:
            status = 'NO_FILL'
        elif s is None:
            exits.append((float(ctx.cl[-1]), qty, 'TIME'))
        else:
            exits.append((stop_px, qty, 'STOP'))
            tt = ctx.first_favorable(side, T, s + 1)
            more = ctx.first_adverse(side, stop - side * R, s + 1)
            if tt is not None and (more is None or tt < more):
                status = 'BAD'
            elif more is not None:
                status = 'GOOD'
            else:
                status = 'NEUTRAL'
        fills = live
    else:
        live = [f for f in fills if f[2] < t]
        qty = sum(w for _, w, _ in live)
        fills = live
        if qty <= 0:
            status = 'NO_FILL'
        elif X == 'X2':
            exits.append((T, qty / 2, 'T1'))
            ctx.ladder(side, t, qty / 2, s, stop_px, exits)
            if exits[-1][2] == 'STOP_LATE':
                status = 'AFTER_TARGET'
        else:
            exits.append((T, qty, 'T1' if X in ('X1', 'X2') else 'X0'))
    rate = {'T1': fees['target'], 'X0': fees['target'], 'T2': fees['target'], 'STOP': fees['stop'], 'STOP_LATE': fees['stop'],
            'CVD_FLAT': fees['market'], 'CVD_AGAINST': fees['market'], 'BAND': fees['market'], 'TIME': fees['market']}
    gross = sum(q * side * px for px, q, _ in exits) - sum(w * side * p for p, w, _ in fills)
    fee = sum(fees['entry'] * p * w for p, w, _ in fills) + sum(rate[r] * px * q for px, q, r in exits)
    planned_fee_share = (fees['entry'] * avg + fees['target'] * T) / R
    return {'net_r': (gross - fee) / R, 'gross_r': gross / R, 'fees_r': fee / R, 'R_price': R, 'stop': stop,
            'avg_entry': (sum(p * w for p, w, _ in fills) / qty) if qty > 0 else None, 'avg_planned': avg,
            'fills': fills, 'exits': exits, 'filled_qty': qty, 'stop_status': status, 'target': T,
            'planned_fee_share': planned_fee_share}


def arm_p(daybars, i, idea, equity=10000., budget=50., fees=FEES_MAIN, mmr=0.005, stop_pct=0.004,
          adds=((0.25, 2), (0.5, 3)), ctx=None):
    """levels_sizing METHOD.md arm: one loss budget, capped 1:2:3 adds at adverse 0.25/0.5 of the initial stop
    distance (filled at the next bar's open, one per bar), stop 0.4 % beyond L1 never widened, staged exits
    (50 % at T1, 25 % of the held size at T2, the rest on CVD against / opposite band). Isolated-margin liquidation
    check with mark = bar low/high (mmr OURS 0.5 %)."""
    ctx = ctx or DayCtx(daybars)
    side, L1, T1 = idea['side'], idea['L1'], idea.get('T1')
    if T1 is None:
        return None
    T2 = idea.get('T2') or (T1 + side * abs(T1 - L1))
    D = stop_pct * L1
    stop = L1 - side * D
    planned = [(L1, 1, 'entry')] + [(L1 - side * frac * D, q, 'add') for frac, q in adds]
    qsum = sum(q for _, q, _ in planned)
    gross_planned = sum(q * side * (p - stop) for p, q, _ in planned)
    fee_planned = sum(fees[kind] * p * q for p, q, kind in planned) + fees['stop'] * stop * qsum
    unit = budget / (abs(gross_planned) + fee_planned)
    s = ctx.first_adverse(side, stop, i)
    t1 = ctx.first_favorable(side, T1, i + 1)
    INF = 10 ** 9
    s_t, t1_t = (INF if s is None else s), (INF if t1 is None else t1)
    end_idx = min(s_t, t1_t, ctx.n - 1)
    fills = [(L1, 1, i, 'entry')]
    last = i
    for p, q, kind in planned[1:]:
        trig = ctx.first_adverse(side, p, i + 1)
        if trig is None:
            continue
        fb = max(trig + 1, last + 1)
        if fb > end_idx:
            continue
        fills.append((float(ctx.op[fb]), q, fb, kind)); last = fb
    # liquidation: after each fill, from that bar to the next fill (or the exit)
    lev_max, liq_price, liq_idx = 0., None, None
    for n_, (p, q, fb, kind) in enumerate(fills):
        held = fills[:n_ + 1]
        qty = sum(x[1] for x in held) * unit
        avg = sum(x[0] * x[1] for x in held) / sum(x[1] for x in held)
        lev = qty * avg / equity
        lev_max = max(lev_max, lev)
        liq = avg * (1 - 1 / lev + mmr) if side > 0 else avg * (1 + 1 / lev - mmr)
        liq_price = liq  # reported at the highest leverage (after the last fill) unless a hit came earlier
        nxt = fills[n_ + 1][2] if n_ + 1 < len(fills) else None
        hit = ctx.first_adverse(side, liq, fb)
        if hit is not None and hit <= (min(s_t, t1_t) if nxt is None else nxt):
            liq_idx = hit
            break
    fee = sum(fees[kind] * p * q * unit for p, q, _, kind in fills)
    qty_total = sum(q for _, q, _, _ in fills) * unit
    cost = sum(p * q for p, q, _, _ in fills) * unit
    exits = []
    pfs = unit * fee_planned / budget
    if liq_idx is not None:
        return {'unit_qty': unit, 'planned_loss_usd': budget, 'fills': [(p, q) for p, q, _, _ in fills], 'exits': [],
                'net_usd': -equity, 'net_r': -equity / budget, 'leverage_max': lev_max, 'liq_price': liq_price,
                'liquidated': True, 'status': 'LIQUIDATED', 'planned_fee_share': pfs,
                'stop_to_liq_pct': abs(stop - liq_price) / L1 * 100}
    if s_t <= t1_t:
        if s is None:
            exits.append((float(ctx.cl[-1]), qty_total, 'TIME')); status = 'TIME'
        else:
            exits.append((stop, qty_total, 'STOP')); status = 'STOP'
    else:
        status = 'TARGET'
        exits.append((T1, qty_total / 2, 'T1'))
        t2 = ctx.first_favorable(side, T2, t1 + 1)
        ctx.ladder(side, t1, qty_total / 2, s, stop, exits, flat_rule=False, t2=t2, t2_px=T2, q_t2=qty_total / 4)
    rate = {'T1': fees['target'], 'T2': fees['target'], 'STOP': fees['stop'], 'STOP_LATE': fees['stop'],
            'CVD_AGAINST': fees['market'], 'BAND': fees['market'], 'TIME': fees['market']}
    gross = sum(q * side * px for px, q, _ in exits) - side * cost
    fee += sum(rate[r] * px * q for px, q, r in exits)
    net = gross - fee
    return {'unit_qty': unit, 'planned_loss_usd': unit * (abs(gross_planned) + fee_planned),
            'fills': [(p, q) for p, q, _, _ in fills], 'exits': exits, 'net_usd': net, 'net_r': net / budget,
            'gross_usd': gross, 'fees_usd': fee, 'leverage_max': lev_max, 'liq_price': liq_price,
            'liquidated': False, 'status': status, 'planned_fee_share': pfs,
            'stop_to_liq_pct': None if liq_price is None else abs(stop - liq_price) / L1 * 100}


class BiasIndex:
    """event_table._bias_at, precomputed once per bar set (same definitions: bars closed strictly before the touch)."""

    def __init__(self, bars):
        self.tf = {}
        for tf, mins in et.TF.items():
            agg = et._agg(bars, mins)
            ends = [b['t'] + 60000 for b in agg]
            closes = [b['c'] for b in agg]
            ema = et._ema(closes)
            hs, ls = [], []
            for i in range(2, len(agg) - 2):
                if agg[i]['h'] > max(x['h'] for x in agg[i - 2:i] + agg[i + 1:i + 3]):
                    hs.append((i + 2, agg[i]['h']))
                if agg[i]['l'] < min(x['l'] for x in agg[i - 2:i] + agg[i + 1:i + 3]):
                    ls.append((i + 2, agg[i]['l']))
            self.tf[tf] = (ends, closes, ema, [c for c, _ in hs], [p for _, p in hs], [c for c, _ in ls], [p for _, p in ls])

    def at(self, touch_t, pd_value, ref):
        out = {'B1_value_area': None if pd_value is None else ('UP' if ref > pd_value['vah'] else 'DOWN' if ref < pd_value['val'] else 'NEUTRAL')}
        for tf, (ends, closes, ema, hc, hp, lc, lp) in self.tf.items():
            n = bisect.bisect_left(ends, touch_t)
            if n < 21:
                out[f'B2_swing_{tf}'] = None; out[f'B3_ema20_{tf}'] = None; continue
            nh, nl = bisect.bisect_right(hc, n - 1), bisect.bisect_right(lc, n - 1)
            if nh > 1 and nl > 1 and hp[nh - 1] > hp[nh - 2] and lp[nl - 1] > lp[nl - 2]:
                sw = 'UP'
            elif nh > 1 and nl > 1 and hp[nh - 1] < hp[nh - 2] and lp[nl - 1] < lp[nl - 2]:
                sw = 'DOWN'
            else:
                sw = 'NEUTRAL'
            out[f'B2_swing_{tf}'] = sw
            e = ema[n - 1]; c = closes[n - 1]
            out[f'B3_ema20_{tf}'] = 'UP' if c > e else 'DOWN' if c < e else 'NEUTRAL'
        return out


class ATRIndex:
    """Plain-SMA ATR(14) of 1h bars closed at or before the touch (FORMULAS.md section 12)."""

    def __init__(self, bars, period=14):
        agg = et._agg(bars, 60)
        self.ends = [b['t'] + 60000 for b in agg]
        tr = []
        for k, b in enumerate(agg):
            if k == 0:
                tr.append(b['h'] - b['l'])
            else:
                pc = agg[k - 1]['c']
                tr.append(max(b['h'] - b['l'], abs(b['h'] - pc), abs(b['l'] - pc)))
        self.tr = tr; self.period = period

    def at(self, touch_t):
        n = bisect.bisect_right(self.ends, touch_t)
        if n < self.period:
            return None
        return sum(self.tr[n - self.period:n]) / self.period


def atr14_1h(bars, touch_t):
    return ATRIndex(bars).at(touch_t)
