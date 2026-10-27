"""T10 demonstrations D1-D5 on DEV 1m BTCUSDT perp bars (open_time < 2024-07-01 only).
Own loader (not a study loader). Read-only on F:/MTS/data. Seed printed. Run from the worktree root:
  python MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T10/t10_demos.py
Writes scripts/T10/out/demos_run.txt. These are illustrations of effect size, not study results."""
import glob, os, sys
import numpy as np
import pandas as pd

SEED = 20261024
DEV_END_MS = int(pd.Timestamp("2024-07-01", tz="UTC").timestamp() * 1000)
SRC = "F:/MTS/data/tom_raw/klines/BTCUSDT-1m-20*.csv"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "demos_run.txt")
COST = 0.14  # percent round trip, screen.py:30 convention


def load():
    fs = sorted(glob.glob(SRC))
    df = pd.concat([pd.read_csv(f, usecols=range(6)) for f in fs], ignore_index=True)
    df = df[df.open_time < DEV_END_MS].drop_duplicates("open_time").sort_values("open_time").reset_index(drop=True)
    assert df.open_time.max() < DEV_END_MS
    return df


lines = []
def p(*a):
    s = " ".join(str(x) for x in a)
    print(s); lines.append(s)


def breakout_events(df, look=60, hold=30):
    c, h, l, o = (df[k].to_numpy() for k in ("close", "high", "low", "open"))
    hh = pd.Series(h).rolling(look).max().shift(1).to_numpy()
    ll = pd.Series(l).rolling(look).min().shift(1).to_numpy()
    ev, i, n = [], look + 1, len(df)
    while i < n - hold - 3:
        if c[i] > hh[i]:
            ev.append((i, 1)); i += look
        elif c[i] < ll[i]:
            ev.append((i, -1)); i += look
        else:
            i += 1
    return ev


def main():
    df = load()
    o, h, l, c = (df[k].to_numpy() for k in ("open", "high", "low", "close"))
    p(f"seed {SEED}; DEV bars {len(df)}; first {df.open_time.iloc[0]} last {df.open_time.iloc[-1]} (< {DEV_END_MS})")
    # D1 entry-delay
    hold = 30
    ev = breakout_events(df, 60, hold)
    p(f"\nD1 entry timing: 60-bar breakout, hold {hold} bars, n={len(ev)}, gross % per trade (cost {COST} not subtracted)")
    for name, d in (("fill at signal close (same-bar)", None), ("next bar open", 1), ("open +1 bar delay", 2)):
        r = []
        for i, s in ev:
            e_ix = i + (d or 0)          # entry bar index (outcome side, after the signal bar)
            x_ix = e_ix + hold - (1 if d else 0)
            ent = c[i] if d is None else o[e_ix]
            ex = c[x_ix]
            r.append(s * (ex / ent - 1) * 100)
        r = np.array(r)
        p(f"  {name:34s} mean {r.mean():+.4f}%  se {r.std(ddof=1)/np.sqrt(len(r)):.4f}")
    # D2 intrabar ambiguity
    p("\nD2 intrabar order ambiguity: share of 1m bars where a long entered at the bar open could hit BOTH stop and target inside that one bar")
    for s, t in ((0.044, 0.088), (0.10, 0.20), (0.13, 0.26)):
        both = ((l <= o * (1 - s / 100)) & (h >= o * (1 + t / 100))).mean() * 100
        stop = (l <= o * (1 - s / 100)).mean() * 100
        p(f"  stop {s}% target {t}%: both-in-bar {both:.2f}% of bars; stop-reachable-in-bar {stop:.2f}%")
    # D3 family-wise pass rate under a random null
    rng = np.random.default_rng(SEED)
    H, N, REPS = 390, 200, 1000
    fwd = (c[H:] / c[:-H] - 1) * 100  # forward 390-bar return from close i
    p(f"\nD3 multiple arms under a placebo null (random entry, random sign, hold {H} bars, n={N}/arm, {REPS} reps, seed {SEED})")
    for K in (1, 4, 12, 40):
        anyp_g = anyp_n = 0
        for _ in range(REPS):
            pg = pn = False
            for _k in range(K):
                idx = rng.integers(0, len(fwd), N)
                r = fwd[idx] * rng.choice([-1, 1], N)
                m, se = r.mean(), r.std(ddof=1) / np.sqrt(N)
                if m >= COST and m / se >= 2: pg = True          # gross mean >= 0.14 and t_gross >= 2
                if (m - COST) / se >= 2: pn = True               # t_net >= 2
            anyp_g += pg; anyp_n += pn
        p(f"  K={K:2d} arms: P(any arm passes gross>=0.14 & t_gross>=2) = {anyp_g/REPS*100:.1f}%;  P(any arm t_net>=2) = {anyp_n/REPS*100:.2f}%")
    # D4 regime drift
    yr = pd.to_datetime(df.open_time, unit="ms", utc=True).dt.year.to_numpy()[:-H]
    p("\nD4 regime drift: mean 390-bar forward return (long-only, %) per calendar year, and a 70/30 long/short random-sign arm")
    for y in sorted(set(yr)):
        m = fwd[yr == y]
        p(f"  {y}: long-only mean {m.mean():+.4f}%  70/30 arm expected {(0.7-0.3)*m.mean():+.4f}%  (pass bar needs +0.14)")
    p(f"  all DEV: long-only mean {fwd.mean():+.4f}%  70/30 arm {0.4*fwd.mean():+.4f}%")
    # D5 vol-scaled slippage
    rng_bps = (h - l) / o * 1e4
    ent_rng = np.take(rng_bps, np.array([i for i, _ in ev]) + 1)
    flat_bps = 2.0
    p(f"\nD5 flat 2 bp slippage vs entry-bar range, breakout entries n={len(ev)}")
    p(f"  all-bars median 1m range {np.median(rng_bps):.1f} bp; entry-bar median {np.median(ent_rng):.1f} bp, mean {ent_rng.mean():.1f} bp")
    ex_cost = 0.10 * ent_rng.mean() / 100 * 2  # slip = 10% of bar range per fill, % round trip
    p(f"  slippage = 10% of entry-bar range per fill => {0.10*ent_rng.mean():.2f} bp per fill vs flat {flat_bps} bp; round-trip extra {(0.10*ent_rng.mean()-flat_bps)*2/100:+.4f}% on top of the 0.14%")
    p(f"  share of entries whose bar range exceeds the whole 14 bp round-trip cost: {(ent_rng>14).mean()*100:.1f}% (all bars {(rng_bps>14).mean()*100:.1f}%)")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
