#!/bin/bash
# Screenshot a URL with headless Chrome.
#   tools/shot.sh <url> <out.png> [width] [height]
#
# Node/Puppeteer are not installed on this machine; Chrome's own headless mode
# does the job with no dependencies.
#
# NOTE: --window-size does NOT emulate a mobile viewport. To check a page at a
# real phone width, load it through tools/frame.html instead:
#   cp tools/frame.html site/_frame.html
#   tools/shot.sh "http://localhost:3000/_frame.html?p=index.html" out.png 420 2200
#   rm site/_frame.html
set -e
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$CHROME" ] || { echo "Chrome not found at $CHROME" >&2; exit 1; }
URL="$1"; OUT="$2"; W="${3:-1440}"; H="${4:-1600}"
[ -n "$URL" ] && [ -n "$OUT" ] || { echo "usage: tools/shot.sh <url> <out.png> [w] [h]" >&2; exit 1; }
mkdir -p "$(dirname "$OUT")"
"$CHROME" --headless --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
  --virtual-time-budget=6000 --window-size="$W,$H" --screenshot="$OUT" "$URL" >/dev/null 2>&1
echo "$OUT ($(du -h "$OUT" | cut -f1))"
