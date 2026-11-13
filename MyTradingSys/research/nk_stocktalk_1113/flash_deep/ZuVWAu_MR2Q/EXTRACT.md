# NK StockTalk Concept Extract (Deep Pass): ZuVWAu_MR2Q

- **Concept:** Nifty Hedge 23 expiry setup under CAS rule
- **Video ID:** `ZuVWAu_MR2Q`
- **Title:** `NIFTY H23 Strategy After CAS Rule | Smart Entry & Exit  | Low Capital Weekly Expiry Hedge Setup`
- **Model:** `gemini-3.8-flash-low`

---

## Verbatim Hindi Caption Quotes

### Quote 1: Strategy Design & Context
> "जो सीए एस आया है उसके अकॉर्डिंग हम लोग हेज टू थ्री कैसे डिजाइन करें"
**Source GPS: ZuVWAu_MR2Q | BEGIN**
- [00:15]
- **TRANSLATION:** According to the CAS that has arrived, how do we design Hedge 23

### Quote 2: Timing on Expiry Day
> "जब भी आपको देखना है तो 2:00 बजे के बाद देखना है"
**Source GPS: ZuVWAu_MR2Q | BEGIN**
- [09:12]
- **TRANSLATION:** Whenever you have to look, look after 2:00 PM

### Quote 3: ATM Strike Selection (Spot vs Future)
> "एटीएम स्ट्राइक मतलब एट द मनी स्ट्राइक जहां स्पॉट है और स्पॉट को देखेंगे फ्यूचर को नहीं"
**Source GPS: ZuVWAu_MR2Q | BEGIN**
- [10:35]
- **TRANSLATION:** ATM strike means At The Money strike where spot is, and look at spot, not future

### Quote 4: Combined CE + PE Premium Threshold
> "सी ई और प्लस पी ई दोनों का जोड़ 50 से नीचे आ रहा हो"
**Source GPS: ZuVWAu_MR2Q | BEGIN**
- [10:55]
- **TRANSLATION:** Sum of both CE and PE should come below 50

### Quote 5: India VIX Filter / Regime
> "जब तक विक्स 15 है तब तक यह रूल है"
**Source GPS: ZuVWAu_MR2Q | BEGIN**
- [11:38]
- **TRANSLATION:** As long as VIX is below 15, this rule applies

### Quote 6: Staggered Averaging Entry Triggers (50-30-20 Method)
> "एवरेजिंग का रूल ये होगा कि हमारी पहली एंट्री 50 पे, दूसरी एंट्री 30 पे, तीसरी एंट्री एंट्री 20 के नीचे"
**Source GPS: ZuVWAu_MR2Q | MIDDLE**
- [16:05]
- **TRANSLATION:** The rule of averaging will be that our first entry is at 50, second entry at 30, third entry below 20

### Quote 7: Stop Loss Definition
> "यहां पे एक स्टॉप लॉस होता है जिसे हम कहते हैं कि नाइन से नीचे या 10 से नीचे"
**Source GPS: ZuVWAu_MR2Q | MIDDLE**
- [23:35]
- **TRANSLATION:** Here there is a stop loss which we say is below 9 or below 10

### Quote 8: Execution Time Windows
> "20 मिलेगा 3:21 के बाद, 30 मिलेगा 3:00 के बाद, 50 मिलेगा 2:00 के बाद"
**Source GPS: ZuVWAu_MR2Q | MIDDLE**
- [25:25]
- **TRANSLATION:** 20 will be available after 3:21, 30 will be available after 3:00, 50 will be available after 2:00

### Quote 9: Profit Target / Exit for Level 30
> "दूसरा जो 30 आ जाता है, तो पहली जो आपकी एग्जिट होगी, वह आपको 70 के ज़ोन में होनी चाहिए"
**Source GPS: ZuVWAu_MR2Q | END**
- [32:10]
- **TRANSLATION:** Secondly when 30 arrives, your first exit should be in the zone of 70

### Quote 10: Profit Target / Exit for Level 20
> "लेकिन अगर 20 पे होता है, तो 45 के पास आधा निकल जाएंगे"
**Source GPS: ZuVWAu_MR2Q | END**
- [32:30]
- **TRANSLATION:** But if it is at 20, half will be exited near 45

### Quote 11: Minimum Risk-Reward Structure
> "वन बाय वन मिनिमम रिवार्ड रखा गया उसके बाद तो बाकी हमें देगा ही 50 का 100 30 का 65 से 70 20 का 45"
**Source GPS: ZuVWAu_MR2Q | END**
- [37:30]
- **TRANSLATION:** 1:1 minimum reward is kept, after that it will give 100 for 50, 65 to 70 for 30, 45 for 20

---

## Explicit Parameters & NOT_STATED Items

- **Indicator settings (RSI / Moving Averages):** NOT_STATED: no RSI or moving averages used for Hedge 23 setup; purely option price and ATM spot based
- **Timeframe:** Expiry day intraday, specifically post 2:00 PM, 3:00 PM, 3:21 PM windows up to 3:30 PM
- **Underlying:** Nifty (Sensex mentioned as pending 1-2 months testing)
- **Strike distance:** ATM (At The Money) based strictly on Spot price
- **Combined premium entry rule:** CE + PE sum < 50
- **Averaging tiers:** Entry 1 at combined 50 (2 lots), Entry 2 at 30 (2 lots), Entry 3 at 20 (2 lots); target effective average cost ~33.33
- **Stop loss:** Premium combined below 9-10 (effective SL at 8, max risk ~25 points)
- **Targets:**
  - For entry at 50: first exit (half) at 100, ride remaining with SL at cost
  - For entry at 30: first exit (half) at 65-70
  - For entry at 20: first exit (half) at 45
- **Regime / VIX filter:** VIX <= 15 (different rule needed if VIX > 15)
- **Hedge / Expiry rules:** Trade only on expiry day (minimum 8 expiries/month across Nifty & Sensex)
- **Crypto mention:** NOT_STATED: no crypto discussion in video
- **What he says it is NOT:** NOT to trade in morning (premiums ~100), NOT OTM under new CAS rules, NOT on futures price
