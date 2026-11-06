"""Boot audit (Windows, stdlib only): what starts at boot/logon, who owns it, and what to do about it.

Usage:
  python scripts/dev/boot_audit.py          table of every boot/logon item with owner and verdict (report only)
  python scripts/dev/boot_audit.py --fix    act on MTS-owned items only: REMOVE -> delete, DELAY -> logon delay + no catch-up start
  python scripts/dev/boot_audit.py --json   the same rows as JSON

Verdicts (SCHEDULING_POLICY.md is the authority for "authorised"):
  KEEP    authorised MTS item, or Windows / operator / third-party owned. --fix never touches these.
  DELAY   ours and needed but not authorised in the policy (AIBridge-Agent: open policy question): starts 3 min after logon,
          and a missed run is not caught up at boot. Removing it would stop the DSA bridge, so the safe default is delay.
  REMOVE  ours and not authorised (any other MTS-* task or Run value): deleted by --fix.
Owner is MTS only for names in MTS_TASK_RE / MTS_RUN_VALUES or a command that runs a repo script; everything else is
never modified. Third-party items that are known heavy are flagged ASK (the operator's call, not ours).
The Windows boot-time events (Diagnostics-Performance 100, 101-110) need an administrator; without one the audit says so.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

DELAY_ISO = "PT3M"          # logon delay for DELAY items (OURS)
MTS_TASK_RE = re.compile(r"^(MTS-.+|mts-.+|AIBridge-Agent)$", re.I)
MTS_CMD_RE = re.compile(r"F:[\\/]+MTS[\\/]|MTS-Worker|BinanceDataFeed|IdeaProjects[\\/]+mts-", re.I)   # a task running MTS files is ours whatever its name (NUC gq*, lab-loop)
AUTHORISED_TASK_RE = re.compile(r"^(MTS-CBP-Ingestion|MTS-WorktreeMaint-.+|MTS-SuccWake-.+)$")   # SCHEDULING_POLICY s4b, 4b3, CBP
DELAY_TASK_RE = re.compile(r"^AIBridge-Agent$")
MTS_RUN_VALUES = {"MTSTempGuard", "MTSLogonWake"}     # SCHEDULING_POLICY s4c, s4d: authorised
HEAVY_RE = re.compile(r"docker|teams|discord|highlight|medal|snipping|openvpn|teamviewer|tailscale|zoom|onedrive|dropbox|"
                      r"spotify|steam|epic|adobe|dsaservice|clicktorun|googleupdate|edgeupdate", re.I)
REPO_CMD_RE = re.compile(r"(BinanceDataFeed|mts[-_ ]|MyTradingSys)[^\"]*\.py", re.I)


def classify(kind, name, command="", state="Ready", enabled=True):
    """Pure rule: (owner, verdict, reason, ask). kind is task | run | startup | service."""
    mts = (bool(MTS_TASK_RE.match(name)) or bool(MTS_CMD_RE.search(command or ""))) if kind == "task" else (name in MTS_RUN_VALUES or bool(REPO_CMD_RE.search(command or "")))
    if not mts:
        ask = bool(HEAVY_RE.search(name + " " + (command or "")))
        return "other", "KEEP", ("third-party, heavy at boot: operator's call" if ask else "not ours"), ask
    if kind == "task":
        if AUTHORISED_TASK_RE.match(name):
            return "MTS", "KEEP", "authorised in SCHEDULING_POLICY.md", False
        if DELAY_TASK_RE.match(name):
            return "MTS", "DELAY", "needed by the DSA bridge, not in the policy list: delay, do not delete", False
        return "MTS", "REMOVE", "MTS task not authorised by SCHEDULING_POLICY.md", False
    if name in MTS_RUN_VALUES:
        return "MTS", "KEEP", "authorised in SCHEDULING_POLICY.md s4c/s4d", False
    return "MTS", "REMOVE", "MTS Run entry not authorised by SCHEDULING_POLICY.md", False


def _ps(script, timeout=60):
    exe = shutil.which("powershell") or shutil.which("pwsh")
    if not exe:
        return ""
    r = subprocess.run([exe, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", script],
                       capture_output=True, text=True, timeout=timeout)
    return r.stdout


def task_rows():
    """Non-Microsoft enabled scheduled tasks with trigger kinds, logon delay and the catch-up flag."""
    ps = ("$ErrorActionPreference='SilentlyContinue';Get-ScheduledTask|?{$_.TaskPath -notmatch '^\\\\Microsoft\\\\' -and $_.State -ne 'Disabled'}|%{"
          "$t=$_;$i=Get-ScheduledTaskInfo -TaskName $t.TaskName -TaskPath $t.TaskPath;$nx=$i.NextRunTime;$l=@($t.Triggers|?{$_.CimClass.CimClassName -eq 'MSFT_TaskLogonTrigger'});"
          "[pscustomobject]@{name=$t.TaskName;path=$t.TaskPath;state=[string]$t.State;"
          "logon=($l.Count -gt 0);delay=[string]($l|select -First 1).Delay;catchup=[bool]$t.Settings.StartWhenAvailable;next=$(if($nx -and $nx.Year -gt 2000){$nx.ToUniversalTime().ToString('o')}else{''});"
          "rep=[bool](@($t.Triggers|?{$_.Repetition.Interval -or $_.CimClass.CimClassName -match 'Daily|Weekly|Monthly|Logon|Boot'}).Count);"
          "trig=(($t.Triggers|%{$_.CimClass.CimClassName -replace 'MSFT_Task|Trigger',''}) -join ',');"
          "cmd=(($t.Actions|select -First 1).Execute+' '+($t.Actions|select -First 1).Arguments)}}|ConvertTo-Json -Compress")
    out = _ps(ps).strip()
    if not out:
        return []
    data = json.loads(out)
    return data if isinstance(data, list) else [data]


RUN_KEYS = (("HKCU", r"Software\Microsoft\Windows\CurrentVersion\Run"), ("HKCU", r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
            ("HKLM", r"Software\Microsoft\Windows\CurrentVersion\Run"), ("HKLM", r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"))


def run_rows():
    try:
        import winreg
    except ImportError:
        return []
    rows = []
    for hive, sub in RUN_KEYS:
        try:
            with winreg.OpenKey((winreg.HKEY_CURRENT_USER if hive == "HKCU" else winreg.HKEY_LOCAL_MACHINE), sub) as k:
                i = 0
                while True:
                    try:
                        n, v, _ = winreg.EnumValue(k, i)
                    except OSError:
                        break
                    rows.append({"hive": hive, "key": sub, "name": n, "cmd": str(v)})
                    i += 1
        except OSError:
            continue
    return rows


def startup_rows():
    dirs = [os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs\Startup"),
            os.path.join(os.environ.get("ProgramData", ""), r"Microsoft\Windows\Start Menu\Programs\StartUp")]
    return [{"name": f, "cmd": os.path.join(d, f)} for d in dirs if os.path.isdir(d) for f in sorted(os.listdir(d)) if f.lower() != "desktop.ini"]


def service_rows():
    ps = ("Get-CimInstance Win32_Service|?{$_.StartMode -eq 'Auto' -and $_.PathName -notmatch 'Windows\\\\|svchost|Defender'}|"
          "%{[pscustomobject]@{name=$_.Name;state=$_.State;cmd=[string]$_.PathName}}|ConvertTo-Json -Compress")
    out = _ps(ps).strip()
    if not out:
        return []
    data = json.loads(out)
    return data if isinstance(data, list) else [data]


def boot_times():
    """(text) the last Diagnostics-Performance event 100 numbers, or why they are unreadable."""
    ps = ("try{$e=Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-Diagnostics-Performance/Operational';Id=100} -MaxEvents 5 -ErrorAction Stop;"
          "$e|%{$d=@{};([xml]$_.ToXml()).Event.EventData.Data|%{$d[$_.Name]=$_.'#text'};"
          "('{0} boot={1}s main={2}s post={3}s' -f $_.TimeCreated.ToString('MM-dd'),[int]($d.BootTime/1000),[int]($d.MainPathBootTime/1000),[int]($d.BootPostBootTime/1000))}"
          "}catch{'UNREADABLE: no boot events visible to this user (log empty or needs an administrator): '+$_.Exception.Message}")
    return _ps(ps).strip() or "UNREADABLE: no PowerShell"


def collect():
    rows = []
    for t in task_rows():
        v = classify("task", t["name"], t.get("cmd", ""), t.get("state", ""))
        rows.append({"kind": "task", "name": t["name"], "detail": "%s%s%s" % (t.get("trig", ""), " logon" if t.get("logon") else "", " delay=" + t["delay"] if t.get("delay") else ""),
                     "cmd": t.get("cmd", ""), "owner": v[0], "verdict": v[1], "reason": v[2], "ask": v[3],
                     "done": (v[1] == "DELAY" and bool(t.get("delay")) and not t.get("catchup")) or v[1] == "KEEP",
                     "raw": t})
    for r in run_rows():
        v = classify("run", r["name"], r["cmd"])
        rows.append({"kind": "run", "name": r["name"], "detail": r["hive"] + (" RunOnce" if "RunOnce" in r["key"] else " Run"), "cmd": r["cmd"],
                     "owner": v[0], "verdict": v[1], "reason": v[2], "ask": v[3], "done": v[1] == "KEEP", "raw": r})
    for s in startup_rows():
        v = classify("startup", s["name"], s["cmd"])
        rows.append({"kind": "startup", "name": s["name"], "detail": "Startup folder", "cmd": s["cmd"], "owner": v[0], "verdict": v[1],
                     "reason": v[2], "ask": v[3], "done": True, "raw": s})
    for s in service_rows():
        v = classify("service", s["name"], s["cmd"])
        if v[0] == "other" and v[3]:    # only the known heavy third-party services are worth a row
            rows.append({"kind": "service", "name": s["name"], "detail": "auto service " + s.get("state", ""), "cmd": s["cmd"], "owner": v[0],
                         "verdict": v[1], "reason": v[2], "ask": v[3], "done": True, "raw": s})
    return rows


def in_flight(raw, now=None):
    """A task that is running now, or a one-shot whose single start is still ahead: someone's job in progress, not a leftover."""
    if raw.get("state") == "Running":
        return True
    nxt = raw.get("next") or ""
    if not nxt or raw.get("rep"):
        return False
    try:
        from datetime import datetime, timezone
        return datetime.fromisoformat(nxt.replace("Z", "+00:00")) > (now or datetime.now(timezone.utc))
    except ValueError:
        return False


def plan_fix(rows, now=None):
    """The actions --fix would take: only owner == MTS rows, REMOVE or not-yet-done DELAY; never a task in flight. Pure, so the test can pin it."""
    acts = []
    for r in rows:
        if r["owner"] != "MTS":
            continue
        if r["verdict"] == "REMOVE" and r["kind"] == "task" and in_flight(r["raw"], now):
            continue
        if r["verdict"] == "REMOVE":
            acts.append(("remove_" + r["kind"], r["name"], r["raw"]))
        elif r["verdict"] == "DELAY" and not r["done"]:
            acts.append(("delay_task", r["name"], r["raw"]))
    return acts


def apply_fix(acts):
    out = []
    for act, name, raw in acts:
        if act == "remove_task":
            res = _ps("try{Unregister-ScheduledTask -TaskName '%s' -Confirm:$false -ErrorAction Stop;'ok'}catch{'FAIL '+$_.Exception.Message}"
                      % name.replace("'", "''")).strip()
            out.append("removed task " + name if res == "ok" else "could not remove task %s (%s)" % (name, res[:80]))
        elif act == "remove_run" and raw.get("hive") == "HKCU":
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, raw["key"], 0, winreg.KEY_SET_VALUE) as k:
                winreg.DeleteValue(k, name)
            out.append("removed Run value " + name)
        elif act == "delay_task":
            _ps("$t=Get-ScheduledTask -TaskName '%s';$t.Triggers|?{$_.CimClass.CimClassName -eq 'MSFT_TaskLogonTrigger'}|%%{$_.Delay='%s'};"
                "$t.Settings.StartWhenAvailable=$false;Set-ScheduledTask -InputObject $t|Out-Null" % (name.replace("'", "''"), DELAY_ISO))
            out.append("delayed task %s (%s after logon, no boot catch-up)" % (name, DELAY_ISO))
        else:
            out.append("skipped " + act + " " + name + " (needs admin or not supported)")
    return out


def render(rows):
    w = max([len(r["name"]) for r in rows] + [4])
    lines = ["%-8s %-*s %-6s %-7s %s" % ("kind", w, "item", "owner", "verdict", "detail / reason")]
    for r in sorted(rows, key=lambda r: (r["owner"] != "MTS", r["kind"], r["name"])):
        lines.append("%-8s %-*s %-6s %-7s %s%s" % (r["kind"], w, r["name"][:60], r["owner"], r["verdict"] + ("*" if r["ask"] else ""),
                                                  r["detail"][:30], "; " + r["reason"]))
    lines.append("* = ASK: third-party and heavy at boot; the operator decides, --fix never touches it")
    return "\n".join(lines)


def free_c_gb():
    try:
        return shutil.disk_usage("C:\\").free / 1e9
    except OSError:
        return -1.0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if sys.platform != "win32":
        print("boot_audit: Windows only")
        return 0
    rows = collect()
    if a.json:
        print(json.dumps([{k: v for k, v in r.items() if k != "raw"} for r in rows], indent=1))
    else:
        print(render(rows))
        print("C: free %.1f GB | boot times: %s" % (free_c_gb(), boot_times().replace("\n", " / ")))
    if a.fix:
        acts = plan_fix(rows)
        for line in apply_fix(acts) or ["nothing to fix (MTS-owned items already compliant)"]:
            print("FIX", line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
