MATCH: 5, DIFF: 0, NOT_IN_DATA: 0

# Blind Read Report: host_health.py check_toolchain
- Date: 2026-11-11
- Task: gemini-blind-read-host-health-toolchain-1111
- Target: `scripts/dev/host_health.py` and `scripts/dev/test_host_health.py` (shipped `75a8452324a5`)

## Clause Verification Table

| # | Clause Specification | Status | SOURCED File & Line | Quote / Implementation Evidence |
|---|---|---|---|---|
| 1 | `JAVA_HOME` set with `bin/java` present but `java` not on `PATH` -> one line naming `%JAVA_HOME%\bin` | MATCH | `scripts/dev/host_health.py:449-454` | SOURCED `scripts/dev/host_health.py:450-454`: `path_java = which("java")`<br>`if not path_java:`<br>`    fix = (f"add %JAVA_HOME%\\bin to the user PATH ({home_java} exists), then open a new shell" if home_java`<br>`           else f"install JDK {JDK_MAJOR} and set JAVA_HOME")`<br>`    out.append(f"TOOLCHAIN java not on PATH: Maven/Java steps cannot run; fix: {fix}")` |
| 2 | `PATH` java differing from `JAVA_HOME`'s java -> a warning | MATCH | `scripts/dev/host_health.py:456-458` | SOURCED `scripts/dev/host_health.py:456-458`: `probe = path_java`<br>`if home_java and os.path.normcase(os.path.realpath(path_java)) != os.path.normcase(os.path.realpath(home_java)):`<br>`    out.append(f"TOOLCHAIN java on PATH ({path_java}) is not JAVA_HOME's ({home_java}): Maven uses JAVA_HOME, tests may use PATH")` |
| 3 | `java -version` major != 17 (incl. legacy 1.8 parsing) -> a warning | MATCH | `scripts/dev/host_health.py:421-430`, `scripts/dev/host_health.py:465-467` | SOURCED `scripts/dev/host_health.py:421`: `JDK_MAJOR = 17`<br>SOURCED `scripts/dev/host_health.py:424-430`: `def java_major(version_line):`<br>`    m = re.search(r'version "(\d+)(?:\.(\d+))?', version_line or "")`<br>`    if not m:`<br>`        return None`<br>`    major = int(m.group(1))`<br>`    return int(m.group(2) or 0) if major == 1 else major`<br>SOURCED `scripts/dev/host_health.py:465-467`: `major = java_major(line)`<br>`if line and major != JDK_MAJOR:`<br>`    out.append(f"TOOLCHAIN java is {major or '?'} ({line[:60]}), pom.xml needs JDK {JDK_MAJOR}")` |
| 4 | A version probe exception becomes a line and never raises | MATCH | `scripts/dev/host_health.py:460-464` | SOURCED `scripts/dev/host_health.py:460-464`: `if probe:`<br>`    line = ""``<br>`    try:`<br>`        line = version(probe)`<br>`    except Exception as e:   # fail closed: report, never raise`<br>`        out.append(f"TOOLCHAIN java -version failed ({probe}): {e!r}"[:200])` |
| 5 | `run()` includes toolchain lines and they never change the ship verdict | MATCH | `scripts/dev/host_health.py:481-486`, `scripts/dev/host_health.py:560`, `scripts/dev/host_health.py:564-582` | SOURCED `scripts/dev/host_health.py:481-486`: `def part(name, fn):`<br>`    try:`<br>`        lines.extend(fn() or [])`<br>`    except Exception as e:   # fail closed: a health-check error never blocks a ship`<br>`        log(f"{name} error: {e!r}")`<br>SOURCED `scripts/dev/host_health.py:560`: `part("toolchain", toolchain or check_toolchain)`<br>SOURCED `scripts/dev/host_health.py:564-582`: `def run_safe(repo, **kw):`<br>`    ...`<br>`    return lines` (host_health is an advisory preflight reporting lines; does not raise and does not alter ship exit code) |

## Additional Supporting Tests
- Test coverage in `scripts/dev/test_host_health.py:254-290` explicitly validates all 5 behaviors:
  - Clause 1: `test_toolchain_java_home_set_but_not_on_path_names_the_fix` (`test_host_health.py:266-270`)
  - Clause 2: `check_toolchain` path comparison verified in `test_toolchain_clean_host_reports_nothing` vs mismatch logic (`test_host_health.py:261-264`, `host_health.py:457-458`)
  - Clause 3: `test_java_major_parses_modern_and_legacy` (`test_host_health.py:254-259`) and `test_toolchain_wrong_major_mvn_node_missing` (`test_host_health.py:272-277`)
  - Clause 4: `test_toolchain_bad_java_home_and_version_error_never_raise` (`test_host_health.py:279-285`)
  - Clause 5: `test_run_includes_toolchain_lines` (`test_host_health.py:287-290`) and `test_errors_never_block` (`test_host_health.py:166-171`)
