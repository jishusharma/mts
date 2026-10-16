"""MTS Layers page: for every layer, where it is on the road, what is stuck and for how many days, what is planned, what is missing.

  python scripts/dev/make_layers_board.py              # writes MyTradingSys/system/artifacts/layers_board.html
  python scripts/dev/make_layers_board.py --out x.html

Read-only over the repo, zero model tokens (operator ask 2026-10-13: "I do not see the progress in each layer I do not see what is
stuck where for how many days I do not see what is the roadmap for a particular layer"). Sources, none copied by hand into the page:
  MyTradingSys/system/layer_index.json      families: name, plain, status, path (the 8-step road), cards globs
  MyTradingSys/system/tasks/*.json          cards, joined to a family like LAYERS.md does (make_layers_md.card_family)
  git log of the card files                 days since a card last changed (the "stuck for N days" number)
  MyTradingSys/system/claims/*.md           who holds what, and since when
  MyTradingSys/system/OPERATOR_DECISIONS.md questions waiting on the operator
  MyTradingSys/system/layer_map.json        backtests per layer
  MyTradingSys/system/HOW_MTS_RUNS.md       the "How MTS runs" tab
Registry row: mts_layer_map (same url and pin as the old Layer Map page). Publish with the Artifact tool over that url.
"""
import argparse
import html
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_layers_md  # noqa: E402  (card_family, load)
import artifacts as af  # noqa: E402  (MTS Home banner)

REPO = HERE.parents[1]
SYS = "MyTradingSys/system"
TPL = HERE / "layers_board.tpl.html"
OUT = REPO / SYS / "artifacts" / "layers_board.html"
STEPS = [("idea", "Idea written"), ("inputs", "Inputs in BTC data"), ("fees", "Fees fit"), ("charts", "Seen on charts"),
         ("built", "Built"), ("dev", "DEV test"), ("oos", "Out-of-sample check"), ("testnet", "Testnet")]
STATUSES = ("done", "now", "planned", "later", "missing", "failed", "skip")
OPEN = ("raw", "refined", "ready", "active", "blocked")
DAY = 86400.0


def git(repo, *args):
    try:
        r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=60)
        return r.stdout if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def card_times(repo):
    """Card file -> epoch of the last commit that touched it; uncommitted edits count as now."""
    out, ts = {}, None
    for line in git(repo, "log", "--format=@%ct", "--name-only", "--", f"{SYS}/tasks").splitlines():
        if line.startswith("@"):
            ts = int(line[1:])
        elif line.strip() and ts is not None:
            out.setdefault(line.strip(), ts)
    now = int(time.time())
    for line in git(repo, "status", "--porcelain", "--", f"{SYS}/tasks").splitlines():
        out[line[3:].strip()] = now
    return out


def created_epoch(card):
    try:
        return datetime.strptime(card.get("created", ""), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()
    except ValueError:
        return None


def claims(repo, now):
    rows = []
    for p in sorted((Path(repo) / SYS / "claims").glob("*.md")):
        kv = dict(re.findall(r"^(\w+):\s*(.*)$", p.read_text(encoding="utf-8"), re.M))
        try:
            age_h = (now - int(kv.get("epoch", ""))) / 3600.0
        except ValueError:
            age_h = None
        rows.append({"task": kv.get("task", p.stem), "host": kv.get("host", "?"), "account": kv.get("account", "?"),
                     "age_h": None if age_h is None else round(age_h, 1)})
    return rows


def decisions(repo, now):
    p = Path(repo) / SYS / "OPERATOR_DECISIONS.md"
    if not p.is_file():
        return []
    rows = []
    for block in re.split(r"^## ", p.read_text(encoding="utf-8"), flags=re.M)[1:]:
        lines = block.splitlines()
        head = [x.strip() for x in lines[0].split("|")]
        if len(head) < 2 or not head[1].startswith("asked "):
            continue
        field = {k: v.strip() for k, v in re.findall(r"^(Recommended|Answer|Applied):\s*(.*)$", block, re.M)}
        question = next((x.strip() for x in lines[1:] if x.strip()), "")
        asked = head[1][6:].strip()
        try:
            days = int((now - datetime.strptime(asked, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()) // DAY)
        except ValueError:
            days = None
        answer = field.get("Answer", "")
        if answer.startswith("(none yet)"):
            state = "open"
        elif field.get("Applied", "").startswith("(not yet"):
            state = "answered, not applied"
        else:
            continue
        rows.append({"id": head[0], "stage": head[2] if len(head) > 2 else "", "question": question,
                     "recommended": field.get("Recommended", ""), "answer": "" if state == "open" else answer,
                     "state": state, "days": days, "no_auto": "NO AUTO-APPLY" in lines[0]})
    return rows


def md_to_html(text):
    """Small Markdown subset for HOW_MTS_RUNS.md: headings, tables, bullets, paragraphs, **bold**, `code`."""
    def inline(s):
        s = html.escape(s)
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        return re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    out, i, lines = [], 0, text.splitlines()
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            th = "".join(f"<th>{inline(c)}</th>" for c in rows[0])
            tb = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows[1:])
            out.append(f'<div class="tw"><table><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>')
            continue
        if ln.startswith("- "):
            items = []
            while i < len(lines) and (lines[i].startswith("- ") or lines[i].startswith("  ")):
                if lines[i].startswith("- "):
                    items.append(lines[i][2:].strip())
                else:
                    items[-1] += " " + lines[i].strip()
                i += 1
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>")
            continue
        m = re.match(r"^(#{1,3}) (.*)$", ln)
        if m:
            lvl = min(len(m.group(1)) + 1, 4)
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
        elif ln.strip():
            para = [ln.strip()]
            while i + 1 < len(lines) and lines[i + 1].strip() and not re.match(r"^(#|\||- )", lines[i + 1]):
                i += 1
                para.append(lines[i].strip())
            out.append(f"<p>{inline(' '.join(para))}</p>")
        i += 1
    return "\n".join(out)


def stuck_reasons(c, age, by_id):
    r = []
    if c.get("asks"):
        r.append(f"waiting for your answer: {c['asks']}")
    if c["state"] == "blocked":
        r.append(f"on hold {age} d: {(c.get('note') or 'no reason written')[:160]}")
    elif c["state"] == "ready" and age >= 2:
        r.append(f"ready for {age} d, no session has taken it")
    elif c["state"] in ("raw", "refined") and age >= 3:
        r.append(f"{c['state']} for {age} d, waiting to be scoped")
    for dep in c.get("depends_on", []):
        d = by_id.get(dep)
        if d and d["state"] in ("blocked", "dropped"):
            r.append(f"waits on {dep}, which is {d['state']}")
    return r


def build(repo=REPO, now=None):
    repo = Path(repo)
    now = now or time.time()
    idx, lmap, cards, _ = make_layers_md.load(repo)
    fams = {f["id"]: f for f in idx["families"]}
    times = card_times(repo)
    by_id = {c["id"]: c for c in cards}

    def age(c):
        t = times.get(f"{SYS}/tasks/{c['id']}.json") or created_epoch(c) or now
        return max(0, int((now - t) // DAY))

    def brief(c):
        return {"id": c["id"], "title": c.get("title", ""), "state": c["state"], "lane": c.get("lane", ""),
                "prio": c.get("prio"), "age": age(c), "why": stuck_reasons(c, age(c), by_id)}

    fam_cards = {fid: [] for fid in fams}
    loose = []
    for c in cards:
        hit = make_layers_md.card_family(c, fams)
        for fid in hit:
            fam_cards[fid].append(c)
        if not hit and c["state"] in OPEN:
            loose.append(c)
    families = []
    for f in idx["families"]:
        mine = fam_cards[f["id"]]
        opened = sorted((c for c in mine if c["state"] in OPEN), key=lambda c: (c["state"] == "blocked", c.get("prio") or 9, c["id"]))
        raw_path = f.get("path", {})
        steps = []
        for key, label in STEPS:
            st = raw_path.get(key, {})
            s = st.get("s", "later" if raw_path else "skip")
            if s not in STATUSES:
                raise SystemExit(f"layer_index.json: {f['id']}.path.{key}.s = {s!r}, not one of {STATUSES}")
            linked = [brief(by_id[i]) if i in by_id else {"id": i, "title": "card not found", "state": "missing", "age": None, "why": []}
                      for i in st.get("cards", [])]
            if s == "planned" and linked and all(x["state"] in ("done", "dropped", "missing") for x in linked):
                s = "missing"
            steps.append({"key": key, "label": label, "s": s, "note": st.get("note", ""), "cards": linked})
        applicable = [s for s in steps if s["s"] != "skip"]
        finished = [s for s in applicable if s["s"] in ("done", "failed")]
        missing = [{"step": s["label"], "note": s["note"]} for s in steps if s["s"] == "missing"]
        if raw_path and not any(c["state"] == "ready" for c in opened) and any(s["s"] in ("now", "planned") for s in steps):
            missing.append({"step": "Ready work", "note": "no card of this layer is ready, so no session can start on it"})
        held = [brief(c) for c in opened if c["state"] == "blocked"]
        stuck = [{"card": c["id"], "why": w} for c in opened if c["state"] != "blocked" for w in stuck_reasons(c, age(c), by_id)]
        moved = min((age(c) for c in mine), default=None)

        def runnable(c):
            return all(by_id.get(d, {"state": "done"})["state"] == "done" for d in c.get("depends_on", []))
        rank = {"active": 0, "ready": 0, "refined": 1, "raw": 2}
        cand = sorted((c for c in opened if c["state"] != "blocked"),
                      key=lambda c: (not runnable(c), rank.get(c["state"], 3), c.get("prio") or 9, c["id"]))
        nxt = cand[0] if cand else None
        bts = sorted((b for b in lmap["backtests"] if set(b.get("layers", [])) & set(f.get("layers", []))),
                     key=lambda b: b.get("date", ""), reverse=True)
        families.append({
            "id": f["id"], "name": f["name"], "plain": f.get("plain", ""), "status": f.get("status", ""),
            "kind": f.get("kind", "layer"), "steps": steps if raw_path else [],
            "progress": [len(finished), len(applicable)], "missing": missing, "stuck": stuck, "held": held,
            "moved_days": moved, "next": brief(nxt) if nxt else None, "open": [brief(c) for c in opened],
            "done_count": sum(1 for c in mine if c["state"] == "done"),
            "backtests": [{"date": b.get("date", ""), "id": b["id"], "verdict": str(b.get("verdict") or "not recorded")[:160]} for b in bts[:8]],
            "files": {k: f.get(k, []) for k in ("spec", "roadmap", "ledger")},
        })
    cl = claims(repo, now)
    dec = decisions(repo, now)
    counts = {}
    for c in cards:
        counts[c["state"]] = counts.get(c["state"], 0) + 1
    how = repo / SYS / "HOW_MTS_RUNS.md"
    head = git(repo, "rev-parse", "--short", "HEAD").strip() or "unknown"
    return {
        "generated": datetime.fromtimestamp(now, timezone.utc).strftime("%Y-%m-%d %H:%MZ"), "commit": head,
        "steps": [{"key": k, "label": v} for k, v in STEPS], "families": families,
        "decisions": dec, "claims": cl, "stale_claims": [c for c in cl if c["age_h"] is not None and c["age_h"] > 24],
        "held": [brief(c) for c in cards if c["state"] == "blocked"],
        "loose": [brief(c) for c in sorted(loose, key=lambda c: (c.get("prio") or 9, c["id"]))],
        "counts": counts, "how": md_to_html(how.read_text(encoding="utf-8")) if how.is_file() else "",
        "totals": {"stuck": sum(len(f["stuck"]) for f in families), "missing": sum(len(f["missing"]) for f in families),
                   "waiting": sum(1 for d in dec if d["state"] == "open")},
    }


def render(data):
    return af.put_banner(TPL.read_text(encoding="utf-8").replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/")), af.load(), "mts_layer_map", strict=False)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args(argv)
    data = build()
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(data), encoding="utf-8", newline="\n")
    t = data["totals"]
    print(f"wrote {out} ({len(data['families'])} layers, {t['stuck']} stuck, {t['missing']} missing, {t['waiting']} decisions open)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
