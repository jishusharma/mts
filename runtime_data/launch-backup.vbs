' MTS-Backup without a console window (operator inbox ca8tetn2qfaoaotj7caq, 2026-10-09).
' 2026-10-11: repo is public, so snapshots go to the local bare repo remote "backup" (F:\MTS_backup.git), never origin.
' Same shape as the other launch-*.vbs wrappers, but waits (bWait=True) so the task's LastTaskResult is the backup's real exit code.
Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = "C:\Users\E-ngineers\IdeaProjects\mts-push"
rc = sh.Run("""C:\Users\E-ngineers\AppData\Local\Microsoft\WindowsApps\python.exe"" scripts\dev\backup_snapshot.py --repo ""C:\Users\E-ngineers\IdeaProjects\mts-push"" --remote backup", 0, True)
WScript.Quit rc
