#!/usr/bin/env python3
"""
Ren'Py WTForge - Generator Module
Genera i file mod per il walkthrough
"""

import os
import re
import json
from pathlib import Path


class WTGenerator:
    def __init__(self, game_path, export_mode='all'):
        """
        Inizializza il generatore
        
        Args:
            game_path: Percorso al gioco
            export_mode: 'all' per tutte le scelte, 'best' per solo le migliori
        """
        self.game_path = Path(game_path)
        self.export_mode = export_mode
        
        # Determina il percorso di output corretto in base alla piattaforma
        if self.game_path.suffix == '.app':
            # macOS .app: NomeGioco.app/Contents/Resources/autorun/game/wtmod
            self.output_dir = self.game_path / "Contents" / "Resources" / "autorun" / "game" / "wtmod"
        else:
            # Windows/Linux: NomeGioco/game/wtmod
            self.output_dir = self.game_path / "game" / "wtmod"
        
        # Colori
        self.color_positive = '#00b894'  # verde
        self.color_negative = '#d63031'  # rosso
        self.color_neutral = '#0984e3'   # blu
        
    def get_color(self, total_score):
        """Restituisce il colore in base al punteggio"""
        if total_score > 0:
            return self.color_positive
        elif total_score < 0:
            return self.color_negative
        else:
            return self.color_neutral
    
    def filter_choices(self, choices):
        """Filtra le scelte in base alla modalità di esportazione"""
        if self.export_mode == 'best':
            return [choice for choice in choices if choice['total_score'] > 0]
        return choices
        
    def create_output_directory(self):
        """Crea la directory di output"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_hint_text(self, variables):
        """Genera il testo hint dalle variabili"""
        hint_parts = []
        for var in variables:
            var_name = var['name']
            var_value = var['value']
            
            # Formatta il valore
            if var_value > 0:
                hint_parts.append(f"{var_name} +{var_value}")
            elif var_value < 0:
                hint_parts.append(f"{var_name} {var_value}")
            else:
                hint_parts.append(var_name)
                
        return ', '.join(hint_parts)
    
    def get_game_dir(self):
        """Restituisce la directory game/ in base alla piattaforma"""
        if self.game_path.suffix == '.app':
            return self.game_path / "Contents" / "Resources" / "autorun" / "game"
        return self.game_path / "game"

    def load_tl_translations(self):
        """Legge tutti i file tl/ e restituisce {original: [translated, ...]} per le scelte menu"""
        tl_dir = self.get_game_dir() / "tl"
        if not tl_dir.exists():
            return {}

        translations = {}  # {original_text: [translation1, translation2, ...]}
        re_old = re.compile(r'^\s*old\s+"(.+)"\s*$')
        re_new = re.compile(r'^\s*new\s+"(.+)"\s*$')

        for rpy_file in tl_dir.rglob("*.rpy"):
            try:
                with open(rpy_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                i = 0
                while i < len(lines) - 1:
                    m_old = re_old.match(lines[i])
                    if m_old:
                        m_new = re_new.match(lines[i + 1])
                        if m_new:
                            orig = m_old.group(1)
                            transl = m_new.group(1)
                            if orig != transl:
                                translations.setdefault(orig, [])
                                if transl not in translations[orig]:
                                    translations[orig].append(transl)
                        i += 2
                        continue
                    i += 1
            except Exception:
                pass

        return translations

    def get_hint_for_choice(self, choice):
        """Restituisce l'hint text da usare (custom se disponibile, altrimenti auto)"""
        if choice.get('hint_text_custom'):
            return choice['hint_text_custom']
        return choice.get('hint_text', self.generate_hint_text(choice['variables']))

    def generate_main_mod_file(self, choices):
        """Genera il file mod principale con il dizionario hint e la screen choice_custom"""
        # Carica traduzioni tl/ esistenti
        tl_map = self.load_tl_translations()

        # Costruisce il dizionario: {choice_text: (color, hint)}
        entries = []
        seen_keys = set()

        def add_entry(text, color, hint):
            raw = text.strip('"').strip("'")
            safe_t = raw.replace('\\', '\\\\').replace('"', '\\"')
            safe_h = hint.replace('\\', '\\\\').replace('"', '\\"')
            if safe_t not in seen_keys:
                seen_keys.add(safe_t)
                entries.append(f'    "{safe_t}": ("{color}", "{safe_h}"),')

        for choice in choices:
            color = self.get_color(choice['total_score'])
            hint = self.get_hint_for_choice(choice)
            raw_text = choice['choice_text'].strip('"').strip("'")
            # Rimuovi condizione if ... residua (es. testo" if var == False)
            if '" if ' in raw_text:
                raw_text = raw_text.split('" if ')[0].strip('"').strip("'")
            add_entry(raw_text, color, hint)
            # Aggiungi anche le traduzioni corrispondenti
            for transl in tl_map.get(raw_text, []):
                add_entry(transl, color, hint)

        entries_str = '\n'.join(entries)

        mod_content = f'''# Ren\'Py WTForge - Generated Walkthrough Mod
# DO NOT EDIT MANUALLY - Regenerate with WTForge

init python:
    wtmod_version = "1.0"
    wtmod_enabled = True
    # choice_text -> (color, hint_text)
    wtmod_hints = {{
{entries_str}
    }}

screen choice(items):
    style_prefix "choice"
    vbox:
        for i in items:
            $ _d = wtmod_hints.get(i.caption, (None, None))
            $ _lbl = ("{{color=" + _d[0] + "}}" + i.caption + "{{/color}}" + ("  {{color=#aaaaaa}}{{size=-8}}(" + _d[1] + "){{/size}}{{/color}}" if _d[1] else "")) if _d[0] else i.caption
            textbutton _lbl action i.action
'''
        return mod_content

    def generate_screens_mod(self):
        """Genera il file mod per screens (solo stub)"""
        return '''# Ren\'Py WTForge - Screens stub
init python:
    wtmod_enabled = True
'''
    
    def generate_config_file(self, variables):
        """Genera il file di configurazione JSON"""
        config = {
            "version": "1.0",
            "variables": {}
        }
        
        for var_name, var_info in variables.items():
            config["variables"][var_name] = {
                "display_name": var_info['display_name'],
                "description": var_info.get('description', ''),
                "occurrences": var_info.get('occurrences', 0)
            }
        
        return json.dumps(config, indent=2)
    
    def generate_mod(self, choices, variables):
        """Genera tutti i file mod"""
        self.create_output_directory()
        
        # Filtra le scelte in base alla modalità di esportazione
        filtered_choices = self.filter_choices(choices)
        
        # Genera file mod principale
        main_mod = self.generate_main_mod_file(filtered_choices)
        main_mod_path = self.output_dir / "wtmod.rpy"
        with open(main_mod_path, 'w', encoding='utf-8') as f:
            f.write(main_mod)
        
        # Genera file screens mod
        screens_mod = self.generate_screens_mod()
        screens_mod_path = self.output_dir / "wtmod_screens.rpy"
        with open(screens_mod_path, 'w', encoding='utf-8') as f:
            f.write(screens_mod)
        
        # Genera file configurazione
        config_json = self.generate_config_file(variables)
        config_path = self.output_dir / "wtmod_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_json)
        
        print(f"Mod generati in: {self.output_dir}")
        print(f"  - wtmod.rpy")
        print(f"  - wtmod_screens.rpy")
        print(f"  - wtmod_config.json")
        
        return True
    
    def generate_gallery_unlocker(self):
        """Genera il contenuto del file Gallery Unlocker"""
        return """# Ren'Py WTForge - Gallery Unlocker
# Generated automatically. Compatible with most Ren'Py games.
# Runs at init priority 666 (after all game code).

init 666 python:
    # Method 1: award_manager-based gallery (used by some games)
    try:
        if hasattr(store, 'award_manager') and award_manager is not None:
            for item in award_manager.awards:
                try:
                    renpy.mark_image_seen(item.unlock_str)
                    item.unlock()
                except Exception:
                    pass
    except Exception:
        pass

    # Method 2: mark all registered images as seen (universal fallback)
    try:
        for img in renpy.list_images():
            try:
                renpy.mark_image_seen(img)
            except Exception:
                pass
    except Exception:
        pass

    # Method 3: unlock all persistent gallery flags if present
    try:
        if hasattr(persistent, 'gallery_unlocked'):
            persistent.gallery_unlocked = True
    except Exception:
        pass

    # Method 4: pattern ["scene_name", False] - used by many Ren'Py games
    try:
        for key in dir(persistent):
            try:
                val = getattr(persistent, key)
                if isinstance(val, list) and len(val) == 2 and isinstance(val[0], str) and isinstance(val[1], bool):
                    val[1] = True
            except Exception:
                pass
    except Exception:
        pass

    # Method 5: Gallery object with unlocked attribute
    try:
        if hasattr(store, 'gallery') and hasattr(store.gallery, 'unlocked_all'):
            store.gallery.unlocked_all()
    except Exception:
        pass
"""

    def export_gallery_unlocker(self):
        """Scrive il file Gallery Unlocker nella directory di output"""
        self.create_output_directory()
        gallery_path = self.output_dir / "wtmod_gallery.rpy"
        with open(gallery_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_gallery_unlocker())
        return gallery_path

    def load_config(self, config_path):
        """Carica la configurazione da un file JSON"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('variables', {})
        except:
            return {}


if __name__ == "__main__":
    # Test del modulo
    import sys
    
    # Test data
    test_variables = {
        'points_sue': {'display_name': 'Love with Sue', 'description': 'Relazione con Sue', 'occurrences': 50},
        'money': {'display_name': 'Soldi', 'description': 'Budget', 'occurrences': 30}
    }
    
    test_choices = [
        {
            'file': '/tmp/script.rpy',
            'line': 100,
            'choice_text': 'Vai al parco',
            'variables': [
                {'name': 'points_sue', 'value': 2, 'original_line': '$ points_sue += 2'},
                {'name': 'money', 'value': -10, 'original_line': '$ money -= 10'}
            ],
            'total_score': 2,
            'is_best': True
        }
    ]
    
    generator = WTGenerator('/tmp/test_game', test_variables)
    generator.generate_mod(test_choices, test_variables)
