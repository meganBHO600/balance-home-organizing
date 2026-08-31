"""Compare each imported post against the live page it came from.

Guards against silent content loss in the HTML cleaning step: fetches the live
post, measures the plain text of its body container, and compares that to the
word count of what we imported.
"""
import html, json, os, re, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
posts = json.load(open(os.path.join(ROOT, "content", "posts.json"), encoding="utf-8"))
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
DIV = re.compile(r"<(/?)div\b", re.I)

def balanced_div(s, anchor):
    i = s.find(anchor)
    if i < 0: return None
    start = s.rfind("<div", 0, i); depth, j = 0, start
    while j < len(s):
        m = DIV.search(s, j)
        if not m: break
        depth += -1 if m.group(1) else 1; j = m.end()
        if depth == 0:
            return s[start:s.find(">", j) + 1]
    return None

def words(frag):
    frag = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", frag or "", flags=re.S)
    return len(re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", frag))).split())

bad = []
for n, p in enumerate(posts, 1):
    try:
        req = urllib.request.Request(p["live_url"], headers=UA)
        with urllib.request.urlopen(req, timeout=40) as r:
            page = r.read().decode("utf-8", "replace")
    except Exception as e:
        print(f"  ! {p['title'][:45]}: {e}"); bad.append((p["title"], "fetch failed")); continue
    live = words(balanced_div(page, 'data-layout-label="Post Body"'))
    mine = p["words"]
    pct = (mine / live * 100) if live else 100
    flag = "" if pct >= 92 else "  <-- SHORT"
    if pct < 92: bad.append((p["title"], f"{mine}/{live} words ({pct:.0f}%)"))
    print(f"  [{n:>2}/37] live {live:>5}  mine {mine:>5}  {pct:>5.0f}%  {p['title'][:44]}{flag}")
    time.sleep(0.3)

print()
if bad:
    print(f"{len(bad)} post(s) may be missing content:")
    for t, why in bad: print(f"  - {t}: {why}")
    sys.exit(1)
print(f"all {len(posts)} posts match the live pages (>=92% of body text)")
