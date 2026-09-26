"""Step 6: make each model's index.htm read the "main" frame's initial page
from the URL hash, so a full browser refresh restores whatever diagram was
open (see assets/navtree.js, which sets `top.location.hash = "main=" +
encodeURIComponent(link)` on every tree click, and restores the tree's
expand/highlight state from that same hash on load).

index.htm builds its frameset via document.write() from a JS string, always
hardcoding the "main" frame's src to "main.htm". This inserts a small
snippet that computes a `mainSrc` variable from location.hash instead, and
splices it into both places that hardcode 'main.htm' (the IE branch and the
else branch - only the else branch actually runs in any modern browser, but
both are kept consistent).

The hash value is validated against a strict relative-path charset before
use: it's spliced directly into a document.write()-built HTML string, so an
unsanitized value (e.g. containing a quote, or a javascript:/data: scheme)
could break out of the intended attribute/string context. A charset with no
":" already blocks scheme-based values; a separate check blocks
protocol-relative "//host/..." values, which the charset alone would allow.
"""
import re

HTM_CODE_DECL_RE = re.compile(r'(\n[ \t]*var htm_code = "";)')
MAIN_SRC_LITERAL = "src='main.htm'"
MAIN_SRC_SPLICED = "src='\"+mainSrc+\"'"

MAIN_SRC_SNIPPET = '''
	var mainSrc = "main.htm";
	(function () {
		var m = /(?:^|[#&])main=([^&]*)/.exec(location.hash);
		if (!m) return;
		var val;
		try { val = decodeURIComponent(m[1]); } catch (e) { return; }
		if (!/^[A-Za-z0-9_\\-.\\/%]+$/.test(val)) return;
		if (val.indexOf("//") === 0) return;
		mainSrc = val;
	})();'''


def process(index_path, dry_run=False):
	with open(index_path, "rb") as f:
		text = f.read().decode("utf-8")

	if "mainSrc" in text:
		return "already fixed"

	if MAIN_SRC_LITERAL not in text:
		return "unexpected structure, skipped"

	new_text, n = HTM_CODE_DECL_RE.subn(MAIN_SRC_SNIPPET + r"\1", text, count=1)
	if n != 1:
		return "unexpected structure, skipped"

	new_text = new_text.replace(MAIN_SRC_LITERAL, MAIN_SRC_SPLICED)

	if not dry_run:
		with open(index_path, "wb") as f:
			f.write(new_text.encode("utf-8"))

	return "would fix" if dry_run else "fixed"


if __name__ == "__main__":
	import sys
	print(process(sys.argv[1]))
