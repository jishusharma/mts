"""sync.push_race_lost: first creation of origin/claims lost to another pusher is a race, not a hard failure."""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sync


def _r(rc, err):
    return subprocess.CompletedProcess([], rc, "", err)


def test_reference_already_exists_is_a_lost_race():
    assert sync.push_race_lost(_r(1, "! [remote rejected] claims (reference already exists)"))


def test_plain_auth_failure_is_not_a_race():
    assert not sync.push_race_lost(_r(128, "fatal: Authentication failed for 'https://github.com/x/y.git/'"))
