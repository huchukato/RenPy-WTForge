#!/usr/bin/env bash
# Crea un bundle .app macOS autocontenuto per Ren'Py WTForge
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR/.."
cd "$PROJECT_DIR"

APP_NAME="RenPy-WTForge"
VERSION=$(grep -E '^version[[:space:]]*=[[:space:]]*"' pyproject.toml | head -1 | sed -E 's/.*"([^"]+)".*/\1/')
BUNDLE_NAME="${APP_NAME}-v${VERSION}"
BUNDLE_DIR="dist/${BUNDLE_NAME}.app"
PROJECT_DST="$BUNDLE_DIR/Contents/Resources/project"
ICNS_SRC="img/logo.icns"

echo "[WTForge Mac] Building ${BUNDLE_NAME}.app..."

rm -rf "$BUNDLE_DIR"
mkdir -p "$BUNDLE_DIR/Contents/MacOS"
mkdir -p "$PROJECT_DST"

# Copia il progetto nel bundle
echo "[WTForge Mac] Copying project into bundle..."
cp -R ".venv" "$PROJECT_DST/.venv"
cp wt_tool.py wt_analyzer.py wt_generator.py wt_extractor.py "$PROJECT_DST/"
cp start.sh start.bat pyproject.toml README.md README_it.md "$PROJECT_DST/"
cp -r img "$PROJECT_DST/img"
cp -r "UnRen Tools" "$PROJECT_DST/UnRen Tools"
mkdir -p "$PROJECT_DST/config"

# Icona
ICNS_FILE="$BUNDLE_DIR/Contents/Resources/${APP_NAME}.icns"
if [ -f "$ICNS_SRC" ]; then
    cp "$ICNS_SRC" "$ICNS_FILE"
    echo "[WTForge Mac] Using $ICNS_SRC as app icon."
else
    echo "[WTForge Mac] Warning: $ICNS_SRC not found, app will have no icon."
fi

# Info.plist
cat > "$BUNDLE_DIR/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleDisplayName</key>
    <string>${APP_NAME}</string>
    <key>CFBundleExecutable</key>
    <string>${APP_NAME}</string>
    <key>CFBundleIconFile</key>
    <string>${APP_NAME}</string>
    <key>CFBundleIdentifier</key>
    <string>com.huchukato.renpywtforge</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>${APP_NAME}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>${VERSION}</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
PLIST

# Script di lancio autocontenuto
LAUNCHER="$BUNDLE_DIR/Contents/MacOS/${APP_NAME}"
cat > "$LAUNCHER" <<'LAUNCHER'
#!/usr/bin/env bash
# Launcher autocontenuto per RenPy-WTForge.app

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT="$APP_DIR/../Resources/project"
cd "$PROJECT"

PYTHON="$PROJECT/.venv/bin/python"
if [ ! -x "$PYTHON" ]; then
    osascript -e 'display dialog "Python virtualenv not found inside the app bundle." buttons {"OK"} default button 1' &
    exit 1
fi

PYTHON_BASE=$("$PYTHON" -c "import sys; print(sys.base_prefix)")
if [ -d "$PYTHON_BASE/lib/tcl8.6" ]; then
    export TCL_LIBRARY="$PYTHON_BASE/lib/tcl8.6"
fi
if [ -d "$PYTHON_BASE/lib/tk8.6" ]; then
    export TK_LIBRARY="$PYTHON_BASE/lib/tk8.6"
fi

export PYTHONPATH="$PROJECT"
exec "$PYTHON" wt_tool.py
LAUNCHER

chmod +x "$LAUNCHER"

echo "[WTForge Mac] Bundle ready: $BUNDLE_DIR"
