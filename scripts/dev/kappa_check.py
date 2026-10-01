"""kappa_check.py - Cohen's kappa for two readers' nominal labels.

usage: python scripts/dev/kappa_check.py first.csv second.csv [--threshold 0.6]
       python scripts/dev/kappa_check.py --selftest
Each CSV has lines `id,label` (a header line `id,verdict` is skipped). Ids must match.
Prints observed agreement, kappa, the label confusion table and every disagreeing id. Exit 0 if kappa >= threshold, else 1.
"""
import csv
import sys
from collections import Counter


def read(path):
    out = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.reader(f):
            if len(row) < 2 or row[0].strip().lower() == "id":
                continue
            out[row[0].strip()] = row[1].strip()
    return out


def kappa(a, b):
    """a, b: equal-length label lists. Returns (observed, expected, kappa)."""
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return po, pe, (1.0 if pe == 1 else (po - pe) / (1 - pe))


def selftest():
    # 2x2 textbook case: 20 yes/yes, 5 yes/no, 10 no/yes, 15 no/no -> po 0.7, pe 0.5, kappa 0.4
    a = ["y"] * 25 + ["n"] * 25
    b = ["y"] * 20 + ["n"] * 5 + ["y"] * 10 + ["n"] * 15
    po, pe, k = kappa(a, b)
    assert abs(po - 0.7) < 1e-9 and abs(pe - 0.5) < 1e-9 and abs(k - 0.4) < 1e-9, (po, pe, k)
    assert kappa(["a", "b"], ["a", "b"])[2] == 1.0
    print("selftest PASS")


def main(argv):
    if "--selftest" in argv:
        selftest()
        return 0
    thr = 0.6
    if "--threshold" in argv:
        i = argv.index("--threshold")
        thr = float(argv[i + 1])
        del argv[i:i + 2]
    first, second = read(argv[1]), read(argv[2])
    if set(first) != set(second):
        print("id sets differ: only in first", sorted(set(first) - set(second)), "only in second", sorted(set(second) - set(first)))
        return 2
    ids = sorted(first)
    a, b = [first[i] for i in ids], [second[i] for i in ids]
    po, pe, k = kappa(a, b)
    print(f"n={len(ids)} observed={po:.3f} expected={pe:.3f} kappa={k:.3f} threshold={thr}")
    conf = Counter(zip(a, b))
    for (x, y), c in sorted(conf.items()):
        print(f"  first={x} second={y}: {c}")
    for i, x, y in zip(ids, a, b):
        if x != y:
            print(f"DISAGREE {i}: first={x} second={y}")
    return 0 if k >= thr else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
