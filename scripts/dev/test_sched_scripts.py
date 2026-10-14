"""Static (and, on Windows, dry-run) tests for the Windows scheduled-task scripts (2026-10-14 catch-up fix).

Diagnosis these pin: JIS-NB is off ~02:00-10:30 IST, so the 06:30-09:10 daily jobs never run on time; the StartWhenAvailable
catch-up fires ~3 min after boot, before any user session exists, and Task Scheduler drops it (event 332) without retry.
The scripts are only ever WRITTEN here, never registered, so the tests read them as text; the ones that execute a script
run only its dry-run / refusal path (no Register-/Set-ScheduledTask). Run: python scripts/dev/test_sched_scripts.py
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PWSH = shutil.which("pwsh") or shutil.which("powershell")
WINDOWS = sys.platform == "win32"
# Runs that touch the real scheduler or the host's python path only mean something on the MTS hosts, not a CI runner.
MTS_HOST = WINDOWS and bool(PWSH) and not os.environ.get("GITHUB_ACTIONS")

MODE = "scripts/core/mode.ps1"
CATCHUP = "scripts/sched/add_logon_catchup.ps1"
CICD = "scripts/sched/register_cicd_tasks.ps1"
MIRROR = "scripts/sched/register_live_mirror.ps1"
BACKUP = "scripts/dev/install_backup_task.ps1"
ALL_PS1 = (MODE, CATCHUP, CICD, MIRROR, BACKUP)

TEN_TASKS = {"MTS-DailyHygiene", "MTS-Make-Status", "MTS-Alert-Rate-Check", "MTS-Audit-Rotation", "MTS-Audit-Digest",
             "MTS-Declutter-Backups", "MTS-Orphan-Watchdog", "MTS-Retention", "MTS testnet status", "MTS-CDriveCare"}


def read(rel):
    p = ROOT / rel
    assert p.exists(), "missing " + rel
    return p.read_text(encoding="utf-8")


def code(text):
    """The script without <# #> blocks and full-line # comments, so a word in a comment never satisfies an assertion."""
    text = re.sub(r"<#.*?#>", "", text, flags=re.S)
    return "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("#"))


def block_after(text, marker):
    """Body of the {...} block that follows the first `marker` (brace matched), '' if there is none."""
    i = text.find(marker)
    if i < 0:
        return ""
    j = text.find("{", i)
    if j < 0:
        return ""
    depth = 0
    for k in range(j, len(text)):
        if text[k] == "{":
            depth += 1
        elif text[k] == "}":
            depth -= 1
            if depth == 0:
                return text[j + 1:k]
    return ""


def split_blocks(text, marker):
    """(inside, outside): the bodies of EVERY brace-matched block that follows `marker`, and the text with those blocks cut out."""
    inside, outside, pos = [], [], 0
    while True:
        i = text.find(marker, pos)
        j = text.find("{", i) if i >= 0 else -1
        if j < 0:
            outside.append(text[pos:])
            return "\n".join(inside), "".join(outside)
        depth, k = 0, j
        while k < len(text):
            depth += {"{": 1, "}": -1}.get(text[k], 0)
            if depth == 0:
                break
            k += 1
        inside.append(text[j + 1:k])
        outside.append(text[pos:i])
        pos = k + 1


def run_ps(rel, *args):
    r = subprocess.run([PWSH, "-NoProfile", "-NonInteractive", "-File", str(ROOT / rel), *args],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


class ModePs1(unittest.TestCase):
    """mode.ps1 re-registers MTS-Supervisor: the hand-added logon trigger is the stack's only boot recovery."""

    def setUp(self):
        self.sup = block_after(read(MODE), "if (-not $supRunning)")
        self.assertTrue(self.sup, "no `if (-not $supRunning)` block in mode.ps1")

    def test_supervisor_gets_both_triggers(self):
        self.assertIn("New-ScheduledTaskTrigger -AtLogOn", self.sup)
        self.assertRegex(self.sup, r"Register-ScheduledTask -TaskName 'MTS-Supervisor'[^\n]*-Trigger @\(\s*\$\w+\s*,\s*\$\w+\s*\)")

    def test_logon_trigger_is_for_the_current_user_with_90s_delay(self):
        self.assertIn('-User "$env:USERDOMAIN\\$env:USERNAME"', self.sup)
        self.assertIn("'PT1M30S'", self.sup)

    def test_settings_survive_battery_and_the_72h_default_limit(self):
        for flag in ("-AllowStartIfOnBatteries", "-DontStopIfGoingOnBatteries", "-MultipleInstances IgnoreNew",
                     "-ExecutionTimeLimit ([TimeSpan]::Zero)"):
            self.assertIn(flag, self.sup)
        self.assertRegex(self.sup, r"Register-ScheduledTask -TaskName 'MTS-Supervisor'[^\n]*-Settings \$\w+")

    def test_wrapper_registration_is_untouched(self):
        # the wrapper is relaunched by the supervisor / mode.ps1 itself: no logon trigger, it must not start before the supervisor
        self.assertEqual(read(MODE).count("-AtLogOn"), 1)


class AddLogonCatchup(unittest.TestCase):
    def test_script_exists_and_is_dry_run_unless_apply(self):
        t = read(CATCHUP)
        self.assertRegex(code(t), r"param\(\s*\[switch\]\$Apply\s*\)")
        applied, outside = split_blocks(code(t), "if ($Apply)")
        self.assertIn("Set-ScheduledTask", applied)
        self.assertNotIn("Set-ScheduledTask", outside, "a write outside the -Apply branch")

    def test_never_registers_or_removes_tasks(self):
        c = code(read(CATCHUP))
        for bad in ("Register-ScheduledTask", "Unregister-ScheduledTask", "schtasks", "Stop-ScheduledTask", "Disable-ScheduledTask"):
            self.assertNotIn(bad, c)

    def test_lists_exactly_the_ten_tasks(self):
        names = set(re.findall(r"'(MTS[- ][^']+)'", code(read(CATCHUP))))
        self.assertEqual(names, TEN_TASKS)

    def test_only_reads_tasks_by_name(self):
        c = code(read(CATCHUP))
        calls = re.findall(r"Get-ScheduledTask\b[^\n]*", c)
        self.assertTrue(calls)
        for call in calls:
            self.assertIn("-TaskName", call, "enumerating tasks would let the script touch other tasks: " + call)

    def test_logon_trigger_shape_and_idempotence(self):
        c = code(read(CATCHUP))
        self.assertIn("MSFT_TaskLogonTrigger", c)                 # skip a task that already has one
        self.assertIn("New-ScheduledTaskTrigger -AtLogOn", c)
        self.assertIn("$env:USERDOMAIN\\$env:USERNAME", c)
        self.assertIn("'PT10M'", c)
        self.assertIn("StartWhenAvailable = $true", c)
        self.assertRegex(c, r"missing|not found")                 # a missing task is skipped with a note

    def test_set_keeps_actions_and_principal(self):
        apply_block, _ = split_blocks(code(read(CATCHUP)), "if ($Apply)")
        self.assertRegex(apply_block, r"Set-ScheduledTask\s+-TaskName")
        for param in ("-Action", "-Principal", "-InputObject"):
            self.assertNotIn(param, apply_block)

    @unittest.skipUnless(MTS_HOST, "dry run reads this host's Windows scheduler")
    def test_dry_run_changes_nothing_and_names_every_task(self):
        rc, out = run_ps(CATCHUP)
        self.assertEqual(rc, 0, out)
        self.assertIn("DRY RUN", out)
        self.assertNotIn("APPLIED", out)
        for name in TEN_TASKS:
            self.assertIn(name, out)


class RegisterLiveMirror(unittest.TestCase):
    def test_params_and_dry_run_default(self):
        c = code(read(MIRROR))
        self.assertRegex(c, r"\[Parameter\(Mandatory\)\]\s*\[string\]\$Repo")
        self.assertIn("[switch]$Apply", c)
        applied, outside = split_blocks(c, "if ($Apply)")
        self.assertIn("Register-ScheduledTask", applied)
        self.assertNotIn("Register-ScheduledTask", outside, "a registration outside the -Apply branch")

    def test_refuses_a_repo_without_mts_live_before_building_anything(self):
        c = code(read(MIRROR))
        refuse = c.index(".mts_live")
        self.assertIn("throw", c[refuse:refuse + 300])
        self.assertLess(refuse, c.index("New-ScheduledTaskAction"))
        self.assertLess(refuse, c.index("Register-ScheduledTask"))

    def test_task_shape(self):
        c = code(read(MIRROR))
        for needle in ("'MTS-LiveMirror'", "scripts\\dev\\live_mirror.py publish", "pythonw.exe", "-WorkingDirectory $Repo",
                       "-RepetitionInterval (New-TimeSpan -Minutes 5)", "-ExecutionTimeLimit (New-TimeSpan -Minutes 5)",
                       "-StartWhenAvailable", "-MultipleInstances IgnoreNew", "-Hidden",
                       "-LogonType Interactive", "-RunLevel Limited"):
            self.assertIn(needle, c)

    def test_publish_is_a_real_live_mirror_command(self):
        src = read("scripts/dev/live_mirror.py")
        self.assertIn('choices=["publish"', src)

    def test_minute_slots_avoid_deploy_and_backup(self):
        m = re.search(r"AddMinutes\((\d+)\)", code(read(MIRROR)))
        self.assertTrue(m, "no start-minute offset")
        slots = {(int(m.group(1)) + 5 * k) % 60 for k in range(12)}
        deploy = {0, 15, 30, 45}                                  # MTS-AutoDeploy
        backup = {7, 22, 37, 52}                                  # MTS-Backup (BACKUP_OFFSET_MIN=7)
        self.assertEqual(len(slots), 12)
        self.assertEqual(slots & deploy, set())
        self.assertEqual(slots & backup, set())

    @unittest.skipUnless(MTS_HOST, "runs the script in PowerShell with this host's python")
    def test_refusal_and_dry_run_for_real(self):
        with tempfile.TemporaryDirectory() as td:
            rc, out = run_ps(MIRROR, "-Repo", td)
            self.assertNotEqual(rc, 0, out)
            self.assertIn("REFUSED", out)
            (Path(td) / ".mts_live").write_text("", encoding="utf-8")
            (Path(td) / "scripts" / "dev").mkdir(parents=True)
            (Path(td) / "scripts" / "dev" / "live_mirror.py").write_text("", encoding="utf-8")
            rc, out = run_ps(MIRROR, "-Repo", td)
            self.assertEqual(rc, 0, out)
            self.assertIn("DRY RUN", out)
            self.assertIn("MTS-LiveMirror", out)


class RegisterCicd(unittest.TestCase):
    def test_repo_param_keeps_the_old_default_and_the_old_switches(self):
        c = code(read(CICD))
        self.assertRegex(c, r"\[string\]\$Repo\b")
        self.assertIn("$PSScriptRoot", c)
        self.assertIn("[switch]$SkipDeploy", c)
        self.assertIn("[switch]$Trigger", c)

    def test_daily_hygiene_also_runs_after_logon(self):
        c = code(read(CICD))
        self.assertIn("New-ScheduledTaskTrigger -AtLogOn", c)
        self.assertIn("'PT10M'", c)
        self.assertRegex(c, r"Register-MtsJob 'MTS-DailyHygiene' 'scripts\\dev\\daily_hygiene\.py' @\(")
        self.assertIn("New-ScheduledTaskTrigger -Daily -At '06:30'", c)

    def test_deploy_job_stays_without_a_logon_trigger(self):
        # AutoDeploy is every 15 min already; the logon trigger is only for the once-a-day jobs
        c = code(read(CICD))
        self.assertRegex(c, r"Register-MtsJob 'MTS-AutoDeploy' 'scripts\\dev\\auto_deploy\.py' \$every15")


class InstallBackup(unittest.TestCase):
    def test_pushes_to_the_local_backup_remote_never_origin(self):
        c = code(read(BACKUP))
        self.assertIn("--remote backup", c)
        self.assertNotIn("--remote origin", c)
        self.assertNotIn("--allow-origin", c)

    def test_refuses_when_the_repo_has_no_backup_remote(self):
        c = code(read(BACKUP))
        self.assertIn("-notcontains 'backup'", c)
        self.assertIn("throw", c)
        self.assertLess(c.index("throw"), c.index("Register-ScheduledTask"))
        # Static on purpose: this installer has no dry run, so executing it from a test would register the real MTS-Backup
        # task the moment the guard above regressed (it did exactly that against the old script on 2026-10-14).


class Hygiene(unittest.TestCase):
    def test_lf_only(self):
        # Check the committed blob (index), not the checkout: a Windows runner's autocrlf turns the working copy into CRLF.
        for rel in ALL_PS1:
            r = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--eol", "--", rel], capture_output=True, text=True)
            self.assertTrue(r.stdout.startswith("i/lf"), f"{rel}: {r.stdout.strip() or r.stderr.strip()}")

    @unittest.skipUnless(PWSH, "no PowerShell to parse with")
    def test_powershell_parses(self):
        script = "$e=$null; $null=[System.Management.Automation.Language.Parser]::ParseFile($env:PS_FILE,[ref]$null,[ref]$e); $e | ForEach-Object { $_.Message }"
        for rel in ALL_PS1:
            r = subprocess.run([PWSH, "-NoProfile", "-NonInteractive", "-Command", script], capture_output=True, text=True,
                               encoding="utf-8", errors="replace", env=dict(os.environ, PS_FILE=str(ROOT / rel)), timeout=120)
            self.assertEqual((r.stdout + r.stderr).strip(), "", rel)


if __name__ == "__main__":
    unittest.main()
