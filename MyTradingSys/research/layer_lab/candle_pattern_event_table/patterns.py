"""Causal candle pattern predicates. Definitions: PRE_REG_CANDLE_PILOT.md:41-56."""
def _bar(b):
    o,h,l,c=(float(b[k]) for k in ('o','h','l','c'))
    return o,h,l,c,abs(c-o),h-l
def engulfing(bars, i):
    if i<1:return 0
    po,ph,pl,pc,pbody,pr=_bar(bars[i-1]); o,h,l,c,body,rng=_bar(bars[i])
    if min(pr,rng)<=0:return 0
    if pc<po and c>o and o<=pc and c>=po and body>pbody:return 1
    if pc>po and c<o and o>=pc and c<=po and body>pbody:return -1
    return 0
def pin_bar(bars, i):
    o,h,l,c,body,rng=_bar(bars[i])
    if rng<=0 or body<=0:return 0
    upper=h-max(o,c); lower=min(o,c)-l
    if lower>=2*body and upper<=.1*rng:return 1
    if upper>=2*body and lower<=.1*rng:return -1
    return 0
def inside_bar(bars, i):
    if i<1:return 0
    _,h,l,_,_,rng=_bar(bars[i]); _,ph,pl,_,_,pr=_bar(bars[i-1])
    return int(rng>0 and pr>0 and h<=ph and l>=pl)
def doji(bars, i):
    _,h,l,_,body,rng=_bar(bars[i])
    return int(rng>0 and body<=.1*rng)
DETECTORS={'engulfing':engulfing,'pin_bar':pin_bar,'inside_bar':inside_bar,'doji':doji}
