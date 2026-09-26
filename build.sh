#!/usr/bin/env bash
# Full pipeline: copy the pristine source, preprocess it, build & start the
# nginx container.
#
# Usage: ./build.sh [SOURCE_DIR]
#   SOURCE_DIR is the already-mounted ISO path (see scripts/copy_source.sh),
#   defaults to /Volumes/WDS_BMW.

set -euo pipefail
cd "$(dirname "$0")"

./scripts/copy_source.sh "$@"
python3 ./scripts/preprocess.py
docker compose up --build -d

echo
echo "Serving at http://localhost:8080/"
