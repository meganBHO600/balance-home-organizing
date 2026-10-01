#!/bin/bash
# Syntax-check Worker JS without Node, using JavaScriptCore via osascript.
#
# ES module syntax (import/export) is stripped first, since JXA parses scripts
# rather than modules. Catches real syntax errors; does not type-check.
#
#   tools/jscheck.sh src/*.js
set -u
fail=0
for f in "$@"; do
  out=$(osascript -l JavaScript <<EOF 2>&1
ObjC.import('Foundation');
var p = '$f';
var s = \$.NSString.stringWithContentsOfFileEncodingError(p, \$.NSUTF8StringEncoding, null).js;
// strip module syntax so this parses as a plain script
s = s.replace(/^\s*import\s+[^;]+;?\s*\$/gm, '');
s = s.replace(/^\s*export\s+default\s+/gm, 'var __d = ');
s = s.replace(/^\s*export\s+/gm, '');
try { new Function(s); 'OK'; }
catch (e) { 'ERR: ' + e.message; }
EOF
)
  if [ "$out" = "OK" ]; then
    printf "  ok    %s\n" "$f"
  else
    printf "  FAIL  %s\n        %s\n" "$f" "$out"
    fail=1
  fi
done
exit $fail
