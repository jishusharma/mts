"""Expand {{key}} quote markers in GLOSSARY_SRC.md into verified quote blocks.

Usage (repo root): python MyTradingSys/research/setup_catalog_2026-10-15/malkan/tools/build_glossary.py
Each English quote becomes   > "text" / **Source GPS: id | POS** / - cite (file:line, timestamp)
POS is computed from the raw transcript (thirds), so verify_extract_quotes.py agrees by construction.
Hindi markers {{hi:<line>}} copy the "Hindi original" line <line> of extract_A-CQiV_UFB4.md and
check it against raw_transcripts_canonical/A-CQiV_UFB4_hi_raw.txt (whitespace-normalised).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
M = ROOT / "MyTradingSys/research/setup_catalog_2026-10-15/malkan"
EXT = ROOT / "MyTradingSys/research/malkan_extract_2026-10-15/extracts"
RAW = ROOT / "raw_transcripts_canonical"

A, G, W, C = "A-CQiV_UFB4", "GbXnw_tNMtw", "Wvq1TZh8aF0", "cQ-y1oULkBw"

Q = {
    # ---- regular bearish
    "rb_w": (W, "It is making a new high from A to B but RSI has made a lower high from A to B, which means its upward speed has reduced at point B."),
    "rb_g1": (G, "you have an uptrend see market made a new height here and RSI made a lower high in that is called as usual normal divergency"),
    "rb_g2": (G, "markets are going up in mark and RSI is going low and this is called normal bearish divergence"),
    "rb_c": (C, "so you have to take the contract rate in the uptrend, which is called a short trick"),
    "contra_w": (W, "Contra means buying signal in down trend and selling signal in up trend."),
    "contra_a": (A, "Normal divergence is always a contra trend. Contra means the market is up, so bearish divergence will show, if it is down, then bullish divergence will show"),
    "contra_g": (G, "contract rate means in analog in an uptrend that right is short if we look at divergences"),
    "close_w": (W, "Now what do we have to compare? Close to close. Because RSI is based on closing price."),
    "close_c": (C, "Always remember that the construction of RSI or it is made on the RSI is at the closing price, so the closing has to match the closing."),
    "swing_g": (G, "we are comparing the lowest the swing lows you see there is a swing low here there's a swing low here"),
    "conf_rb_w": (W, "It will be confirmed when he shows the red candle."),
    "stop_rb_w": (W, "What would be my stop loss above the high, understand there is a shadow here also in this candle."),
    "targetC_w": (W, "The target is this point between A and B which we let's call it C. Right C point is my target."),
    "uturn_w": (W, "The function of divergence is to make the trend take a U-turn. The U-turn can be small or big."),
    "conf_c": (C, "the more you should not trade blindly just by looking at divergence. It should get confirmation. That will be train line confirmation. It will get a break or the break will move upwards."),
    "failed_w": (W, "so divergence says that it is slowing down will it take a U turn after slowing down or will it take a right"),
    # ---- regular bullish
    "rbu_w1": (W, "Bullish divergence will come in a down trend. Right? And he will give us the signal to buy."),
    "rbu_w2": (W, "A to B is lower but A to B is higher."),
    "rbu_c1": (C, "Now you will see that first the market is going down. Look, the sentiment has made a new low from A to B. But what is the RSI doing? It is above B, which means it is not making a new low, which means the speed of going down has reduced, which means now it has to make a U-turn upwards."),
    "rbu_c2": (C, "So, this divergence is now telling us to buy in Do Trade."),
    "rbu_g": (G, "closely this chart there are normal bullish divergence is also between the price if you compare the lows"),
    "rbu_a": (A, "In an uptrend, you will see normal divergence and PRD. What can be seen in a downtrend? Bullish divergence will be seen and along with it, NRD will also be seen. NRD means negative reverse divergence"),
    "conf_rbu_w": (W, "how do I get a confirmation that it is going to work when I see a bullish candle the bullish candle is formed it is confirmed my entry is done means buy"),
    # ---- bars / levels / timeframe of regular divergence
    "bars_w1": (W, "the shorter the divergence is, the more powerful it is, what I mean is that the fewer the number of bars in the divergence, the more powerful the divergence will be."),
    "bars_w2": (W, "I will say that less than 10 bars is the most powerful divergence. It should be between three and 10."),
    "bars_w3": (W, "If you have 30 times divergence, 50 times divergence, that is diluted."),
    "bars_w4": (W, "Three. Because one will go up, one down, then one up again. Right? So three is the minimum requirement."),
    "bars_c1": (C, "The fewer they are, the more powerful it will be. That means there are three bars, five bars, seven bars."),
    "bars_c2": (C, "As the number of bars increases, you see 15, 20, 25, 30, 40 bars. The divergence gets diluted completely and it has not worked."),
    "bars_c3": (C, "how much is it between this and this, 15 to 20 times, this is still fine because the number of lee and a big U turn from here"),
    "lvl_w": (W, "the most powerful divergence come near 60 bearish divergence and the most powerful bullish divergence comes near 40."),
    "lvl_w2": (W, "Because there will also be reverse divergences which will negate that divergence or its effect will be very short term."),
    "tf_c": (C, "Right, if it's on the daily, there will be a small U-turn. If it's on the weekly, there will be a big U-turn. And if it's on the monthly, there will be a very big U-turn."),
    "tf_w": (W, "There will be no direct trade in the weekly because Monday will come first."),
    "tf_w2": (W, "Meaning if you have to do short-term trading , which is like swing trading, two-four days, then this is one of the most powerful things to do, which is three bar divergence, five bar divergence."),
    # ---- PRD
    "prd_a1": (A, "market, that is, the price, makes a higher top, higher bottom, like when A and B, then this is a straight uptrend. Right, at this time, when we look at the RSI, when RSI reacts to A and B, then the B leg is down."),
    "prd_a2": (A, "Reverse divergence means that there is a lot of pressure. Basically, force means momentum. I applied a lot of pressure, but still the market is not going below B."),
    "prd_a3": (A, "price is making a higher bottom and RSI is making a lower bottom. That's reverse divergence and positive reversal in an up trend."),
    "prd_a4": (A, "that means this uptrend is going to intensify because it is a reverse divergence, because despite applying pressure, the price of B is not going down. That means it is very strong"),
    "prd_a5": (A, "what is your signal to buy, this is where we get a signal, this is the uptrend, we capture on PRD, PRD means positive reverse divergence"),
    "prd_a6": (A, "Who will win? PRD will win. Why? Because that is trend following."),
    "prd_a7": (A, "if one PRD is found and that too is found in the starting, in the starting, meaning when the trend is starting. When did the trend start? It went above 60 from here. Right after that, I immediately got the PRD. That is the best opportunity to have a very low risk buy trade."),
    "prd_a8": (A, "it is visible on all time frames, but where you can trade it, it is mostly daily and at the most weekly. Sometimes it will be visible on monthly as well, but then trading monthly would be very difficult"),
    "prd_a9": (A, "Whenever you look at an up trend, what I have to look for is a positive reverse divergence."),
    "prd_a10": (A, "meaning there can be multiple PRDs"),
    "prd_g1": (G, "called reverse divergence where price makes a higher high RSI makes a lower low and it's an uptrend and it confirms an uptrend that is going to go high and make a new high after this"),
    "prd_g2": (G, "what is reverse divergence in an uptrend it is making higher top higher bottom on price and RSI makes a lower bottom"),
    "prd_g3": (G, "in this uptrend there are bearish divergences and there are positive reverse divergences"),
    "prd_g4": (G, "when you look at positive reverse divergences you want to go long"),
    "prd_g5": (G, "because it is a trend following indicator whereas normal divergences which is the bearish and the bullish divergences are our contract"),
    "prd_g6": (G, "that's where I'm going to buy here at this point and put a stop loss below this the swing low"),
    "prd_g7": (G, "the number of bars which is very important if you see this reverse divergence was within seven eight bars this is another seven eight bars but this is like more than fifteen twenty bars so I that dilutes the reverse divergence"),
    "prd_g8": (G, "uptrend you're going to compare the lows that's when you're going to get that a worse divergence and then if you have number of bars which are less than 15 and if they both the points are about 60 and RSI is lower price is higher that calls for positive reverse divergence"),
    "prd_g9": (G, "number of bar should be between five to fifty and both the point should be about sixty if it's a positive edge divergence and of course if it's a negative reverse divergence it should be below forty"),
    "prd_g10": (G, "it's possible on daily weekly monthly it's also possible in intraday and it works on all time frames and the same rules can be applied everywhere"),
    "prd_g11": (G, "you need to buy a good trending stock at support"),
    # ---- NRD
    "nrd_a1": (A, "the market is making a new low, A and B are lower, right, but what will happen, RSI will make a higher high, what does this mean, that point B tried to go up by applying more pressure, yet the price could not go above A and that is what we call a negative reverse divergence"),
    "nrd_a2": (A, "where will you see this, you will see it in a downtrend The NRD will be visible within the down trend that is already underway."),
    "nrd_a3": (A, "look at this NRD down trend and after that it made a new low which is a short signal for us"),
    "nrd_a4": (A, "you have to look for where the NRD is found to know that this market is going to go further down."),
    "nrd_g1": (G, "now in an uptrend we were comparing the lows so now in a Downton we are going to compare the highs"),
    "nrd_g2": (G, "but if you compare the highs you get a negative bearish or sorry negative reverse divergence which is bearish"),
    "nrd_g3": (G, "that's why it's called the negative reverse divergence and then market goes and makes a new low"),
    # ---- hidden / aliases
    "hid_a1": (A, "a very powerful and very hidden concept which is called reverse divergence, which many people also call hidden divergence"),
    "hid_a2": (A, "look at this one, the price is going up, A and B are above, ideally we should mark A and B right then, and here A and B are below, that means there is a reverse divergence"),
    "unconv_g": (G, "now people who know the unconventional RSI which is very few people"),
    "naming_g": (G, "whenever you are talking about reverse divergence you are going to say positive reverse divergence and negative reverse divergence"),
    "naming_a": (A, "there is a lot of difference between reverse divergence and divergence and sometimes when you learn both together, when you see the chart, you will get confused"),
    # ---- priority
    "pri_a1": (A, "we have to deal with reverse divergence first. If that fails, then we have to move on to divergence."),
    "pri_a2": (A, "When the PRD fails, I will see a bearish divergence."),
    "pri_a3": (A, "Where there is PRD, there can usually be a low divergence as well. Therefore, when we look at both together, we have to give preference to PRD first."),
    "pri_a4": (A, "Sometimes, like here, there is a divergence as well, the normal one and the PRD as well, so which of the two to trade will depend on your skill, your judgment and your analysis"),
    "pri_a5": (A, "divergence used to fail many times and I could not understand what was happening"),
    # ---- stars / multiples
    "star_a1": (A, "seven star reverse divergence means if all the conditions are matched then it will become seven star"),
    "star_a2": (A, "so there are certain conditions but I think if I give so much together then you will feel like over whelm"),
    "star_g": (G, "created this reverse divergence between a 3 star 5 star and 7 star based on certain more parameters advanced"),
    "star_w1": (W, "but if the monthly is at 60 and there is divergence on the daily, then it becomes a seven star signal"),
    "star_w2": (W, "RSI monthly above 60 and RSI daily below 40 and there is divergence visible, that is one of the best trades"),
    "multi_c": (C, "within a divergence, there can be a single divergence, multiple divergences, one divergence or more than one, and the second one is Class 8, Class B, Class C, dimensions, meaning there are three different types of divergences."),
    "multi_w": (W, "monthly above 60 double divergence triple divergence then goes like a rocket"),
}


def norm(s):
    return " ".join(re.sub(r"[^a-z0-9%]+", " ", s.lower()).split())


def load_raw(vid, hi=False):
    p = RAW / (f"{vid}_hi_raw.txt" if hi else f"{vid}_raw.txt")
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    k = lines.index("# ---") + 1 if "# ---" in lines else 0
    return lines, k


_cache = {}


def locate(vid, text):
    """Return (pos_tag, raw_line_no, timestamp) for a quote."""
    if vid not in _cache:
        lines, k = load_raw(vid)
        parts, offs, o = [], [], 0
        for i in range(k, len(lines)):
            n = norm(re.sub(r"\[\d+:\d{2}(?::\d{2})?\]", " ", lines[i]))
            offs.append((o, i + 1))
            parts.append(n)
            o += len(n) + 1
        _cache[vid] = (" ".join(parts), offs, lines)
    body, offs, lines = _cache[vid]
    at = body.find(norm(text))
    if at < 0:
        return None
    third = ("BEGIN", "MIDDLE", "END")[min(2, 3 * at // max(1, len(body)))]
    ln = max(l for o, l in offs if o <= at)
    ts = ""
    for j in range(ln - 1, 6, -1):
        m = re.match(r"\[(\d+:\d{2}(?::\d{2})?)\]", lines[j])
        if m:
            ts = m.group(1)
            break
    return third, ln, ts


def ext_line(vid, text):
    p = EXT / f"extract_{vid}.md"
    t = norm(text)
    for i, l in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        if l.startswith('> "') and t in norm(l):
            return i
    return None


def block(key):
    vid, text = Q[key]
    loc = locate(vid, text)
    if loc is None:
        print("MISSING QUOTE", key)
        sys.exit(1)
    pos, ln, ts = loc
    if vid == G:
        cite = f"raw_transcripts_canonical/{vid}_raw.txt:{ln} (video {vid} at {ts})"
    else:
        el = ext_line(vid, text)
        cite = f"extract_{vid}.md:{el}" if el else f"raw_transcripts_canonical/{vid}_raw.txt"
        cite += f" (video {vid})"
    return f'> "{text}"\n**Source GPS: {vid} | {pos}**\n- cite: {cite}\n'


def hindi(n):
    ext = (EXT / f"extract_{A}.md").read_text(encoding="utf-8").splitlines()
    line = ext[int(n) - 1]
    m = re.match(r'- Hindi original: "(.+)"\s*$', line)
    if not m:
        print("BAD HINDI LINE", n)
        sys.exit(1)
    txt = m.group(1)
    lines, k = load_raw(A, hi=True)
    body = " ".join(" ".join(lines[k:]).split())
    if " ".join(txt.split()) not in body:
        print("HINDI NOT IN RAW", n)
        sys.exit(1)
    return f'- Hindi original ({A}, extract_{A}.md:{n}, checked against {A}_hi_raw.txt): "{txt}"'


def main():
    src = (M / "tools/GLOSSARY_SRC.md").read_text(encoding="utf-8")
    src = re.sub(r"\{\{hi:(\d+)\}\}", lambda m: hindi(m.group(1)), src)
    src = re.sub(r"\{\{(\w+)\}\}", lambda m: block(m.group(1)), src)
    (M / "MALKAN_DIVERGENCE_GLOSSARY.md").write_text(src, encoding="utf-8", newline="\n")
    print("written", len(src))


main()
