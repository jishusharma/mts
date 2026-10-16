Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"
sh.Run """C:\Users\E-ngineers\AppData\Local\Microsoft\WindowsApps\pwsh.exe"" -NoProfile -ExecutionPolicy Bypass -File ""C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\scripts\core\loop-supervisor.ps1"" -Mode armed -IntervalMin 1", 0, False
