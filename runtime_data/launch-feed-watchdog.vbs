Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"
sh.Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -File ""C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\scripts\live\feed-watchdog.ps1""", 0, False
