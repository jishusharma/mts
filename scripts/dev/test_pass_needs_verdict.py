"""A PASS needs the whole D7 condition, not only a register row.

D7_ROADMAP.md (changed 2026-11-03): "No PASS without a VERDICTS.csv row, a causal replay test and one
re-run from the trade loop by another model."

What this gate can check from the repo, per PASS subject (a layer_map value starting PASS, a task
card result starting PASS, or a PASS row of VERDICTS.csv):
  1. REGISTER   a VERDICTS.csv row with verdict PASS for the study (and arm, when named).  Verified.
  2. REPLAY     evidence field causal_replay_test: a repo file that exists and names the study.
                File existence and the study link are verified; that the test really is causal is NOT
                (needs a reviewer).
  3. RERUN      evidence fields rerun.file (exists, names the study), rerun.model and author_model, the
                two differing, rerun.trade_loop true.  Existence, the link and a different model name
                are verified; that the re-run really came from the trade loop and was independent is NOT.
Missing evidence fails closed.  The gate therefore enforces the D7 condition as CITED evidence, not as
proven evidence.  KNOWN_OFFENDERS below are NOT certified: each stays only so CI is green until its
evidence exists, and a stale allowance (the subject no longer offends) fails the suite.
"""
import csv
import json
import re
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MTS = REPO / "MyTradingSys"
PASS_RE = re.compile(r"\s*PASS\b")

# subject -> {"study_dir": register study, "arm": optional, "causal_replay_test": repo path,
#             "rerun": {"file": repo path, "model": "...", "trade_loop": true}, "author_model": "..."}
# Subjects: "layer_map:<id>:<field>", "card:<task id>", "register:<study_dir>/<arm>".
EVIDENCE = {}

# Named, with the reason each stays.  An allowance is NOT evidence of anything.
KNOWN_OFFENDERS = {
    "register:carry_basis_2026-10-18/CARRY_always_unlevered":
        "NOT certified: PASS row exists (REGISTER ok) but no causal replay test and no independent "
        "trade-loop re-run is on file; carry has not entered promoted_setups.json. Clears when evidence is added.",
    "register:carry_basis_2026-10-18/CARRY_switch_unlevered":
        "NOT certified: same as CARRY_always_unlevered; RESULT.md calls it strictly worse than always-on. "
        "Clears when evidence is added.",
    "card:meta-label-ext-pass-verdict-recheck":
        "NOT certified: card result says PASS STANDS under the literal frozen rule, but VERDICTS.csv has no "
        "PASS row for meta_label_dev_ext_2026-10-31 and no replay or re-run; the setup stays parked "
        "pre-DEV (REVIEW.md item 4). Clears when a row and evidence exist or the card result is reworded.",
}


def load_register(path=None):
    with open(path or MTS / "research" / "VERDICTS.csv", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def subjects(layer_map, cards, register):
    """Yield (subject, study_dir_or_None, arm_or_None) for every PASS claim."""
    for sect in ("backtests", "layers"):
        for row in layer_map.get(sect, []):
            for k, v in row.items():
                if isinstance(v, str) and PASS_RE.match(v):
                    yield f"layer_map:{row.get('id')}:{k}", None, None
    for c in cards:
        r = c.get("result")
        if isinstance(r, str) and PASS_RE.match(r):
            yield f"card:{c.get('id')}", None, None
    for r in register:
        if r.get("verdict", "").strip() == "PASS":
            yield f"register:{r['study_dir']}/{r['arm']}", r["study_dir"], r["arm"]


def _file_names_study(repo, rel, study):
    p = repo / rel
    if not p.is_file():
        return f"{rel} does not exist"
    if study.split("/")[0] not in p.read_text(encoding="utf-8", errors="replace"):
        return f"{rel} does not name study {study}"
    return None


def problems(subject, study, arm, register, evidence, repo=REPO):
    ev = evidence.get(subject) or {}
    study = study or ev.get("study_dir")
    arm = arm or ev.get("arm")
    out = []
    if not study:
        out.append("REGISTER: evidence has no study_dir")
    else:
        rows = [r for r in register if r["study_dir"] == study and r["verdict"].strip() == "PASS"
                and (arm is None or r["arm"] == arm)]
        if not rows:
            out.append(f"REGISTER: no VERDICTS.csv PASS row for {study} {arm or ''}".rstrip())
    rp = ev.get("causal_replay_test")
    if not rp:
        out.append("REPLAY: no causal_replay_test file cited")
    elif study:
        e = _file_names_study(repo, rp, study)
        if e:
            out.append("REPLAY: " + e)
    rr = ev.get("rerun") or {}
    if not rr.get("file"):
        out.append("RERUN: no rerun.file cited")
    elif study:
        e = _file_names_study(repo, rr["file"], study)
        if e:
            out.append("RERUN: " + e)
    if not rr.get("trade_loop"):
        out.append("RERUN: rerun.trade_loop is not true")
    m = str(rr.get("model", "")).strip().lower()
    a = str(ev.get("author_model", "")).strip().lower()
    if not m or not a:
        out.append("RERUN: rerun.model and author_model must both be named")
    elif m == a:
        out.append("RERUN: re-run model equals author model, not independent")
    return out


def audit(layer_map, cards, register, evidence, repo=REPO):
    """subject -> list of problems, for every PASS subject (empty list = evidence complete)."""
    return {s: problems(s, st, ar, register, evidence, repo) for s, st, ar in subjects(layer_map, cards, register)}


def load_cards():
    out = []
    for f in sorted((MTS / "system" / "tasks").glob("*.json")):
        try:
            out.append(json.loads(f.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            pass
    return out


def load_layer_map():
    return json.loads((MTS / "system" / "layer_map.json").read_text(encoding="utf-8"))


class Planted(unittest.TestCase):
    REG = [{"study_dir": "s_2026", "arm": "A", "verdict": "PASS"}]

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "replay.py").write_text("# causal replay for s_2026\n", encoding="utf-8")
        (self.tmp / "rerun.md").write_text("rerun of s_2026 by codex\n", encoding="utf-8")
        self.good = {"study_dir": "s_2026", "arm": "A", "causal_replay_test": "replay.py",
                     "rerun": {"file": "rerun.md", "model": "codex", "trade_loop": True},
                     "author_model": "claude"}

    def run_one(self, reg, ev):
        lm = {"backtests": [{"id": "X", "verdict": "PASS on DEV"}]}
        evidence = {"layer_map:X:verdict": ev} if ev is not None else {}
        return audit(lm, [], reg, evidence, self.tmp)["layer_map:X:verdict"]

    def test_pass_without_row_fails(self):
        self.assertTrue(any(p.startswith("REGISTER") for p in self.run_one([], self.good)))

    def test_row_alone_is_not_enough(self):
        got = self.run_one(self.REG, {"study_dir": "s_2026", "arm": "A"})
        self.assertTrue(any(p.startswith("REPLAY") for p in got), got)
        self.assertTrue(any(p.startswith("RERUN") for p in got), got)

    def test_no_evidence_at_all_fails_closed(self):
        self.assertTrue(self.run_one(self.REG, None))

    def test_full_evidence_passes(self):
        self.assertEqual(self.run_one(self.REG, self.good), [])

    def test_missing_replay_file_fails(self):
        ev = dict(self.good, causal_replay_test="nope.py")
        self.assertTrue(any("REPLAY" in p for p in self.run_one(self.REG, ev)))

    def test_replay_not_naming_study_fails(self):
        (self.tmp / "replay.py").write_text("# other\n", encoding="utf-8")
        self.assertTrue(any("REPLAY" in p for p in self.run_one(self.REG, self.good)))

    def test_same_model_rerun_fails(self):
        ev = dict(self.good, author_model="Codex")
        self.assertTrue(any("not independent" in p for p in self.run_one(self.REG, ev)))

    def test_rerun_not_trade_loop_fails(self):
        ev = dict(self.good, rerun=dict(self.good["rerun"], trade_loop=False))
        self.assertTrue(any("trade_loop" in p for p in self.run_one(self.REG, ev)))

    def test_card_and_non_pass_detection(self):
        lm = {"backtests": [{"id": "Y", "verdict": "parity PASS"}, {"id": "Z", "verdict": "FAIL"}]}
        cards = [{"id": "c", "result": "PASS STANDS"}, {"id": "d", "result": "FAIL"}]
        self.assertEqual(list(audit(lm, cards, [], {}, self.tmp)), ["card:c"])


class RealRepo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = audit(load_layer_map(), load_cards(), load_register(), EVIDENCE)

    def test_every_pass_has_full_evidence_or_named_allowance(self):
        bad = {s: p for s, p in self.audit.items() if p and s not in KNOWN_OFFENDERS}
        self.assertFalse(bad, "PASS without full D7 evidence (register row + causal replay + independent "
                              "trade-loop re-run):\n" + "\n".join(f"{s}: {p}" for s, p in bad.items()))

    def test_allowances_are_named_uncertified_and_not_stale(self):
        for s, reason in KNOWN_OFFENDERS.items():
            self.assertIn("NOT certified", reason, s)
            self.assertTrue(self.audit.get(s), f"stale allowance, remove it: {s}")

    def test_evidence_entries_point_at_real_subjects(self):
        for s in EVIDENCE:
            self.assertIn(s, self.audit, f"evidence for unknown subject {s}")


if __name__ == "__main__":
    unittest.main()
