"""Pull every blog post from the live Squarespace site into content/posts.json.

The site will eventually replace balancehomeorganizing.com, so the posts have to
live here rather than linking back. Squarespace's own JSON API is the
authoritative list — the design prototypes only ever showed 37 tiles.
"""
import html, json, os, re, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "content")
BASE = "https://balancehomeorganizing.com/tips"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode("utf-8", "replace"))

def text_of(h):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h or ""))).strip()

def get_html(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", "replace")

DIV = re.compile(r"<(/?)div\b", re.I)

def balanced_div(src, anchor):
    """The full <div>...</div> containing `anchor`, matching nesting properly."""
    i = src.find(anchor)
    if i < 0:
        return None
    start = src.rfind("<div", 0, i)
    depth, j = 0, start
    while j < len(src):
        m = DIV.search(src, j)
        if not m:
            break
        depth += -1 if m.group(1) else 1
        j = m.end()
        if depth == 0:
            k = src.find(">", j)
            return src[start:k + 1]
    return None

def article_html(page_url):
    """Scrape the rendered post body.

    The JSON API's `body` field is NOT complete — Squarespace product and summary
    blocks live outside it, so some posts lose most of their content (one dropped
    from 508 words to 78). The rendered page is the only complete source.
    """
    try:
        page = get_html(page_url)
    except Exception as e:
        print(f"  ! {page_url}: {e}", file=sys.stderr)
        return None
    for anchor in ('data-layout-label="Post Body"', 'class="blog-item-content-wrapper"'):
        frag = balanced_div(page, anchor)
        if frag and len(frag) > 500:
            return frag
    return None

items, url, seen, page = [], BASE + "?format=json", set(), 0
while url:
    d = get(url)
    page += 1
    batch = d.get("items", [])
    new = 0
    for it in batch:
        if it["id"] in seen:
            continue
        seen.add(it["id"])
        items.append(it)
        new += 1
    print(f"  page {page}: {len(batch)} items ({new} new), total {len(items)}")
    pg = d.get("pagination") or {}
    nxt = pg.get("nextPageUrl") if pg.get("nextPage") else None
    if not nxt or new == 0:
        break
    url = "https://balancehomeorganizing.com" + nxt + ("&" if "?" in nxt else "?") + "format=json"
    time.sleep(0.5)

posts = []
print("\nscraping rendered bodies (the API body field is incomplete):")
for n, it in enumerate(items, 1):
    full = "https://balancehomeorganizing.com" + (it.get("fullUrl") or "")
    scraped = article_html(full)
    body = scraped or it.get("body") or ""
    src = "page" if scraped else "api-fallback"
    print(f"  [{n:>2}/{len(items)}] {src:<12} {text_of(it.get('title'))[:52]}")
    time.sleep(0.35)
    posts.append({
        "id": it["id"],
        "title": text_of(it.get("title")),
        "slug": it.get("urlId"),
        "published_ms": it.get("publishOn"),
        "author": (it.get("author") or {}).get("displayName", ""),
        "excerpt": text_of(it.get("excerpt"))[:400],
        "tags": it.get("tags") or [],
        "categories": it.get("categories") or [],
        "live_url": "https://balancehomeorganizing.com" + (it.get("fullUrl") or ""),
        "thumb": (it.get("assetUrl") or None),
        "body_html": body,
        "body_chars": len(body),
        "body_source": src,
    })

posts.sort(key=lambda p: p["published_ms"] or 0, reverse=True)
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "posts.json"), "w", encoding="utf-8") as f:
    json.dump(posts, f, indent=2, ensure_ascii=False)

print(f"\n{len(posts)} posts written to content/posts.json")
print(f"  scraped from page : {sum(1 for p in posts if p['body_source'] == 'page')}")
print(f"  api fallback      : {sum(1 for p in posts if p['body_source'] != 'page')}")
print(f"  with thumbnail    : {sum(1 for p in posts if p['thumb'])}")
