#!/usr/bin/env python3
"""
Ren'Py WTForge - Main GUI
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
import json
import threading
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
        'hint_placeholder': "Auto-generated from variables. Edit to customize.",
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
        'dev_tools_error': "Error generating Dev Tools: {}"
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
        'hint_placeholder': "Generato automaticamente. Modifica per personalizzare.",
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
        'dev_tools_error': "Errore generazione Dev Tools: {}"
    }
}


class RenPyWTTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Ren'Py WTForge")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)

        # Icona finestra
        _icon_path = Path(__file__).parent / "logo_256.png"
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

    def change_language(self):
        self.current_lang = 'en' if self.current_lang == 'it' else 'it'
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
        logo_path = Path(__file__).parent / "logo_48.png"
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
        parent.grid_rowconfigure(1, weight=1)
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

        # Split: lista sinistra, dettagli destra
        split = ctk.CTkFrame(parent, corner_radius=0, fg_color="transparent")
        split.grid(row=1, column=0, sticky="nsew")
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
                        background="#1f1f1f", foreground="#aaaaaa",
                        relief="flat")
        style.map("Dark.Treeview", background=[("selected", "#1f538d")])

        self.choices_list = ttk.Treeview(tree_frame, columns=('text', 'score', 'file'),
                                          show='headings', style="Dark.Treeview")
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
        right_panel.grid_rowconfigure(1, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        # Editor hint
        ctk.CTkLabel(right_panel, text=self.t('edit_choice'),
                     font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 2))
        hint_row = ctk.CTkFrame(right_panel, corner_radius=0, fg_color="transparent")
        hint_row.grid(row=0, column=0, sticky="ew", padx=10, pady=(28, 0))
        hint_row.grid_columnconfigure(0, weight=1)

        self.choice_edit_var = ctk.StringVar()
        ctk.CTkEntry(hint_row, textvariable=self.choice_edit_var,
                     placeholder_text="hint text...").grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkButton(hint_row, text=self.t('save_choice'), width=90,
                      command=self.save_choice_edit).grid(row=0, column=1)

        # Dettagli
        ctk.CTkLabel(right_panel, text=self.t('choice_details'),
                     font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, sticky="w", padx=10, pady=(10, 2))
        self.choice_details_text = ctk.CTkTextbox(right_panel, state="disabled",
                                                   font=ctk.CTkFont(family="monospace", size=12))
        self.choice_details_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=(30, 10))

    def setup_log_tab(self, parent):
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        self.log_text = ctk.CTkTextbox(parent, font=ctk.CTkFont(family="monospace", size=12))
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

    def setup_action_buttons(self):
        frame = ctk.CTkFrame(self.root, corner_radius=8)
        frame.grid(row=3, column=0, sticky="ew", padx=12, pady=(4, 12))

        btn_cfg = dict(height=32, corner_radius=6)
        ctk.CTkButton(frame, text=self.t('analyze_game'), command=self.analyze_game, **btn_cfg).pack(side="left", padx=6, pady=8)
        ctk.CTkButton(frame, text=self.t('generate_mod'), command=self.generate_mod,
                      fg_color="#00b894", hover_color="#019874", **btn_cfg).pack(side="left", padx=4, pady=8)
        ctk.CTkButton(frame, text=self.t('gallery_unlocker'), command=self.generate_gallery_unlocker,
                      fg_color="#6c5ce7", hover_color="#5a4dcc", **btn_cfg).pack(side="left", padx=4, pady=8)
        ctk.CTkButton(frame, text=self.t('dev_tools'), command=self.generate_devtools,
                      fg_color="#fd79a8", hover_color="#e0678f", **btn_cfg).pack(side="left", padx=4, pady=8)
        ctk.CTkButton(frame, text=self.t('export_mod'), command=self.export_mod,
                      fg_color="#e17055", hover_color="#c0604a", **btn_cfg).pack(side="left", padx=4, pady=8)
        ctk.CTkButton(frame, text=self.t('save_config'), command=self.save_config, **btn_cfg).pack(side="left", padx=4, pady=8)
        ctk.CTkButton(frame, text=self.t('load_config'), command=self.load_config, **btn_cfg).pack(side="left", padx=4, pady=8)

        lang_text = "IT" if self.current_lang == 'en' else "EN"
        ctk.CTkButton(frame, text=lang_text, width=48, command=self.change_language,
                      fg_color="gray30", hover_color="gray40", **btn_cfg).pack(side="right", padx=8, pady=8)
        
    def browse_app(self):
        path = filedialog.askopenfilename(title=self.t('select_app'))
        if path:
            self.game_path_var.set(path)
            self.game_path = Path(path)
            self.status_label.configure(text=self.t('game_selected', self.game_path.name), text_color="#00b894")

    def browse_folder(self):
        path = filedialog.askdirectory(title=self.t('select_folder'))
        if path:
            self.game_path_var.set(path)
            self.game_path = Path(path)
            self.status_label.configure(text=self.t('game_selected', self.game_path.name), text_color="#00b894")
            
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
        self.apply_filter()
            
    def apply_filter(self):
        """Applica filtro alla lista scelte"""
        self.filter_mode = self.filter_var.get()
        self.choices_list.delete(*self.choices_list.get_children())
        
        for idx, choice in enumerate(self.choices):
            score = choice['total_score']
            if self.filter_mode == 'best' and score <= 0:
                continue
            elif self.filter_mode == 'neutral' and score != 0:
                continue
            elif self.filter_mode == 'bad' and score >= 0:
                continue
            
            hint = choice.get('hint_text_custom') or choice.get('hint_text', '')
            display_text = f"{choice['choice_text'][:40]}  ({hint})" if hint else choice['choice_text'][:50]
            self.choices_list.insert('', 'end', iid=str(idx), values=(
                display_text,
                score,
                Path(choice['file']).name
            ))
    
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
            
    def on_choice_select(self, event):
        selection = self.choices_list.selection()
        if selection:
            idx = int(selection[0])
            choice = self.choices[idx]
            current_hint = choice.get('hint_text_custom') or choice.get('hint_text', '')
            self.choice_edit_var.set(current_hint)
            details = f"Choice: {choice['choice_text']}\n"
            details += f"Score: {choice['total_score']}\n"
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

    def save_config(self):
        """Salva configurazione"""
        config_path = Path(__file__).parent / "config" / "choices_config.json"
        config_path.parent.mkdir(exist_ok=True)
        
        # Salva hint_text_custom indicizzati per choice_text (chiave stabile)
        hint_edits = {}
        for idx, choice in enumerate(self.choices):
            if choice.get('hint_text_custom'):
                hint_edits[choice['choice_text']] = choice['hint_text_custom']
        
        config = {
            'hint_edits': hint_edits,
            'export_mode': self.export_mode
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
        messagebox.showinfo("Saved", self.t('config_saved', config_path))
        
    def load_config(self):
        """Carica configurazione"""
        config_path = Path(__file__).parent / "config" / "choices_config.json"
        
        if not config_path.exists():
            messagebox.showwarning("Warning", self.t('no_config'))
            return
            
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        hint_edits = config.get('hint_edits', {})
        self.export_mode = config.get('export_mode', 'all')
        self.export_var.set(self.export_mode)
        
        # Applica hint_text_custom alle scelte correnti
        for choice in self.choices:
            ct = choice['choice_text']
            if ct in hint_edits:
                choice['hint_text_custom'] = hint_edits[ct]
        
        self.apply_filter()
        messagebox.showinfo("Loaded", self.t('config_loaded', len(hint_edits)))


def main():
    root = ctk.CTk()
    app = RenPyWTTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()
