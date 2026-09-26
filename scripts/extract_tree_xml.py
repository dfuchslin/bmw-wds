"""Step 1a: extract <model>/tree/files.zip -> a plain XML sibling file.

The zip's internal filename doesn't reliably follow the language directory
name (e.g. the "spa" language dir's data is named "..._sp_files.xml", not
"..._spa_files.xml"), so the extracted name is discovered by inspecting the
zip's contents rather than guessed.
"""
import os
import zipfile


def process(model_dir, dry_run=False):
    """Returns (xml_rel_path, status) where xml_rel_path is e.g. 'tree/e3802_wds_en_files.xml',
    or (None, reason) if there's nothing to extract."""
    zip_path = os.path.join(model_dir, "tree", "files.zip")
    if not os.path.isfile(zip_path):
        return None, "no tree/files.zip"

    with zipfile.ZipFile(zip_path) as zf:
        xml_names = [n for n in zf.namelist() if n.lower().endswith(".xml")]
        if len(xml_names) != 1:
            return None, "expected exactly 1 xml in zip, found {}".format(xml_names)
        xml_name = xml_names[0]
        dest_path = os.path.join(model_dir, "tree", xml_name)

        if os.path.isfile(dest_path):
            return "tree/" + xml_name, "already extracted"

        if dry_run:
            return "tree/" + xml_name, "would extract"

        with zf.open(xml_name) as src, open(dest_path, "wb") as dst:
            dst.write(src.read())

    return "tree/" + xml_name, "extracted"


if __name__ == "__main__":
    import sys
    for d in sys.argv[1:]:
        print(d, process(d))
