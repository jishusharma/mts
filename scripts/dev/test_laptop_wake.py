import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import laptop_wake as lw


class T(unittest.TestCase):
    def test_allowed_verbs(self):
        for v in ("status", "ps", "job-log"):
            cmd = lw.gate_cmd(v, "x" if v == "job-log" else "")
            self.assertIn(v, cmd)

    def test_refused_verbs(self):
        for v in ("ps-bg", "powershell", "rm -rf /", "", "status; dir"):
            with self.assertRaises(ValueError):
                lw.gate_cmd(v)

    def test_bad_job_name(self):
        with self.assertRaises(ValueError):
            lw.gate_cmd("job-log", "a;b")

    def test_script_one_shot_self_unregister(self):
        s = lw.build_script("m", name="t1")
        self.assertIn("Register-ScheduledTask", s)
        self.assertIn("Unregister-ScheduledTask -TaskName MTS-LaptopWake-t1", s)
        self.assertNotIn("-Trigger", s)   # no standing/repeating trigger


if __name__ == "__main__":
    unittest.main()
