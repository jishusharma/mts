"""POST-HOC supplement (not in PRE_REG gates): carry and buy-and-hold by window, descriptive. Carry has no parameters, so the
extra look costs no overfit; labelled exploratory. VAL and HOLD are the project's non-sealed windows; sealed 2025-07+ untouched."""
import sys, numpy as np
sys.argv = ["x", "dev"]
import run_pub as R
a = R.load_1h(); f = R.load_funding()
b = R.Bars(R.resample(a, "1d"), f, "1d")
for name, args in (("CARRY_always", (0,)), ("CARRY_switch", (1,))):
    s = R.S_carry(b, *args); held = R.held_from(s, s["kind"])
    r = R.net_series(b, held, "carry", None)
    for w in ("DEV", "VAL", "HOLD"):
        m = R.window_mask(b, w); st = R.stats(r[m], 365)
        bh = R.stats(R.net_series(b, np.ones(b.n), "held", None)[m], 365)
        print(f"{name:13s} {w:4s} net_ann={st['ann']:6.1f}% sharpe={st['sharpe']:5.2f} mdd={st['mdd']*100:5.1f}%  buy&hold ann={bh['ann']:6.1f}% "
              f"mean_funding_ann={b.fund[m].mean()*365*100:5.1f}% min_30d_funding_ann={np.convolve(b.fund[m],np.ones(30)/30,'valid').min()*365*100:5.1f}%")
