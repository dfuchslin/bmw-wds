#!/usr/bin/env bash
# Copies the pristine WDS tree from an already-mounted ISO path into
# DEST_DIR, wiping any previous copy so every run starts fresh.
#
# Usage: copy_source.sh [SOURCE_DIR] [DEST_DIR]
#   SOURCE_DIR defaults to $SOURCE_DIR env var, then /Volumes/WDS_BMW
#   (where `hdiutil attach -readonly -nobrowse BMW_WDS_12.0.iso` lands it).
#   DEST_DIR defaults to "data" at the project root.
#
# This script does not mount or unmount the .iso itself - mount it
# yourself first (e.g. `hdiutil attach -readonly -nobrowse /path/to/BMW_WDS_12.0.iso`).

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

SOURCE_DIR="${1:-${SOURCE_DIR:-/Volumes/WDS_BMW}}"
DEST_DIR="${2:-$PROJECT_ROOT/data}"

if [ ! -d "$SOURCE_DIR" ]; then
	echo "error: source dir '$SOURCE_DIR' does not exist. Mount the ISO first, e.g.:" >&2
	echo "  hdiutil attach -readonly -nobrowse /path/to/BMW_WDS_12.0.iso" >&2
	exit 1
fi

if [ ! -f "$SOURCE_DIR/index.htm" ] || [ ! -d "$SOURCE_DIR/release" ]; then
	echo "error: '$SOURCE_DIR' doesn't look like the WDS root (expected index.htm and release/ there)" >&2
	exit 1
fi

echo "Copying $SOURCE_DIR -> $DEST_DIR ..."
rm -rf "$DEST_DIR"
mkdir -p "$DEST_DIR"

if command -v rclone >/dev/null 2>&1; then
	THREADS="$(sysctl -n hw.ncpu 2>/dev/null || nproc 2>/dev/null || echo 4)"
	[ "$THREADS" -gt 4 ] 2>/dev/null && THREADS=4
	echo "Using rclone ($THREADS streams) ..."
	rclone copy "$SOURCE_DIR"/ "$DEST_DIR"/ \
		--progress \
		--links \
		--multi-thread-streams="$THREADS" \
		--transfers="$THREADS" \
		--checkers="$((THREADS * 2))"
else
	rsync -a "$SOURCE_DIR"/ "$DEST_DIR"/
fi

echo "Making copy writable ..."
chmod -R u+w "$DEST_DIR"

echo "Done. $(du -sh "$DEST_DIR" | cut -f1) at $DEST_DIR"
