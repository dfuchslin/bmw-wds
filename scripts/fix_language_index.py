"""Step 4: fix release/<lang>/index.htm.

The original page branch-detects "Microsoft Internet Explorer" (true for
no modern browser) to pick a frameset, and inside that branch calls a
VBScript ActiveX check (isSVGControlInstalled, via Adobe's old SVG plugin)
to decide between the real content page and a "system requirements not
met" page. Since no modern browser satisfies the outer check, every user
today falls into the "browser without dynamic frame resize" else-branch,
which loads the <lang>_invalid.htm "CAUTION" page instead of real content.

Fix: drop the VBScript block and the outer if/else entirely, keeping only
what the "good" branch produced (real content, assuming native SVG support
- true for every modern browser, no plugin needed).
"""
import re

VBSCRIPT_RE = re.compile(r'<script language="VBScript">[\s\S]*?</script>\s*', re.IGNORECASE)
JS_BLOCK_RE = re.compile(r'<script language="JavaScript" type="text/javascript">[\s\S]*?</script>', re.IGNORECASE)

META_SRC_RE = re.compile(r"name='vmeta' src='([^']+)'")
MAIN_SRC_RE = re.compile(r"name='vmain' src='([^']+)'")
BOTTOM_SRC_RE = re.compile(r"name='vbottom' src='([^']+)'")

NEW_JS_TEMPLATE = (
	'<script language="JavaScript" type="text/javascript">\n'
	'\tvar htm_code = ""; \n'
	'\thtm_code+="<frameset rows=\'75,*,48\' border=\'4\' frameborder=\'0\' framespacing=\'0\'>";\n'
	'\thtm_code+="<frame name=\'vmeta\' src=\'{meta}\' scrolling=\'no\' frameborder=\'0\' marginheight=\'0\' marginwidth=\'0\' noresize>";\n'
	'\thtm_code+="<frame name=\'vmain\' src=\'{main}\' scrolling=\'yes\' frameborder=\'1\' marginheight=\'10\' marginwidth=\'7\'>";\n'
	'\thtm_code+="<frame name=\'vbottom\' src=\'{bottom}\' scrolling=\'no\' frameborder=\'0\' marginheight=\'0\' marginwidth=\'0\' noresize>";\n'
	'\thtm_code+="</frameset>";\n'
	'\n'
	'\tdocument.open();\n'
	'\tdocument.write(htm_code);\n'
	'\tdocument.close();\n'
	'</script>'
)


def process(index_path, dry_run=False):
	with open(index_path, "rb") as f:
		text = f.read().decode("utf-8")

	if "VBScript" not in text and "isSVGControlInstalled" not in text:
		return "already fixed"

	meta_m = META_SRC_RE.search(text)
	main_ms = MAIN_SRC_RE.findall(text)
	bottom_m = BOTTOM_SRC_RE.search(text)
	if not meta_m or not main_ms or not bottom_m:
		return "unexpected structure, skipped"

	# Document order: 1st vmain = isSVGControlInstalled()==true branch (real
	# content) - the one we keep. 2nd = ...==false (system.htm), 3rd = the
	# outer else (invalid.htm) - both dropped.
	new_js = NEW_JS_TEMPLATE.format(meta=meta_m.group(1), main=main_ms[0], bottom=bottom_m.group(1))

	new_text = VBSCRIPT_RE.sub("", text)
	new_text, n = JS_BLOCK_RE.subn(new_js, new_text)
	if n != 1:
		return "unexpected script block count ({}), skipped".format(n)

	if not dry_run:
		with open(index_path, "wb") as f:
			f.write(new_text.encode("utf-8"))

	return "would fix" if dry_run else "fixed"


if __name__ == "__main__":
	import sys
	print(process(sys.argv[1]))
