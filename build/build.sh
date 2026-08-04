#!/bin/bash
# Build script per WTForge - crea un archivio zip da distribuire
# Uso: ./build/build.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR/.."
cd "$PROJECT_DIR"

VERSION=$(grep -E '^version[[:space:]]*=[[:space:]]*"' pyproject.toml | head -1 | sed -E 's/.*"([^"]+)".*/\1/')
DIST_DIR="dist"
BUILD_NAME="RenPy-WTForge-v${VERSION}"
BUILD_DIR="${DIST_DIR}/${BUILD_NAME}"

echo "[WTForge Build] Version: ${VERSION}"

# Pulisci build precedente
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"

# Copia file principali
cp wt_tool.py wt_analyzer.py wt_generator.py wt_extractor.py wt_effects.py wt_gallery.py "${BUILD_DIR}/"
cp start.sh start.bat pyproject.toml README.md README_it.md "${BUILD_DIR}/"
cp -r img "${BUILD_DIR}/"

# Copia UnRen Tools (solo file necessari, escludi asset inutili)
mkdir -p "${BUILD_DIR}/UnRen Tools/decompiler"
cp "UnRen Tools/unrpyc.py" "UnRen Tools/rpatool" "UnRen Tools/deobfuscate.py" "${BUILD_DIR}/UnRen Tools/"
cp -r "UnRen Tools/decompiler/" "${BUILD_DIR}/UnRen Tools/decompiler/"

# Crea cartella config vuota
mkdir -p "${BUILD_DIR}/config"

# Rendi start.sh eseguibile
chmod +x "${BUILD_DIR}/start.sh"

# Rimuove file superflui dal pacchetto
find "${BUILD_DIR}" -type d -name '__pycache__' -exec rm -rf {} +
find "${BUILD_DIR}" -type f \( -name '.DS_Store' -o -name '*.pyc' -o -name 'Icon?' \) -delete

# Crea zip
rm -f "${DIST_DIR}/${BUILD_NAME}.zip"
cd "${DIST_DIR}"
zip -r "${BUILD_NAME}.zip" "${BUILD_NAME}"
cd ..

echo "[WTForge Build] Done: ${DIST_DIR}/${BUILD_NAME}.zip"
