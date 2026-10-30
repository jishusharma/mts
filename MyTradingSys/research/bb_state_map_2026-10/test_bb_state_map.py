import numpy as np
from study import classify


def test_hand_built_series():
    # 20 flat bars at 100 then a spike up: close above upper band, green, moving
    n = 30
    c = np.full(n, 100.0); c[-1] = 110.0
    o = c.copy(); o[-1] = 100.0
    h = c + 1; l = c - 1
    mid, up, lo, st, cd, rg, ok = classify(o, h, l, c)
    assert ok[-1]
    assert st[-1] == 'ABOVE_UP' and cd[-1] == 'GREEN' and rg[-1] == 'NOT_MOVING'
    # flat bars: close==mid -> UP_HALF, doji-ish, not moving
    assert st[28] == "UP_HALF" and rg[28] == 'NOT_MOVING'


def test_ramp_is_moving():
    c = np.linspace(100, 160, 40)
    mid, up, lo, st, cd, rg, ok = classify(c - 0.5, c + 0.2, c - 0.6, c)
    assert rg[-1] == 'MOVING' and cd[-1] == 'GREEN'
