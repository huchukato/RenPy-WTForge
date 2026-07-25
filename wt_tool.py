#!/usr/bin/env python3
"""
Ren'Py WTForge - Main GUI
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
import json
import threading
from datetime import datetime
from PIL import Image

from wt_extractor import WTExtractor
from wt_analyzer import WTAnalyzer
from wt_generator import WTGenerator

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# Localizzazione
TRANSLATIONS = {
    'en': {
        'title': "Ren'Py WTForge",
        'game_selection': "Game Selection",
        'no_game_selected': "No game selected",
        'game_selected': "Game selected: {}",
        'app_button': ".app",
        'folder_button': "Folder",
        'progress': "Progress",
        'ready': "Ready",
        'choices_tab': "Choices",
        'log_tab': "Log",
        'choices_analyzed': "Choices Analyzed:",
        'choice': "Choice",
        'score': "Score",
        'file': "File",
        'choice_details': "Choice Details",
        'filter': "Filter",
        'all': "All",
        'best': "Best",
        'neutral': "Neutral",
        'bad': "Bad",
        'export_options': "Export Options",
        'export_all': "Export all with colors",
        'export_best': "Export only best",
        'edit_choice': "Hint Text",
        'save_choice': "Save Hint",
        'reset_choice': "Reset",
        'hint_placeholder': "Auto-generated from variables. Edit to customize.",
        'color_label': "Color",
        'color_auto': "Auto",
        'color_best': "Best",
        'color_neutral': "Neutral",
        'color_bad': "Bad",
        'color_none': "None",
        'search': "Search",
        'search_placeholder': "Search choices...",
        'all_files': "All files",
        'analyze_game': "Analyze Game",
        'generate_mod': "Generate Mod",
        'save_config': "Save Config",
        'load_config': "Load Config",
        'language': "Language",
        'select_app': "Select game .app file",
        'select_folder': "Select Ren'Py game directory",
        'saved': "Saved: {} -> {}",
        'config_saved': "Configuration saved to: {}",
        'config_loaded': "Configuration loaded: {} variables",
        'no_config': "No configuration found",
        'error': "Error",
        'select_game_first': "Select a game first",
        'analysis_complete': "Analysis complete: {} choices, {} variables",
        'extraction': "Extraction",
        'decompilation': "Decompilation",
        'analysis_in_progress': "Analysis in progress...",
        'mod_generated': "Mod generated successfully!",
        'mod_generated_path': "Mod generated in game/wtmod/",
        'mod_saved_path': "Mod saved to:\n{}",
        'generation_error': "Error generating mod: {}",
        'analysis_error': "Error during analysis: {}",
        'no_rpa_found': "No .rpa files found",
        'no_rpyc_found': "No .rpyc files found to decompile",
        'analyzing': "Analyzing {} .rpy files...",
        'extracting': "Extracting {} .rpa files...",
        'decompiling': "Decompiling {} .rpyc files...",
        'gallery_unlocker': "Gallery Unlocker",
        'gallery_generated': "Gallery Unlocker generated!",
        'gallery_saved_path': "Gallery Unlocker saved to:\n{}",
        'gallery_error': "Error generating Gallery Unlocker: {}",
        'export_mod': "Export Mod",
        'export_mod_title': "Choose destination folder for '{}'",
        'export_mod_done': "Mod exported to:\n{}",
        'export_mod_error': "Export error: {}",
        'no_mod_to_export': "Generate the mod first before exporting.",
        'dev_tools': "Dev Tools",
        'dev_tools_generated': "Dev Tools enabled!",
        'dev_tools_saved_path': "Dev Tools saved to:\n{}",
        'dev_tools_error': "Error generating Dev Tools: {}",
        'manual_edits_saved': "Manual edits saved: {}",
        'manual_edits_loaded': "Loaded {} manual edits",
        'manual_edits_load_error': "Error loading manual edits: {}",
        'replace_all': "Replace All",
        'replace_all_title': "Replace in hints",
        'find': "Find",
        'replace': "Replace with",
        'case_sensitive': "Case sensitive",
        'replace_scope_all': "All choices",
        'replace_scope_filtered': "Filtered choices only",
        'replace_count': "Replaced {} hints",
        'cancel': "Cancel"
    },
    'it': {
        'title': "Ren'Py WTForge",
        'game_selection': "Selezione Gioco",
        'no_game_selected': "Nessun gioco selezionato",
        'game_selected': "Gioco selezionato: {}",
        'app_button': ".app",
        'folder_button': "Cartella",
        'progress': "Progresso",
        'ready': "Pronto",
        'choices_tab': "Scelte",
        'log_tab': "Log",
        'choices_analyzed': "Scelte Analizzate:",
        'choice': "Scelta",
        'score': "Punteggio",
        'file': "File",
        'choice_details': "Dettagli Scelta",
        'filter': "Filtro",
        'all': "Tutte",
        'best': "Migliori",
        'neutral': "Neutre",
        'bad': "Cattive",
        'export_options': "Opzioni Esportazione",
        'export_all': "Esporta tutte con colori",
        'export_best': "Esporta solo migliori",
        'edit_choice': "Testo Hint",
        'save_choice': "Salva Hint",
        'reset_choice': "Ripristina",
        'hint_placeholder': "Generato automaticamente. Modifica per personalizzare.",
        'color_label': "Colore",
        'color_auto': "Auto",
        'color_best': "Migliore",
        'color_neutral': "Neutro",
        'color_bad': "Cattivo",
        'color_none': "Nessuno",
        'search': "Cerca",
        'search_placeholder': "Cerca scelte...",
        'all_files': "Tutti i file",
        'analyze_game': "Analizza Gioco",
        'generate_mod': "Genera Mod",
        'save_config': "Salva Config",
        'load_config': "Carica Config",
        'language': "Lingua",
        'select_app': "Seleziona file .app del gioco",
        'select_folder': "Seleziona directory gioco Ren'Py",
        'saved': "Salvato: {} -> {}",
        'config_saved': "Configurazione salvata in: {}",
        'config_loaded': "Configurazione caricata: {} variabili",
        'no_config': "Nessuna configurazione trovata",
        'error': "Errore",
        'select_game_first': "Seleziona prima un gioco",
        'analysis_complete': "Analisi completata: {} scelte, {} variabili",
        'extraction': "Estrazione",
        'decompilation': "Decompilazione",
        'analysis_in_progress': "Analisi in corso...",
        'mod_generated': "Mod generati con successo!",
        'mod_generated_path': "Mod generati in game/wtmod/",
        'mod_saved_path': "Mod salvati in:\n{}",
        'generation_error': "Errore generazione mod: {}",
        'analysis_error': "Errore durante analisi: {}",
        'no_rpa_found': "Nessun file .rpa trovato",
        'no_rpyc_found': "Nessun file .rpyc trovato da decompilare",
        'analyzing': "Analisi di {} file .rpy...",
        'extracting': "Estrazione di {} file .rpa...",
        'decompiling': "Decompilazione di {} file .rpyc...",
        'gallery_unlocker': "Sblocca Gallery",
        'gallery_generated': "Gallery Unlocker generato!",
        'gallery_saved_path': "Gallery Unlocker salvato in:\n{}",
        'gallery_error': "Errore generazione Gallery Unlocker: {}",
        'export_mod': "Esporta Mod",
        'export_mod_title': "Scegli cartella destinazione per '{}'",
        'export_mod_done': "Mod esportata in:\n{}",
        'export_mod_error': "Errore export: {}",
        'no_mod_to_export': "Genera prima la mod prima di esportarla.",
        'dev_tools': "Dev Tools",
        'dev_tools_generated': "Dev Tools abilitati!",
        'dev_tools_saved_path': "Dev Tools salvati in:\n{}",
        'dev_tools_error': "Errore generazione Dev Tools: {}",
        'manual_edits_saved': "Modifiche manuali salvate: {}",
        'manual_edits_loaded': "Caricate {} modifiche manuali",
        'manual_edits_load_error': "Errore caricamento modifiche manuali: {}",
        'replace_all': "Sostituisci tutto",
        'replace_all_title': "Sostituisci negli hint",
        'find': "Trova",
        'replace': "Sostituisci con",
        'case_sensitive': "Maiuscole/minuscole",
        'replace_scope_all': "Tutte le scelte",
        'replace_scope_filtered': "Solo scelte filtrate",
        'replace_count': "Sostituiti {} hint",
        'cancel': "Annulla"
    },
    'es': {
        'title': "Ren'Py WTForge",
        'game_selection': "Selección de juego",
        'no_game_selected': "Ningún juego seleccionado",
        'game_selected': "Juego seleccionado: {}",
        'app_button': ".app",
        'folder_button': "Carpeta",
        'progress': "Progreso",
        'ready': "Listo",
        'choices_tab': "Opciones",
        'log_tab': "Registro",
        'choices_analyzed': "Opciones analizadas:",
        'choice': "Opción",
        'score': "Puntuación",
        'file': "Archivo",
        'choice_details': "Detalles de la opción",
        'filter': "Filtro",
        'all': "Todas",
        'best': "Mejores",
        'neutral': "Neutras",
        'bad': "Peores",
        'export_options': "Opciones de exportación",
        'export_all': "Exportar todas con colores",
        'export_best': "Exportar solo las mejores",
        'edit_choice': "Texto de pista",
        'save_choice': "Guardar pista",
        'reset_choice': "Restablecer",
        'hint_placeholder': "Generado automáticamente. Modifica para personalizar.",
        'color_label': "Color",
        'color_auto': "Auto",
        'color_best': "Mejor",
        'color_neutral': "Neutral",
        'color_bad': "Peor",
        'color_none': "Ninguno",
        'search': "Buscar",
        'search_placeholder': "texto opción...",
        'all_files': "Todos los archivos",
        'analyze_game': "Analizar juego",
        'generate_mod': "Generar mod",
        'save_config': "Guardar config",
        'load_config': "Cargar config",
        'language': "Idioma",
        'select_app': "Seleccionar archivo .app del juego",
        'select_folder': "Seleccionar directorio del juego Ren'Py",
        'saved': "Guardado: {} -> {}",
        'config_saved': "Configuración guardada en: {}",
        'config_loaded': "Configuración cargada: {} variables",
        'no_config': "No se encontró configuración",
        'error': "Error",
        'select_game_first': "Selecciona un juego primero",
        'analysis_complete': "Análisis completado: {} opciones, {} variables",
        'extraction': "Extracción",
        'decompilation': "Descompilación",
        'analysis_in_progress': "Análisis en curso...",
        'mod_generated': "Mod generado correctamente",
        'mod_generated_path': "Mod generado en game/wtmod/",
        'mod_saved_path': "Mod guardado en:\n{}",
        'generation_error': "Error generando mod: {}",
        'analysis_error': "Error durante el análisis: {}",
        'no_rpa_found': "No se encontraron archivos .rpa",
        'no_rpyc_found': "No se encontraron archivos .rpyc para descompilar",
        'analyzing': "Analizando {} archivos .rpy...",
        'extracting': "Extrayendo {} archivos .rpa...",
        'decompiling': "Descompilando {} archivos .rpyc...",
        'gallery_unlocker': "Desbloquear galería",
        'gallery_generated': "Gallery Unlocker generado",
        'gallery_saved_path': "Gallery Unlocker guardado en:\n{}",
        'gallery_error': "Error generando Gallery Unlocker: {}",
        'export_mod': "Exportar mod",
        'export_mod_title': "Elige carpeta destino para '{}'",
        'export_mod_done': "Mod exportado a:\n{}",
        'export_mod_error': "Error de exportación: {}",
        'no_mod_to_export': "Genera primero la mod antes de exportarla.",
        'dev_tools': "Herramientas dev",
        'dev_tools_generated': "Herramientas dev habilitadas",
        'dev_tools_saved_path': "Herramientas dev guardadas en:\n{}",
        'dev_tools_error': "Error generando herramientas dev: {}",
        'manual_edits_saved': "Ediciones manuales guardadas: {}",
        'manual_edits_loaded': "Cargadas {} ediciones manuales",
        'manual_edits_load_error': "Error al cargar ediciones manuales: {}",
        'replace_all': "Reemplazar todo",
        'replace_all_title': "Reemplazar en pistas",
        'find': "Buscar",
        'replace': "Reemplazar con",
        'case_sensitive': "Distinguir mayúsculas",
        'replace_scope_all': "Todas las opciones",
        'replace_scope_filtered': "Solo opciones filtradas",
        'replace_count': "Reemplazados {} pistas",
        'cancel': "Cancelar"
    }
}


class RenPyWTTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Ren'Py WTForge")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)

        # Icona finestra
        _icon_path = Path(__file__).parent / "img" / "logo_256.png"
        if _icon_path.exists():
            from PIL import ImageTk
            self._tk_icon = ImageTk.PhotoImage(Image.open(_icon_path))
            self.root.iconphoto(True, self._tk_icon)

        # Variabili
        self.game_path = None
        self.extractor = None
        self.analyzer = None
        self.generator = None
        self.choices = []
        self.variables = {}
        self.current_lang = 'en'

        # Filtro e opzioni
        self.filter_mode = 'all'
        self.export_mode = 'all'
        self.choice_edits = {}

        # Setup UI
        self.setup_ui()

    def t(self, key, *args):
        text = TRANSLATIONS[self.current_lang].get(key, key)
        if args:
            return text.format(*args)
        return text

    def _lang_options(self):
        return {"English": "en", "Italiano": "it", "Español": "es"}

    def _lang_name(self, code):
        for name, c in self._lang_options().items():
            if c == code:
                return name
        return "English"

    def change_language(self, selected=None):
        new_lang = self._lang_options().get(selected)
        if new_lang and new_lang != self.current_lang:
            self.current_lang = new_lang
            self.root.title(self.t('title'))
            self.refresh_ui()

    def refresh_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_ui()

    def setup_ui(self):
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.setup_game_selection()
        self.setup_progress_section()
        self.setup_tabs()
        self.setup_action_buttons()

    def setup_game_selection(self):
        frame = ctk.CTkFrame(self.root, corner_radius=8)
        frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 4))
        frame.grid_columnconfigure(1, weight=1)

        # Logo
        logo_path = Path(__file__).parent / "img" / "logo_48.png"
        if logo_path.exists():
            pil_img = Image.open(logo_path)
            ctk_logo = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(48, 48))
            ctk.CTkLabel(frame, image=ctk_logo, text="").grid(
                row=0, column=0, rowspan=3, padx=(10, 6), pady=8, sticky="w")
            title_col = 1
        else:
            title_col = 0

        ctk.CTkLabel(frame, text=self.t('game_selection'),
                     font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=title_col, columnspan=4, sticky="w", padx=12, pady=(8, 2))

        self.game_path_var = ctk.StringVar()
        ctk.CTkEntry(frame, textvariable=self.game_path_var, width=500,
                     placeholder_text="Game path...").grid(
            row=1, column=title_col, padx=12, pady=(2, 8), sticky="ew")

        ctk.CTkButton(frame, text=self.t('app_button'), width=70,
                      command=self.browse_app).grid(row=1, column=title_col + 1, padx=4, pady=(2, 8))
        ctk.CTkButton(frame, text=self.t('folder_button'), width=80,
                      command=self.browse_folder).grid(row=1, column=title_col + 2, padx=4, pady=(2, 8))

        self.lang_var = ctk.StringVar(value=self._lang_name(self.current_lang))
        ctk.CTkOptionMenu(frame, values=list(self._lang_options().keys()), variable=self.lang_var,
                          command=self.change_language, width=100).grid(
            row=1, column=title_col + 3, padx=(12, 10), pady=(2, 8), sticky="e")

        self.status_label = ctk.CTkLabel(frame, text=self.t('no_game_selected'),
                                          text_color="gray")
        self.status_label.grid(row=2, column=title_col, columnspan=3, padx=12, pady=(0, 8), sticky="w")

    def setup_progress_section(self):
        frame = ctk.CTkFrame(self.root, corner_radius=8)
        frame.grid(row=1, column=0, sticky="ew", padx=12, pady=4)
        frame.grid_columnconfigure(0, weight=1)

        self.progress = ctk.CTkProgressBar(frame, mode='determinate')
        self.progress.set(0)
        self.progress.grid(row=0, column=0, sticky="ew", padx=12, pady=8)

        self.progress_label = ctk.CTkLabel(frame, text=self.t('ready'), text_color="gray")
        self.progress_label.grid(row=0, column=1, padx=12, pady=8)

    def setup_tabs(self):
        self.tabview = ctk.CTkTabview(self.root, corner_radius=8)
        self.tabview.grid(row=2, column=0, sticky="nsew", padx=12, pady=4)

        self.tabview.add(self.t('choices_tab'))
        self.tabview.add(self.t('log_tab'))

        self.setup_choices_tab(self.tabview.tab(self.t('choices_tab')))
        self.setup_log_tab(self.tabview.tab(self.t('log_tab')))

    def setup_choices_tab(self, parent):
        parent.grid_rowconfigure(2, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # Barra superiore: filtri + esportazione
        top_bar = ctk.CTkFrame(parent, corner_radius=6)
        top_bar.grid(row=0, column=0, sticky="ew", pady=(4, 6))

        ctk.CTkLabel(top_bar, text=self.t('filter') + ":",
                     font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(10, 4))
        self.filter_var = ctk.StringVar(value=self.filter_mode)
        for key, label in [('all', self.t('all')), ('best', self.t('best')),
                            ('neutral', self.t('neutral')), ('bad', self.t('bad'))]:
            ctk.CTkRadioButton(top_bar, text=label, variable=self.filter_var,
                               value=key, command=self.apply_filter).pack(side="left", padx=6, pady=6)

        ctk.CTkLabel(top_bar, text="  |  " + self.t('export_options') + ":",
                     font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(10, 4))
        self.export_var = ctk.StringVar(value=self.export_mode)
        ctk.CTkRadioButton(top_bar, text=self.t('export_all'), variable=self.export_var,
                           value='all', command=self.update_export_mode).pack(side="left", padx=6, pady=6)
        ctk.CTkRadioButton(top_bar, text=self.t('export_best'), variable=self.export_var,
                           value='best', command=self.update_export_mode).pack(side="left", padx=6, pady=6)

        # Barra ricerca e filtro file
        filter_bar = ctk.CTkFrame(parent, corner_radius=6)
        filter_bar.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        ctk.CTkLabel(filter_bar, text=self.t('search') + ":",
                     font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(10, 4))
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.apply_filter())
        ctk.CTkEntry(filter_bar, textvariable=self.search_var, width=240,
                     placeholder_text=self.t('search_placeholder')).pack(side="left", padx=(0, 12), pady=6)
        ctk.CTkLabel(filter_bar, text=self.t('file') + ":",
                     font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(10, 4))
        self.file_filter_var = ctk.StringVar(value=self.t('all_files'))
        self.file_filter_combo = ctk.CTkComboBox(filter_bar, values=[self.t('all_files')], width=180,
                                                 variable=self.file_filter_var, command=self.apply_filter)
        self.file_filter_combo.pack(side="left", padx=4, pady=6)
        ctk.CTkButton(filter_bar, text=self.t('replace_all'), width=100,
                      fg_color="#5c6d7d", hover_color="#4a5966",
                      command=self.open_replace_dialog).pack(side="left", padx=(12, 4), pady=6)

        # Split: lista sinistra, dettagli destra
        split = ctk.CTkFrame(parent, corner_radius=0, fg_color="transparent")
        split.grid(row=2, column=0, sticky="nsew")
        split.grid_rowconfigure(0, weight=1)
        split.grid_columnconfigure(0, weight=3)
        split.grid_columnconfigure(1, weight=2)

        # --- Lista scelte (Treeview con tkinter per compatibilità) ---
        import tkinter as tk
        from tkinter import ttk
        list_outer = ctk.CTkFrame(split, corner_radius=6)
        list_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        list_outer.grid_rowconfigure(1, weight=1)
        list_outer.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(list_outer, text=self.t('choices_analyzed'),
                     font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", padx=8, pady=(6, 2))

        tree_frame = ctk.CTkFrame(list_outer, corner_radius=0, fg_color="transparent")
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Dark.Treeview",
                        background="#2b2b2b", foreground="white",
                        fieldbackground="#2b2b2b", rowheight=24,
                        borderwidth=0)
        style.configure("Dark.Treeview.Heading",
                        background="#1f1f1f", foreground="#adaead",
                        relief="flat")
        style.map("Dark.Treeview", background=[("selected", "#4f728f")])

        self.choices_list = ttk.Treeview(tree_frame, columns=('text', 'score', 'file'),
                                          show='headings', style="Dark.Treeview")
        self.choices_list.tag_configure('manual', foreground='#facc15')
        self.choices_list.heading('text', text=self.t('choice'))
        self.choices_list.heading('score', text=self.t('score'))
        self.choices_list.heading('file', text=self.t('file'))
        self.choices_list.column('text', width=380, minwidth=200)
        self.choices_list.column('score', width=60, anchor="center")
        self.choices_list.column('file', width=140)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.choices_list.yview)
        self.choices_list.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky="ns")
        self.choices_list.grid(row=0, column=0, sticky="nsew")
        self.choices_list.bind('<<TreeviewSelect>>', self.on_choice_select)

        # --- Pannello destra: hint editor + dettagli ---
        right_panel = ctk.CTkFrame(split, corner_radius=6)
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_rowconfigure(2, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        # Color override
        color_row = ctk.CTkFrame(right_panel, corner_radius=0, fg_color="transparent")
        color_row.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        color_row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(color_row, text=self.t('color_label') + ":",
                     font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=(0, 6))
        self.color_option_map = {
            self.t('color_auto'): None,
            self.t('color_best'): 'best',
            self.t('color_neutral'): 'neutral',
            self.t('color_bad'): 'bad',
            self.t('color_none'): 'none'
        }
        self.color_override_var = ctk.StringVar(value=self.t('color_auto'))
        self.color_menu = ctk.CTkOptionMenu(
            color_row,
            width=140,
            values=list(self.color_option_map.keys()),
            variable=self.color_override_var,
            command=self.save_color_override
        )
        self.color_menu.grid(row=0, column=1, sticky="w")

        # Editor hint
        ctk.CTkLabel(right_panel, text=self.t('edit_choice'),
                     font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, sticky="w", padx=10, pady=(10, 2))
        hint_row = ctk.CTkFrame(right_panel, corner_radius=0, fg_color="transparent")
        hint_row.grid(row=1, column=0, sticky="ew", padx=10, pady=(28, 0))
        hint_row.grid_columnconfigure(0, weight=1)

        self.choice_edit_var = ctk.StringVar()
        ctk.CTkEntry(hint_row, textvariable=self.choice_edit_var,
                     placeholder_text="hint text...").grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkButton(hint_row, text=self.t('save_choice'), width=90,
                      fg_color="#4f728f", hover_color="#3e5c75",
                      command=self.save_choice_edit).grid(row=0, column=1, padx=(0, 6))
        ctk.CTkButton(hint_row, text=self.t('reset_choice'), width=90,
                      fg_color="#86878a", hover_color="#6b6c6e",
                      command=self.reset_choice_edit).grid(row=0, column=2)

        # Dettagli
        ctk.CTkLabel(right_panel, text=self.t('choice_details'),
                     font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, sticky="w", padx=10, pady=(10, 2))
        self.choice_details_text = ctk.CTkTextbox(right_panel, state="disabled",
                                                   font=ctk.CTkFont(family="monospace", size=12))
        self.choice_details_text.grid(row=2, column=0, sticky="nsew", padx=10, pady=(30, 10))

    def setup_log_tab(self, parent):
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        self.log_text = ctk.CTkTextbox(parent, font=ctk.CTkFont(family="monospace", size=12))
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

    def setup_action_buttons(self):
        frame = ctk.CTkFrame(self.root, corner_radius=8)
        frame.grid(row=3, column=0, sticky="ew", padx=12, pady=(4, 12))

        btn_cfg = dict(height=32, corner_radius=6)
        ctk.CTkButton(frame, text=self.t('analyze_game'), command=self.analyze_game,
                      fg_color="#4f728f", hover_color="#3e5c75", **btn_cfg).pack(side="left", padx=6, pady=8)
        ctk.CTkButton(frame, text=self.t('generate_mod'), command=self.generate_mod,
                      fg_color="#4f728f", hover_color="#3e5c75", **btn_cfg).pack(side="left", padx=4, pady=8)
        ctk.CTkButton(frame, text=self.t('gallery_unlocker'), command=self.generate_gallery_unlocker,
                      fg_color="#5c6d7d", hover_color="#4a5966", **btn_cfg).pack(side="left", padx=4, pady=8)
        ctk.CTkButton(frame, text=self.t('dev_tools'), command=self.generate_devtools,
                      fg_color="#6f7d8a", hover_color="#5e6b75", **btn_cfg).pack(side="left", padx=4, pady=8)
        ctk.CTkButton(frame, text=self.t('export_mod'), command=self.export_mod,
                      fg_color="#464e5a", hover_color="#353d47", **btn_cfg).pack(side="left", padx=4, pady=8)

    def browse_app(self):
        path = filedialog.askopenfilename(title=self.t('select_app'))
        if path:
            self.game_path_var.set(path)
            self.game_path = Path(path)
            self.status_label.configure(text=self.t('game_selected', self.game_path.name), text_color="#4f728f")

    def browse_folder(self):
        path = filedialog.askdirectory(title=self.t('select_folder'))
        if path:
            self.game_path_var.set(path)
            self.game_path = Path(path)
            self.status_label.configure(text=self.t('game_selected', self.game_path.name), text_color="#4f728f")
            
    def log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="normal")
        self.root.update_idletasks()
        
    def update_progress(self, current, total, message=""):
        if total > 0:
            self.progress.set(current / total)
            self.progress_label.configure(text=f"{message} ({current}/{total})")
        self.root.update_idletasks()
        
    def analyze_game(self):
        if not self.game_path:
            messagebox.showerror(self.t('error'), self.t('select_game_first'))
            return
        self.progress.set(0)
        self.progress_label.configure(text=self.t('analysis_in_progress'))
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.choices_list.delete(*self.choices_list.get_children())
        self.choice_edits = {}
        
        # Run in thread
        thread = threading.Thread(target=self._analyze_game_thread)
        thread.start()
        
    def _analyze_game_thread(self):
        """Thread per analisi gioco"""
        try:
            self.log(f"Starting analysis of: {self.game_path}")
            
            # Estrazione
            self.log("Phase 1: Extracting .rpa files...")
            self.extractor = WTExtractor(self.game_path)
            self.extractor.extract_rpa_files(
                progress_callback=lambda c, t: self.update_progress(c, t, self.t('extraction'))
            )
            
            # Decompilazione
            self.log("Phase 2: Decompiling .rpyc files...")
            self.extractor.decompile_rpyc_files(
                progress_callback=lambda c, t: self.update_progress(c, t, self.t('decompilation'))
            )
            
            # Analisi
            self.log("Phase 3: Analyzing .rpy files...")
            self.analyzer = WTAnalyzer()
            self.choices, self.variables = self.analyzer.analyze_directory(self.extractor.output_dir)
            
            # Aggiorna UI
            self.root.after(0, self._update_analysis_ui)
            
        except Exception as e:
            err_msg = str(e)
            self.log(f"Error during analysis: {err_msg}")
            self.root.after(0, lambda m=err_msg: messagebox.showerror(self.t('error'), m))
            
    def _update_analysis_ui(self):
        self.progress.set(1.0)
        self.progress_label.configure(text=self.t('analysis_complete', len(self.choices), len(self.variables)))
        self.log(self.t('analysis_complete', len(self.choices), len(self.variables)))
        self._populate_file_filter()
        self._load_manual_edits()
        self.apply_filter()

    def _populate_file_filter(self):
        """Popola il dropdown dei file dopo l'analisi"""
        if not hasattr(self, 'file_filter_combo') or not self.choices:
            return
        all_label = self.t('all_files')
        files = sorted(set(Path(c['file']).name for c in self.choices))
        self.file_filter_combo.configure(values=[all_label] + files)
        self.file_filter_var.set(all_label)

    def _get_game_dir(self):
        """Restituisce la directory game/ del gioco selezionato"""
        if not self.game_path:
            return None
        if self.game_path.suffix == '.app':
            return self.game_path / "Contents" / "Resources" / "autorun" / "game"
        return self.game_path / "game"

    def _manual_edits_path(self):
        """Percorso del file JSON che traccia le modifiche manuali"""
        game_dir = self._get_game_dir()
        if not game_dir:
            return None
        return game_dir / "wtmod" / "wtforge_edits.json"

    def _save_manual_edits(self):
        """Salva le modifiche manuali in wtforge_edits.json dentro il gioco"""
        if not self.game_path or not self.choices:
            return
        edits = []
        for choice in self.choices:
            if not choice.get('hint_text_custom') and not choice.get('color_override'):
                continue
            entry = {
                'choice_text': choice['choice_text'],
                'file': Path(choice['file']).name,
                'line': choice['line'],
            }
            if choice.get('hint_text_custom'):
                entry['hint_text_custom'] = choice['hint_text_custom']
            if choice.get('color_override'):
                entry['color_override'] = choice['color_override']
            entry['timestamp'] = datetime.now().isoformat()
            edits.append(entry)
        path = self._manual_edits_path()
        if not path:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            'version': '1.0',
            'game_path': str(self.game_path),
            'edits': edits
        }
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.log(self.t('manual_edits_saved', path))
        except Exception as e:
            self.log(self.t('manual_edits_load_error', str(e)))

    def _load_manual_edits(self):
        """Carica e applica le modifiche manuali da wtforge_edits.json"""
        if not self.game_path or not self.choices:
            return
        path = self._manual_edits_path()
        if not path or not path.exists():
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            edits = data.get('edits', [])
            lookup = {edit['choice_text']: edit for edit in edits}
            applied = 0
            for choice in self.choices:
                edit = lookup.get(choice['choice_text'])
                if not edit:
                    continue
                if 'hint_text_custom' in edit:
                    choice['hint_text_custom'] = edit['hint_text_custom']
                if 'color_override' in edit:
                    choice['color_override'] = edit['color_override']
                applied += 1
            if applied:
                self.log(self.t('manual_edits_loaded', applied))
        except Exception as e:
            self.log(self.t('manual_edits_load_error', str(e)))
            
    def apply_filter(self, *args):
        """Applica filtro, ricerca e filtro file alla lista scelte"""
        self.filter_mode = self.filter_var.get()
        self.choices_list.delete(*self.choices_list.get_children())
        
        search_text = self.search_var.get().lower() if hasattr(self, 'search_var') else ''
        selected_file = self.file_filter_var.get() if hasattr(self, 'file_filter_var') else self.t('all_files')
        all_files_label = self.t('all_files')
        
        for idx, choice in enumerate(self.choices):
            score = choice['total_score']
            if self.filter_mode == 'best' and score <= 0:
                continue
            elif self.filter_mode == 'neutral' and score != 0:
                continue
            elif self.filter_mode == 'bad' and score >= 0:
                continue
            
            if search_text:
                choice_text = choice['choice_text'].lower()
                hint = choice.get('hint_text_custom') or choice.get('hint_text', '')
                if search_text not in choice_text and search_text not in hint.lower():
                    continue
            
            file_name = Path(choice['file']).name
            if selected_file != all_files_label and selected_file != file_name:
                continue
            
            hint = choice.get('hint_text_custom') or choice.get('hint_text', '')
            display_text = f"{choice['choice_text'][:40]}  ({hint})" if hint else choice['choice_text'][:50]
            manual = bool(choice.get('hint_text_custom') or choice.get('color_override'))
            self.choices_list.insert('', 'end', iid=str(idx), values=(
                display_text,
                score,
                file_name
            ), tags=('manual',) if manual else ())
    
    def update_export_mode(self):
        """Aggiorna modalità esportazione"""
        self.export_mode = self.export_var.get()
    
    def save_choice_edit(self):
        """Salva hint text personalizzato"""
        selection = self.choices_list.selection()
        if selection:
            idx = int(selection[0])
            new_hint = self.choice_edit_var.get().strip()
            self.choice_edits[idx] = new_hint
            self.choices[idx]['hint_text_custom'] = new_hint if new_hint else None
            self.apply_filter()
            # Ri-seleziona la riga
            if self.choices_list.exists(str(idx)):
                self.choices_list.selection_set(str(idx))
            self._save_manual_edits()

    def save_color_override(self, selected):
        """Salva override colore per la scelta selezionata"""
        selection = self.choices_list.selection()
        if selection:
            idx = int(selection[0])
            override_key = self.color_option_map.get(selected)
            self.choices[idx]['color_override'] = override_key
            self._save_manual_edits()

    def reset_choice_edit(self):
        """Ripristina hint e colore della scelta selezionata ai valori automatici"""
        selection = self.choices_list.selection()
        if selection:
            idx = int(selection[0])
            self.choices[idx]['hint_text_custom'] = None
            self.choices[idx]['color_override'] = None
            self.choice_edit_var.set(self.choices[idx].get('hint_text', ''))
            self.color_override_var.set(self.t('color_auto'))
            self.apply_filter()
            if self.choices_list.exists(str(idx)):
                self.choices_list.selection_set(str(idx))
            self._save_manual_edits()

    def open_replace_dialog(self):
        """Apre il dialog per sostituire testo in blocco negli hint"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(self.t('replace_all_title'))
        dialog.geometry("520x420")
        dialog.minsize(480, 380)
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.after(100, lambda: (dialog.lift(), dialog.focus_force()))

        pad = {"padx": 16, "pady": 6}
        ctk.CTkLabel(dialog, text=self.t('find') + ":").pack(anchor="w", **pad)
        find_entry = ctk.CTkEntry(dialog, width=380)
        find_entry.pack(**pad)

        ctk.CTkLabel(dialog, text=self.t('replace') + ":").pack(anchor="w", **pad)
        replace_entry = ctk.CTkEntry(dialog, width=380)
        replace_entry.pack(**pad)

        case_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(dialog, text=self.t('case_sensitive'), variable=case_var).pack(anchor="w", **pad)

        scope_var = ctk.StringVar(value="all")
        ctk.CTkRadioButton(dialog, text=self.t('replace_scope_all'), variable=scope_var,
                           value="all").pack(anchor="w", **pad)
        ctk.CTkRadioButton(dialog, text=self.t('replace_scope_filtered'), variable=scope_var,
                           value="filtered").pack(anchor="w", **pad)

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=12)

        def do_replace():
            find_text = find_entry.get()
            replace_text = replace_entry.get()
            if find_text:
                self.apply_replace_all(find_text, replace_text, case_var.get(), scope_var.get())
            dialog.destroy()

        ctk.CTkButton(btn_frame, text=self.t('replace_all'), command=do_replace,
                      fg_color="#4f728f", hover_color="#3e5c75").pack(side="left", padx=8)
        ctk.CTkButton(btn_frame, text=self.t('cancel'), command=dialog.destroy,
                      fg_color="#86878a", hover_color="#6b6c6e").pack(side="left", padx=8)

    def apply_replace_all(self, find_text, replace_text, case_sensitive, scope):
        """Applica la sostituzione del testo negli hint"""
        if not self.choices:
            return
        if scope == "filtered":
            indices = [int(iid) for iid in self.choices_list.get_children()]
        else:
            indices = range(len(self.choices))

        if case_sensitive:
            find = find_text
            new_hint_func = lambda h: h.replace(find, replace_text)
        else:
            find = find_text.lower()
            def new_hint_func(h):
                out = []
                i = 0
                lh = h.lower()
                flen = len(find)
                while i < len(h):
                    pos = lh.find(find, i)
                    if pos == -1:
                        out.append(h[i:])
                        break
                    out.append(h[i:pos])
                    out.append(replace_text)
                    i = pos + flen
                return "".join(out)

        replaced = 0
        for idx in indices:
            choice = self.choices[idx]
            original = choice.get('hint_text_custom') or choice.get('hint_text', '')
            if find not in (original if case_sensitive else original.lower()):
                continue
            new_hint = new_hint_func(original)
            if new_hint != original:
                # Se il nuovo hint è identico a quello auto, non forzare un override manuale
                if new_hint == choice.get('hint_text', ''):
                    choice['hint_text_custom'] = None
                    self.choice_edits.pop(idx, None)
                else:
                    choice['hint_text_custom'] = new_hint
                    self.choice_edits[idx] = new_hint
                replaced += 1

        if replaced:
            self.apply_filter()
            self._save_manual_edits()
            self.log(self.t('replace_count', replaced))

    def on_choice_select(self, event):
        selection = self.choices_list.selection()
        if selection:
            idx = int(selection[0])
            choice = self.choices[idx]
            current_hint = choice.get('hint_text_custom') or choice.get('hint_text', '')
            self.choice_edit_var.set(current_hint)

            # Imposta dropdown override colore
            override_key = choice.get('color_override')
            selected_label = self.t('color_auto')
            for label, key in self.color_option_map.items():
                if key == override_key:
                    selected_label = label
                    break
            self.color_override_var.set(selected_label)

            details = f"Choice: {choice['choice_text']}\n"
            details += f"Score: {choice['total_score']}\n"
            if choice.get('color_override'):
                details += f"Color override: {choice['color_override']}\n"
            details += f"Hint (auto): {choice.get('hint_text', '')}\n"
            if choice.get('hint_text_custom'):
                details += f"Hint (custom): {choice['hint_text_custom']}\n"
            details += f"File: {Path(choice['file']).name}  line {choice['line']}\n\n"
            details += "Variables:\n"
            for var in choice['variables']:
                sign = '+' if var['value'] >= 0 else ''
                details += f"  {var['name']}: {sign}{var['value']}\n"
            self.choice_details_text.configure(state="normal")
            self.choice_details_text.delete("1.0", "end")
            self.choice_details_text.insert("end", details)
            self.choice_details_text.configure(state="disabled")
                    
    def generate_mod(self):
        """Genera i file mod"""
        if not self.game_path or not self.choices:
            messagebox.showerror(self.t('error'), self.t('select_game_first'))
            return
            
        try:
            self.generator = WTGenerator(self.game_path, self.export_mode)
            self.generator.generate_mod(self.choices, self.variables)
            
            # Mostra popup con percorso completo
            mod_path = self.generator.output_dir
            messagebox.showinfo("Success", self.t('mod_saved_path', mod_path))
            self.log(self.t('mod_saved_path', mod_path))
        except Exception as e:
            messagebox.showerror(self.t('error'), self.t('generation_error', str(e)))
            
    def generate_gallery_unlocker(self):
        """Genera il file Gallery Unlocker"""
        if not self.game_path:
            messagebox.showerror(self.t('error'), self.t('select_game_first'))
            return
            
        try:
            self.generator = WTGenerator(self.game_path, self.export_mode)
            gallery_path = self.generator.export_gallery_unlocker()
            messagebox.showinfo(self.t('gallery_generated'), self.t('gallery_saved_path', gallery_path))
            self.log(self.t('gallery_saved_path', gallery_path))
        except Exception as e:
            messagebox.showerror(self.t('error'), self.t('gallery_error', str(e)))

    def generate_devtools(self):
        """Genera il file Dev Tools"""
        if not self.game_path:
            messagebox.showerror(self.t('error'), self.t('select_game_first'))
            return
        try:
            gen = WTGenerator(self.game_path, self.export_mode)
            devtools_path = gen.export_devtools()
            messagebox.showinfo(self.t('dev_tools_generated'), self.t('dev_tools_saved_path', devtools_path))
            self.log(self.t('dev_tools_saved_path', devtools_path))
        except Exception as e:
            messagebox.showerror(self.t('error'), self.t('dev_tools_error', str(e)))

    def _game_display_name(self) -> str:
        _skip = {"game", "autorun", "Contents", "Resources", "MacOS", "data"}
        p = Path(self.game_path)
        for part in reversed(p.parts):
            if part.endswith(".app"):
                return part[:-4]
            if part not in _skip:
                return part
        return p.name

    def export_mod(self):
        if not self.game_path or not self.generator:
            messagebox.showwarning(self.t('error'), self.t('no_mod_to_export'))
            return
        wtmod_src = self.generator.output_dir
        if not wtmod_src.exists():
            messagebox.showwarning(self.t('error'), self.t('no_mod_to_export'))
            return
        game_name = self._game_display_name()
        default_name = f"{game_name}-wtmod"
        dest = filedialog.askdirectory(title=self.t('export_mod_title', default_name))
        if not dest:
            return
        import shutil
        export_dir = Path(dest) / default_name / "game" / "wtmod"
        try:
            if export_dir.exists():
                shutil.rmtree(export_dir)
            shutil.copytree(wtmod_src, export_dir)
            messagebox.showinfo(self.t('export_mod'), self.t('export_mod_done', export_dir.parent.parent))
            self.log(self.t('export_mod_done', export_dir.parent.parent))
        except Exception as e:
            messagebox.showerror(self.t('error'), self.t('export_mod_error', str(e)))

def main():
    root = ctk.CTk()
    app = RenPyWTTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()
