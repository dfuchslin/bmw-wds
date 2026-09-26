"""Step 2: install the shared navtree.js + CSS block into one language's
release/<lang>/scripts and release/<lang>/styles.

Content-based, not just existence-based: re-running after assets/navtree.js
or assets/navtree.css changes must actually refresh the deployed copies,
not silently skip them because a file of that name already exists.
"""
import os
import re

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
NAVTREE_JS_SRC = os.path.join(ASSETS_DIR, "navtree.js")
NAVTREE_CSS_SRC = os.path.join(ASSETS_DIR, "navtree.css")

CSS_MARKER_START = "/* --- navtree.css (managed - do not edit below, see assets/navtree.css) --- */"
CSS_MARKER_END = "/* --- end navtree.css --- */"
CSS_BLOCK_RE = re.compile(re.escape(CSS_MARKER_START) + r"[\s\S]*?" + re.escape(CSS_MARKER_END))


def process(lang_dir, dry_run=False):
	results = {}

	scripts_dir = os.path.join(lang_dir, "scripts")
	dest_js = os.path.join(scripts_dir, "navtree.js")
	with open(NAVTREE_JS_SRC, "rb") as f:
		js_src = f.read()

	current_js = None
	if os.path.isfile(dest_js):
		with open(dest_js, "rb") as f:
			current_js = f.read()

	if current_js == js_src:
		results["navtree.js"] = "already up to date"
	else:
		results["navtree.js"] = "would update" if dry_run else "updated"
		if not dry_run:
			os.makedirs(scripts_dir, exist_ok=True)
			with open(dest_js, "wb") as f:
				f.write(js_src)

	css_path = os.path.join(lang_dir, "styles", "basic.css")
	with open(NAVTREE_CSS_SRC, "r", encoding="utf-8") as f:
		css_block_raw = f.read()
	managed_block = CSS_MARKER_START + "\n" + css_block_raw.strip("\n") + "\n" + CSS_MARKER_END

	with open(css_path, "rb") as f:
		original_css_text = f.read().decode("utf-8")

	# one-time migration: an older version of this script appended the raw
	# block with no marker wrapper - drop that exact copy (whether or not a
	# managed block was *also* already inserted alongside it) so re-runs
	# don't leave the styles duplicated once the logic below (re-)inserts
	# the managed block.
	working_text = original_css_text
	if css_block_raw in working_text:
		working_text = working_text.replace(css_block_raw, "", 1)

	if CSS_MARKER_START in working_text:
		new_css_text = CSS_BLOCK_RE.sub(managed_block, working_text, count=1)
	else:
		# basic.css wraps its whole body in a legacy <!-- --> CDO/CDC pair;
		# insert before the trailing "-->" so new rules stay inside it,
		# matching the convention the rest of the file already uses.
		idx = working_text.rfind("-->")
		if idx == -1:
			new_css_text = working_text + managed_block
		else:
			new_css_text = working_text[:idx] + managed_block + working_text[idx:]

	if new_css_text == original_css_text:
		results["basic.css"] = "already up to date"
	else:
		results["basic.css"] = "would update" if dry_run else "updated"
		if not dry_run:
			with open(css_path, "wb") as f:
				f.write(new_css_text.encode("utf-8"))

	return results


if __name__ == "__main__":
	import sys
	print(process(sys.argv[1]))
