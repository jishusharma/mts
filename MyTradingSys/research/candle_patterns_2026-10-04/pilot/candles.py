"""Candle pattern detectors. Definitions are frozen in PRE_REG_CANDLE_PILOT.md section 4; this file only implements them.
Pure functions on a bar list (dicts with o,h,l,c). A signal at index i uses bars[<= i] only (causal).
"""
import sys
sys.dont_write_bytecode = True

# expected direction of the textbook claim: +1 bullish, -1 bearish
DIRECTIONAL = {
    "bull_engulf": 1, "bear_engulf": -1, "bull_harami": 1, "bear_harami": -1,
    "hammer": 1, "hanging_man": -1, "inv_hammer": 1, "shooting_star": -1,
    "morning_star": 1, "evening_star": -1, "three_white_soldiers": 1, "three_black_crows": -1,
    "piercing": 1, "dark_cloud": -1, "hikkake_bull": 1, "hikkake_bear": -1,
    "marubozu_up": 1, "marubozu_dn": -1,
}
VOL_STATES = ("doji", "inside_bar", "nr7")


def _f(b):
    o, h, l, c = b["o"], b["h"], b["l"], b["c"]
    body, rng = abs(c - o), h - l
    return {"o": o, "h": h, "l": l, "c": c, "body": body, "rng": rng,
            "up": h - max(o, c), "lo": min(o, c) - l, "green": c > o, "red": c < o}


def signals(bars):
    """Return {name: [i, ...]} for every directional pattern and volatility state."""
    n = len(bars)
    f = [_f(b) for b in bars]
    out = {k: [] for k in list(DIRECTIONAL) + list(VOL_STATES)}

    def add(name, i):
        out[name].append(i)

    for i in range(n):
        x = f[i]
        if x["rng"] <= 0:
            continue
        # --- single bar / volatility states
        if x["body"] <= 0.1 * x["rng"]:
            add("doji", i)
        if i >= 1 and x["h"] <= f[i - 1]["h"] and x["l"] >= f[i - 1]["l"]:
            add("inside_bar", i)
        if i >= 6 and x["rng"] <= min(f[j]["rng"] for j in range(i - 6, i)):
            add("nr7", i)
        if i >= 4:
            down = f[i - 1]["c"] < f[i - 4]["c"]
            up = f[i - 1]["c"] > f[i - 4]["c"]
            if x["body"] > 0 and x["lo"] >= 2 * x["body"] and x["up"] <= 0.1 * x["rng"]:
                if down:
                    add("hammer", i)
                if up:
                    add("hanging_man", i)
            if x["body"] > 0 and x["up"] >= 2 * x["body"] and x["lo"] <= 0.1 * x["rng"]:
                if down:
                    add("inv_hammer", i)
                if up:
                    add("shooting_star", i)
        if i >= 14 and x["body"] >= 0.9 * x["rng"]:
            mean_rng = sum(f[j]["rng"] for j in range(i - 14, i)) / 14.0
            if x["rng"] >= 1.5 * mean_rng:
                add("marubozu_up" if x["green"] else "marubozu_dn", i)
        # --- two bar
        if i >= 1:
            p = f[i - 1]
            if p["rng"] > 0:
                if p["red"] and x["green"] and x["o"] <= p["c"] and x["c"] >= p["o"] and x["body"] > p["body"]:
                    add("bull_engulf", i)
                if p["green"] and x["red"] and x["o"] >= p["c"] and x["c"] <= p["o"] and x["body"] > p["body"]:
                    add("bear_engulf", i)
                if p["red"] and x["green"] and x["o"] > p["c"] and x["c"] < p["o"]:
                    add("bull_harami", i)
                if p["green"] and x["red"] and x["o"] < p["c"] and x["c"] > p["o"]:
                    add("bear_harami", i)
                mid = (p["o"] + p["c"]) / 2.0
                if p["red"] and x["green"] and x["o"] <= p["c"] and mid < x["c"] < p["o"]:
                    add("piercing", i)
                if p["green"] and x["red"] and x["o"] >= p["c"] and p["o"] < x["c"] < mid:
                    add("dark_cloud", i)
        # --- three bar
        if i >= 2:
            a, b = f[i - 2], f[i - 1]
            if a["red"] and b["body"] <= 0.3 * a["body"] and x["green"] and x["c"] > (a["o"] + a["c"]) / 2.0:
                add("morning_star", i)
            if a["green"] and b["body"] <= 0.3 * a["body"] and x["red"] and x["c"] < (a["o"] + a["c"]) / 2.0:
                add("evening_star", i)
            if a["green"] and b["green"] and x["green"] and a["c"] < b["c"] < x["c"] \
                    and a["o"] <= b["o"] <= a["c"] and b["o"] <= x["o"] <= b["c"]:
                add("three_white_soldiers", i)
            if a["red"] and b["red"] and x["red"] and a["c"] > b["c"] > x["c"] \
                    and a["c"] <= b["o"] <= a["o"] and b["c"] <= x["o"] <= b["o"]:
                add("three_black_crows", i)
        # --- hikkake: mother m, inside m+1, false break m+2, first confirming close at i in m+3..m+5
        for m in (i - 3, i - 4, i - 5):
            if m < 0:
                continue
            mo, ins, brk = f[m], f[m + 1], f[m + 2]
            if not (ins["h"] < mo["h"] and ins["l"] > mo["l"]):
                continue
            if brk["h"] < ins["h"] and brk["l"] < ins["l"]:     # false break down -> bullish
                if x["c"] > ins["h"] and all(f[j]["c"] <= ins["h"] for j in range(m + 3, i)):
                    add("hikkake_bull", i)
                    break
            if brk["h"] > ins["h"] and brk["l"] > ins["l"]:     # false break up -> bearish
                if x["c"] < ins["l"] and all(f[j]["c"] >= ins["l"] for j in range(m + 3, i)):
                    add("hikkake_bear", i)
                    break
    return out
