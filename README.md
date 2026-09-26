# BMW Wiring Diagram System

Allowing 20+ year old wiring diagram system to work with modern browsers.

## Usage

1. Mount the WDS ISO (read-only, so the pristine source is never touched):

   ```sh
   hdiutil attach -readonly -nobrowse /path/to/BMW_WDS_12.0.iso
   ```

2. Run the build pipeline:

   ```sh
   ./build.sh [SOURCE_DIR] [DEST_DIR]
   ```

   - `SOURCE_DIR` is the mounted ISO path, defaults to `/Volumes/WDS_BMW`.
   - `DEST_DIR` is where the processed, browser-ready site is written,
     defaults to `data/` at the project root. It's gitignored — regenerate
     it any time by re-running `build.sh`.

   This copies the source, patches it (swaps the dead Java applet nav tree
   for `assets/navtree.js`, fixes missing charset declarations, fixes the
   broken browser-sniffing language entry pages), then builds and starts
   the nginx container.

3. Open <http://localhost:8080/>.

### Running pipeline steps individually

- `scripts/copy_source.sh [SOURCE_DIR] [DEST_DIR]` — just the copy step.
- `scripts/preprocess.py [--dry-run] [--root DEST_DIR]` — just the patching
  step (idempotent, safe to re-run against an existing `DEST_DIR`).
