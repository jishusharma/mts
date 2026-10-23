"""Small deterministic harness for shadowing finished CODEX lab cards."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
import tasks
import lab_flow

OUT = ROOT / "MyTradingSys/research/lab_guy/planted"
FLOW = ROOT / "MyTradingSys/research/lab_guy/FLOW_PLANTED_2026-10-18.md"
RUNS = tasks.RUNS_JSONL
CLASSES = ["wrong data copy", "one-bar shift", "holdout leak", "expected value copied from code",
           "deleted trial rows", "zero slippage", "edited gate constant", "mislabelled SOURCED number",
           "wrong data copy", "mislabelled SOURCED number"]

def _read_json(p):
    return json.loads(p.read_text(encoding="utf-8"))

def _runs():
    return [json.loads(s) for s in RUNS.read_text(encoding="utf-8").splitlines() if s.strip()] if RUNS.is_file() else []

def _ledger(cid):
    return [s for s in (ROOT / tasks.TRIALS).read_text(encoding="utf-8").splitlines() if cid in s]

def eligible():
    out = []
    for p in sorted((ROOT / tasks.DIR / "archive").glob("*.json")):
        c = _read_json(p)
        if c.get("state") != "done" or c.get("lane") != "CODEX":
            continue
        m = re.search(r"MyTradingSys/research/layer_lab/reports/[\w./-]+\.md", c.get("result", ""))
        if not m or not (ROOT / m.group()).is_file():
            continue
        if tasks.problems(c, tasks.load_all(ROOT), tasks.registry(ROOT), repo=ROOT):
            continue
        if lab_flow.gate(c, tasks.load_all(ROOT), ROOT):
            continue
        try:
            lab_flow.fingerprint(ROOT, c.get("scope_in", []), c.get("flow", {}).get("data_scope"))
        except (ValueError, OSError):
            continue
        led = _ledger(c["id"])
        count = sum(r.get("card") == c["id"] for r in _runs())
        if len(led) == count:
            out.append((c, ROOT / m.group(), led, count))
    return out

def _plant(card, ledger, cls):
    shadow = json.loads(json.dumps(card))
    if cls == "deleted trial rows":
        if not ledger:
            raise ValueError("selected card has no trial rows")
        return shadow, [], "TRIALS excerpt", ledger, []
    before = shadow.get("result", "")
    suffix = {
        "wrong data copy": " [wrong data copy]",
        "one-bar shift": " [bar-open shifted +1]",
        "holdout leak": " [HOLDOUT read]",
        "expected value copied from code": " [expected value copied from code]",
        "zero slippage": " [slippage=0]",
        "edited gate constant": " [gate constant=0]",
        "mislabelled SOURCED number": " SOURCED: 999 (source omitted)",
    }[cls]
    shadow["result"] = before + suffix
    return shadow, ledger, "card.result", before, shadow["result"]

def _checks(card, ledger):
    failed = []
    if tasks.problems(card, tasks.load_all(ROOT), tasks.registry(ROOT), repo=ROOT):
        failed.append("tasks.problems")
    if lab_flow.gate(card, tasks.load_all(ROOT), ROOT):
        failed.append("lab_flow.gate")
    try:
        lab_flow.fingerprint(ROOT, card.get("scope_in", []), card.get("flow", {}).get("data_scope"))
    except (ValueError, OSError):
        failed.append("lab_flow.fingerprint")
    nrun = sum(r.get("card") == card.get("id") for r in _runs())
    if len(ledger) != nrun:
        failed.append("tasks.trial_ledger_runs_count")
    return failed

def run():
    pool = eligible()
    if len(pool) < 10:
        raise RuntimeError(f"only {len(pool)} clean originals pass all checks; need 10")
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    for i, ((card, report_path, ledger, nrun), cls) in enumerate(zip(pool[:10], CLASSES), 1):
        original = json.loads(json.dumps(card))
        report = report_path.read_text(encoding="utf-8")
        if _checks(original, ledger):
            raise AssertionError(f"clean original fails: {card['id']}")
        shadow, led_shadow, location, before, after = _plant(card, ledger, cls)
        if before == after:
            raise AssertionError("no-op plant rejected")
        changed = sum(shadow.get(k) != card.get(k) for k in set(shadow) | set(card)) + (led_shadow != ledger)
        if changed != 1:
            raise AssertionError(f"expected one changed hunk, observed {changed}")
        rejects = _checks(shadow, led_shadow)
        d = OUT / f"{i:02d}"
        d.mkdir(parents=True, exist_ok=True)
        (d / "card.original.json").write_text(json.dumps(original, indent=2, ensure_ascii=False)+"\n", encoding="utf-8", newline="\n")
        (d / "card.shadow.json").write_text(json.dumps(shadow, indent=2, ensure_ascii=False)+"\n", encoding="utf-8", newline="\n")
        (d / "report.md").write_text(report, encoding="utf-8", newline="\n")
        (d / "trials_excerpt.md").write_text("\n".join(led_shadow)+"\n", encoding="utf-8", newline="\n")
        runrows = [r for r in _runs() if r.get("card") == card["id"]]
        (d / "runs_excerpt.jsonl").write_text("".join(json.dumps(r, sort_keys=True)+"\n" for r in runrows), encoding="utf-8", newline="\n")
        records.append({"n": i, "card": card["id"], "report": report_path.relative_to(ROOT).as_posix(),
                        "class": cls, "location": location, "original_value": before, "planted_value": after,
                        "trial_rows": len(ledger), "run_rows": nrun, "caught": bool(rejects),
                        "rejecting_checks": rejects, "changed_hunks": 1})
    manifest = {"shadows": records, "machine_checks": ["tasks.problems", "lab_flow.gate", "lab_flow.fingerprint", "tasks.trial_ledger_runs_count"]}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False)+"\n", encoding="utf-8", newline="\n")
    lines = ["# Planted-error trial: machine layer", "", "Verdict: MACHINE-ONLY; stack rows remain for the coordinator.", "",
             "| Error class | Caught | Missed | Cheap Haiku/Flash (tokens / effort) | Expensive Argon/GPT-high (tokens / effort) |", "|---|---:|---:|---|---|"]
    for cls in sorted(set(CLASSES)):
        subset = [r for r in records if r["class"] == cls]
        lines.append(f"| {cls} | {sum(r['caught'] for r in subset)} | {sum(not r['caught'] for r in subset)} |  |  |")
    lines += ["", "| Shadow | Card | Class | Result | Rejecting checks |", "|---:|---|---|---|---|"]
    for r in records:
        lines.append(f"| {r['n']} | {r['card']} | {r['class']} | {'CAUGHT' if r['caught'] else 'MISSED'} | {', '.join(r['rejecting_checks']) or 'none'} |")
    lines += ["", "Missed-shadow packets are in each numbered planted folder. Prose-only semantic errors are outside machine-check visibility; model desk rows should report their tokens and effort.", ""]
    FLOW.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return manifest

if __name__ == "__main__":
    try:
        print(json.dumps(run(), indent=2))
    except (RuntimeError, AssertionError, OSError, ValueError) as exc:
        raise SystemExit(f"planted_error_trial: {exc}")
