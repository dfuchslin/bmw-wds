"""Step 1b: replace the atc50c.jar <applet> block in a model's navi.htm with
the JS navtree.js equivalent.

Uses a structural regex match (not an exact-byte template) so it's robust to
minor whitespace differences between models/languages, and pulls the
per-language loadingMessage text out of the applet block it's replacing
instead of hardcoding English text.
"""
import json
import re

APPLET_RE = re.compile(r'<applet\b[^>]*name="stree"[\s\S]*?</applet>', re.IGNORECASE)
PARAM_RE = r'<param\s+name="{0}"\s+value="([^"]*)"\s*/?>'
HEAD_CLOSE_RE = re.compile(r'</head>', re.IGNORECASE)

DEFAULT_LOADING_MESSAGE = "Loading Navigation ..."

HEAD_ADDITIONS = (
	'<link rel="stylesheet" type="text/css" href="../styles/basic.css">\n'
	'<script type="text/javascript" src="../scripts/navtree.js"></script>\n'
)


def extract_param(applet_block, name, default=None):
	m = re.search(PARAM_RE.format(re.escape(name)), applet_block, re.IGNORECASE)
	return m.group(1) if m else default


def build_body_replacement(xml_rel_path, loading_message):
	return (
		'<div id="navtree"></div>\n'
		'<script type="text/javascript">\n'
		'\tNavTree.init({{\n'
		'\t\tdataUrl: {data},\n'
		'\t\ttarget: "main",\n'
		'\t\topenFolderIcon: "images/openfolder.gif",\n'
		'\t\tcloseFolderIcon: "images/closedfolder.gif",\n'
		'\t\tleafIcon: "images/document.gif",\n'
		'\t\tloadingMessage: {loading}\n'
		'\t}});\n'
		'</script>'
	).format(data=json.dumps(xml_rel_path), loading=json.dumps(loading_message))


def process(navi_path, xml_rel_path, dry_run=False):
	"""Returns a short status string."""
	with open(navi_path, "rb") as f:
		text = f.read().decode("utf-8")

	if "NavTree.init" in text:
		return "already patched"

	m = APPLET_RE.search(text)
	if not m:
		return "no applet block found"

	applet_block = m.group(0)
	loading_message = extract_param(applet_block, "loadingMessage", DEFAULT_LOADING_MESSAGE)

	new_text = text[:m.start()] + build_body_replacement(xml_rel_path, loading_message) + text[m.end():]

	hm = HEAD_CLOSE_RE.search(new_text)
	if not hm:
		return "no </head> found"
	if "navtree.js" not in new_text[:hm.start()]:
		new_text = new_text[:hm.start()] + HEAD_ADDITIONS + new_text[hm.start():]

	if not dry_run:
		with open(navi_path, "wb") as f:
			f.write(new_text.encode("utf-8"))

	return "would patch" if dry_run else "patched"


if __name__ == "__main__":
	import sys
	navi, xml_rel = sys.argv[1], sys.argv[2]
	print(process(navi, xml_rel))
