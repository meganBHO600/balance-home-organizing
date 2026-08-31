"""Resolve every image reference in content/*.json to a real, downloadable URL.

The prototype bundle references 33 local asset files but ships only 2, so any
record pointing at a missing assets/*.jpg (or at no image at all) is resolved by
fetching its own live page on balancehomeorganizing.com and reading the og:image.
"""
import json, os, re, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")
BUNDLE = os.path.join(ROOT, "design_handoff_balance_home_organizing", "assets")
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
OG = re.compile(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', re.I)
OG2 = re.compile(r'<meta[^>]+content="([^"]+)"[^>]+property="og:image"', re.I)

cache_path = os.path.join(CONTENT, "_og_cache.json")
cache = json.load(open(cache_path)) if os.path.exists(cache_path) else {}

def og_image(page_url):
    if page_url in cache:
        return cache[page_url]
    try:
        req = urllib.request.Request(page_url, headers=UA)
        with urllib.request.urlopen(req, timeout=25) as r:
            body = r.read().decode("utf-8", "replace")
        m = OG.search(body) or OG2.search(body)
        found = m.group(1) if m else None
    except Exception as e:
        print(f"  ! {page_url} -> {e}", file=sys.stderr)
        found = None
    cache[page_url] = found
    json.dump(cache, open(cache_path, "w"), indent=2)
    time.sleep(0.4)
    return found

def bundled(path):
    return path and path.startswith("assets/") and \
        os.path.exists(os.path.join(BUNDLE, os.path.basename(path)))

def needs_resolution(img):
    return img is None or (img.startswith("assets/") and not bundled(img))

changed = 0
for fname in ("services.json", "products.json"):
    path = os.path.join(CONTENT, fname)
    records = json.load(open(path))
    for rec in records:
        if not needs_resolution(rec.get("image")):
            continue
        url = og_image(rec["href"])
        rec["missing_source"] = rec.get("image")
        rec["image"] = url
        rec["resolved_from_live_site"] = bool(url)
        changed += 1
        print(f"{'ok ' if url else 'FAIL'} {rec['title'][:52]:<54} {url or ''}")
    json.dump(records, open(path, "w"), indent=2, ensure_ascii=False)
print(f"\nresolved {changed} records")
