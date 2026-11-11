"""Tests for dsa_seed.py and the DSA prompt's Parallel sessions section (operator 2026-11-07: several DSA chats at once)."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dsa  # noqa: E402
import dsa_seed  # noqa: E402


class ParallelSeed(unittest.TestCase):
    def test_seed_names_chat_slug_other_chats_cards_and_utf8(self):
        t = dsa_seed.build_seed("JIS-NB", slug="jis-nb-1107-1800", claimed=["card-a", "card-b"])
        self.assertIn("$id = 'jis-nb-1107-1800'", t)
        self.assertNotIn("(hostname).ToLower()", t)
        self.assertIn("Held by other DSA chats now: card-a, card-b", t)
        self.assertIn("PYTHONUTF8", t)
        self.assertIn("PYTHONIOENCODING", t)
        self.assertEqual(t.count("# AIRUN cwd="), 1)
        self.assertLess(len(t.encode("ascii")), dsa.SEED_MAX_BYTES)
        self.assertIn("Held by other DSA chats now: none", dsa_seed.build_seed("JIS-NB", slug="x", claimed=[]))
        many = dsa_seed.build_seed("JIS-NB", slug="x", claimed=["c%02d-" % i + "z" * 30 for i in range(40)])
        self.assertLess(len(many.encode("ascii")), dsa.SEED_MAX_BYTES)   # a long claim list is cut, never over the cap
        self.assertIn("more)", many)
        for ln in many.splitlines():
            self.assertLess(len(ln), 200, ln)
            self.assertFalse(ln.startswith("#") and not ln.startswith("# AIRUN"), ln)

    def test_env_line_comes_before_set_location(self):
        lines = dsa_seed.build_seed("JIS-NB", slug="x", claimed=[]).splitlines()
        env = next(i for i, l in enumerate(lines) if l.startswith("$env:PYTHONUTF8"))
        loc = next(i for i, l in enumerate(lines) if l.startswith("Set-Location"))
        self.assertLess(env, loc)

    def test_active_dsa_cards_parse_from_tasks_list(self):
        out = ("alpha-card              active   p2 DSA      S  one\n"
               "beta-card               active   p1 DSA-NUC  S  two\n"
               "beta-card               active   p1 DSA-NUC  S  dup\n\n")
        self.assertEqual(dsa_seed.parse_card_ids(out), ["alpha-card", "beta-card"])
        self.assertEqual(dsa_seed.parse_card_ids(""), [])

    def test_prompt_has_the_parallel_sessions_section(self):
        s = (HERE.parent.parent / "DSA_SESSION_PROMPT.md").read_text(encoding="utf-8")
        sec = s[s.index("## 0b. PARALLEL SESSIONS"):s.index("## 1. ROLE")]
        for needle in ("tasks.py take", "A refused take", "One card at a time", "mts-dsa-<chat>", "A second ship within 10 minutes",
                       "wait 3 minutes", "tasks.py tried", "sync.py release", "PYTHONUTF8", "PYTHONIOENCODING", "dsa_seed.py"):
            self.assertIn(needle, sec, needle)


if __name__ == "__main__":
    unittest.main(verbosity=1)
