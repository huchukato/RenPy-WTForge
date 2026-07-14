#!/bin/bash
# Build script per WTForge - crea un archivio zip da distribuire
# Uso: ./build.sh [versione]  es: ./build.sh 1.0.1

VERSION=${1:-"1.0.0"}
DIST_DIR="dist"
BUILD_NAME="RenPy-WTForge-v${VERSION}"
BUILD_DIR="${DIST_DIR}/${BUILD_NAME}"

echo "[WTForge Build] Version: ${VERSION}"

# Pulisci build precedente
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"

# Copia file principali
cp wt_tool.py wt_analyzer.py wt_generator.py wt_extractor.py "${BUILD_DIR}/"
cp start.sh start.bat pyproject.toml README.md README_it.md "${BUILD_DIR}/"
cp logo_48.png logo_256.png logo_512.png gui.png "${BUILD_DIR}/"

# Copia UnRen Tools (solo file necessari, escludi asset inutili)
mkdir -p "${BUILD_DIR}/UnRen Tools/decompiler"
cp "UnRen Tools/unrpyc.py" "UnRen Tools/rpatool" "UnRen Tools/deobfuscate.py" "${BUILD_DIR}/UnRen Tools/"
cp -r "UnRen Tools/decompiler/" "${BUILD_DIR}/UnRen Tools/decompiler/"

# Crea cartella config vuota
mkdir -p "${BUILD_DIR}/config"

# Rendi start.sh eseguibile
chmod +x "${BUILD_DIR}/start.sh"

# Crea zip
cd "${DIST_DIR}"
zip -r "${BUILD_NAME}.zip" "${BUILD_NAME}"
cd ..

echo "[WTForge Build] Done: ${DIST_DIR}/${BUILD_NAME}.zip"
