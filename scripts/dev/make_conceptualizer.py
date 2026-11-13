"""Conceptualizer page: every trading layer's concepts in one app (operator 2026-11-12: "turn these PPTs into an application called
Conceptualizer ... put them inside one application, something like the one-page simulator").

  python scripts/dev/make_conceptualizer.py              # writes MyTradingSys/system/artifacts/conceptualizer.html
  python scripts/dev/make_conceptualizer.py --out x.html

Read-only over the repo, zero model tokens. Data, none typed into the page by hand:
  MyTradingSys/research/conceptualizer/concepts.json    layers -> concepts (a new concept = one row)
  MyTradingSys/research/conceptualizer/diagrams/*.svg   one diagram per concept (the `diagram` field)
Registry row: conceptualizer. Publish with the Artifact tool over that url, then artifacts.py publish-record --slug conceptualizer.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artifacts as af  # noqa: E402  (stamp, MTS Home banner)

REPO = HERE.parents[1]
SRC = REPO / "MyTradingSys" / "research" / "conceptualizer"
TPL = HERE / "conceptualizer.tpl.html"
OUT = REPO / "MyTradingSys" / "system" / "artifacts" / "conceptualizer.html"
STATUSES = ("failed", "inconclusive", "promising", "untested")
FIDELITY = ("match", "simplified", "distorted", "untested")
TAGS = ("SOURCED", "OURS", "NOT_SEEN")  # NOT_SEEN = a slot of the trader's that no verified source states
TAG = re.compile(r"(SOURCED|OURS|NOT_SEEN)(?=$|[\s:(*;,])")  # the whole word: "OURSELVES" is not a tag
# public repo, context only: no position sizes in rows ("10lots", "lot_size", Hindi लॉट, Rs/INR included)
SIZE = re.compile(r"(?<![a-z])lots?(?![a-z])|लॉट|₹|\brupees?\b|\b(?:rs|inr)\.?\s*\d", re.I)
NEEDED = ("id", "name", "who", "status", "quote", "rule", "ours", "params", "code", "fidelity", "support", "test", "sim", "ideas", "question")
TEXT = ("id", "name", "who", "rule", "ours")  # must be non-empty strings


def problems(data, src=SRC):
    """Every row the page cannot render, as text (empty list = ok). Never raises on odd input."""
    out = []
    layers = data.get("layers") if isinstance(data, dict) else None
    if not isinstance(layers, list):
        return ["layers is not a list"]
    lids = set()
    for L in layers:
        if not isinstance(L, dict) or not isinstance(L.get("concepts"), list):
            out.append(f"layer {L.get('id') if isinstance(L, dict) else L!r}: concepts is not a list")
            continue
        if L.get("id") in lids:
            out.append(f"{L.get('id')}: duplicate layer id")
        lids.add(L.get("id"))
        seen = set()
        for n, c in enumerate(L["concepts"]):
            if not isinstance(c, dict):
                out.append(f"{L.get('id')}/#{n}: concept is not an object")
                continue
            cid = f"{L.get('id')}/{c.get('id') or '#' + str(n)}"
            out += [f"{cid}: no {k}" for k in NEEDED if k not in c]
            out += [f"{cid}: empty {k}" for k in TEXT if k in c and not (isinstance(c[k], str) and c[k].strip())]
            if c.get("id") and c["id"] in seen:
                out.append(f"{cid}: duplicate id")
            seen.add(c.get("id"))
            if c.get("status") not in STATUSES:
                out.append(f"{cid}: status {c.get('status')!r} not one of {STATUSES}")
            fid = c.get("fidelity")
            if not (isinstance(fid, list) and fid and fid[0] in FIDELITY):
                out.append(f"{cid}: fidelity grade not one of {FIDELITY}")
            if not isinstance(c.get("quote"), dict):
                out.append(f"{cid}: quote is not an object")
            params = c.get("params", [])
            if not isinstance(params, list):
                out.append(f"{cid}: params is not a list")
                params = []
            for p in params:
                if not (isinstance(p, list) and len(p) == 3 and all(isinstance(x, str) for x in p) and TAG.match(p[2])):
                    out.append(f"{cid}: param {p!r} needs 3 strings and a SOURCED, OURS or NOT_SEEN tag")
                    continue
                if SIZE.search(" ".join(p)):
                    out.append(f"{cid}: param {p[0]!r} carries a size word (lot, rupee)")
            d = c.get("diagram")
            if d and not (isinstance(d, str) and d.endswith(".svg") and "/" not in d and "\\" not in d and (src / "diagrams" / d).is_file()):
                out.append(f"{cid}: diagram {d} missing (a .svg file name in diagrams/)")
    return out


def load(src=SRC):
    data = json.loads((src / "concepts.json").read_text(encoding="utf-8"))
    bad = problems(data, src)
    if bad:
        raise SystemExit("conceptualizer: " + "; ".join(bad))
    for L in data["layers"]:
        for c in L["concepts"]:
            d = c.get("diagram")
            c["svg"] = lf((src / "diagrams" / d).read_text(encoding="utf-8")).strip() if d else ""
    return data


def lf(text):
    """LF line ends on every host, so a Windows checkout and CI build the same page hash."""
    return text.replace("\r\n", "\n")


def render(data):
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return af.put_banner(lf(TPL.read_text(encoding="utf-8")).replace("__DATA__", blob), af.load(), "conceptualizer", strict=False)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    af.write_stamped(out, render(load()))
    print(f"conceptualizer: wrote {out}")


if __name__ == "__main__":
    main()
