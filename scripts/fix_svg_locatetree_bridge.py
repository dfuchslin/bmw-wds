"""Step 5: fix release/<lang>/scripts/tree.js so javascript:locateTree(...)
links inside SVG diagrams actually work, and make hideButton()/showButton()
resilient to a frame-load race that deep linking (fix_deep_linking_main.py)
makes newly reachable.

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

Separately, hideButton()/showButton() both do
`parent.bottom.document.getElementById("svgbuttons").style...` with no null
check. Before deep linking, "main" only ever loaded a diagram/content page
via an in-app click (by which point "bottom" was long since loaded), so this
never threw. Deep linking can now land straight on such a page from a full
top-level page load, where "bottom" may not have finished loading yet -
guard both lookups so that race doesn't throw (which would also abort the
rest of showButton(), including the locateTree bridge above).
"""
import re

ANCHOR_RE = re.compile(
	r'(var svgimg ?= ?parent\.main\.document\.embeds\[0\]\.getSVGDocument\(\);\r?\n)'
)
BRIDGE_MARKER = "svgimg.defaultView.locateTree"

SVGBUTTONS_GET = 'parent.bottom.document.getElementById("svgbuttons")'
HIDE_LITERAL = SVGBUTTONS_GET + '.style.visibility = "hidden";'
SHOW_LITERAL = SVGBUTTONS_GET + '.style.visibility = "visible";'
SVGBUTTONS_MARKER = "var svgbuttons = " + SVGBUTTONS_GET


def process(tree_js_path, dry_run=False):
	with open(tree_js_path, "rb") as f:
		text = f.read().decode("utf-8")

	eol = "\r\n" if "\r\n" in text[:2000] else "\n"
	changed = False

	if BRIDGE_MARKER not in text:
		bridge_lines = (
			"\tif (svgimg && svgimg.defaultView) {" + eol +
			"\t\tsvgimg.defaultView.locateTree = locateTree;" + eol +
			"\t}" + eol
		)
		text, n = ANCHOR_RE.subn(lambda m: m.group(1) + bridge_lines, text, count=1)
		if n != 1:
			return "unexpected structure, skipped"
		changed = True

	if SVGBUTTONS_MARKER not in text:
		if HIDE_LITERAL not in text or SHOW_LITERAL not in text:
			return "unexpected structure, skipped"
		guarded = (
			"var svgbuttons = " + SVGBUTTONS_GET + ";" + eol +
			"\tif (svgbuttons) svgbuttons.style.visibility = \"{}\";"
		)
		text = text.replace(HIDE_LITERAL, guarded.format("hidden"), 1)
		text = text.replace(SHOW_LITERAL, guarded.format("visible"), 1)
		changed = True

	if not changed:
		return "already fixed"

	if not dry_run:
		with open(tree_js_path, "wb") as f:
			f.write(text.encode("utf-8"))

	return "would fix" if dry_run else "fixed"


if __name__ == "__main__":
	import sys
	print(process(sys.argv[1]))
