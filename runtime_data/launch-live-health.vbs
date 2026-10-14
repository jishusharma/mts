' MTS-Live-Health (every 5 min): stale recorder/loop file or dropped live process -> desktop popup.
' Runs the detector from the registry worktree against the live tree (read-only on the live system).
Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed.registry"
sh.Run """C:\Users\E-ngineers\AppData\Local\Python\pythoncore-3.14-64\python.exe"" scripts\sched\check_live_health.py --root ""C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"" --alert", 0, True
