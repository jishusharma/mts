"""Rewrite the `split` column of bigtrade fire CSVs from fires_kline.split_of(t_fire_ms) (repo split map).
Backs up each original first, then rewrites in place. Only the split column changes. Data stays on F: (never commit)."""
import csv, os, shutil, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fires_kline as fk

DEFAULT_DIRS = ("F:/MTS/data/bigtrade/fires", "F:/MTS/data/bigtrade/fires_spot")
BACKUP_ROOT = "F:/MTS/data/bigtrade/fires_presplit_backup_2026-10-17"


def relabel_file(path, backup_dir):
    """Returns (before_counts, after_counts, n_rows). Idempotent; backup is never overwritten."""
    os.makedirs(backup_dir, exist_ok=True)
    bk = os.path.join(backup_dir, os.path.basename(path))
    if not os.path.exists(bk):
        shutil.copy2(path, bk)
    before, after = collections.Counter(), collections.Counter()
    out = path + ".tmp"
    n = 0
    with open(path, newline="", encoding="utf-8") as f, open(out, "w", newline="", encoding="utf-8") as g:
        r = csv.reader(f)
        w = csv.writer(g, lineterminator="\n")
        hdr = next(r)
        w.writerow(hdr)
        i_t, i_s = hdr.index("t_fire_ms"), hdr.index("split")
        for row in r:
            before[row[i_s]] += 1
            row[i_s] = fk.split_of(int(row[i_t]))
            after[row[i_s]] += 1
            n += 1
            w.writerow(row)
    os.replace(out, path)
    return before, after, n


def main(dirs=DEFAULT_DIRS):
    tot_b, tot_a = collections.Counter(), collections.Counter()
    for d in dirs:
        sub = os.path.join(BACKUP_ROOT, os.path.basename(d))
        for fn in sorted(os.listdir(d)):
            if not (fn.startswith("fires_") and fn.endswith(".csv")):
                continue
            b, a, n = relabel_file(os.path.join(d, fn), sub)
            assert sum(b.values()) == sum(a.values()) == n
            tot_b.update(b); tot_a.update(a)
            print(os.path.basename(d), fn, n, dict(b), "->", dict(a))
    print("TOTAL before", dict(tot_b), "after", dict(tot_a))


if __name__ == "__main__":
    main()
