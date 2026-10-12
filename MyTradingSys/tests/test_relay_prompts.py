"""B172 b172-trim: every relay/dispatcher prompt carries the output cap line."""
import glob
import os

D = os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "sched", "relay_prompts")


def test_prompts_carry_output_caps():
    files = sorted(glob.glob(os.path.join(D, "*.SKILL.md"))) + [os.path.join(D, "relay_session.md")]
    assert len(files) >= 7
    missing = []
    for f in files:
        t = open(f, encoding="utf-8").read()
        if "tail -20" not in t or "--quiet" not in t:
            missing.append(os.path.basename(f))
    assert not missing, missing
