#!/usr/bin/env bash
# Full pipeline: copy the pristine source, preprocess it, build & start the
# nginx container.
#
# Usage: ./build.sh [SOURCE_DIR] [DEST_DIR]
#   SOURCE_DIR is the already-mounted ISO path (see scripts/copy_source.sh),
#   defaults to /Volumes/WDS_BMW.
#   DEST_DIR is where the processed site is written, defaults to ./data
#   (gitignored).

set -euo pipefail
cd "$(dirname "$0")"

SOURCE_DIR="${1:-}"
DEST_DIR="${2:-data}"

./scripts/copy_source.sh "$SOURCE_DIR" "$DEST_DIR"
python3 ./scripts/preprocess.py --root "$DEST_DIR"

echo
echo "Done! To start, run:"
echo "WDS_DATA_DIR=\"$DEST_DIR\" docker compose up --build -d"
