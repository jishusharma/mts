"""Count the labels and NOT FOUND cells of the rule table in drafts/MAL-BB-RSI-4060.md (section 2). Usage: python count_rule_table.py <draft.md>"""
import re, sys, collections
t = open(sys.argv[1], encoding="utf-8").read()
sec = t.split("## 2. Rule table", 1)[1].split("Q1-Q7 quotes", 1)[0]
rows = [l for l in sec.splitlines() if re.match(r"\|\s*\d+\s*\|", l)]
lab = collections.Counter(); nf = []; web = []
for l in rows:
    c = [x.strip() for x in l.strip().strip("|").split("|")]
    n, mal, label = c[0], c[2], c[3]
    k = "SOURCED" if label.startswith("SOURCED") else "OPERATOR" if label.startswith("OPERATOR") else "OURS" if label.startswith("OURS") else "?"
    lab[k] += 1
    if "NOT FOUND" in mal: nf.append(n)
    if "SOURCED-WEB" in label: web.append(n)
print("rows", len(rows), dict(lab), "NOT FOUND cells", len(nf), nf, "rows with a SOURCED-WEB sentence", web)
