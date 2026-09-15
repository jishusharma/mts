$root = "C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"
Get-Content "$root\data\apparatus_log.txt" | Select-String "ALERT #" | Select -Last 10
