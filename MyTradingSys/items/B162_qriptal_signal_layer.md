# B162 - Qriptal (Habib) signal layer: Discord feed, verified record, testnet trades of his calls

Status: OPEN. Severity: MED. Opened 2026-10-10.
Source: Control Room inbox aj9lwmaqvn651mzh5jhj (2026-10-09T22:31Z, kind requirement). Full text verbatim in
MyTradingSys/system/OPERATOR_INBOX.md under that id.

## Operator's words (verbatim excerpts)

> There is new research on Imbalance trading that DSA did  - We have a analyst from you tube who also posts on discord. Habib his name.  Imbalance trader. Discord is setup with his chanel - we need the feed - he provides trades with entried andtargets - he trades candles on diff time frames with imbalnces on diff exchanges - so we need his layer!

> Working! It is easy - just place trades that he says! and do see his past record - verify.

> howis it that pp are selling 86 setups and we do not know any??

## What exists

- extracts/_staged_2026-09-27/MyTradingSys/research/analyst_layers_2026-09-27/ANALYST_LAYER_FRAMEWORK.md:61, :88-93:
  Qriptal is an external signal to be scored, not a rule source. His "imbalance" indicator is sold and undisclosed,
  so a rule built from it is REJECT tier (playbook Part I). His imbalance = small-body high-volume candle; it is not an
  FVG and not the order-book imbalance in research/imbalance_2026-10-10/RESEARCH.md (term collision, keep separate IDs).
- 22 raw Qriptal transcripts staged in extracts/_staged_2026-09-27/ (not canonical).
- One call scored: extracts/_staged_2026-09-27/extracts/qriptal/trade_log/2026-09-20_ZPFK3ZsLwoo.md (plan invalidated ~14 h later).
- qriptal.com (operator paste): 86 setups, 67.1% win rate, 49 W / 13 BE / 24 L, avg winner 3.99%, avg loser 0.63%.
  Self-reported; not verified.

## Plan

1. Score his public setups (site list, YouTube, Discord history) on Binance klines with fees: entry, stop and targets
   exactly as he posted them, time of post as the earliest entry. Report n, win rate, net R, against his own numbers.
2. Feed route: Control Room decision D21 (follow his announcement channel into the operator's server with a read-only
   bot, or paste calls into the Inbox). Bot token is the operator's; sessions never read secrets.
3. Layer `layer:qriptal:` on its own testnet account; his stop and targets only (provenance: his words). Testnet only.

# END

## 2026-10-10 Control Room D21
Operator: "Follow his channel into my server; set up a read-only bot" (note: "Also read youtube trasncripts").
Applied: DSA desk task 20261009-231508 (captions + scorecard). Bot: operator steps (Follow the announcement channel into their own server, create a bot with read-only Message Content scope, keep the token outside the repo); session builds a read-only logger that writes calls to a jsonl, token from an env var the session never reads. No trades until the scorecard exists.
