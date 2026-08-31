#!/bin/bash
# Full pipeline, in dependency order. Run this, not the individual steps.
#
#   extract      prototypes -> content/*.json (services, products, team, process)
#   resolve      fill in images the prototype bundle referenced but never shipped
#   download     pull those images local, rewrite JSON to local paths
#   build        render site/*.html + site/blog/*.html
#
# The blog is refreshed separately because it hits the live site 37+ times:
#   ./tools/build_all.sh --with-blog     also re-import every post
#   python3 tools/verify_posts.py        check imports against the live pages
set -e
cd "$(dirname "$0")/.."

if [ "$1" = "--with-blog" ]; then
  python3 tools/fetch_posts.py
  python3 tools/clean_posts.py
fi

python3 tools/extract.py
python3 tools/resolve_images.py
python3 tools/download_images.py | tail -6
python3 tools/build.py
