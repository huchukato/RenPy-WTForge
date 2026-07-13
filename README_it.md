# 🎮 Ren'Py WTForge

<p align="center">
  <img src="logo_512.png" alt="Ren'Py WTForge Logo" width="160">
</p>

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Piattaforma-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/Licenza-As--Is-orange)
![GUI](https://img.shields.io/badge/GUI-customtkinter-green)
![Status](https://img.shields.io/badge/Stato-Attivo-brightgreen)

> Uno strumento GUI universale per generare automaticamente **mod walkthrough** per i giochi Ren'Py — con scelte colorate, etichette hint personalizzabili e sblocco gallery. Nessun codice richiesto.

---

## ✨ Funzionalità

| Funzione | Descrizione |
|---|---|
| 📦 **Estrazione automatica** | Estrae archivi `.rpa` tramite rpatool |
| 🔓 **Decompilazione** | Decompila file `.rpyc` tramite unrpyc |
| 🧠 **Analisi intelligente** | Rileva scelte con punteggi numerici, booleani (`True`/`False`) e chiamate a funzione (`change_relationship("alice", 1)`) |
| 🎨 **Colorazione scelte** | 🟢 Scelte migliori, 🔴 Scelte peggiori, 🔵 Scelte neutre |
| ✏️ **Editor Hint** | Personalizza il testo hint accanto a ogni scelta (es. `rel_alice +1` → `Alice +1`) |
| 🖼️ **Gallery Unlocker** | Genera con un click uno script per sbloccare tutta la gallery |
| 🔍 **Filtri** | Mostra Tutte / Migliori / Neutre / Cattive |
| 📤 **Modalità esportazione** | Esporta tutte le scelte con colori OPPURE solo le migliori |
| 💾 **Salva/Carica Config** | Salva i tuoi hint personalizzati e riutilizzali nelle sessioni successive |
| 🌐 **IT / EN** | Cambio lingua interfaccia con un tasto |

---

## 🖥️ Screenshot

**GUI:**

<p align="center">
  <img src="gui.png" alt="WTForge GUI" width="800">
</p>

**Scelte in gioco con colore e hint:**

```
{color=#00b894}La mia ragazza.{/color}  {color=#aaaaaa}(Alice +1){/color}
{color=#d63031}Un'amica.{/color}        {color=#aaaaaa}(Alice -1){/color}
```

---

## 📋 Requisiti

- **Python 3.9+** — nessun pacchetto esterno necessario (solo stdlib)
- **tkinter** — di solito incluso con Python
  - Linux: `sudo apt-get install python3-tk`
  - macOS (Homebrew): `brew install python-tk`
- Un gioco Ren'Py (`.app` su macOS o cartella su Windows/Linux)

---

## 🚀 Avvio rapido

**Windows:**
```bat
start.bat
```

**macOS / Linux:**
```bash
./start.sh
```

**Oppure direttamente:**
```bash
python3 wt_tool.py
```

---

## 🔧 Flusso di lavoro

1. **Seleziona il gioco** — Clicca `.app` (macOS) o `Cartella` (Windows/Linux)
2. **Analizza il gioco** — Estrae `.rpa`, decompila `.rpyc`, analizza tutti gli script
3. **Sfoglia le scelte** — Usa i filtri (Tutte / Migliori / Neutre / Cattive)
4. **Modifica l'hint** — Clicca una scelta e personalizza il testo hint (es. `ch2sharing +1` → `Sharing Route`)
5. **Scegli la modalità** — Esporta tutte le scelte con colori, o solo le migliori
6. **Genera Mod** — Crea `wtmod.rpy` nella directory corretta del gioco
7. *(Opzionale)* **Sblocca Gallery** — Genera `wtmod_gallery.rpy` per sbloccare tutte le CG

---

## 📁 Struttura output

I file mod vengono salvati automaticamente nel percorso corretto per ogni piattaforma:

**macOS (`.app`):**
```
NomeGioco.app/Contents/Resources/autorun/game/wtmod/
├── wtmod.rpy              # Mod principale: colori + dizionario hint + screen override
├── wtmod_screens.rpy      # File screen stub
└── wtmod_config.json      # Configurazione variabili
```

**Windows / Linux:**
```
NomeGioco/game/wtmod/
├── wtmod.rpy
├── wtmod_screens.rpy
└── wtmod_config.json
```

> Dopo la generazione viene mostrato un popup con il percorso esatto di salvataggio.

---

## 🗂️ Struttura del progetto

```
RenPy-WTForge/
├── wt_tool.py          # GUI principale (tkinter)
├── wt_analyzer.py      # Parser script — trova scelte, variabili, punteggi
├── wt_generator.py     # Generatore file mod
├── wt_extractor.py     # Estrattore .rpa + decompilatore .rpyc
├── start.bat           # Launcher Windows
├── start.sh            # Launcher macOS/Linux
├── config/             # Configurazioni hint salvate
└── UnRen Tools/        # Utility UnRen incluse
```

---

## ⚠️ Risoluzione problemi

| Problema | Soluzione |
|---|---|
| *"Nessun file .rpa trovato"* | Gli script del gioco potrebbero essere già estratti come `.rpy` — clicca comunque **Analizza** |
| *Errore di decompilazione* | Alcuni giochi usano obfuscation non supportata da unrpyc |
| *tkinter non trovato* | Installa con: `sudo apt-get install python3-tk` (Linux) o `brew install python-tk` (macOS) |
| *Gallery unlocker crasha* | Il gioco potrebbe non usare `award_manager` — lo script lo ignora silenziosamente e usa un fallback |

---

## 🙏 Crediti

- 💡 Concetto originale walkthrough mod di **[fergz](https://patreon.com/fergz)**
- 🔧 UnRen Tools di **huchukato, goobdoob, jimmy5 & Sam**
- 📦 rpatool di **[Shiz](https://codeberg.org/shiz/rpatool)**
- 🔓 unrpyc di **[CensoredUsername](https://github.com/CensoredUsername/unrpyc)**

---

## 📄 Licenza

Questo tool è fornito **"così com'è"** senza garanzie. Usalo a tuo rischio.
I file originali del gioco non vengono mai modificati — la mod viene sempre salvata nella directory separata `wtmod/`.
