"""nk_extract_concepts.py: producer for the Conceptualizer layer `nk-stocktalk` (one concept per NK extract video) and NK_FACTS.md.

  python scripts/dev/nk_extract_concepts.py sync    # rewrites the nkx-* concepts in concepts.json and NK_FACTS.md from interviews/*/EXTRACT.md
  python scripts/dev/nk_extract_concepts.py check   # exit 1 when concepts.json / NK_FACTS.md differ from what sync would write

Consumer: make_conceptualizer.py (problems() validates every concept, so a bad row breaks the page build) and
scripts/dev/test_nk_extract_concepts.py. Every quote in a concept is copied from an extract that passes verify_extract_quotes.py;
the concept's source cell names the extract and the caption file. Status is `untested` unless a study folder tests that very rule.
"""
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_conceptualizer as mc  # noqa: E402

REPO = HERE.parents[1]
IV = REPO / "MyTradingSys" / "research" / "nk_stocktalk_1113" / "interviews"
CONCEPTS = mc.SRC / "concepts.json"
FACTS = mc.SRC / "NK_FACTS.md"
LAYER = "nk-stocktalk"
PREFIX = "nkx-"
# id -> (concept name, kind, what the video is, question, ours)
VIDEOS = {
    "77zgR9gLsdk": ("Process and psychology talk (Josh Talks)", "interview", "Interview: mindset, no indicator rules.",
                    "Can a process rule (year-long horizon, no recovery trading) be tested without his P&L?",
                    "Not testable as a price rule; no indicator or number in the extract"),
    "AKZ-7zvDxpY": ("2025 plan: two-close rule and Supertrap", "own class", "NK's 2025 plan and the Supertrap pattern.",
                    "Does the two-close breach rule beat a one-close rule on BTC daily and monthly?",
                    "Two-close tested as NKN-02 (UNDERPOWERED); Supertrap too rare in earlier proxies"),
    "PV9HZB8Sb8Q": ("Hilega Milega uses class", "own class", "NK's class on gap-up entry, timeframe choice and the two intraday setups.",
                    "Do the gap-up wait and the 20/50 MA short-only filter hold on crypto 15m to 1h?",
                    "Gap-entry proxy and HM states tested in NK4/NKN-05; the 20/50 MA short-only filter not tested alone"),
    "myTLQIDeBWs": ("HM backtest by a third party", "third party", "Digital Nivesh restating the Hilega Milega rule.",
                    "Does the third-party restatement match NK's own class formula (RSI 9, WMA 21, EMA 3)?",
                    "Third-party words, not NK's; used only to cross-check the formula"),
    "ph29IMvOlhc": ("F&O hedging interview (Face2Face)", "interview", "Interview on hedging; no HM, band or pivot rules.",
                    "Is any hedge ratio stated that can be mapped to Deribit testnet options?",
                    "Options hedging only; no option chain in the pipeline, not testable"),
    "tNUicfATYOo": ("HM strategy tested 100 times (third party)", "third party", "Trader Insights restating the rule with a 100-trade test.",
                    "Do the third party's trade counts and rules match what we tested as HM?",
                    "Third-party claim; tested as HM flips in NK4 and NKN-05, not as his 100 trades"),
    "yLordo6aLP0": ("Advance HM top formation (blue line)", "third-party channel", "48-second short in NK's voice on the blue line reversal.",
                    "Is the blue line signal a testable state or only a description?",
                    "Single claim, no number; not testable as stated"),
}
BLOCK = re.compile(r'^> "(?P<q>.+)"\n\*\*Source GPS: (?P<vid>[^ |]+) \| (?P<third>[A-Z]+)\*\*\n- \[(?P<ts>[0-9:]+)\] (?P<rule>.+)$', re.M)


def extract_rows(vid):
    text = (IV / vid / "EXTRACT.md").read_text(encoding="utf-8")
    rows = [m.groupdict() for m in BLOCK.finditer(text)]
    return [r for r in rows if r["vid"] == vid and not mc.SIZE.search(r["q"] + " " + r["rule"])]


def build_concept(vid, rows):
    name, kind, what, question, ours = VIDEOS[vid]
    cap = f"MyTradingSys/research/nk_stocktalk_1113/interviews/{vid}/CAPTIONS_timed.txt"
    first = rows[0]
    return {
        "id": PREFIX + vid.lower().replace("_", "-"),
        "name": name,
        "who": "Nitish Kumar (NK StockTalk)" if kind in ("own class", "interview") else f"NK StockTalk, {kind} source",
        "status": "untested",
        "diagram": "",
        "quote": {
            "text": first["q"],
            "src": f"MyTradingSys/research/nk_stocktalk_1113/interviews/{vid}/EXTRACT.md | {cap} [{first['ts']}]",
            "check": "verified (verify_extract_quotes.py exit 0)",
        },
        "rule": f"{what} {len(rows)} quoted rule(s) in the extract; first: {first['rule']}",
        "ours": ours,
        "params": [[r["rule"][:90], f"quoted at [{r['ts']}]", f"SOURCED: «{r['q']}» {vid} {r['ts']}"] for r in rows[:8]],
        "code": "none",
        "fidelity": ["untested", f"{kind}; auto-captions garble Hindi and English terms"],
        "support": [["NK extract", vid, "research"]],
        "test": {"study": "none for this video as a whole", "n": "-", "net": "-", "verdict": "UNTESTED", "lesson": ours},
        "sim": {"where": "none", "path": "no study for this on the sim desk", "status": "not on sim"},
        "ideas": {},
        "question": question,
    }


def facts_md(per_video):
    out = ["# NK facts from the 7 extract videos (generated by scripts/dev/nk_extract_concepts.py, do not edit)", "",
           "Every quote below is copied from `interviews/<id>/EXTRACT.md` (verify_extract_quotes.py exit 0). Rows with a lot or rupee word are dropped (public repo).",
           "NOT_SEEN gaps: no caption track for QOawWwI4zUQ, X8W0pWK0GnM, 1bpY43ybo_I, 3hhkEwBfWeo (see interviews/EXTRACT.md); the SRP acronym is never spoken.", ""]
    for vid, rows in per_video.items():
        out += [f"## {vid}: {VIDEOS[vid][0]} ({VIDEOS[vid][1]})", ""]
        out += [f"- [{r['ts']}] {r['rule']}  \n  > {r['q']}" for r in rows]
        out.append("")
    return "\n".join(out)


def desired(data):
    per_video = {v: extract_rows(v) for v in VIDEOS}
    data = json.loads(json.dumps(data))
    layer = next(L for L in data["layers"] if L["id"] == LAYER)
    layer["concepts"] = [c for c in layer["concepts"] if not c["id"].startswith(PREFIX)]
    layer["concepts"] += [build_concept(v, r) for v, r in per_video.items() if r]
    return data, facts_md(per_video)


def current():
    return json.loads(CONCEPTS.read_text(encoding="utf-8"))


def render_json(data):
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def differs():
    data, facts = desired(current())
    out = []
    if render_json(data) != CONCEPTS.read_text(encoding="utf-8"):
        out.append(str(CONCEPTS))
    if not FACTS.is_file() or FACTS.read_text(encoding="utf-8") != facts:
        out.append(str(FACTS))
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "sync":
        d, f = desired(current())
        CONCEPTS.write_text(render_json(d), encoding="utf-8", newline="\n")
        FACTS.write_text(f, encoding="utf-8", newline="\n")
        print("synced", len([c for c in next(L for L in d["layers"] if L["id"] == LAYER)["concepts"] if c["id"].startswith(PREFIX)]), "nkx concepts")
    else:
        bad = differs()
        print("OK" if not bad else "OUT OF SYNC: " + ", ".join(bad))
        sys.exit(1 if bad else 0)
