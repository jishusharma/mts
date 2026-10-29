"""Deterministic harness for shadowing finished CODEX lab cards (lab-planted-error-trial)."""
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
CLASSES = [
    "wrong data copy",
    "one-bar shift",
    "holdout leak",
    "expected value copied from code",
    "deleted trial rows",
    "zero slippage",
    "edited gate constant",
    "mislabelled SOURCED number",
]
MIN_CLEAN = 6


def _read_json(p):
    return json.loads(p.read_text(encoding="utf-8"))


def _runs():
    return [json.loads(s) for s in RUNS.read_text(encoding="utf-8").splitlines() if s.strip()] if RUNS.is_file() else []


def _ledger(cid):
    return [s for s in (ROOT / tasks.TRIALS).read_text(encoding="utf-8").splitlines() if cid in s]


def eligible():
    clean = []
    skipped = []
    for p in sorted((ROOT / tasks.DIR / "archive").glob("*.json")):
        c = _read_json(p)
        cid = c.get("id", p.stem)
        if c.get("state") != "done" or c.get("lane") != "CODEX":
            skipped.append({"card": cid, "reason": f"state={c.get('state')} lane={c.get('lane')}"})
            continue
        m = re.search(r"MyTradingSys/research/layer_lab/reports/[\w./-]+\.md", c.get("result", ""))
        if not m or not (ROOT / m.group()).is_file():
            skipped.append({"card": cid, "reason": "missing or invalid report path in result"})
            continue
        prob = tasks.problems(c, tasks.load_all(ROOT), tasks.registry(ROOT), repo=ROOT)
        if prob:
            skipped.append({"card": cid, "reason": f"tasks.problems: {prob}"})
            continue
        gate_err = lab_flow.gate(c, tasks.load_all(ROOT), ROOT)
        if gate_err:
            skipped.append({"card": cid, "reason": f"lab_flow.gate: {gate_err}"})
            continue
        if c.get("flow"):
            try:
                lab_flow.fingerprint(ROOT, c["flow"].get("scope_in", []), c["flow"].get("data_scope"))
            except (ValueError, OSError) as e:
                skipped.append({"card": cid, "reason": f"lab_flow.fingerprint: {e}"})
                continue
        led = _ledger(cid)
        count = sum(r.get("card") == cid for r in _runs())
        if len(led) != count:
            skipped.append({"card": cid, "reason": f"trial rows count mismatch (TRIALS={len(led)}, runs.jsonl={count})"})
            continue
        clean.append((c, ROOT / m.group(), led, count))
    return clean, skipped


def _plant(card, ledger, cls):
    shadow = json.loads(json.dumps(card))
    if cls == "deleted trial rows":
        if not ledger:
            raise ValueError(f"selected card {card['id']} has no trial rows")
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
    if card.get("flow"):
        try:
            lab_flow.fingerprint(ROOT, card["flow"].get("scope_in", []), card["flow"].get("data_scope"))
        except (ValueError, OSError):
            failed.append("lab_flow.fingerprint")
    nrun = sum(r.get("card") == card.get("id") for r in _runs())
    if len(ledger) != nrun:
        failed.append("tasks.trial_ledger_runs_count")
    return failed


def run():
    pool, skipped = eligible()
    if len(pool) < MIN_CLEAN:
        raise RuntimeError(f"only {len(pool)} clean originals pass all checks; need {MIN_CLEAN}")

    # Ensure a card with trial rows is available at index 4 (where 'deleted trial rows' is planted)
    with_ledger = [item for item in pool if len(item[2]) > 0]
    without_ledger = [item for item in pool if len(item[2]) == 0]
    # Construct ordered pool of 6 clean cards with at least one ledger-carrying card at index 4
    ordered_clean = [without_ledger[0], with_ledger[0], with_ledger[1], without_ledger[1], with_ledger[2], without_ledger[2]]

    target_classes = CLASSES   # card lab-planted-error-trial: 8 shadows, one per class (a pool of >= 10 made 10: classes 1-2 twice)

    OUT.mkdir(parents=True, exist_ok=True)
    records = []

    for i, cls in enumerate(target_classes, 1):
        card, report_path, ledger, nrun = ordered_clean[(i - 1) % len(ordered_clean)]
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
        (d / "card.original.json").write_text(json.dumps(original, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        (d / "card.shadow.json").write_text(json.dumps(shadow, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        (d / "report.md").write_text(report, encoding="utf-8", newline="\n")
        (d / "trials_excerpt.md").write_text("\n".join(led_shadow) + "\n", encoding="utf-8", newline="\n")
        runrows = [r for r in _runs() if r.get("card") == card["id"]]
        (d / "runs_excerpt.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in runrows), encoding="utf-8", newline="\n")

        records.append({
            "n": i,
            "card": card["id"],
            "report": report_path.relative_to(ROOT).as_posix(),
            "class": cls,
            "location": location,
            "original_value": before,
            "planted_value": after,
            "trial_rows": len(ledger),
            "run_rows": nrun,
            "caught": bool(rejects),
            "rejecting_checks": rejects,
            "changed_hunks": 1,
        })

    manifest = {
        "shadows": records,
        "clean_cards": [c["id"] for c, _, _, _ in ordered_clean],
        "machine_checks": ["tasks.problems", "lab_flow.gate", "lab_flow.fingerprint", "tasks.trial_ledger_runs_count"],
        "skipped_candidates": skipped,
        "note": f"6 clean cards available (not 10). {len(target_classes)} shadows generated round-robin per codex-unstick-2026-10-23.md decision."
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    lines = [
        "# Planted-error trial: machine layer",
        "",
        f"Verdict: MACHINE-ONLY; 6 clean cards available (not 10), generating {len(target_classes)} shadows round-robin per `codex-unstick-2026-10-23.md` decision. Stack rows remain for the coordinator.",
        "",
        "| Error class | Caught | Missed | Cheap Haiku/Flash (tokens / effort) | Expensive Argon/GPT-high (tokens / effort) |",
        "|---|---:|---:|---|---|",
    ]
    for cls in sorted(set(target_classes)):
        subset = [r for r in records if r["class"] == cls]
        lines.append(f"| {cls} | {sum(r['caught'] for r in subset)} | {sum(not r['caught'] for r in subset)} |  |  |")
    lines += [
        "",
        "| Shadow | Card | Class | Result | Rejecting checks |",
        "|---:|---|---|---|---|",
    ]
    for r in records:
        lines.append(f"| {r['n']} | {r['card']} | {r['class']} | {'CAUGHT' if r['caught'] else 'MISSED'} | {', '.join(r['rejecting_checks']) or 'none'} |")
    lines += [
        "",
        "Missed-shadow packets are in each numbered planted folder (`MyTradingSys/research/lab_guy/planted/<n>/`). Prose-only semantic errors are outside machine-check visibility; model desk rows should report their tokens and effort.",
        "",
    ]
    FLOW.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return manifest


if __name__ == "__main__":
    try:
        print(json.dumps(run(), indent=2))
    except (RuntimeError, AssertionError, OSError, ValueError) as exc:
        raise SystemExit(f"planted_error_trial: {exc}")
