"""Score the replayed Live Aid flags (events.json from replay.js). Descriptive, in-sample, no fees: a review, not a backtest."""
import json, pathlib, statistics as st
E = json.loads((pathlib.Path(__file__).parent / "events.json").read_text())
E = [e for e in E if e["r1h"] is not None]
sg = lambda x: (x > 0) - (x < 0) if x is not None else 0
def row(name, ev):
    if not ev: return "| %s | 0 | - | - | - | - |" % name
    r = [e["r1h"] for e in ev]; w = sum(1 for x in r if x > 0)
    return "| %s | %d | %d%% | %+.2f | %+.2f | %+.2f |" % (name, len(ev), round(100 * w / len(ev)), st.mean(r), st.mean(e["mfe1h"] for e in ev), st.mean(e["mae1h"] for e in ev))
def table(title, groups):
    print("\n### " + title + "\n\n| group | flags | right after 1h | avg move 1h % | avg best % | avg worst % |\n|---|---|---|---|---|---|")
    for n, ev in groups: print(row(n, ev))
S = lambda e: 1 if e["side"] == "LONG" else -1
def parts(e):
    return {"home": {"LONG": 1, "SHORT": -1}.get(e["home"], 0), "grid": {"UP": 1, "DOWN": -1}.get(e["grid"], 0),
            "adx15": sg(e["adx15"]) if e["adx15"] is not None and abs(e["adx15"]) >= 20 else 0, "adx1h": sg(e["adx1h"]) if e["adx1h"] is not None and abs(e["adx1h"]) >= 20 else 0,
            "vfi15": sg(e["vfi15"]), "wt30": sg(e["wt30"]), "wt15": sg(e["wt15"])}
for e in E: e["p"] = parts(e); e["ag"] = sum(S(e) * v for k, v in e["p"].items() if k != "wt15"); e["hr"] = (e["ts"] // 3600000) % 24
table("By flag kind", [(k, [e for e in E if e["kind"] == k]) for k in ("idea", "setup", "timing")])
ideas = [e for e in E if e["kind"] == "idea"]
table("Idea by level state", [(s, [e for e in ideas if e["state"] == s]) for s in ("REJECTED", "FAILED BREAK", "ACCEPTED")])
for kind in ("idea", "setup"):
    ev = [e for e in E if e["kind"] == kind]
    table(kind + ": agree minus disagree over 6 readings (home direction, pulse grid, ADX/DI 15m, ADX/DI 1h, Volume Flow 15m, WaveTrend 30m)",
          [("net <= -2 (against)", [e for e in ev if e["ag"] <= -2]), ("net -1..+1 (mixed)", [e for e in ev if -1 <= e["ag"] <= 1]), ("net >= +2 (with)", [e for e in ev if e["ag"] >= 2]), ("net >= +4", [e for e in ev if e["ag"] >= 4])])
    g = []
    for k in ("home", "grid", "adx15", "adx1h", "vfi15", "wt30", "wt15"):
        g += [(k + " agrees", [e for e in ev if S(e) * e["p"][k] > 0]), (k + " against", [e for e in ev if S(e) * e["p"][k] < 0])]
    table(kind + ": each reading on its own", g)
rng = lambda e: e["adx15"] is not None and abs(e["adx15"]) < 20
fade = lambda e: e["state"] in ("REJECTED", "FAILED BREAK")
table("Idea by 15m ADX regime", [("fade, ADX<20 range", [e for e in ideas if fade(e) and rng(e)]), ("fade, ADX>=20 trend", [e for e in ideas if fade(e) and not rng(e)]),
    ("accepted, ADX<20 range", [e for e in ideas if not fade(e) and rng(e)]), ("accepted, ADX>=20 trend", [e for e in ideas if not fade(e) and not rng(e)])])
table("By session (UTC)", [("Asia 00-07", [e for e in E if e["hr"] < 7]), ("Europe 07-13", [e for e in E if 7 <= e["hr"] < 13]), ("US 13-21", [e for e in E if 13 <= e["hr"] < 21]), ("late 21-24", [e for e in E if e["hr"] >= 21])])
E.sort(key=lambda e: e["ts"]); fl = 0
for i, e in enumerate(E):
    if any(x["side"] != e["side"] and 0 <= x["ts"] - e["ts"] <= 1800000 for x in E[i + 1:i + 15]): fl += 1
days = len({e["ts"] // 86400000 for e in E})
print("\nFlags: %d over %d days = %.0f a day. Followed by an opposite flag within 30 min: %d (%d%%)." % (len(E), days, len(E) / days, fl, round(100 * fl / len(E))))
last = max(e["ts"] for e in E) // 86400000
table("Last two days only", [(k, [e for e in E if e["kind"] == k and e["ts"] // 86400000 >= last - 1]) for k in ("idea", "setup", "timing")])
# his own structure: which level, and the fade of a prior-day / prior-week extreme
table("Idea fades (rejected / failed break) by level", [(n, [e for e in ideas if fade(e) and e["at"] == n]) for n in sorted({e["at"] for e in ideas})])
big = lambda e: e["at"] in ("Yesterday high", "Yesterday low", "2-day-ago high", "2-day-ago low", "Last week high", "Last week low")
table("Fade of a prior-day / prior-week extreme", [("all hours", [e for e in ideas if fade(e) and big(e)]), ("US 13-21Z", [e for e in ideas if fade(e) and big(e) and 13 <= e["hr"] < 21]),
    ("US, failed break only (swept, closed back)", [e for e in ideas if e["state"] == "FAILED BREAK" and big(e) and 13 <= e["hr"] < 21]),
    ("first such flag of the day at that level", [e for i, e in enumerate(ideas) if fade(e) and big(e) and not any(x["at"] == e["at"] and fade(x) and x["ts"] // 86400000 == e["ts"] // 86400000 and x["ts"] < e["ts"] for x in ideas)])])
r4 = [e for e in ideas if e.get("r4h") is not None]
print("\nIdea after 4h: %d flags, right %d%%, avg %+.2f%%" % (len(r4), round(100 * sum(1 for e in r4 if e["r4h"] > 0) / len(r4)), st.mean(e["r4h"] for e in r4)))
