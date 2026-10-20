"""B172 b172-trim: every relay/dispatcher prompt carries the output cap line. 2026-10-15: the dispatcher prompt is a ~2 KB stub that makes
ONE `relay.py tick` call, the retired launch path (mts-relay-a/b, mts-dispatcher-night, `relay.py gate`) is in no prompt, RELAY.md stays small."""
import glob
import os

HERE = os.path.dirname(__file__)
D = os.path.join(HERE, "..", "..", "scripts", "sched", "relay_prompts")
RELAY_MD = os.path.join(HERE, "..", "system", "RELAY.md")
STUB = os.path.join(D, "mts-dispatcher.SKILL.md")
SESSION = os.path.join(D, "relay_session.md")
HISTORY = os.path.join(HERE, "..", "archive", "relay_2026-10-15", "RELAY_HISTORY.md")


def read(p):
    return open(p, encoding="utf-8").read()


def prompt_files():
    return sorted(glob.glob(os.path.join(D, "*.SKILL.md"))) + [os.path.join(D, "relay_session.md")]


def test_prompts_carry_output_caps():
    files = prompt_files()
    assert len(files) >= 4   # mts-control-room, mts-dispatcher, mts-lane-watch + relay_session.md
    missing = []
    for f in files:
        t = read(f)
        if "tail -20" not in t or "--quiet" not in t:
            missing.append(os.path.basename(f))
    assert not missing, missing


def test_dispatcher_stub_is_one_tick_call_and_small():
    t = read(STUB)
    assert len(t.encode("utf-8")) <= 2048, "the dispatcher prompt is re-read on every call of every tick: keep it a stub"
    assert 'relay.py" tick' in t and "handoff_lint" in t   # relay.py imports its sibling handoff_lint, so both are copied
    assert "MODEL GUARD" in t and '"opus"' in t   # operator 2026-10-14
    for rule in ("image name", "HALT files", "other scheduled tasks"):   # the safety lines
        assert rule in t, rule
    for gone in ("date +%M", "ArtifactData", "mts-relay-a", "mts-relay-b", "mts-dispatcher-night", "model: sonnet", "run_scheduled_task"):
        assert gone not in t, gone


def test_no_prompt_names_the_retired_launch_path():
    for f in prompt_files() + [os.path.join(D, "TWO_HOST.md"), os.path.join(D, "INSTALL.md"), RELAY_MD]:
        t = read(f)
        for gone in ("mts-relay-a", "mts-relay-b", "mts-dispatcher-night", "relay.py gate", "--started-id"):
            assert gone not in t, (os.path.basename(f), gone)


def test_cadence_is_stated_the_same_everywhere():
    # 2026-10-14 operator: every 10 min, no hourly wait. RELAY.md said 30 min, TWO_HOST.md 'hourly 07-23', the repo prompt 'hourly 07-23'.
    for f in (STUB, os.path.join(D, "TWO_HOST.md"), os.path.join(D, "INSTALL.md"), RELAY_MD):
        t = read(f)
        assert "0 7-23" not in t and "hourly 07-23" not in t, os.path.basename(f)
        if not f.endswith("INSTALL.md"):   # INSTALL.md's lane-watch paragraph names the Codex lab tick, which really is every 30 min
            assert "every 30 min" not in t, os.path.basename(f)
    assert "every 10 min" in read(STUB)
    for f in (os.path.join(D, "TWO_HOST.md"), os.path.join(D, "INSTALL.md"), RELAY_MD):
        assert "*/10 * * * *" in read(f), os.path.basename(f)


def test_relay_md_stays_current_truth_and_small():
    t = read(RELAY_MD)
    assert len(t.encode("utf-8")) <= 6144   # was 13222 B of history and contradictions; history is in archive/relay_2026-10-15/
    # cited by name at runtime: relay.py (handoff refusal), handoff_lint.py, turn_meter.py
    assert "## Task list standard" in t and "## Turn meter" in t


def test_session_prompt_keeps_the_look_return_path():
    # operator 2026-10-14 (GPT/DSA lanes): `kick` still wakes a session for `look=N` and `begin` only takes a card, so without this
    # step a finished lane result is never read, its Qn stays open and the same KICK repeats every hour
    t = read(SESSION)
    for need in ("look=", "desk.py list --all", "tasks.py brief", "ONE claim", "DONE", "BEGIN FAILED: no ready", "worktree:"):
        assert need in t, need
    assert t.index("look=") < t.index("2. Otherwise run the card"), "the look step belongs before the card step"


def test_relay_md_keeps_the_curating_and_lane_directives():
    # operator 2026-10-14 "GPT and DSA for as much as possible": the session that writes the handoff reads this, nowhere else
    t = read(RELAY_MD)
    for need in ("Curating when the list runs low", "scoping task", "GPT and DSA for as much as possible", "tag every task a lane can do alone",
                 "look=", "codex_look"):
        assert need in t, need
    h = read(HISTORY)
    for need in ("Curating when the list runs low: read STATUS.md", "A candidate you cannot scope in one session becomes a scoping task",
                 "Writing the task list: when curating, tag every task a lane can do alone", "`codex_look=N` (JIS-NUC only)"):
        assert need in h, need


def test_prompts_warn_against_reading_claudemd():
    # B183 trim 2: workers must be clearly instructed that CLAUDE.md is already in context
    for f in prompt_files():
        t = read(f)
        assert ("CLAUDE.md is already in context" in t or "CLAUDE.md is already loaded" in t), (
            f"{os.path.basename(f)} should instruct workers that CLAUDE.md is already in context"
        )
        assert ("do not cat or Read CLAUDE.md" in t or "do not read it" in t), (
            f"{os.path.basename(f)} should instruct workers not to cat or Read CLAUDE.md"
        )

