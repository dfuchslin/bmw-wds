#!/usr/bin/env python3
"""Orchestrates steps 1-4 (applet -> navtree.js swap, per-language assets,
charset-meta fix, language index.htm fix) across every language and model
under the data root (see --root).

Usage:
    python3 preprocess.py [--dry-run] [--root data]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import extract_tree_xml
import patch_navi_htm
import add_language_assets
import fix_charset_meta
import fix_language_index
import fix_svg_locatetree_bridge
import fix_deep_linking_main
import fix_navi_frame_scroll

LANGUAGES = [
	"ch", "de", "en", "fr", "gr", "it", "ja", "ko", "ni",
	"po", "ru", "spa", "sv", "th", "tr", "us",
]


def find_model_dirs(lang_dir):
	"""A model dir is any immediate subdir of a language dir that has a navi.htm."""
	for name in sorted(os.listdir(lang_dir)):
		path = os.path.join(lang_dir, name)
		if os.path.isdir(path) and os.path.isfile(os.path.join(path, "navi.htm")):
			yield path


def run(root, dry_run):
	release_dir = os.path.join(root, "release")
	found_langs = [d for d in LANGUAGES if os.path.isdir(os.path.join(release_dir, d))]
	missing_langs = [d for d in LANGUAGES if d not in found_langs]
	if missing_langs:
		print("WARNING: expected language dirs not found, skipping:", missing_langs)

	totals = {
		"models_patched": 0, "models_already": 0, "models_stub": 0,
		"models_error": 0, "assets_copied": 0, "assets_already": 0,
		"index_fixed": 0, "index_already": 0, "index_error": 0,
		"treejs_fixed": 0, "treejs_already": 0, "treejs_error": 0,
		"deeplink_fixed": 0, "deeplink_already": 0, "deeplink_error": 0,
		"naviscroll_fixed": 0, "naviscroll_already": 0, "naviscroll_error": 0,
	}
	errors = []

	for lang in found_langs:
		lang_dir = os.path.join(release_dir, lang)

		for model_dir in find_model_dirs(lang_dir):
			model_name = os.path.basename(model_dir)
			is_real = os.path.isfile(os.path.join(model_dir, "tree", "atc50c.jar"))
			if not is_real:
				totals["models_stub"] += 1
				continue

			xml_rel, status1 = extract_tree_xml.process(model_dir, dry_run=dry_run)
			if xml_rel is None:
				totals["models_error"] += 1
				errors.append("{}/{}: extract_tree_xml: {}".format(lang, model_name, status1))
				continue

			navi_path = os.path.join(model_dir, "navi.htm")
			status2 = patch_navi_htm.process(navi_path, xml_rel, dry_run=dry_run)
			if status2 in ("patched", "would patch"):
				totals["models_patched"] += 1
			elif status2 == "already patched":
				totals["models_already"] += 1
			else:
				totals["models_error"] += 1
				errors.append("{}/{}: patch_navi_htm: {}".format(lang, model_name, status2))

			model_index_path = os.path.join(model_dir, "index.htm")
			status3 = fix_deep_linking_main.process(model_index_path, dry_run=dry_run)
			if status3 in ("fixed", "would fix"):
				totals["deeplink_fixed"] += 1
			elif status3 == "already fixed":
				totals["deeplink_already"] += 1
			else:
				totals["deeplink_error"] += 1
				errors.append("{}/{}/index.htm: fix_deep_linking_main: {}".format(lang, model_name, status3))

			status6 = fix_navi_frame_scroll.process(model_index_path, dry_run=dry_run)
			if status6 in ("fixed", "would fix"):
				totals["naviscroll_fixed"] += 1
			elif status6 == "already fixed":
				totals["naviscroll_already"] += 1
			else:
				totals["naviscroll_error"] += 1
				errors.append("{}/{}/index.htm: fix_navi_frame_scroll: {}".format(lang, model_name, status6))

		asset_result = add_language_assets.process(lang_dir, dry_run=dry_run)
		for _key, val in asset_result.items():
			if val in ("updated", "would update"):
				totals["assets_copied"] += 1
			else:
				totals["assets_already"] += 1

		index_path = os.path.join(lang_dir, "index.htm")
		if os.path.isfile(index_path):
			status4 = fix_language_index.process(index_path, dry_run=dry_run)
			if status4 in ("fixed", "would fix"):
				totals["index_fixed"] += 1
			elif status4 == "already fixed":
				totals["index_already"] += 1
			else:
				totals["index_error"] += 1
				errors.append("{}/index.htm: fix_language_index: {}".format(lang, status4))

		tree_js_path = os.path.join(lang_dir, "scripts", "tree.js")
		if os.path.isfile(tree_js_path):
			status5 = fix_svg_locatetree_bridge.process(tree_js_path, dry_run=dry_run)
			if status5 in ("fixed", "would fix"):
				totals["treejs_fixed"] += 1
			elif status5 == "already fixed":
				totals["treejs_already"] += 1
			else:
				totals["treejs_error"] += 1
				errors.append("{}/scripts/tree.js: fix_svg_locatetree_bridge: {}".format(lang, status5))

	print("=== Steps 1-2 summary ({}) ===".format("DRY RUN" if dry_run else "APPLIED"))
	print("languages processed:", len(found_langs))
	print("models patched:      ", totals["models_patched"])
	print("models already done: ", totals["models_already"])
	print("models stub/skipped: ", totals["models_stub"])
	print("models errored:      ", totals["models_error"])
	print("language assets installed:", totals["assets_copied"])
	print("language assets already present:", totals["assets_already"])
	print("language index.htm fixed:", totals["index_fixed"])
	print("language index.htm already fixed:", totals["index_already"])
	print("language index.htm errors:", totals["index_error"])
	print("tree.js locateTree bridge fixed:", totals["treejs_fixed"])
	print("tree.js locateTree bridge already fixed:", totals["treejs_already"])
	print("tree.js locateTree bridge errors:", totals["treejs_error"])
	print("model index.htm deep-linking fixed:", totals["deeplink_fixed"])
	print("model index.htm deep-linking already fixed:", totals["deeplink_already"])
	print("model index.htm deep-linking errors:", totals["deeplink_error"])
	print("model index.htm navi frame scroll fixed:", totals["naviscroll_fixed"])
	print("model index.htm navi frame scroll already fixed:", totals["naviscroll_already"])
	print("model index.htm navi frame scroll errors:", totals["naviscroll_error"])
	if errors:
		print("--- errors ---")
		for e in errors:
			print(" ", e)

	print()
	print("=== Step 3: charset meta fix (whole tree) ===")
	charset_result = fix_charset_meta.process(root, dry_run=dry_run)
	print("files changed:     ", charset_result["changed"])
	print("already had charset:", charset_result["already_ok"])
	if charset_result["skipped_no_head"]:
		print("skipped (no <head> found):", len(charset_result["skipped_no_head"]))
		for p in charset_result["skipped_no_head"][:20]:
			print("  ", p)


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--dry-run", action="store_true")
	parser.add_argument("--root", default="data")
	args = parser.parse_args()

	if not os.path.isdir(args.root):
		print("error: root dir '{}' does not exist - run copy_source.sh first".format(args.root))
		sys.exit(1)

	run(args.root, args.dry_run)
