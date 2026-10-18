"""VTT (YouTube rolling captions) -> '[HH:MM:SS] text' lines, de-duplicated. Usage: vtt_to_timed.py in.vtt out.txt header..."""
import re, sys
src, dst = sys.argv[1], sys.argv[2]
hdr = sys.argv[3:]
out, last = [], ""
cur = None
for line in open(src, encoding="utf-8"):
    line = line.rstrip("\n")
    m = re.match(r"(\d+):(\d\d):(\d\d)\.\d+ --> ", line)
    if m:
        cur = "%02d:%s:%s" % (int(m.group(1)), m.group(2), m.group(3)); continue
    if not line.strip() or line.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")) or cur is None:
        continue
    t = re.sub(r"<[^>]+>", "", line).strip()
    if t and t != last:
        out.append("[%s] %s" % (cur, t)); last = t
with open(dst, "w", encoding="utf-8", newline="\n") as f:
    for h in hdr: f.write("# " + h + "\n")
    f.write("# ---\n" + "\n".join(out) + "\n")
print(dst, len(out))
