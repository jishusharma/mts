"""Install/status/remove the operator-authorized CBP-only twice-daily Windows task.

Install from a durable MTS checkout on the host holding CBP data:
    python scripts/dev/cbp_schedule.py install --home F:/CryptoScrapper
Task times (OURS): 09:00 UTC (Europe underway), 13:00 UTC (before US cash open).
No trading process is started. The signed-in user's existing Claude login is used.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from xml.sax.saxutils import escape

TASK = "MTS-CBP-Ingestion"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "MyTradingSys"))
import cbp  # noqa: E402


def task_xml(python, script, home):
    args = subprocess.list2cmdline([str(script), "run", "--home", str(home)])
    triggers = "".join(
        '<CalendarTrigger><StartBoundary>2026-10-26T%s:00:00Z</StartBoundary>'
        '<Enabled>true</Enabled><ScheduleByDay><DaysInterval>1</DaysInterval>'
        '</ScheduleByDay></CalendarTrigger>' % hour for hour in ("09", "13"))
    return ('<?xml version="1.0" encoding="UTF-16"?>'
            '<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">'
            '<RegistrationInfo><Description>CBP fetch, extract, verify, store twice daily</Description></RegistrationInfo>'
            '<Triggers>' + triggers + '</Triggers>'
            '<Principals><Principal id="Author"><LogonType>InteractiveToken</LogonType>'
            '<RunLevel>LeastPrivilege</RunLevel></Principal></Principals>'
            '<Settings><MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>'
            '<DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>'
            '<StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>'
            '<StartWhenAvailable>true</StartWhenAvailable><WakeToRun>true</WakeToRun>'
            '<ExecutionTimeLimit>PT3H</ExecutionTimeLimit>'
            '<RestartOnFailure><Interval>PT15M</Interval><Count>3</Count></RestartOnFailure>'
            '</Settings><Actions Context="Author"><Exec><Command>' + escape(str(python)) +
            '</Command><Arguments>' + escape(args) + '</Arguments><WorkingDirectory>' +
            escape(str(ROOT)) + '</WorkingDirectory></Exec></Actions></Task>')


def preflight(home):
    config = home / "cbp_v2" / "analysts.json"
    if not config.is_file():
        raise ValueError("missing analyst config: " + str(config))
    data = json.loads(config.read_text(encoding="utf-8"))
    if not any(a.get("enabled") and a.get("profile") == "actionable" for a in data["analysts"]):
        raise ValueError("no enabled actionable analysts")
    if not shutil.which("claude"):
        raise ValueError("claude executable unavailable to this user")
    subprocess.run([sys.executable, "-c", "import yt_dlp"], check=True, capture_output=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", choices=("install", "run", "status", "remove", "check"))
    ap.add_argument("--home", type=Path, default=None)
    a = ap.parse_args(argv)
    home = (a.home or cbp.default_cbp_home()).resolve()
    if a.command in ("status", "remove"):
        cmd = ["schtasks", "/Query", "/TN", TASK, "/V", "/FO", "LIST"] if a.command == "status" else [
            "schtasks", "/Delete", "/TN", TASK, "/F"]
        return subprocess.run(cmd).returncode
    try:
        preflight(home)
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as e:
        print("cbp preflight failed: " + str(e), file=sys.stderr)
        return 1
    if a.command == "check":
        print("cbp prerequisites OK; data host=" + str(home))
        return 0
    state = home / "cbp_store"
    state.mkdir(parents=True, exist_ok=True)
    if a.command == "install":
        xml = state / "schedule.xml"
        xml.write_text(task_xml(sys.executable, Path(__file__).resolve(), home), encoding="utf-16")
        return subprocess.run(["schtasks", "/Create", "/TN", TASK, "/XML", str(xml), "/F"]).returncode
    env = dict(os.environ, CBP_HOME=str(home), CBP_STORE=str(state / "rows.json"),
               CBP_STAMP=str(state / "stamp.json"), CBP_TRANSCRIPTS=str(home / "raw_transcripts_canonical"))
    # Append stderr as well as stdout; the task's LastTaskResult retains the failure code.
    with (state / "ingestion.log").open("a", encoding="utf-8") as log:
        return subprocess.run([sys.executable, str(ROOT / "scripts/dev/cbp_run.py"), "--due"],
                              env=env, stdout=log, stderr=subprocess.STDOUT, cwd=ROOT).returncode


if __name__ == "__main__":
    sys.exit(main())
