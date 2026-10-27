# MTS live: trend - last 15 snapshots, side by side
# usage:    . .\scripts\load.ps1   then type: trend
$root = (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
Get-ChildItem "$root\runtime_data\snapshots\BTCUSDT_*.json" | Sort LastWriteTime -Desc | Select -First 15 | Sort LastWriteTime |
ForEach-Object {
  $jj = Get-Content $_.FullName -Raw | ConvertFrom-Json
  [PSCustomObject]@{
    T      = $jj.timestamp_utc.Substring(11,8)
    Price  = $jj.current_price
    CVD    = [math]::Round($jj.cvd.value,0)
    CVD_1h = [math]::Round($jj.cvd.cvd_recent.delta_1h,0)
    ND_1m  = [math]::Round($jj.trade_flow.net_delta_1m,0)
    ND_5m  = [math]::Round($jj.trade_flow.net_delta_5m,0)
    OI     = $jj.open_interest.direction
    Book   = $jj.conditions.book_imbalance
  }
} | Format-Table -AutoSize
