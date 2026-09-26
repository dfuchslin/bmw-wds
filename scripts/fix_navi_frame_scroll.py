"""Step 7: let the "navi" (left tree) frame scroll.

Each model's index.htm frameset (same template patched by
fix_deep_linking_main.py) hardcodes scrolling='no' on the "navi" frame -
presumably left over from the original Java applet, which had its own
internal scroll/viewport within a fixed canvas, so the frame-level
scrollbar was suppressed to avoid a doubled-up scrollbar. Our DOM-based
navtree.js replacement has no such internal scroll mechanism, so a long
branch (e.g. the X-connector components) just gets silently clipped with no
way to reach the rest of it. "main" already uses scrolling='auto' in the
same template - bring "navi" in line with it.
"""
import re

NAVI_FRAME_NO_SCROLL_RE = re.compile(r"(name='navi'[^>]*?)scrolling='no'")
NAVI_FRAME_AUTO_SCROLL_RE = re.compile(r"name='navi'[^>]*?scrolling='auto'")


def process(index_path, dry_run=False):
	with open(index_path, "rb") as f:
		text = f.read().decode("utf-8")

	if "name='navi'" not in text:
		return "unexpected structure, skipped"

	new_text, n = NAVI_FRAME_NO_SCROLL_RE.subn(r"\1scrolling='auto'", text)
	if n == 0:
		if NAVI_FRAME_AUTO_SCROLL_RE.search(text):
			return "already fixed"
		return "unexpected structure, skipped"

	if not dry_run:
		with open(index_path, "wb") as f:
			f.write(new_text.encode("utf-8"))

	return "would fix" if dry_run else "fixed"


if __name__ == "__main__":
	import sys
	print(process(sys.argv[1]))
