Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"
sh.Run "pwsh.exe -NoProfile -File MyTradingSys\mts\research\rerun_monitor.ps1", 0, False
