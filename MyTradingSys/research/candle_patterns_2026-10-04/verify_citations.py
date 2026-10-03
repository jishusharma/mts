"""Citation check for the BTC candle-pattern research (playbook Part I, STEP 3a).

For every claimed source: ask the Crossref registry for the best bibliographic match and print
title / authors / venue / year / DOI. A citation is VERIFIED only when a human (or the caller) sees
title + first author + year + venue agree with the claim; this script prints the evidence, it does
not judge. Output goes to citations_verified.txt with the run date.

Run: python MyTradingSys/research/candle_patterns_2026-10-04/verify_citations.py
Needs internet. Stdlib only. Crossref is a DOI registry, not a paywall bypass: abstracts appear
only when the publisher deposited them; otherwise the finding is tagged 'metadata only'.
"""
import sys
sys.dont_write_bytecode = True
import json, re, urllib.parse, urllib.request, datetime
from pathlib import Path

# (claim label, bibliographic query, expected first-author surname, expected year)
CLAIMS = [
    ("MYR2006", "Candlestick technical trading strategies: Can they create value for investors? Marshall Young Rose", "Marshall", 2006),
    ("MYC2008", "Are candlestick technical trading strategies profitable in the Japanese equity market? Marshall Young Cahan", "Marshall", 2008),
    ("Cohen2021", "Optimizing candlesticks patterns for Bitcoin's trading systems", "Cohen", 2021),
    ("MoserBrauneis2026", "Intraday price forecasts using candlestick patterns in cryptocurrency markets", "Moser", 2026),
    ("Lu2012", "Profitable candlestick trading strategies - The evidence from a new perspective Lu", "Lu", 2012),
    ("Tharavanij2017", "Profitability of Candlestick Charting Patterns in the Stock Exchange of Thailand", "Tharavanij", 2017),
    ("CaginalpLaurent1998", "The predictive power of price patterns Caginalp Laurent", "Caginalp", 1998),
    ("FockKleinZwergel2005", "Performance of candlestick analysis on intraday futures data", "Fock", 2005),
    ("LoMamayskyWang2000", "Foundations of technical analysis: computational algorithms, statistical inference, and empirical implementation", "Lo", 2000),
    ("BrockLakLeBaron1992", "Simple technical trading rules and the stochastic properties of stock returns", "Brock", 1992),
    ("SullivanTW1999", "Data-snooping, technical trading rule performance, and the bootstrap", "Sullivan", 1999),
    ("White2000", "A reality check for data snooping", "White", 2000),
    ("Hansen2005", "A test for superior predictive ability", "Hansen", 2005),
    ("HsuHsuKuan2010", "Testing the predictive ability of technical analysis using a new stepwise test without data snooping bias", "Hsu", 2010),
    ("BaileyLdP2014DSR", "The deflated Sharpe ratio: correcting for selection bias, backtest overfitting and non-normality", "Bailey", 2014),
    ("BaileyPBO2017", "The probability of backtest overfitting Bailey Borwein Lopez de Prado Zhu Journal of Computational Finance", "Bailey", 2017),
    ("HarveyLiuZhu2016", "and the Cross-Section of Expected Returns Harvey Liu Zhu Review of Financial Studies", "Harvey", 2016),
    ("ParkIrwin2007", "What do we know about the profitability of technical analysis Park Irwin Journal of Economic Surveys", "Park", 2007),
    ("Gerritsen2020", "The profitability of technical trading rules in the Bitcoin market", "Gerritsen", 2020),
    ("Corbet2019", "The effectiveness of technical trading rules in cryptocurrency markets", "Corbet", 2019),
    ("HudsonUrquhart2021", "Technical trading and cryptocurrencies", "Hudson", 2021),
    ("LiuTsyvinski2021", "Risks and Returns of Cryptocurrency Liu Tsyvinski Review of Financial Studies", "Liu", 2021),
    ("GaoHanLiZhou2018", "Market intraday momentum Gao Han Li Zhou Journal of Financial Economics", "Gao", 2018),
    ("WenBouri2022", "Intraday return predictability in the cryptocurrency markets: Momentum, reversal, or both", "Wen", 2022),
    ("Detzel2021", "Learning and predictability via technical analysis: Evidence from bitcoin and stocks with hard-to-value fundamentals", "Detzel", 2021),
    ("Plastun2019", "Price overreactions in the cryptocurrency market", "Plastun", 2019),
    ("CaporalePlastun2019", "The day of the week effect in the cryptocurrency market", "Caporale", 2019),
    ("Romano2005", "Stepwise multiple testing as formalized data snooping", "Romano", 2005),
    ("BenjaminiHochberg1995", "Controlling the false discovery rate: a practical and powerful approach to multiple testing", "Benjamini", 1995),
    ("Ho2021", "Do Candlestick Patterns Work in Cryptocurrency Trading? IEEE International Conference on Big Data", "Ho", 2021),
    ("Cohen2023", "Intraday algorithmic trading strategies for cryptocurrencies", "Cohen", 2023),
    ("Urquhart2016", "The inefficiency of Bitcoin", "Urquhart", 2016),
    ("Tzouvanas2020", "Momentum trading in cryptocurrencies: Short-term returns and diversification benefits", "Tzouvanas", 2020),
    ("Osler2003", "Currency orders and exchange rate dynamics: an explanation for the predictive success of technical analysis", "Osler", 2003),
    ("ZarattiniORB2024", "A profitable day trading strategy for the U.S. equity market", "Zarattini", 2024),
    ("ZarattiniVWAP2023", "Volume Weighted Average Price (VWAP): The Holy Grail for Day Trading Systems", "Zarattini", 2023),
    ("Parkinson1980", "The extreme value method for estimating the variance of the rate of return", "Parkinson", 1980),
    ("GarmanKlass1980", "On the estimation of security price volatilities from historical data", "Garman", 1980),
    ("Efron1979", "Bootstrap methods: another look at the jackknife", "Efron", 1979),
    ("PolitisRomano1994", "The stationary bootstrap Politis Romano Journal of the American Statistical Association", "Politis", 1994),
]


def lookup(q):
    url = "https://api.crossref.org/works?rows=3&select=title,author,container-title,issued,DOI,type,abstract&query.bibliographic=" + urllib.parse.quote(q)
    req = urllib.request.Request(url, headers={"User-Agent": "MTS-research-citecheck/1.0 (mailto:noreply@example.invalid)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["message"]["items"]


def year(it):
    try:
        return it["issued"]["date-parts"][0][0]
    except Exception:
        return None


def main():
    out = [f"citation check run {datetime.date.today().isoformat()} (Crossref registry)"]
    for label, q, surname, yr in CLAIMS:
        try:
            items = lookup(q)
        except Exception as e:
            out.append(f"{label}: LOOKUP-ERROR {e}")
            continue
        best = None
        for it in items:
            au = [a.get("family", "") for a in it.get("author", [])]
            if surname.lower() in " ".join(au).lower()[:60].lower() and year(it) in range(yr - 2, yr + 3):
                best = it
                break
        if best is None:
            out.append(f"{label}: NO-MATCH expected {surname} {yr}; top hit: {items[0]['title'][0][:80] if items else 'none'}")
            continue
        au = ", ".join(a.get("family", "?") for a in best.get("author", [])[:5])
        ab = re.sub(r"<[^>]+>", "", best.get("abstract", "")).strip()
        out.append(f"{label}: MATCH | {best['title'][0]} | {au} | {(best.get('container-title') or ['?'])[0]} | {year(best)} | doi:{best['DOI']} | abstract:{'yes' if ab else 'no'}")
    text = "\n".join(out)
    print(text.encode("ascii", "replace").decode())
    Path(__file__).with_name("citations_verified.txt").write_text(text + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
