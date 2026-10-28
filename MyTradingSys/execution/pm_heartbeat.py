import sys
sys.dont_write_bytecode = True

"""
pm_heartbeat module for position manager heartbeat tracking.

This module provides functions to create, read, and manage heartbeat files
that indicate which position manager processes are alive and managing which plans.
"""

import json
import os
import re
import sys
import tempfile
import datetime
from pathlib import Path
from typing import List, Dict, Any, Callable, Set

DEFAULT_HB_DIR = Path(__file__).resolve().parent / "pm_heartbeats"
DEFAULT_LABEL = "default"
PLAN_ID_RE = re.compile(r"[A-Za-z0-9_.-]{1,80}")
# B148 part 5, operator D10 2026-10-09: a heartbeat not refreshed for this long means the manager is dead,
# even if Windows has handed its pid to another process. A safety limit, not a trader parameter.
DEFAULT_MAX_AGE_S = 600


def hb_path(plan_id: str, hb_dir=None) -> Path:
    """Return the path for a heartbeat file for plan_id in hb_dir.
    
    Args:
        plan_id: The plan identifier
        hb_dir: The directory to place the heartbeat file. Defaults to DEFAULT_HB_DIR
        
    Returns:
        Path to the heartbeat file
        
    Raises:
        ValueError: If plan_id does not match PLAN_ID_RE
    """
    if hb_dir is None:
        hb_dir = DEFAULT_HB_DIR
    
    if not PLAN_ID_RE.fullmatch(plan_id):
        raise ValueError(f"Invalid plan_id: {plan_id}")
    
    return Path(hb_dir) / f"{plan_id}.json"


def write_heartbeat(plan_id: str, account=None, pid=None, hb_dir=None, now=None, started_utc=None) -> Path:
    """Write a heartbeat file for the given plan.
    
    Args:
        plan_id: The plan identifier
        account: The account name (defaults to None)
        pid: The process ID (defaults to current process)
        hb_dir: The directory to place the heartbeat file. Defaults to DEFAULT_HB_DIR
        now: The timestamp (defaults to current UTC time)
        
    Returns:
        Path to the written heartbeat file
    """
    if hb_dir is None:
        hb_dir = DEFAULT_HB_DIR
    
    if pid is None:
        pid = os.getpid()
    
    if now is None:
        now = datetime.datetime.now(datetime.timezone.utc)
    
    path = hb_path(plan_id, hb_dir)
    hb_dir = Path(hb_dir)
    hb_dir.mkdir(parents=True, exist_ok=True)
    
    payload = {
        "plan_id": plan_id,
        "account": account,
        "pid": pid,
        "started_utc": started_utc or now.isoformat(),
        "beat_utc": now.isoformat()
    }
    
    # Write atomically using a temporary file
    with tempfile.NamedTemporaryFile(mode="w", dir=hb_dir, delete=False, suffix=".tmp") as f:
        temp_path = Path(f.name)
        json.dump(payload, f, separators=(',', ':'), ensure_ascii=True)
        f.flush()
        os.fsync(f.fileno())
    
    # Replace the temporary file with the final path
    os.replace(temp_path, path)
    
    return path


def beat(plan_id: str, hb_dir=None, now=None) -> bool:
    """Refresh beat_utc of an existing heartbeat (account, pid and started_utc are kept).

    Returns False and writes nothing if the file is gone or unreadable: a refresh never resurrects a heartbeat
    that remove_heartbeat() has deleted.
    """
    try:
        data = json.loads(hb_path(plan_id, hb_dir).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    if not isinstance(data, dict):
        return False
    write_heartbeat(plan_id, account=data.get("account"), pid=data.get("pid"), hb_dir=hb_dir, now=now,
                    started_utc=data.get("started_utc"))
    return True


def remove_heartbeat(plan_id: str, hb_dir=None) -> bool:
    """Remove a heartbeat file.
    
    Args:
        plan_id: The plan identifier
        hb_dir: The directory containing the heartbeat file. Defaults to DEFAULT_HB_DIR
        
    Returns:
        True if the file existed and was removed, False otherwise
    """
    if hb_dir is None:
        hb_dir = DEFAULT_HB_DIR
    
    path = hb_path(plan_id, hb_dir)
    
    try:
        path.unlink()
        return True
    except FileNotFoundError:
        return False


def read_heartbeats(hb_dir=None) -> List[Dict[str, Any]]:
    """Read all heartbeat files in the directory.
    
    Args:
        hb_dir: The directory to read heartbeat files from. Defaults to DEFAULT_HB_DIR
        
    Returns:
        A list of decoded heartbeat dictionaries, sorted by plan_id
    """
    if hb_dir is None:
        hb_dir = DEFAULT_HB_DIR
    
    path = Path(hb_dir)
    
    if not path.exists():
        return []
    
    result = []
    
    for file_path in path.glob("*.json"):
        try:
            content = file_path.read_text(encoding="utf-8")
            data = json.loads(content)
            
            if isinstance(data, dict):
                result.append(data)
        except (json.JSONDecodeError, OSError):
            # Silently skip files that cannot be read or are not valid JSON
            continue
    
    return sorted(result, key=lambda x: x["plan_id"])


def pid_alive(pid) -> bool:
    """Fail-safe liveness check: returns False ONLY when the process is
    positively known to be gone. Anything unknown (bad pid value, access
    denied, API error) is treated as alive so a watchdog never HALTs on a
    live position manager.
    """
    if isinstance(pid, bool) or not isinstance(pid, int) or pid <= 0:
        return True  # corrupt/unknown pid: cannot prove it is dead
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes
            k32 = ctypes.windll.kernel32
            handle = k32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
            if not handle:
                # 87 = ERROR_INVALID_PARAMETER: no such pid. Anything else (e.g. access denied) = unknown.
                return k32.GetLastError() != 87
            try:
                exit_code = wintypes.DWORD()
                if k32.GetExitCodeProcess(handle, ctypes.byref(exit_code)) == 0:
                    return True
                return exit_code.value == 259  # STILL_ACTIVE
            finally:
                k32.CloseHandle(handle)
        except Exception:  # noqa: BLE001
            return True
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except Exception:  # noqa: BLE001 - PermissionError and anything unknown
        return True


def _age_seconds(heartbeat, now):
    """Seconds since beat_utc, or None when it cannot be known (legacy file without the field, unparseable,
    naive time): unknown age fails open, so only a positively stale beat can condemn a manager."""
    raw = heartbeat.get("beat_utc")
    if not isinstance(raw, str):
        return None
    try:
        t = datetime.datetime.fromisoformat(raw)
    except ValueError:
        return None
    if t.tzinfo is None:
        return None
    return (now - t).total_seconds()


def live_accounts(hb_dir=None, alive=None, max_age_s=DEFAULT_MAX_AGE_S, now=None) -> Set[str]:
    """Get the set of accounts with live heartbeat processes.
    
    Args:
        hb_dir: The directory to read heartbeat files from. Defaults to DEFAULT_HB_DIR
        alive: A function that checks if a PID is alive. Defaults to pid_alive
        max_age_s: a heartbeat whose beat_utc is older than this is dead whatever the pid says (None = off)
        now: current time for the age rule (defaults to UTC now)
        
    Returns:
        A set of account names with active heartbeat processes
    """
    if hb_dir is None:
        hb_dir = DEFAULT_HB_DIR
    
    if alive is None:
        alive = pid_alive
    
    result = set()
    if now is None:
        now = datetime.datetime.now(datetime.timezone.utc)
    
    for heartbeat in read_heartbeats(hb_dir):
        pid = heartbeat.get("pid")
        age = _age_seconds(heartbeat, now) if max_age_s is not None else None
        if age is not None and age > max_age_s:
            continue
        
        if alive(pid):
            account = heartbeat.get("account")
            
            if not account:
                account = DEFAULT_LABEL
            
            result.add(account)
    
    return result
