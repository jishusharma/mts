Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(fso.GetParentFolderName(WScript.ScriptFullName))
Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = root
' Daily task MTS-Orphan-Watchdog (09:10). 7 sweeps x 120 s; HALT only if an account is an orphan in all 7
' (window 720 s > max_entry_seconds 600). Waits, then returns the CLI exit code as LastTaskResult
' (0 ok, 1 read errors, 3 orphan HALT written).
WScript.Quit sh.Run("""python"" MyTradingSys\execution\orphan_watchdog_cli.py --interval 120 --confirm-sweeps 7 --max-sweeps 7", 0, True)