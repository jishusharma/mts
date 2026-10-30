"""Mutation proof for test_auto_trader_failclosed.py: break one line in a temp copy of auto_trader.py and require the
named test to FAIL there (and to pass on the unmutated copy). Run: python MyTradingSys/execution/mutation_check_auto_trader_failclosed.py"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = (HERE / "auto_trader.py").read_text(encoding="utf-8")
T = "test_auto_trader_failclosed"

# (test, exact text in auto_trader.py, replacement)
MUTANTS = [
    ("ExchangeFlatTest.test_auth_error_is_unreadable_not_flat", "    except Exception:  # noqa: BLE001\n        return None\n    finally:",
     "    except Exception:  # noqa: BLE001\n        return True\n    finally:"),
    ("ExchangeFlatTest.test_position_error_or_garbage_size_is_unreadable_not_flat", "    except Exception:  # noqa: BLE001\n        return None\n    finally:",
     "    except Exception:  # noqa: BLE001\n        return False\n    finally:"),
    ("ExchangeFlatTest.test_size_decides_flat_and_short_position_is_open", "int(do.get_position(token, instrument).get(\"size\") or 0) == 0",
     "int(do.get_position(token, instrument).get(\"size\") or 0) <= 0"),
    ("ExchangeFlatTest.test_account_env_restored_after_error_and_success", "        if prev is None:\n            os.environ.pop(\"MTS_ACCOUNT\", None)\n        else:\n            os.environ[\"MTS_ACCOUNT\"] = prev",
     "        pass"),
    ("SettleSlotFailureTest.test_respawn_exception_keeps_dead_proc_and_retries_next_cycle", "except Exception as e:  # noqa: BLE001 - the dead proc",
     "except KeyError as e:  # noqa: BLE001 - the dead proc"),
    ("SettleSlotFailureTest.test_unreadable_position_counts_and_logs_throttled", "            return False\n        if flat is False:",
     "            pass\n        if flat is False:"),
    ("SettleSlotFailureTest.test_ledger_failure_does_not_stop_close", "    except Exception as e:  # noqa: BLE001\n        log({\"event\": \"ledger_error\"",
     "    except KeyError as e:  # noqa: BLE001\n        log({\"event\": \"ledger_error\""),
    ("SettleSlotFailureTest.test_running_manager_keeps_slot_and_does_not_touch_exchange", "    if rc is None:\n        return False\n    if rc != 0:",
     "    if rc is None:\n        rc = 0\n    if rc != 0:"),
    ("PlaceRefusalTest.test_plan_refused_nonzero_or_no_saved_id_never_reaches_executor", "if rc != 0 or not m:", "if not m:"),
    ("PlaceRefusalTest.test_executor_api_error_is_entry_failed_and_no_manager", "    if rc != 0:\n        return {\"outcome\": \"entry_failed\"",
     "    if False:\n        return {\"outcome\": \"entry_failed\""),
    ("PlaceRefusalTest.test_no_fill_spawns_no_manager", 'if "no_fill" in out:', 'if "no_fill_x" in out:'),
    ("PlaceRefusalTest.test_dry_run_never_sends_go", "    if dry_run:\n        rc, out", "    if False:\n        rc, out"),
    ("RecoveryTest.test_reentered_plan_after_close_is_open_again_and_garbage_lines_skipped", "            closed.discard(pid)\n", "            pass\n"),
    ("RecoveryTest.test_two_live_managers_one_account_adopts_newest_only_and_alerts", "        if taken:\n            if pids:", "        if False:\n            if pids:"),
    ("RecoveryTest.test_older_dead_plan_same_account_is_superseded_with_ledger_row", "                record_ledger(pid, e.get(\"source\"), acct, ADOPTED_RC)\n",
     "                pass\n"),
    ("RecoveryTest.test_dead_manager_slot_with_open_position_is_respawned_not_freed", "        if flat is False:\n            n = slot.get(\"respawns\", 0)",
     "        if flat is not None:\n            n = slot.get(\"respawns\", 0)\n            flat = True\n            return True\n        if flat is False:\n            n = 0"),
    ("RecoveryTest.test_dead_manager_slot_with_unreadable_exchange_stays_busy", "        if flat is None:\n            slot[", "        if flat is False:\n            slot["),
    ("RecoveryTest.test_manager_pids_exact_plan_token_and_python_only", r"(\s|$)'", "'"),
    ("RecoveryTest.test_process_enumeration_failure_returns_empty_list", "    except Exception:  # noqa: BLE001\n        return []\n\n\ndef manager_pids",
     "    except OSError:  # noqa: BLE001\n        return []\n\n\ndef manager_pids"),
]


def run(test, src):
    d = Path(tempfile.mkdtemp(prefix="mut_")) / "a" / "execution"
    d.mkdir(parents=True)
    (d / "auto_trader.py").write_text(src, encoding="utf-8", newline="\n")
    shutil.copy(HERE / f"{T}.py", d / f"{T}.py")
    env = {**os.environ, "MTS_REPO_ROOT": str(HERE.parents[1])}
    r = subprocess.run([sys.executable, str(d / f"{T}.py"), test], capture_output=True, text=True, env=env, cwd=str(d))
    shutil.rmtree(d.parents[1], ignore_errors=True)
    return r.returncode


def main():
    bad = 0
    for test, old, new in MUTANTS:
        if SRC.count(old) != 1:
            print(f"BAD-MUTANT (anchor count {SRC.count(old)}): {test}")
            bad += 1
            continue
        base = run(test, SRC)
        mut = run(test, SRC.replace(old, new))
        ok = base == 0 and mut != 0
        print(f"{'OK  ' if ok else 'FAIL'} base_pass={base == 0} fails_on_mutant={mut != 0}  {test}")
        bad += (not ok)
    print(f"{len(MUTANTS) - bad}/{len(MUTANTS)} proven")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
