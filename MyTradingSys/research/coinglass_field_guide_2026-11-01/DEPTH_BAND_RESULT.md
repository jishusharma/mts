# Depth-band audit — reachability result (JIS-NUC rerun)

Row: 20261107-172114-depth-band-audit-rerun-from-jis-nuc-fapi
Card: depth-band-audit-marketdatasnapshot-bid-
Run from: JIS-NUC (host JIS-NUC), 2026-11-10

## Reachable: NO

Public IP country: India (ifconfig.co/country -> `India`; IP `2405:201:a416:9046:1073:b2e2:85ea:f48e`, IPv6).

| Target | Method | Timeout | Result |
|---|---|---|---|
| `https://fapi.binance.com/fapi/v1/ping` | Invoke-WebRequest, 20 s | 20 s | FAILED — operation has timed out |
| `https://fapi.binance.com/fapi/v1/depth?symbol=BTCUSDT&limit=5` | urllib, 15 s | 30.04 s wall | FAILED — `URLError: <urlopen error timed out>` |
| `https://fapi.binance.com/fapi/v1/depth?symbol=ETHUSDT&limit=5` | urllib, 15 s | 30.04 s wall | FAILED — `URLError: <urlopen error timed out>` |

The depth_band_check.py commands of the card were NOT run (fapi unreachable, no JSON came back).

## The card is still blocked

Same symptom as JIS-NB on 2026-11-01: every `fapi.binance.com` request times out from this network. The card
`depth-band-audit-marketdatasnapshot-bid-` needs a host whose egress reaches `fapi.binance.com`. JIS-NUC does not.

## Next

- The card's commands need a host with fapi reachability (operator decision or a VPN exit node). Both hosts tried
  so far (JIS-NB, JIS-NUC, India egress) time out.
- Alternatively, capture a MarketDataSnapshot bid/ask band from the live feed's own logs (the runtime path that already
  uses `bidAskRatioFromDepth`) and audit the span from that data. That belongs to a separate card.
