#!/bin/bash
# Rebuild the renderable reference harness from the .dc.html prototypes and
# serve it on :3001, so the build can be screenshot-diffed against it.
#
# The prototypes ship broken — they load a design-system stylesheet and a
# support.js that are not in the bundle, and 33 local images that are missing.
# This substitutes site/assets/css/styles.css for the former and the resolved
# images for the latter.
set -e
cd "$(dirname "$0")/.."
REF="${1:-.refsite}"
python3 - "$REF" <<'PY'
import json,os,re,shutil,sys
ref=sys.argv[1]; pages="design_handoff_balance_home_organizing/pages"
shutil.rmtree(ref,ignore_errors=True); os.makedirs(os.path.join(ref,"assets"),exist_ok=True)
mapping={}
for f in ("posts_recent.json","posts_older.json","services.json","products.json"):
    for r in json.load(open("content/"+f)):
        if r.get("missing_source") and r.get("local_image"):
            mapping[os.path.basename(r["missing_source"])]=r["local_image"]
mapping["products-hero-shelf.jpg"]=json.load(open("content/images.json"))["products-hero"]
for name,local in mapping.items():
    shutil.copy2(os.path.join("site",local), os.path.join(ref,"assets",name))
for f in ("logo.png","hiring-flyer.jpg"):
    shutil.copy2(os.path.join("design_handoff_balance_home_organizing/assets",f), os.path.join(ref,"assets",f))
for f in ("instagram.svg","yelp.svg","google.svg"):
    shutil.copy2(os.path.join("site/assets/icons",f), os.path.join(ref,"assets",f))
shutil.copy2("site/assets/css/styles.css", os.path.join(ref,"ds.css"))
for f in os.listdir(pages):
    if not f.endswith(".dc.html"): continue
    s=open(os.path.join(pages,f),encoding="utf-8").read()
    s=s.replace('<script src="./support.js"></script>','')
    s=re.sub(r'<link rel="stylesheet" href="_ds/[^"]+">','<link rel="stylesheet" href="ds.css">',s)
    s=re.sub(r'<script src="_ds/[^"]+"></script>','',s)
    open(os.path.join(ref,f),"w",encoding="utf-8").write(s)
print(f"reference harness: {ref} ({len(mapping)} images remapped)")
PY
cd "$REF" && echo "serving reference on http://localhost:3001" && python3 -m http.server 3001
