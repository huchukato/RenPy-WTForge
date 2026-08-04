# 🎮 Ren'Py WTForge v1.2.0 — Release Notes

**Release Date:** 2026-08-04

Ren'Py WTForge is a universal GUI tool that automatically generates **walkthrough mods** for Ren'Py games. It color-codes choices, lets you customize hint labels, and can generate a universal gallery unlocker — all without manual script editing.

---

## ✨ Highlights

- 🎨 **Color-coded choices** — best, bad, and neutral choices are shown in-game with a refreshed palette.
- ✏️ **Custom hint labels** — rename raw variables like `rel_alice +1` to `Alice +1`.
- 🎨 **Manual color override** — override Auto / Best / Neutral / Bad / None per choice directly in the GUI.
- 💾 **Per-game edit tracking** — manual edits are auto-saved inside the game as `game/wtmod/wtforge_edits.json` and reapplied on re-analysis.
- 🖼️ **Gallery Unlocker** — one-click generator for unlocking all CGs in `award_manager` based games.
- 🧠 **Smart analysis** — detects numeric scores, booleans, and function calls such as `change_relationship("alice", 1)`.
- 🔍 **Search + file filter** — quickly find choices and filter by source `.rpy` file.
- 🌐 **EN / IT / ES UI** — switch interface language on the fly.
- 🍎 **macOS `.app` build support** — build a self-contained bundle with `build/build_mac_app.sh`.
- 📦 **Centralized assets** — all images moved under `img/`.

---

## 🆕 What's New in v1.2.0

- 🛤️ **Detected routes** — view jump/call labels per choice and filter by route.
- 🧩 **Choice effects panel** — see all extracted effects per choice in the GUI details.
- ✂️ **Concise in-game hints** — hints now display up to the 3 most impactful variables.
- 🌟 **Wildcard include/exclude filters** — fine-grained control over which variables affect scoring.
- ⚡ **Cached `.rpyc` decompilation** — skips decompilation when the corresponding `.rpy` is already newer.
- 📈 **Live progress bar** — progress now updates during extraction, decompilation, and `.rpy` analysis.
- 🪲 **Detected routes dropdown fix** — route selection now populates correctly.

## 🆕 What's New in v1.1.0

- 🎨 **Manual color override** — choose Auto / Best / Neutral / Bad / None per choice directly in the GUI.
- 💾 **Per-game JSON auto-save** — manual hint and color edits are automatically tracked inside the game as `game/wtmod/wtforge_edits.json` and reapplied on re-analysis.
- 🔍 **Search + file filter** — quickly find choices by text and filter by source `.rpy` file.
- 🌐 **Spanish UI** — interface language dropdown now supports English, Italian, and Spanish.
- 🟡 **Bright yellow hints** — generated in-game hint labels now use `#facc15` for better visibility.
- 🔄 **Reset hint button** — one-click restore of the original auto-generated hint.
- 🟨 **Manual edit highlight** — choices with custom hints or colors are highlighted in yellow in the list.

## 🗓️ Previous Release: v1.0.0

- Initial public release of Ren'Py WTForge.
- Refreshed color palette derived from the new logo tones (`#22c55e`, `#d63031`, `#86878a`, `#adaead`).
- All image assets moved to the `img/` directory and references updated across the tool, build scripts, and READMEs.
- New `build/` directory with `build.sh` (zip release) and `build_mac_app.sh` (macOS bundle).
- `build/build.sh` now reads the version from `pyproject.toml` automatically.
- Updated English and Italian README files with new screenshots paths and color examples.

---

## 📋 Requirements

- **Python 3.9+**
- **tkinter** — usually bundled with Python
  - Linux: `sudo apt-get install python3-tk`
  - macOS (Homebrew): `brew install python-tk`
- A Ren'Py game (`.app` on macOS or folder on Windows/Linux)

---

## 🚀 Installation & Quick Start

### macOS / Linux

```bash
./start.sh
```

### Windows

```batch
start.bat
```

### Manual

```bash
pip install customtkinter pillow
python3 wt_tool.py
```

---

## ⬇️ Download

- 🎁 **Latest release:** [RenPy-WTForge-v1.2.0.zip](LINK_HERE)
- 💻 **Source:** [GitHub repository](https://github.com/huchukato/RenPy-WTForge)

---

## 📸 In-Game Preview

```text
{color=#22c55e}My girlfriend.{/color}  {color=#facc15}(Alice +1){/color}
{color=#d63031}A friend.{/color}       {color=#facc15}(Alice -1){/color}
```

---

## 📝 Notes

- Generated mod files are saved in `game/wtmod/` (or `GameName.app/Contents/Resources/autorun/game/wtmod/` on macOS).
- The original game files are never modified.
- If you also use **Ren'Py Translator**, translate the game first, then run WTForge so the mod picks up translated choice texts.

---

## 🙏 Credits

- 💡 Original walkthrough mod concept by **[fergz](https://f95zone.to/threads/global-walkthrough-mod-for-most-renpy-games-1-1-fergz.128702/)** — Global Walkthrough Mod v1.1
- 🛠️ WTForge by **huchukato**
- 🔧 UnRen Tools by **huchukato, goobdoob, jimmy5 & Sam**
- 📦 rpatool by **[Shiz](https://codeberg.org/shiz/rpatool)**
- 🔓 unrpyc by **[CensoredUsername](https://github.com/CensoredUsername/unrpyc)**
