"""Exit-rule engine for the RSI-confirm exits study (PRE_REG.md). numpy only, vectorised over trades.
Global arrays hold all coins concatenated; a trade is given by g0 = global index of the entry bar (last 1h bar of the confirm bar);
the walk reads bars g0+1+k only (the entry bar is never read). Forward-reading helpers are named fwd_*."""
import numpy as np

WIN = 168

# name: dict(kind, params); kinds: time, tgt, rsi, ma_touch, ma_close, be_tgt, trail, half_trail
RULES = [
    ("time2", dict(kind="time", n=2)), ("time4", dict(kind="time", n=4)), ("time8", dict(kind="time", n=8)),
    ("tgt0.5R", dict(kind="tgt", r=0.5, cap=72)), ("tgt0.75R", dict(kind="tgt", r=0.75, cap=72)),
    ("rsi30", dict(kind="rsi", x=30.0, cap=168)), ("rsi40", dict(kind="rsi", x=40.0, cap=168)), ("rsi50", dict(kind="rsi", x=50.0, cap=168)),
    ("ma20touch", dict(kind="ma_touch", cap=168)), ("ma20close", dict(kind="ma_close", cap=168)),
    ("be_tgt2", dict(kind="be_tgt", r=2.0, cap=72)), ("trail", dict(kind="trail", cap=168)), ("half_trail", dict(kind="half_trail", cap=168)),
    ("confstop_1R", dict(kind="tgt", r=1.0, cap=72, conf=True)), ("confstop_2R", dict(kind="tgt", r=2.0, cap=72, conf=True)),
    ("base_1R", dict(kind="tgt", r=1.0, cap=72)),
]


def fwd_sim(p, G, g0, entry, stop):
    """Walk the forward 1h bars. G = dict(o,h,l,c,rsi,sma) global arrays. Returns gross fraction return per trade (no costs).
    Within a bar: trail update (prior bar low) -> stop check (fill min(stop, open)) -> target/exit -> arming. Stop first."""
    kind = p["kind"]
    n = len(g0)
    risk = entry - stop
    cap = p.get("n", p.get("cap", WIN))
    st = np.asarray(stop, float).copy()
    armed = np.zeros(n, bool)
    w = np.ones(n)
    real = np.zeros(n)
    out = np.full(n, np.nan)
    done = np.zeros(n, bool)
    tp = entry + p["r"] * risk if kind in ("tgt", "be_tgt") else None
    arm_px = entry + 0.5 * risk
    for k in range(cap):
        act = np.flatnonzero(~done)
        if len(act) == 0:
            break
        i = g0[act] + 1 + k
        o, h, l, c = G["o"][i], G["h"][i], G["l"][i], G["c"][i]
        en = entry[act]
        if kind in ("trail", "half_trail"):
            st[act] = np.where(armed[act], np.maximum(st[act], G["l"][i - 1]), st[act])
        s = st[act]
        hit = l <= s
        res = np.where(hit, real[act] + w[act] * (np.minimum(s, o) - en) / en, np.nan)
        ex = hit.copy()
        if kind in ("tgt", "be_tgt"):
            t = (~ex) & (h >= tp[act])
            res = np.where(t, real[act] + w[act] * (tp[act] - en) / en, res)
            ex |= t
        elif kind == "rsi":
            t = (~ex) & (G["rsi"][i] > p["x"])
            res = np.where(t, real[act] + w[act] * (c - en) / en, res)
            ex |= t
        elif kind == "ma_touch":
            lvl = G["sma"][i - 1]
            t = (~ex) & (h >= lvl)
            res = np.where(t, real[act] + w[act] * (np.maximum(lvl, o) - en) / en, res)
            ex |= t
        elif kind == "ma_close":
            t = (~ex) & (c > G["sma"][i])
            res = np.where(t, real[act] + w[act] * (c - en) / en, res)
            ex |= t
        if k == cap - 1:
            t = ~ex
            res = np.where(t, real[act] + w[act] * (c - en) / en, res)
            ex |= t
        if kind in ("be_tgt", "trail", "half_trail"):
            na = (~ex) & (~armed[act]) & (h >= arm_px[act])
            ia = act[na]
            armed[ia] = True
            if kind == "be_tgt":
                st[ia] = np.maximum(st[ia], entry[ia])
            elif kind == "half_trail":
                real[ia] = 0.5 * (arm_px[ia] - entry[ia]) / entry[ia]
                w[ia] = 0.5
        out[act[ex]] = res[ex]
        done[act[ex]] = True
    return out


def costs(taker, slip_rt):
    return 2 * taker + slip_rt
