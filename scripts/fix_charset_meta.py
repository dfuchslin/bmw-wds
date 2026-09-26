"""Step 3: insert <meta charset> into any .htm file under a directory tree
that's missing one. Idempotent - safe to re-run.
"""
import os
import re

HEAD_OPEN_RE = re.compile(rb'<head>', re.IGNORECASE)
META_LINE = b'<meta http-equiv="Content-Type" content="text/html; charset=utf-8">'


def process(root_dir, dry_run=False):
	changed = []
	skipped_no_head = []
	already_ok = 0

	for dirpath, _dirnames, filenames in os.walk(root_dir):
		for fn in filenames:
			if not fn.lower().endswith(".htm"):
				continue
			path = os.path.join(dirpath, fn)
			with open(path, "rb") as f:
				data = f.read()

			if b"charset" in data.lower():
				already_ok += 1
				continue

			m = HEAD_OPEN_RE.search(data)
			if not m:
				skipped_no_head.append(path)
				continue

			if not dry_run:
				eol = b"\r\n" if b"\r\n" in data[:2000] else b"\n"
				new_data = data[:m.end()] + eol + META_LINE + data[m.end():]
				with open(path, "wb") as f:
					f.write(new_data)
			changed.append(path)

	return {
		"changed": len(changed),
		"already_ok": already_ok,
		"skipped_no_head": skipped_no_head,
	}


if __name__ == "__main__":
	import sys
	print(process(sys.argv[1]))
