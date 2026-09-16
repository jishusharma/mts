# MTS live: deltas - last 12 minutes of one-minute bars
# usage:    . .\scripts\load.ps1   then type: deltas
$k = Invoke-RestMethod "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=12"
$k | ForEach-Object {
  [PSCustomObject]@{
    T   = ([DateTimeOffset]::FromUnixTimeMilliseconds($_[0])).ToString("HH:mm")
    C   = [double]$_[4]
    Vol = [math]::Round([double]$_[5],1)
    Dlt = [math]::Round((2*[double]$_[9] - [double]$_[5]),1)
  }
} | Format-Table -AutoSize
