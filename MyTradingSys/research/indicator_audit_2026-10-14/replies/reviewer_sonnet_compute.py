import json, glob, math, os
D = os.path.dirname(os.path.abspath(__file__))

def bb(c, n=20, m=2.0):
    if len(c) < n: return None
    w = c[-n:]
    mid = sum(w) / n
    sd = math.sqrt(sum((x - mid) ** 2 for x in w) / n)
    return {'BB_mid': mid, 'BB_up': mid + m * sd, 'BB_low': mid - m * sd}

def rsi_series(c, p):
    out = [None] * len(c)
    if len(c) <= p: return out
    d = [c[i] - c[i - 1] for i in range(1, len(c))]  # d[i-1] is delta at index i
    g = [max(x, 0) for x in d]; l = [max(-x, 0) for x in d]
    ag = sum(g[:p]) / p; al = sum(l[:p]) / p
    def val(ag, al):
        if al == 0: return 100.0 if ag > 0 else 50.0
        return 100 - 100 / (1 + ag / al)
    out[p] = val(ag, al)
    for i in range(p + 1, len(c)):
        ag = (ag * (p - 1) + g[i - 1]) / p
        al = (al * (p - 1) + l[i - 1]) / p
        out[i] = val(ag, al)
    return out

def sma_series(s, n):
    out = [None] * len(s)
    for i in range(len(s)):
        if i - n + 1 >= 0:
            w = s[i - n + 1:i + 1]
            if all(x is not None for x in w):
                out[i] = sum(w) / n
    return out

def stochrsi(c, rl=14, sl=14, kl=3, dl=3):
    r = rsi_series(c, rl)
    raw = [None] * len(c)
    for i in range(len(c)):
        if i - sl + 1 < 0: continue
        w = r[i - sl + 1:i + 1]
        if any(x is None for x in w): continue
        hi, lo = max(w), min(w)
        raw[i] = 0.0 if hi == lo else 100 * (r[i] - lo) / (hi - lo)
    k = sma_series(raw, kl); dd = sma_series(k, dl)
    return k[-1], dd[-1]

# worked-example checks
b = bb([8, 10, 10, 12, 14, 12], 4, 2)
assert abs(b['BB_up'] - 14.828427) < 1e-6 and abs(b['BB_low'] - 9.171573) < 1e-6
assert abs(rsi_series([10, 12, 11, 14], 3)[3] - 83.3333333) < 1e-6
r = rsi_series([10, 11, 10, 12, 11, 13], 2)
assert abs(r[2] - 50) < 1e-9 and abs(r[3] - 83.33333333) < 1e-6 and abs(r[4] - 50) < 1e-9 and abs(r[5] - 80.76923077) < 1e-6
k, _ = stochrsi([10, 11, 10, 12, 11, 13], 2, 3, 2, 1)
assert abs(k - 46.15385) < 1e-4, k
k, _ = stochrsi([10, 11, 10, 12, 11, 13], 2, 3, 1, 1)
assert abs(k - 92.30769) < 1e-4, k
print('worked examples OK')

res = {}
for f in sorted(glob.glob(os.path.join(D, 'blind_packets', '*.json'))):
    p = json.load(open(f, encoding='utf-8'))
    c = p['closes']; assert len(c) == 500
    ind = p['indicator']
    if ind == 'BB': res[p['id']] = bb(c)
    elif ind == 'RSI': res[p['id']] = {'RSI': rsi_series(c, 14)[-1]}
    elif ind == 'STOCHRSI':
        k, d = stochrsi(c); res[p['id']] = {'StochRSI_K': k, 'StochRSI_D': d}
    assert set(res[p['id']]) == set(p['answer_keys'])
json.dump(res, open(os.path.join(D, 'replies_sonnet.json'), 'w'), indent=1)
print(len(res), 'packets written')
