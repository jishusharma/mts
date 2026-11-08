"""Hand-listed non-calendar news events (OURS grouping). Public record, short titles only, no headline text.

Fields: class, subclass, date, time_utc ('' = unknown), quality, title, source_hint.
quality: exact = minute known from a public clock (market open, on-chain epoch, block, scheduled speech);
         approx = hour known to about +-1 h from memory of press coverage; day = only the date is known.
date_check is 'recalled' for every row here: the date comes from the author's recall of public coverage, NOT fetched this
session (the fetched rows are the BLS and Fed calendars). The REPORT lists this as a gap.
Rows from analyst transcripts: none (F:/CryptoScrapper/cbp_v2 and the transcript store are absent on this machine).
"""
SEED = [
    # ETF / SEC decisions
    ("ETF_SEC", "spot_btc_fake_tweet", "2024-01-09", "21:12", "approx", "SEC X account false spot BTC ETF approval post", "press 2024-01-09"),
    ("ETF_SEC", "spot_btc_approval", "2024-01-10", "", "day", "SEC approves spot BTC ETF listings", "SEC statement 2024-01-10"),
    ("ETF_SEC", "spot_btc_first_trading", "2024-01-11", "14:30", "exact", "Spot BTC ETFs begin trading (US open)", "exchange open 09:30 ET"),
    ("ETF_SEC", "eth_etf_surprise", "2024-05-20", "", "day", "Report SEC reversal on ETH ETF 19b-4", "Bloomberg 2024-05-20"),
    ("ETF_SEC", "eth_etf_19b4", "2024-05-23", "", "day", "SEC approves ETH ETF 19b-4 filings", "SEC 2024-05-23"),
    ("ETF_SEC", "eth_etf_first_trading", "2024-07-23", "13:30", "exact", "Spot ETH ETFs begin trading (US open)", "exchange open 09:30 ET"),
    ("ETF_SEC", "options_listing", "2024-11-19", "", "day", "IBIT options begin trading", "Nasdaq 2024-11-19"),
    ("ETF_SEC", "in_kind", "2025-07-29", "", "day", "SEC allows in-kind creation for crypto ETPs", "SEC 2025-07-29"),
    ("ETF_SEC", "generic_listing", "2025-09-17", "", "day", "SEC approves generic listing standards for crypto ETPs", "SEC 2025-09-17"),
    # Hacks and theft
    ("HACK", "exchange", "2024-05-31", "", "day", "DMM Bitcoin theft disclosed (about 305 M USD)", "DMM notice 2024-05-31"),
    ("HACK", "exchange", "2024-07-18", "", "day", "WazirX multisig theft (about 230 M USD)", "WazirX 2024-07-18"),
    ("HACK", "exchange", "2025-02-21", "14:13", "approx", "Bybit cold wallet theft (about 1.5 B USD)", "on-chain 2025-02-21"),
    ("HACK", "defi", "2025-11-03", "", "day", "Balancer v2 exploit", "press 2025-11-03"),
    ("HACK", "exchange", "2026-10-29", "20:39", "exact", "Binance hot wallet outflows (Tree News first headline)", "MyTradingSys/research/news_feeds_2026-10-30/REPORT.md"),
    # Government and supply overhang wallet moves
    ("SUPPLY_OVERHANG", "mtgox", "2024-05-28", "", "day", "Mt Gox wallet moves first of 2024", "Arkham 2024-05-28"),
    ("SUPPLY_OVERHANG", "mtgox", "2024-07-05", "", "day", "Mt Gox wallet moves before repayment", "Arkham 2024-07-05"),
    ("SUPPLY_OVERHANG", "germany", "2024-06-19", "", "day", "German state wallets start moving seized BTC", "Arkham 2024-06-19"),
    ("SUPPLY_OVERHANG", "germany", "2024-07-04", "", "day", "German state large BTC transfers to exchanges", "Arkham 2024-07-04"),
    ("SUPPLY_OVERHANG", "us_gov", "2024-06-26", "", "day", "US government Silk Road wallet transfers", "Arkham 2024-06-26"),
    ("SUPPLY_OVERHANG", "mtgox", "2024-11-12", "", "day", "Mt Gox wallet moves", "Arkham 2024-11-12"),
    # Politics and election
    ("POLITICS_US", "assassination_attempt", "2024-07-13", "22:11", "approx", "Shooting at Trump rally Butler PA", "press 2024-07-13"),
    ("POLITICS_US", "biden_withdraws", "2024-07-21", "17:46", "approx", "Biden ends re-election bid", "press 2024-07-21"),
    ("POLITICS_US", "bitcoin_conf_speech", "2024-07-27", "", "day", "Trump Bitcoin 2024 Nashville speech", "press 2024-07-27"),
    ("POLITICS_US", "debate", "2024-09-11", "01:00", "approx", "Trump-Harris debate starts", "ABC 2024-09-10 21:00 ET"),
    ("POLITICS_US", "wlfi_announce", "2024-09-16", "", "day", "World Liberty Financial announced", "press 2024-09-16"),
    ("POLITICS_US", "election_call", "2024-11-06", "07:30", "approx", "Trump win called by networks", "press 2024-11-06"),
    ("POLITICS_US", "gensler_exit", "2024-11-21", "", "day", "Gensler to step down from SEC announced", "SEC 2024-11-21"),
    ("POLITICS_US", "inauguration", "2025-01-20", "17:00", "exact", "Trump sworn in (noon ET)", "swearing-in 12:00 ET"),
    ("POLITICS_US", "trump_memecoin", "2025-01-17", "", "day", "TRUMP memecoin launched", "press 2025-01-17"),
    ("POLITICS_US", "crypto_eo", "2025-01-23", "", "day", "Executive order on digital assets signed", "White House 2025-01-23"),
    ("POLITICS_US", "reserve_post", "2025-03-02", "", "day", "Trump names coins for a crypto reserve", "Truth Social 2025-03-02"),
    ("POLITICS_US", "reserve_eo", "2025-03-06", "", "day", "Strategic Bitcoin Reserve executive order", "White House 2025-03-06"),
    ("POLITICS_US", "crypto_summit", "2025-03-07", "", "day", "White House crypto summit", "White House 2025-03-07"),
    ("POLITICS_US", "sec_drops_coinbase", "2025-02-21", "", "day", "SEC drops Coinbase case", "SEC 2025-02-21"),
    ("POLITICS_US", "sec_drops_binance", "2025-05-29", "", "day", "SEC dismisses Binance case", "SEC 2025-05-29"),
    ("POLITICS_US", "genius_signed", "2025-07-18", "", "day", "GENIUS stablecoin act signed", "White House 2025-07-18"),
    ("POLITICS_US", "401k_eo", "2025-08-07", "", "day", "Executive order on crypto in 401k plans", "White House 2025-08-07"),
    ("POLITICS_US", "cz_pardon", "2025-10-23", "", "day", "CZ pardon announced", "press 2025-10-23"),
    ("POLITICS_US", "kr_martial_law", "2024-12-03", "13:27", "approx", "South Korea martial law declared", "press 2024-12-03 22:27 KST"),
    # Tariffs and trade
    ("TARIFF_TRADE", "tariff_announce", "2025-02-01", "", "day", "Tariffs on Canada Mexico China signed", "White House 2025-02-01"),
    ("TARIFF_TRADE", "tariff_pause", "2025-02-03", "", "day", "Tariff pause for Canada and Mexico", "press 2025-02-03"),
    ("TARIFF_TRADE", "liberation_day", "2025-04-02", "20:00", "approx", "Liberation Day tariff announcement (4 pm ET)", "White House 2025-04-02"),
    ("TARIFF_TRADE", "asia_open_selloff", "2025-04-07", "", "day", "Global sell-off on tariff fear", "press 2025-04-07"),
    ("TARIFF_TRADE", "pause_90d", "2025-04-09", "17:18", "approx", "Tariff 90-day pause post", "Truth Social 2025-04-09"),
    ("TARIFF_TRADE", "geneva_deal", "2025-05-12", "", "day", "US-China tariff truce announced", "press 2025-05-12"),
    ("TARIFF_TRADE", "eu_threat", "2025-05-23", "", "day", "EU 50 percent tariff threat", "Truth Social 2025-05-23"),
    ("TARIFF_TRADE", "china_100", "2025-10-10", "20:00", "approx", "100 percent China tariff threat and liquidation cascade", "press 2025-10-10"),
    # Geopolitics
    ("GEOPOLITICS", "iran_israel", "2025-06-13", "", "day", "Israel strikes Iran", "press 2025-06-13"),
    ("GEOPOLITICS", "us_strikes", "2025-06-22", "", "day", "US strikes Iranian nuclear sites", "press 2025-06-21/22"),
    ("GEOPOLITICS", "ceasefire", "2025-06-24", "", "day", "Israel-Iran ceasefire announced", "press 2025-06-23/24"),
    # Macro shocks outside the data calendar
    ("MACRO_SHOCK", "boj_hike_yen", "2024-08-05", "", "day", "Yen carry-trade unwind sell-off", "press 2024-08-05"),
    ("MACRO_SHOCK", "deepseek", "2025-01-27", "", "day", "AI model sell-off in US tech", "press 2025-01-27"),
    ("MACRO_SHOCK", "moodys", "2025-05-16", "", "day", "Moody's downgrades US sovereign", "Moody's 2025-05-16"),
    ("MACRO_SHOCK", "shutdown_start", "2025-10-01", "", "day", "US federal government shutdown starts", "press 2025-10-01"),
    ("MACRO_SHOCK", "shutdown_end", "2025-11-12", "", "day", "US federal government shutdown ends", "press 2025-11-12"),
    ("MACRO_SHOCK", "bls_chief_fired", "2025-08-01", "", "day", "BLS commissioner dismissed after jobs report", "press 2025-08-01"),
    ("MACRO_SHOCK", "musk_feud", "2025-06-05", "", "day", "Trump-Musk public feud", "press 2025-06-05"),
    # Central bank speeches and non-US decisions
    ("CB_OTHER", "boj", "2024-03-19", "", "day", "BoJ ends negative rates", "BoJ 2024-03-19"),
    ("CB_OTHER", "boj", "2024-07-31", "", "day", "BoJ hike to 0.25 percent", "BoJ 2024-07-31"),
    ("CB_OTHER", "boj", "2025-12-19", "", "day", "BoJ hike to 0.75 percent", "BoJ 2025-12-19"),
    ("CB_OTHER", "ecb", "2024-06-06", "12:15", "exact", "ECB first cut of cycle", "ECB 14:15 CEST"),
    ("CB_OTHER", "ecb", "2024-09-12", "12:15", "exact", "ECB cut", "ECB 14:15 CEST"),
    ("FED_SPEECH", "jackson_hole", "2024-08-23", "14:00", "exact", "Powell Jackson Hole speech (10:00 ET)", "Fed 2024-08-23"),
    ("FED_SPEECH", "jackson_hole", "2025-08-22", "14:00", "exact", "Powell Jackson Hole speech (10:00 ET)", "Fed 2025-08-22"),
    ("FED_SPEECH", "powell_attack", "2025-04-21", "", "day", "Trump attacks Powell, firing talk", "press 2025-04-21"),
    # Protocol and corporate events
    ("PROTOCOL_CORP", "halving", "2024-04-20", "00:09", "exact", "Bitcoin halving block 840000", "on-chain block time"),
    ("PROTOCOL_CORP", "dencun", "2024-03-13", "13:55", "exact", "Ethereum Dencun upgrade", "on-chain epoch 269568"),
    ("PROTOCOL_CORP", "pectra", "2025-05-07", "10:05", "exact", "Ethereum Pectra upgrade", "on-chain epoch 364032"),
    ("PROTOCOL_CORP", "fusaka", "2025-12-03", "21:49", "exact", "Ethereum Fusaka upgrade", "on-chain epoch 411392"),
    ("PROTOCOL_CORP", "btc_100k", "2024-12-05", "01:00", "approx", "BTC first trades above 100k", "price print"),
    ("PROTOCOL_CORP", "circle_ipo", "2025-06-05", "", "day", "Circle IPO day", "NYSE 2025-06-05"),
    ("PROTOCOL_CORP", "coinbase_sp500", "2025-05-12", "", "day", "Coinbase added to S&P 500 announced", "S&P 2025-05-12"),
]
