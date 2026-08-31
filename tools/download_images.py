"""Download every referenced image into site/assets/img/ and rewrite the content
JSON to point at the local copies, so the built site has no external image hosts.

Page-level imagery (heroes, section photos, CTA band) is listed in PAGE_IMAGES;
list/grid imagery comes from content/*.json.
"""
import hashlib, json, os, re, shutil, sys, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")
BUNDLE = os.path.join(ROOT, "design_handoff_balance_home_organizing", "assets")
IMGDIR = os.path.join(ROOT, "site", "assets", "img")
CDN = "https://images.squarespace-cdn.com/content/v1/61ef194b95c76364803c6431/"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

PAGE_IMAGES = {
    "home-hero":        CDN + "cb7a27f1-6b2a-4026-bcae-c296a8e185d5/BalanceHomeOrganizing-Main.jpg",
    "home-help":        CDN + "d56aca52-4260-4f16-b29a-7814b8000a9c/Balance+Home+Living+Room.jpg",
    "cta-jars":         CDN + "1648545928349-YXX0JXK6S0VAG6OO7GSW/balance-home-organizing-jars.png",
    "process-hero":     CDN + "1645026285522-6HSDS7CBCUQMES6M1ZYU/unsplash-image-nvzvOPQW0gc.jpg",
    "about-founder":    CDN + "6ac275d5-b8e8-4653-8c2e-fe5eb2626a40/Megan-Massuto.jpg",
    "products-hero":    CDN + "b22471b2-6767-4a6c-ab0d-083be9f60a6c/Shelves+-+Balance+Home+Organizing.jpg",
    "favicon":          CDN + "ccd4f012-ab05-41cb-92f1-6fbeafe0dcf4/favicon.ico",
}

os.makedirs(IMGDIR, exist_ok=True)
manifest_path = os.path.join(CONTENT, "images.json")
manifest = json.load(open(manifest_path)) if os.path.exists(manifest_path) else {}

def slug(s, maxlen=48):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:maxlen].strip("-")

def ext_of(url):
    path = urllib.parse.urlparse(url).path
    e = os.path.splitext(path)[1].lower()
    return e if e in (".jpg", ".jpeg", ".png", ".webp", ".gif", ".ico") else ".jpg"

def fetch(url, dest_name):
    dest = os.path.join(IMGDIR, dest_name)
    if os.path.exists(dest) and os.path.getsize(dest) > 1024:
        return dest_name
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=45) as r:
            data = r.read()
        if len(data) < 512:
            raise ValueError(f"suspiciously small ({len(data)} bytes)")
        with open(dest, "wb") as f:
            f.write(data)
        time.sleep(0.15)
        return dest_name
    except Exception as e:
        print(f"  ! FAILED {dest_name}: {e}", file=sys.stderr)
        return None

failures = []

# 1. page-level imagery
for name, url in PAGE_IMAGES.items():
    got = fetch(url, name + ext_of(url))
    if got:
        manifest[name] = "assets/img/" + got
        print(f"ok  {name:<18} {got}")
    else:
        failures.append(name)

# 2. bundled assets ship as-is
for f in ("logo.png", "hiring-flyer.jpg"):
    src = os.path.join(BUNDLE, f)
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(IMGDIR, f))
        manifest[os.path.splitext(f)[0]] = "assets/img/" + f
        print(f"ok  {'bundled':<18} {f}")

# 3. list/grid imagery from the content JSON
for fname, prefix in (("services.json", "service"), ("products.json", "product"),
                      ("team.json", "team"), ("process.json", "step"),
                      ("process_home.json", "step")):
    path = os.path.join(CONTENT, fname)
    records = json.load(open(path))
    for i, rec in enumerate(records):
        url = rec.get("image")
        if not url:
            rec["local_image"] = None
            failures.append(f"{fname}#{i} {rec.get('title') or rec.get('name')}")
            continue
        if url.startswith("//"):
            url = "https:" + url
        label = rec.get("title") or rec.get("name") or f"{i}"
        name = f"{prefix}-{slug(label)}{ext_of(url)}"
        got = fetch(url, name)
        if got:
            rec["local_image"] = "assets/img/" + got
        else:
            rec["local_image"] = None
            failures.append(f"{fname}#{i} {label}")
    json.dump(records, open(path, "w"), indent=2, ensure_ascii=False)
    print(f"--- {fname}: {sum(1 for r in records if r.get('local_image'))}/{len(records)} images local")

json.dump(manifest, open(manifest_path, "w"), indent=2)
print(f"\n{len(os.listdir(IMGDIR))} files in site/assets/img")
if failures:
    print("UNRESOLVED:", *failures, sep="\n  ")
