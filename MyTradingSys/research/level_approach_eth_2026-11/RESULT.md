# RESULT: level approach (C15) replicated on ETHUSDT and BTC+ETH pooled, DEV only, descriptive, fee-free

Pre-reg `PRE_REG.md` sha256 7a878da8c836faf161b76a60eb13b1367355afb08591ae791eedc9716d03432f. Data: BTCUSDT + ETHUSDT USD-M futures 1m 2022-01..2024-06; VALIDATION and HOLDOUT not read. Card ms-level-approach-eth-replicate.

**Verdict: REPLICATES.** 64 near_miss / wick_back sequence rows judged: 4 AGREE, 20 DISAGREE, 40 UNDERPOWERED (a cell under n 30). No edge claim; an agreeing row is a hypothesis for a fresh-window test.

Regime mix: POOL 260 weeks: bull 36 (14%) | bear 0 (0%) | range 224 (86%) | n/a 0 (0%) (BTCUSDT 130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%); ETHUSDT 130 weeks: bull 11 (8%) | bear 0 (0%) | range 119 (92%) | n/a 0 (0%))

## Reproduction check (BTC row first)
BTC futures through the unchanged C15 code: 10822 events (C15 shipped 10822); 32 kind x class x TF cells compared with the shipped tables.csv, 0 n mismatches.

## C15 invalidation row (named in advance)
near_miss 1m, RSI<50, CVD12<=0, below daily BB mid: BTC n 466 p 0.210 (A 0.222 / B 0.176); ETH n 423 p 0.281 (A 0.287 / B 0.275); pooled n 889 p 0.244 vs pooled base 0.278; AGREES.

## Agreeing rows (all four symbol x half cells n >= 30, same sign vs each symbol's class base, pooled CI excludes pooled base)
|cls|tf|rsi|cvd|bbmid|BTC n|p|A|B|ETH n|p|A|B|POOL n|p|ci|base|agreement|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|near_miss|1m|0|0|0|466|0.210|0.222|0.176|423|0.281|0.287|0.275|889|0.244|0.217-0.273|0.278|AGREES|
|near_miss|1m|0|0|1|641|0.287|0.286|0.289|753|0.321|0.343|0.299|1394|0.306|0.282-0.330|0.278|AGREES|
|near_miss|5m|0|0|1|187|0.369|0.409|0.312|214|0.407|0.382|0.429|401|0.389|0.343-0.438|0.325|AGREES|
|wick_back|5m|1|1|0|175|0.309|0.302|0.333|188|0.282|0.281|0.286|363|0.295|0.250-0.344|0.369|AGREES|

## Powered rows that disagree
|cls|tf|rsi|cvd|bbmid|BTC n|p|A|B|ETH n|p|A|B|POOL n|p|ci|base|agreement|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|near_miss|15m|1|0|1|98|0.347|0.343|0.349|88|0.273|0.273|0.273|186|0.312|0.250-0.382|0.323|DISAGREES|
|near_miss|15m|1|1|0|215|0.344|0.344|0.344|167|0.383|0.451|0.303|382|0.361|0.315-0.411|0.323|DISAGREES|
|near_miss|15m|1|1|1|255|0.341|0.416|0.269|208|0.308|0.281|0.330|463|0.326|0.285-0.370|0.323|DISAGREES|
|near_miss|1h|1|1|1|97|0.361|0.529|0.174|67|0.343|0.250|0.429|164|0.354|0.285-0.429|0.332|DISAGREES|
|near_miss|1m|0|1|0|122|0.230|0.212|0.270|111|0.180|0.140|0.222|233|0.206|0.159-0.263|0.278|DISAGREES|
|near_miss|1m|0|1|1|146|0.274|0.329|0.209|195|0.308|0.312|0.302|341|0.293|0.247-0.344|0.278|DISAGREES|
|near_miss|1m|1|0|0|310|0.239|0.257|0.190|272|0.309|0.346|0.272|582|0.271|0.237-0.309|0.278|DISAGREES|
|near_miss|1m|1|0|1|412|0.299|0.292|0.305|455|0.292|0.280|0.302|867|0.295|0.266-0.326|0.278|DISAGREES|
|near_miss|1m|1|1|0|894|0.217|0.234|0.181|779|0.300|0.356|0.231|1673|0.256|0.235-0.277|0.278|DISAGREES|
|near_miss|1m|1|1|1|1307|0.287|0.299|0.274|1227|0.293|0.273|0.312|2534|0.290|0.272-0.308|0.278|DISAGREES|
|near_miss|5m|0|0|0|140|0.257|0.309|0.140|113|0.327|0.382|0.276|253|0.289|0.236-0.347|0.325|DISAGREES|
|near_miss|5m|1|0|0|118|0.237|0.203|0.308|99|0.343|0.421|0.295|217|0.286|0.230-0.349|0.325|DISAGREES|
|near_miss|5m|1|0|1|169|0.331|0.375|0.299|164|0.372|0.443|0.319|333|0.351|0.302-0.404|0.325|DISAGREES|
|near_miss|5m|1|1|0|416|0.264|0.277|0.239|301|0.372|0.434|0.286|717|0.310|0.277-0.344|0.325|DISAGREES|
|near_miss|5m|1|1|1|530|0.330|0.360|0.301|433|0.298|0.326|0.271|963|0.316|0.287-0.346|0.325|DISAGREES|
|wick_back|15m|1|1|0|165|0.327|0.311|0.372|182|0.374|0.386|0.340|347|0.352|0.303-0.403|0.364|DISAGREES|
|wick_back|15m|1|1|1|214|0.360|0.344|0.386|215|0.367|0.398|0.322|429|0.364|0.320-0.410|0.364|DISAGREES|
|wick_back|1h|1|1|1|182|0.291|0.268|0.329|147|0.476|0.511|0.424|329|0.374|0.323-0.427|0.361|DISAGREES|
|wick_back|1m|1|1|1|194|0.392|0.409|0.355|262|0.412|0.436|0.367|456|0.404|0.359-0.449|0.376|DISAGREES|
|wick_back|5m|1|1|1|224|0.362|0.349|0.385|286|0.360|0.358|0.363|510|0.361|0.320-0.403|0.369|DISAGREES|

## Class base rates (near_miss, wick_back; both level kinds pooled, features known)
|scope|cls|tf|n|p|ci|nA|pA|nB|pB|
|---|---|---|---|---|---|---|---|---|---|
|BTCUSDT|near_miss|15m|755|0.331|0.298-0.365|425|0.369|330|0.282|
|ETHUSDT|near_miss|15m|621|0.314|0.279-0.352|298|0.332|323|0.297|
|POOL|near_miss|15m|1376|0.323|0.299-0.349|723|0.354|653|0.289|
|BTCUSDT|near_miss|1h|247|0.352|0.295-0.414|132|0.447|115|0.243|
|ETHUSDT|near_miss|1h|169|0.302|0.238-0.375|78|0.295|91|0.308|
|POOL|near_miss|1h|416|0.332|0.288-0.378|210|0.390|206|0.272|
|BTCUSDT|near_miss|1m|4298|0.260|0.247-0.273|2595|0.266|1703|0.251|
|ETHUSDT|near_miss|1m|4215|0.297|0.283-0.311|2156|0.307|2059|0.286|
|POOL|near_miss|1m|8513|0.278|0.269-0.288|4751|0.284|3762|0.270|
|BTCUSDT|near_miss|5m|1646|0.305|0.283-0.328|960|0.325|686|0.277|
|ETHUSDT|near_miss|5m|1436|0.349|0.325-0.374|716|0.381|720|0.317|
|POOL|near_miss|5m|3082|0.325|0.309-0.342|1676|0.349|1406|0.297|
|BTCUSDT|wick_back|15m|485|0.336|0.295-0.379|317|0.325|168|0.357|
|ETHUSDT|wick_back|15m|563|0.387|0.348-0.428|337|0.404|226|0.363|
|POOL|wick_back|15m|1048|0.364|0.335-0.393|654|0.365|394|0.360|
|BTCUSDT|wick_back|1h|385|0.309|0.265-0.357|239|0.314|146|0.301|
|ETHUSDT|wick_back|1h|413|0.409|0.363-0.457|238|0.424|175|0.389|
|POOL|wick_back|1h|798|0.361|0.328-0.395|477|0.369|321|0.349|
|BTCUSDT|wick_back|1m|452|0.385|0.341-0.431|337|0.377|115|0.409|
|ETHUSDT|wick_back|1m|619|0.370|0.333-0.409|421|0.373|198|0.364|
|POOL|wick_back|1m|1071|0.376|0.348-0.406|758|0.375|313|0.380|
|BTCUSDT|wick_back|5m|539|0.375|0.335-0.416|384|0.372|155|0.381|
|ETHUSDT|wick_back|5m|665|0.364|0.328-0.401|407|0.346|258|0.391|
|POOL|wick_back|5m|1204|0.369|0.342-0.396|791|0.359|413|0.387|

## Read this first
- Wilson CIs treat events as independent; 1m events cluster within days, so true CIs are wider.
- 64 rows looked at, no multiplicity correction; p_above_level for the through classes is partly built in and is not judged.
- Full per class x TF x sequence table for BTC, ETH and pooled (n, p, Wilson CI, halves A/B, base, agreement): `sequences.csv`; class tables: `classes.csv`.
