"""Step 2: install the shared navtree.js + CSS block into one language's
release/<lang>/scripts and release/<lang>/styles, once per language.
"""
import os
import shutil

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
NAVTREE_JS_SRC = os.path.join(ASSETS_DIR, "navtree.js")
NAVTREE_CSS_SRC = os.path.join(ASSETS_DIR, "navtree.css")


def process(lang_dir, dry_run=False):
	results = {}

	scripts_dir = os.path.join(lang_dir, "scripts")
	dest_js = os.path.join(scripts_dir, "navtree.js")
	if os.path.isfile(dest_js):
		results["navtree.js"] = "already present"
	else:
		results["navtree.js"] = "would copy" if dry_run else "copied"
		if not dry_run:
			os.makedirs(scripts_dir, exist_ok=True)
			shutil.copyfile(NAVTREE_JS_SRC, dest_js)

	css_path = os.path.join(lang_dir, "styles", "basic.css")
	with open(NAVTREE_CSS_SRC, "r", encoding="utf-8") as f:
		css_block = f.read()

	with open(css_path, "rb") as f:
		css_text = f.read().decode("utf-8")

	if ".navtree" in css_text:
		results["basic.css"] = "already present"
	else:
		results["basic.css"] = "would append" if dry_run else "appended"
		if not dry_run:
			# basic.css wraps its whole body in a legacy <!-- --> CDO/CDC pair;
			# insert before the trailing "-->" so new rules stay inside it,
			# matching the convention the rest of the file already uses.
			idx = css_text.rfind("-->")
			if idx == -1:
				new_css_text = css_text + css_block
			else:
				new_css_text = css_text[:idx] + css_block + css_text[idx:]
			with open(css_path, "wb") as f:
				f.write(new_css_text.encode("utf-8"))

	return results


if __name__ == "__main__":
	import sys
	print(process(sys.argv[1]))
