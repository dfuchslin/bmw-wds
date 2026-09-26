"""Step 5: fix release/<lang>/scripts/tree.js so javascript:locateTree(...)
links inside SVG diagrams actually work.

Diagrams are shown via <embed type="image/svg+xml">. Old IE + Adobe SVG
Viewer ran a clicked javascript: URI in the host page's script context, but
a modern browser's <embed> is a real nested browsing context with its own
window - tree.js (loaded only by the wrapper .htm) is never loaded into that
scope, so locateTree() is undefined there and the click silently no-ops.

Fix: bridge locateTree onto the embedded SVG document's own window from
inside showButton() (already fires on every wrapper page's <body
onload="showButton()">, and already retrieves the SVG document via
getSVGDocument() for the font-size/family hack). Because locateTree keeps
its original closure over `parent` (the wrapper page's window) when assigned
as a property of a different window, it still resolves
parent.navi.document.stree.expand(...) correctly however it's invoked.
"""
import re

ANCHOR_RE = re.compile(
	r'(var svgimg ?= ?parent\.main\.document\.embeds\[0\]\.getSVGDocument\(\);\r?\n)'
)
BRIDGE_MARKER = "svgimg.defaultView.locateTree"


def process(tree_js_path, dry_run=False):
	with open(tree_js_path, "rb") as f:
		text = f.read().decode("utf-8")

	if BRIDGE_MARKER in text:
		return "already fixed"

	eol = "\r\n" if "\r\n" in text[:2000] else "\n"
	bridge_lines = (
		"\tif (svgimg && svgimg.defaultView) {" + eol +
		"\t\tsvgimg.defaultView.locateTree = locateTree;" + eol +
		"\t}" + eol
	)

	new_text, n = ANCHOR_RE.subn(lambda m: m.group(1) + bridge_lines, text, count=1)
	if n != 1:
		return "unexpected structure, skipped"

	if not dry_run:
		with open(tree_js_path, "wb") as f:
			f.write(new_text.encode("utf-8"))

	return "would fix" if dry_run else "fixed"


if __name__ == "__main__":
	import sys
	print(process(sys.argv[1]))
