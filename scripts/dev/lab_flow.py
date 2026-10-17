"""Reusable ordered lab recipes. launch SPEC.json [--preview]; finish CARD --report PATH --verdict PASS|REWORK|BLOCKED --result TEXT; status ID."""
import argparse
import hashlib
import csv
import json
import re
import zipfile
from pathlib import Path

import tasks

FLOWS = "MyTradingSys/research/layer_lab/flows"
DATA_ROOT = Path("F:/MTS/data")
HOLDOUT_PARTS = {"holdout", "holdouts", "validation_holdout", "test_holdout"}
DEV_CUTOFF_MS = 1719792000000  # 2024-07-01T00:00:00Z
RECIPES = {
    "critical-audit": [("map", "codex", "audit", "gpt-6.1-sol", "medium", "Map claims to source evidence; expose missing inputs and assumptions."),
                       ("challenge", "gemini", "audit", "gemini-2.5-pro", "low", "Independently try to falsify the prior findings; reproduce one material claim and resolve disagreements against sources.")],
    "build-review": [("build", "codex", "build", "gpt-6.1-sol", "medium", "Implement the scoped contract with spec-derived fail-first tests."),
                     ("challenge", "gemini", "audit", "gemini-2.5-pro", "low", "Review the resulting diff and reproduce failure modes; independently check goal coverage.")],
    "run-review": [("run", "codex", "run", "gpt-6-luna", "low", "Execute only the supplied development-data commands and record inputs, trial identity and numbers."),
                   ("verify", "gemini", "audit", "gemini-2.5-pro", "low", "Independently reproduce a headline number and check leakage, fees, trial accounting and missing data.")],
}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def safe_file(repo, rel):
    """Resolve an allowed file; only DATA_ROOT files get content timestamp checks."""
    root = Path(repo).resolve()
    requested = Path(rel)
    data_root = Path(DATA_ROOT).resolve()
    if requested.is_absolute():
        p = requested.resolve()
        if not p.is_relative_to(data_root):
            raise ValueError(f"not an existing repo or data file: {rel}")
    else:
        p = (root / requested).resolve()
        if not p.is_relative_to(root):
            raise ValueError(f"not an existing repo file: {rel}")
    if not p.is_file():
        raise ValueError(f"not an existing repo or data file: {rel}")
    if any(part.lower() in HOLDOUT_PARTS for part in p.parts):
        raise ValueError(f"holdout path refused: {rel}")
    parts = [x.lower() for x in (p.relative_to(root).parts if p.is_relative_to(root) else p.relative_to(data_root).parts)]
    if any(x in (".secrets", ".git", "execution", "alerts") or x.startswith(".env") for x in parts):
        raise ValueError(f"protected scope: {rel}")
    # Timestamp gate applies to data inputs by content, including renamed/copied files.
    if p.is_relative_to(data_root):
        try:
            if p.suffix.lower() == ".npz":
                import numpy as np
                with np.load(p, allow_pickle=False) as data:
                    if "t" not in data.files or data["t"].size == 0:
                        raise ValueError("missing open-time axis t")
                    max_open = _epoch_ms(data["t"].max())
            elif p.suffix.lower() == ".csv":
                with p.open(newline="", encoding="utf-8-sig") as f:
                    reader = csv.DictReader(f)
                    key = next((k for k in (reader.fieldnames or []) if k.lower() in ("t", "open_time", "timestamp")), None)
                    if key is None:
                        raise ValueError("missing open-time column (t/open_time/timestamp)")
                    times = [_epoch_ms(row[key]) for row in reader if row.get(key)]
                    if not times:
                        raise ValueError("empty open-time column")
                    max_open = max(times)
            elif p.suffix.lower() == ".zip":
                with zipfile.ZipFile(p) as archive:
                    csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
                    if not csv_names:
                        raise ValueError("zip has no CSV timestamp source")
                    max_open = 0
                    for name in csv_names:
                        with archive.open(name) as raw:
                            reader = csv.DictReader((line.decode("utf-8-sig") for line in raw))
                            key = next((k for k in (reader.fieldnames or []) if k.lower() in ("t", "open_time", "timestamp")), None)
                            if key is None:
                                raise ValueError(f"missing open-time column in {name}")
                            times = [_epoch_ms(row[key]) for row in reader if row.get(key)]
                            if not times:
                                raise ValueError(f"empty open-time column in {name}")
                            max_open = max(max_open, max(times))
            else:
                raise ValueError(f"unsupported data format for timestamp verification: {p.suffix or '<none>'}")
        except (OSError, ValueError, KeyError) as e:
            raise ValueError(f"cannot verify data timestamps: {rel}: {e}") from e
        if max_open is not None and max_open >= DEV_CUTOFF_MS:
            raise ValueError(f"post-cutoff data refused (max open {max_open}): {rel}")
    return p


def _epoch_ms(value):
    """Normalize Unix seconds to milliseconds; candle open times use either epoch scale."""
    timestamp = int(value)
    return timestamp * 1000 if abs(timestamp) < 100_000_000_000 else timestamp


def fingerprint(repo, scope, data_scope=None):
    hashes = {rel: hashlib.sha256(safe_file(repo, rel).read_bytes()).hexdigest() for rel in scope}
    data_root = Path(DATA_ROOT).resolve()
    for rel in data_scope or []:
        requested = Path(rel)
        p = safe_file(repo, str((data_root / requested).resolve()) if not requested.is_absolute() else str(requested))
        key = "data:" + p.relative_to(data_root).as_posix()
        hashes[key] = hashlib.sha256(p.read_bytes()).hexdigest()
    return hashes


def contract(flow):
    value = {k: flow[k] for k in ("id", "recipe", "goal", "criteria", "scope_in")}
    for key in ("risk_class", "same_vendor_override"):
        if key in flow:
            value[key] = flow[key]
    if flow.get("data_scope"):
        value["data_scope"] = flow["data_scope"]
    for key in ("commands", "tests", "mutation_check"):
        if flow.get(key):
            value[key] = flow[key]
    return digest(value)


def accepted(card, repo):
    """Runner-side verification also catches a hand-edited done flag or a stale receipt."""
    try:
        flow, receipt = card["flow"], card["flow_receipt"]
        report = safe_file(repo, receipt["report"])
        stage = RECIPES[flow["recipe"]][flow["stage"] - 1]
        return (receipt["verdict"] == "PASS" and receipt["contract"] == contract(flow) == flow["contract"]
                and receipt.get("vendor") == stage[1] and receipt.get("model") == stage[3]
                and receipt["criteria"] == ["PASS"] * len(flow["criteria"])
                and receipt["sources"] == fingerprint(repo, flow["scope_in"], flow.get("data_scope"))
                and receipt["report_sha256"] == hashlib.sha256(report.read_bytes()).hexdigest()
                and not gate(card, tasks.load_all(repo), repo))
    except (KeyError, ValueError, OSError, TypeError):
        return False


def reject_run(repo, cid, reason):
    """A runner-observed model mismatch cannot leave a valid receipt or runnable child."""
    card = tasks.get(repo, cid)
    card.update(state="blocked", result=reason)
    card.pop("flow_receipt", None)
    tasks.save(repo, card)
    for child in tasks.load_all(repo):
        if child.get("flow", {}).get("id") == card["flow"]["id"] and cid in child.get("depends_on", []):
            child["state"] = "blocked"
            tasks.save(repo, child)
    return card


def gate(card, cards, repo):
    """Receipt and artifact checks supplement the ordinary dependency state check."""
    flow = card.get("flow")
    if not flow:
        return []
    errors = []
    if flow.get("contract") != contract(flow):
        errors.append("flow contract changed; launch a new flow")
    if card.get("goal") != flow["goal"] or card.get("scope_in") != flow["scope_in"]:
        errors.append("flow card goal/scope drifted from the shared contract")
    for key in ("commands", "tests", "mutation_check"):
        if flow.get(key) and card.get("kind") == ("run" if key == "commands" else "build") and card.get(key) != flow[key]:
            errors.append(f"flow contract {key} changed; launch a new flow")
    try:
        _, vendor, kind, model, effort, lens = RECIPES[flow["recipe"]][flow["stage"] - 1]
        producer_vendor = RECIPES[flow["recipe"]][0][1]
        stage_lens = f"{vendor}/{model}: {lens}"
        if flow["stage"] < 1 or card.get("vendor") != vendor or card.get("kind") != kind or tasks.codex_setting(card) != (model, effort) or flow.get("lens") != stage_lens:
            errors.append("flow vendor/kind/model/lens drifted from the recipe")
        if flow.get("risk_class") not in (None, "C0", "C1", "C2", "C3"):
            errors.append("flow risk_class must be C0, C1, C2 or C3")
        if flow.get("same_vendor_override") is True and flow.get("risk_class") != "C0":
            errors.append("same-vendor override is allowed only for C0 cards")
        if "same_vendor_override" in flow and type(flow["same_vendor_override"]) is not bool:
            errors.append("same_vendor_override must be a boolean")
        if flow["stage"] > 1 and vendor == producer_vendor and not (
                flow.get("risk_class") == "C0" and flow.get("same_vendor_override") is True):
            errors.append("flow reviewer vendor must differ from producer vendor; explicit same_vendor_override is C0-only")
    except (KeyError, IndexError, TypeError):
        errors.append("flow recipe/stage is invalid")
    expected = []
    try:
        if flow["stage"] > 1:
            expected = [f'{flow["id"]}-{flow["stage"] - 1}-{RECIPES[flow["recipe"]][flow["stage"] - 2][0]}']
    except (KeyError, IndexError, TypeError):
        pass
    if "depends_on" in card and card.get("depends_on", []) != expected:
        errors.append(f"flow depends_on must equal {expected}")
    prev = card.get("depends_on", [])
    byid = {c["id"]: c for c in cards}
    for cid in prev:
        old = byid.get(cid, {})
        receipt = old.get("flow_receipt", {})
        if receipt.get("verdict") != "PASS" or receipt.get("contract") != flow["contract"]:
            errors.append(f"flow predecessor {cid} needs a PASS receipt for this contract")
            continue
        try:
            if fingerprint(repo, flow["scope_in"], flow.get("data_scope")) != receipt["sources"]:
                errors.append(f"flow predecessor {cid} source changed; review again")
            report = safe_file(repo, receipt["report"])
            if hashlib.sha256(report.read_bytes()).hexdigest() != receipt["report_sha256"]:
                errors.append(f"flow predecessor {cid} report changed; review again")
        except (ValueError, KeyError, OSError) as e:
            errors.append(f"flow receipt invalid: {e}")
    return errors


def launch(repo, spec, preview=False):
    cid = spec["id"]
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,23}", cid):
        raise ValueError("flow id: 1-24 lower-case letters, digits or hyphens")
    recipe = spec["recipe"]
    stages = RECIPES[recipe]
    for field in ("goal", "criteria", "scope_in"):
        if not spec.get(field):
            raise ValueError(f"{field} required")
    if not isinstance(spec["criteria"], list) or any(not isinstance(x, str) or not x.strip() for x in spec["criteria"]):
        raise ValueError("criteria must be nonempty text items")
    if any(len(x) > tasks.MAX_FIELD for x in spec["criteria"]):
        raise ValueError("criterion exceeds card text size; use a source reference")
    if spec.get("data_scope") is not None and (not isinstance(spec["data_scope"], list) or any(not isinstance(x, str) or not x for x in spec["data_scope"])):
        raise ValueError("data_scope must be a list of data file paths")
    fingerprint(repo, spec["scope_in"], spec.get("data_scope"))
    flow = {k: spec[k] for k in ("id", "recipe", "goal", "criteria", "scope_in")}
    for key in ("risk_class", "same_vendor_override"):
        if key in spec:
            flow[key] = spec[key]
    if spec.get("data_scope"):
        flow["data_scope"] = spec["data_scope"]
    for key in ("commands", "tests", "mutation_check"):
        if spec.get(key):
            flow[key] = spec[key]
    flow["contract"] = contract(flow)
    out = []
    for index, (name, vendor, kind, model, effort, lens) in enumerate(stages):
        key = f"{cid}-{index + 1}-{name}"
        stage_lens = f"{vendor}/{model}: {lens}"
        c = tasks.blank(key, f"{cid}: {name}", lane="CODEX", prio=spec.get("prio", 3), layers=spec.get("layers", []))
        c.update(vendor=vendor, kind=kind, model=model, effort=effort, size="S", goal=flow["goal"], scope_in=flow["scope_in"],
                 flow={**flow, "stage": index + 1, "vendor": vendor, "model": model, "lens": stage_lens}, gpt_only=True,
                 crucial=model == "gpt-6-astra", state="ready" if index == 0 else "blocked",
                 depends_on=[out[-1]["id"]] if out else [],
                 scope_out=["live path, secrets, holdout data, relay and unrelated files"],
                 steps=[stage_lens, "Read original sources before the prior report; report C1..Cn as PASS, REWORK or BLOCKED with file/command evidence."],
                 commands=spec.get("commands", []) if kind == "run" else [],
                 tests=spec.get("tests", "") if kind == "build" else "",
                 mutation_check=spec.get("mutation_check", "") if kind == "build" else "",
                 done_when="Each criterion has evidence; finish through lab_flow.py finish; failed criteria stop the flow.")
        if vendor == "gemini":
            c["steps"].append("Run agy.exe --print for this lens. Inline the complete report text in the prompt because headless agy cannot read report files.")
        if kind == "run":
            c["steps"].append("Append one row per execution to layer_lab/TRIALS.md with command, DEV range and result; missing inputs are NOT_IN_DATA.")
        if kind == "build":
            c["steps"].append("New behavior stays off by default; register new tests and modules in the existing gates; run only the named tests (runner gates the ship).")
        # Downstream dependencies cannot pass yet; validate the rest before writing anything.
        errors = tasks.problems({k: v for k, v in c.items() if k != "depends_on"}, tasks.load_all(repo), repo=repo)
        if errors:
            raise ValueError("; ".join(errors))
        if tasks.path_of(repo, key).exists():
            raise ValueError(f"card exists: {key}")
        out.append(c)
    manifest = Path(repo) / FLOWS / f"{cid}.json"
    if manifest.exists():
        raise ValueError(f"flow exists: {cid}")
    if not preview:
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(json.dumps({**spec, "contract": flow["contract"], "cards": [c["id"] for c in out]}, indent=2) + "\n", encoding="utf-8", newline="\n")
        for c in out:
            tasks.save(repo, c)
    return out


def finish(repo, cid, report, verdict, result):
    card = tasks.get(repo, cid)
    flow = card["flow"]
    if verdict not in ("PASS", "REWORK", "BLOCKED"):
        raise ValueError("unknown verdict")
    gate = tasks.review_gate(card, finishing=True, result=result)
    if gate:
        raise ValueError("; ".join(gate))
    if verdict == "PASS" and card.get("state") != "active":
        raise ValueError("only an active flow card can be marked done")
    errors = tasks.problems(card, tasks.load_all(repo), tasks.registry(repo), repo=repo)
    if errors:
        raise ValueError("; ".join(errors))
    p = safe_file(repo, report)
    rel = p.relative_to(Path(repo).resolve()).as_posix()
    if not rel.startswith(tasks.LAB_REPORTS + "/"):
        raise ValueError("report must be under lab reports")
    for other in tasks.load_all(repo):
        receipt = other.get("flow_receipt", {})
        if other["id"] != cid and receipt.get("report") == rel:
            raise ValueError(f"report already used by {other['id']}")
    text = p.read_text(encoding="utf-8")
    if not re.search(rf"(?m)^.*\b{re.escape(cid)}\b.*$", text):
        raise ValueError(f"report must contain a line naming card id {cid}")
    statuses = []
    for i in range(len(flow["criteria"])):
        matches = re.findall(rf"^C{i + 1}: (PASS|REWORK|BLOCKED)\s*$", text, re.M)
        if len(matches) != 1:
            raise ValueError(f"report needs one C{i + 1}: PASS|REWORK|BLOCKED line")
        statuses.extend(matches)
    evidence = len(re.findall(r"(?m)(?:\b[\w./-]+\.\w+:\d+\b|```[^\n]*\n[\s\S]*?\n```)", text))
    if evidence < len(flow["criteria"]):
        raise ValueError("report needs at least one path:line or fenced command evidence token per criterion")
    if verdict == "PASS" and any(s != "PASS" for s in statuses):
        raise ValueError("PASS contradicts criterion results")
    card.update(state="done" if verdict == "PASS" else "blocked", result=result, closed=tasks.now(),
                flow_receipt={"verdict": verdict, "contract": flow["contract"], "report": rel,
                              "vendor": card["vendor"], "model": card["model"],
                              "report_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                              "sources": fingerprint(repo, flow["scope_in"], flow.get("data_scope")), "criteria": statuses})
    tasks.save(repo, card)
    if verdict == "PASS":
        cards = tasks.load_all(repo)
        for nxt in cards:
            if nxt.get("flow", {}).get("id") == flow["id"] and nxt.get("depends_on") == [cid] and nxt["state"] == "blocked":
                if not tasks.problems(nxt, cards, tasks.registry(repo), repo=repo):
                    nxt["state"] = "ready"
                    tasks.save(repo, nxt)
    return card


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("launch")
    p.add_argument("spec")
    p.add_argument("--preview", action="store_true")
    p = sub.add_parser("finish")
    p.add_argument("card")
    p.add_argument("--report", required=True)
    p.add_argument("--verdict", required=True, choices=("PASS", "REWORK", "BLOCKED"))
    p.add_argument("--result", required=True)
    p = sub.add_parser("status")
    p.add_argument("id")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "launch":
            for c in launch(tasks.REPO, json.loads(Path(a.spec).read_text(encoding="utf-8")), a.preview):
                print(c["id"], c["state"], *tasks.codex_setting(c), c["flow"]["lens"])
        elif a.cmd == "finish":
            c = finish(tasks.REPO, a.card, a.report, a.verdict, a.result)
            print(c["id"], c["state"], a.verdict)
        else:
            cards = tasks.load_all(tasks.REPO)
            for c in cards:
                if c.get("flow", {}).get("id") == a.id:
                    print(c["id"], c["state"], c.get("flow_receipt", {}).get("verdict", "waiting"), "; ".join(tasks.problems(c, cards)))
    except (ValueError, KeyError, OSError) as e:
        raise SystemExit(f"lab_flow: {e}") from e


if __name__ == "__main__":
    main()
