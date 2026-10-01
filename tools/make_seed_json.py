"""Build src/seed-posts.json — the 37 imported posts, trimmed to what D1 needs.

Loaded once by the Worker's /api/admin/seed endpoint. D1's dashboard console
can't take a 194KB SQL file, and there's no CLI on this machine.
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
posts = json.load(open(os.path.join(ROOT, "content", "posts.json"), encoding="utf-8"))

def term_slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-") or "untagged"

out = []
for p in posts:
    out.append({
        "slug": p["slug"],
        "title": p["title"],
        "excerpt": (p.get("excerpt") or "")[:400],
        "body_html": p.get("body_clean", "").replace("%ROOT%", "../"),
        "thumb": p.get("local_thumb"),
        "author": p.get("author") or "Megan Mossuto",
        "published_at": p.get("published_ms"),
        "terms": (
            [{"kind": "category", "name": c, "slug": term_slug(c)} for c in (p.get("categories") or [])] +
            [{"kind": "tag", "name": t, "slug": term_slug(t)} for t in (p.get("tags") or [])]
        ),
    })

dest = os.path.join(ROOT, "src", "seed-posts.json")
json.dump(out, open(dest, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(f"{len(out)} posts -> src/seed-posts.json ({os.path.getsize(dest):,} bytes)")
