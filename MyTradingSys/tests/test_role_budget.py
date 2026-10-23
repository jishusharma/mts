"""Role files stay short and current (operator 2026-10-20: simplify every role, make each apt for its job).

A role file is injected into every turn of its session, so its size is paid on every turn. Budgets are OURS: the
2026-10-20 simplified size plus about 10 percent headroom. Retired wording must not come back.
"""
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROLES = REPO / "MyTradingSys" / "system" / "roles"

BUDGET = {  # bytes, OURS
    "1985artifacts_guy.md": 2200, "admin_guy.md": 5200, "builder.md": 1500, "eagle_eyes.md": 7100, "lab_guy.md": 8300,
    "mts_doctor.md": 1700, "pipeliner.md": 9200, "session_planner.md": 11500, "supervisor.md": 7000, "thinker.md": 9300,
}

RETIRED = [  # (pattern, why it is retired)
    (r"<=\s*40 turns", "turn caps replaced by context caps (WORKERS.md rule 5)"),
    (r"tool-turn cap", "turn caps replaced by context caps"),
    (r"500k context", "Opus/Thinker caps replaced (WORKERS.md rule 5)"),
    (r"Live_Chart_Runner", "old role name"),
    (r"filed from the operator's paste", "history note, not an instruction"),
]
OWNED_ELSEWHERE = {"supervisor.md"}  # rewritten on branch super-5h-no-cap; checked for size only


def crlf_size(data):
    """Bytes on a Windows (CRLF) checkout, the same on every OS: 2026-10-22 supervisor.md was 6984 bytes on Linux and passed, 7050 on
    the Windows CI shard and failed."""
    lf = data.replace(b"\r\n", b"\n")
    return len(lf) + lf.count(b"\n")


class TestRoleBudget(unittest.TestCase):
    def test_every_role_file_has_a_budget_and_fits(self):
        files = sorted(p.name for p in ROLES.glob("*.md"))
        self.assertEqual(sorted(BUDGET), files, "a new role needs a budget line here")
        for name in files:
            size = crlf_size((ROLES / name).read_bytes())
            self.assertLessEqual(size, BUDGET[name], f"{name} is {size} bytes with CRLF, budget {BUDGET[name]}")

    def test_size_is_counted_as_on_windows(self):
        self.assertEqual(crlf_size(b"ab\ncd\n"), 8)
        self.assertEqual(crlf_size(b"ab\r\ncd\r\n"), 8)

    def test_no_retired_wording(self):
        for p in sorted(ROLES.glob("*.md")):
            if p.name in OWNED_ELSEWHERE:
                continue
            text = p.read_text(encoding="utf-8")
            for pat, why in RETIRED:
                self.assertIsNone(re.search(pat, text), f"{p.name}: '{pat}' ({why})")

    def test_first_screen_names_the_job(self):
        for p in sorted(ROLES.glob("*.md")):
            if p.name in OWNED_ELSEWHERE:
                continue
            head = "\n".join(p.read_text(encoding="utf-8").splitlines()[:8])
            self.assertTrue(re.search(r"^# \S+: ", head, re.M), f"{p.name}: line 2 must be '# <Role>: <job>'")
            self.assertIn("Model", head, f"{p.name}: the model must be on the first screen")

    def test_eagle_eyes_v4_think_mode(self):
        text = (ROLES / "eagle_eyes.md").read_text(encoding="utf-8")
        self.assertIn("| version: v4 |", text.splitlines()[0])
        self.assertIn("## Think mode", text)
        sect = text.split("## Think mode", 1)[1].split("\n## ", 1)[0]
        for needle in ("MISMATCH or NOT_IN_DATA", "roles/thinker.md", "LITE", "RECOMMEND", "Cost", "ROI", "Risk",
                       "PENDING OPERATOR: needs Opus Thinker", "OPERATOR_DECISIONS.md", "tasks.py new", "STALE mirror",
                       "no trade advice", "7 days"):
            self.assertIn(needle, sect, needle)


if __name__ == "__main__":
    unittest.main()
