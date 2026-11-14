"""Fixed 60-coin universe, copied verbatim from edge6 capitulation_breadth PRE_REG.md (rule there: listing <= 2021-12-31, still trading Nov 2026, top 60 by 90-day volume)."""
COINS = ("BTC ETH SOL ZEC XRP NEAR BNB DOGE UNI TRX LINK ADA AVAX LTC AAVE XLM HBAR BCH DASH FIL DOT ICP ONE CAKE SAND CRV SHIB AR RUNE ALGO "
         "ETC RLC ATOM GALA BAT AXS VET ENS ONT CHZ COMP GRT XTZ SKL ZIL IOTA ENJ RVN CVC DYDX EGLD SUSHI CELR MANA KAVA HOT THETA FLOW NEO CTK").split()
assert len(COINS) == 60 and len(set(COINS)) == 60
