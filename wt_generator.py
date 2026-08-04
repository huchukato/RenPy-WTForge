#!/usr/bin/env python3
"""
Ren'Py WTForge - Generator Module
Genera i file mod per il walkthrough
"""

import os
import re
import json
from pathlib import Path

from wt_effects import WTVariableFilter


class WTGenerator:
    def __init__(self, game_path, export_mode='all', variable_filter=None, route_name=''):
        """
        Inizializza il generatore

        Args:
            game_path: Percorso al gioco
            export_mode: 'all' per tutte le scelte, 'best' per solo le migliori
            variable_filter: WTVariableFilter per escludere variabili non rilevanti
            route_name: nome della route (es. 'elea') per file distinti
        """
        self.game_path = Path(game_path)
        self.export_mode = export_mode
        self.variable_filter = variable_filter or WTVariableFilter()
        self.route_name = route_name
        
        # Determina il percorso di output corretto in base alla piattaforma
        if self.game_path.suffix == '.app':
            # macOS .app: NomeGioco.app/Contents/Resources/autorun/game/wtmod
            self.output_dir = self.game_path / "Contents" / "Resources" / "autorun" / "game" / "wtmod"
        else:
            # Windows/Linux: NomeGioco/game/wtmod
            self.output_dir = self.game_path / "game" / "wtmod"
        
        # Colori
        self.color_positive = '#22c55e'  # verde
        self.color_negative = '#d63031'  # rosso
        self.color_neutral = '#86878a'   # grigio
        self.hint_color = '#facc15'      # giallo brillante per hint
        
    def get_color(self, total_score):
        """Restituisce il colore in base al punteggio"""
        if total_score > 0:
            return self.color_positive
        elif total_score < 0:
            return self.color_negative
        else:
            return self.color_neutral
    
    def get_override_color(self, override):
        """Restituisce il colore per override manuale"""
        if override == 'best':
            return self.color_positive
        elif override == 'bad':
            return self.color_negative
        elif override == 'neutral':
            return self.color_neutral
        return self.get_color(0)
    
    def get_choice_score(self, choice):
        """Restituisce lo score filtrato se disponibile, altrimenti il totale"""
        return choice.get('filtered_score', choice['total_score'])

    def is_choice_best(self, choice):
        """True se la scelta è la migliore considerando il filtro variabili"""
        return choice.get('is_best_filtered', choice.get('is_best', self.get_choice_score(choice) > 0))

    def filter_choices(self, choices):
        """Filtra le scelte in base alla modalità di esportazione"""
        if self.export_mode == 'best':
            return [choice for choice in choices if self.is_choice_best(choice)]
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

    def generate_hint_text_from_effects(self, effects):
        """Genera hint testo solo dagli effetti rilevanti per il filtro attivo."""
        if not effects:
            return ''
        relevant = self.variable_filter.filtered_effects(effects)
        if not relevant:
            return ''
        parts = []
        for e in relevant:
            var = e['var']
            val = e.get('value') or 0
            if val > 0:
                parts.append(f"{var} +{val}")
            elif val < 0:
                parts.append(f"{var} {val}")
            else:
                parts.append(var)
        return ', '.join(parts)
    
    def get_game_dir(self):
        """Restituisce la directory game/ in base alla piattaforma"""
        if self.game_path.suffix == '.app':
            return self.game_path / "Contents" / "Resources" / "autorun" / "game"
        return self.game_path / "game"

    def find_custom_choice_screens(self):
        """Cerca nel gioco menu che usano screen personalizzate (es. menu(screen='choice_custom'))"""
        screens = set()
        game_dir = self.get_game_dir()
        pattern = re.compile(r'menu\s*\(\s*screen\s*=\s*["\']([^"\']+)["\']\s*\)')
        for rpy_file in game_dir.rglob('*.rpy'):
            try:
                with open(rpy_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        m = pattern.search(line)
                        if m:
                            screens.add(m.group(1))
            except Exception:
                pass
        return screens

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
        """Restituisce l'hint text da usare (custom se disponibile, altrimenti filtrato)"""
        if choice.get('hint_text_custom'):
            return choice['hint_text_custom']
        # Se ci sono gli effetti estratti, mostra solo quelli rilevanti
        if 'effects' in choice:
            return self.generate_hint_text_from_effects(choice['effects'])
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
            score = self.get_choice_score(choice)
            if choice.get('color_override') == 'none':
                # Lascia la scelta esattamente come nel gioco originale
                color = ''
                hint = ''
            elif choice.get('color_override'):
                color = self.get_override_color(choice['color_override'])
                hint = self.get_hint_for_choice(choice)
            elif score == 0:
                # Scelte neutre senza override: lascia colore originale del gioco
                color = ''
                hint = ''
            else:
                color = self.get_color(score)
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
    wtmod_hint_color = "#facc15"
    # choice_text -> (color, hint_text)
    wtmod_hints = {{
{entries_str}
    }}

screen choice(items):
    style_prefix "choice"
    vbox:
        for i in items:
            $ _d = wtmod_hints.get(i.caption, (None, None))
            $ _lbl = ("{{color=" + _d[0] + "}}" + i.caption + "{{/color}}" + ("  {{color=" + wtmod_hint_color + "}}{{size=-8}}(" + _d[1] + "){{/size}}{{/color}}" if _d[1] else "")) if _d[0] else i.caption
            textbutton _lbl action i.action
'''
        # Override per eventuali screen di scelta personalizzate (es. choice_custom)
        custom_screens = self.find_custom_choice_screens()
        for name in sorted(custom_screens):
            if name == 'choice':
                continue
            mod_content += f'''
screen {name}(items):
    tag menu
    modal True
    use choice(items)
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

        # Suffix per route
        suffix = f"_{self.route_name}" if self.route_name else ''

        # Genera file mod principale
        main_mod = self.generate_main_mod_file(filtered_choices)
        main_mod_path = self.output_dir / f"wtmod{suffix}.rpy"
        with open(main_mod_path, 'w', encoding='utf-8') as f:
            f.write(main_mod)

        # Genera file screens mod
        screens_mod = self.generate_screens_mod()
        screens_mod_path = self.output_dir / f"wtmod{suffix}_screens.rpy"
        with open(screens_mod_path, 'w', encoding='utf-8') as f:
            f.write(screens_mod)

        # Genera file configurazione
        config_json = self.generate_config_file(variables)
        config_path = self.output_dir / f"wtmod{suffix}_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_json)

        print(f"Mod generati in: {self.output_dir}")
        print(f"  - wtmod{suffix}.rpy")
        print(f"  - wtmod_screens{suffix}.rpy")
        print(f"  - wtmod_config{suffix}.json")

        return True
    
    def generate_gallery_unlocker(self, detection=None):
        """Genera il contenuto del file Gallery Unlocker"""
        detection = detection or {}
        lines = [
            "# Ren'Py WTForge - Gallery Unlocker",
            "# Generated automatically. Compatible with most Ren'Py games.",
            "# Runs at init priority 666 (after all game code).",
            "",
            "init 666 python:",
        ]

        # Targeted blocks from detected systems
        if detection.get('award_manager'):
            lines.extend([
                "    # Detected: award_manager",
                "    try:",
                "        if hasattr(store, 'award_manager') and award_manager is not None:",
                "            for item in award_manager.awards:",
                "                try:",
                "                    renpy.mark_image_seen(item.unlock_str)",
                "                    item.unlock()",
                "                except Exception:",
                "                    pass",
                "    except Exception:",
                "        pass",
                "",
            ])

        for name in detection.get('gallery_objects', []):
            lines.extend([
                f"    # Detected: Gallery object '{name}'",
                "    try:",
                f"        _gallery_obj = getattr(store, {name!r}, None)",
                "        if _gallery_obj is not None:",
                "            for _btn in getattr(_gallery_obj, 'buttons', []):",
                "                try:",
                "                    _gallery_obj.unlock(_btn)",
                "                except Exception:",
                "                    pass",
                "            for _img in getattr(_gallery_obj, 'images', []):",
                "                try:",
                "                    _gallery_obj.unlock(_img)",
                "                    renpy.mark_image_seen(_img)",
                "                except Exception:",
                "                    pass",
                "            for _cond in list(getattr(_gallery_obj, 'conditions', {}).keys()):",
                "                try:",
                "                    _gallery_obj.unlock(_cond)",
                "                except Exception:",
                "                    pass",
                "            if hasattr(_gallery_obj, 'unlocked_all'):",
                "                try:",
                "                    _gallery_obj.unlocked_all()",
                "                except Exception:",
                "                    pass",
                "    except Exception:",
                "        pass",
                "",
            ])

        for var in detection.get('persistent_vars', []):
            lines.extend(self._generate_persistent_var_block(var))

        # Fallback methods
        lines.extend(self._gallery_fallback_lines())
        return "\n".join(lines)

    def _generate_persistent_var_block(self, var):
        """Genera il blocco di unlock per una variabile persistente rilevata"""
        name = var['name']
        shape = var.get('shape', 'unknown')
        block = [f"    # Detected persistent variable: {name} ({shape})", "    try:"]
        if shape == 'set':
            block.extend([
                f"        _val = getattr(persistent, {name!r}, set())",
                "        if isinstance(_val, set):",
                "            _val.update(set(renpy.list_images()))",
                f"        setattr(persistent, {name!r}, _val)",
            ])
        elif shape == 'dict':
            block.extend([
                f"        _val = getattr(persistent, {name!r}, {{}})",
                "        if isinstance(_val, dict):",
                "            for _k in list(_val.keys()):",
                "                _val[_k] = True",
                "            for _img in renpy.list_images():",
                "                _val[_img] = True",
                f"        setattr(persistent, {name!r}, _val)",
            ])
        elif shape == 'list':
            block.extend([
                f"        _val = getattr(persistent, {name!r}, [])",
                "        if isinstance(_val, list):",
                "            for _i in range(len(_val)):",
                "                _item = _val[_i]",
                "                if isinstance(_item, bool):",
                "                    _val[_i] = True",
                "                elif isinstance(_item, (list, tuple)) and len(_item) == 2:",
                "                    _item[1] = True",
                "            for _img in renpy.list_images():",
                "                if _img not in _val:",
                "                    _val.append(_img)",
                f"        setattr(persistent, {name!r}, _val)",
            ])
        elif shape == 'bool':
            block.extend([
                f"        setattr(persistent, {name!r}, True)",
            ])
        else:
            block.extend([
                f"        _val = getattr(persistent, {name!r}, None)",
                "        if isinstance(_val, dict):",
                "            for _k in list(_val.keys()):",
                "                _val[_k] = True",
                "        elif isinstance(_val, set):",
                "            _val.update(set(renpy.list_images()))",
                "        elif isinstance(_val, list):",
                "            for _pair in _val:",
                "                if isinstance(_pair, (list, tuple)) and len(_pair) == 2:",
                "                    _pair[1] = True",
                "        elif isinstance(_val, bool):",
                f"            setattr(persistent, {name!r}, True)",
            ])
        block.extend(["    except Exception:", "        pass", ""])
        return block

    def _gallery_fallback_lines(self):
        """Restituisce i metodi fallback universali"""
        return [
            "    # Fallback methods for unknown gallery systems",
            "    try:",
            "        if hasattr(store, 'award_manager') and award_manager is not None:",
            "            for item in award_manager.awards:",
            "                try:",
            "                    renpy.mark_image_seen(item.unlock_str)",
            "                    item.unlock()",
            "                except Exception:",
            "                    pass",
            "    except Exception:",
            "        pass",
            "",
            "    try:",
            "        for img in renpy.list_images():",
            "            try:",
            "                renpy.mark_image_seen(img)",
            "                renpy.mark_seen(img)",
            "            except Exception:",
            "                pass",
            "    except Exception:",
            "        pass",
            "",
            "    try:",
            "        for _lbl in renpy.get_all_labels():",
            "            try:",
            "                renpy.mark_seen(_lbl)",
            "            except Exception:",
            "                pass",
            "    except Exception:",
            "        pass",
            "",
            "    try:",
            "        if hasattr(persistent, 'gallery_unlocked'):",
            "            persistent.gallery_unlocked = True",
            "    except Exception:",
            "        pass",
            "",
            "    try:",
            "        for key in dir(persistent):",
            "            try:",
            "                val = getattr(persistent, key)",
            "                if isinstance(val, bool):",
            "                    setattr(persistent, key, True)",
            "                elif isinstance(val, list):",
            "                    for _i in range(len(val)):",
            "                        _v = val[_i]",
            "                        if isinstance(_v, bool):",
            "                            val[_i] = True",
            "                        elif isinstance(_v, (list, tuple)) and len(_v) == 2 and isinstance(_v[1], bool):",
            "                            _v[1] = True",
            "                elif isinstance(val, set):",
            "                    val.update(set(renpy.list_images()))",
            "                elif isinstance(val, dict):",
            "                    for _k in list(val.keys()):",
            "                        val[_k] = True",
            "            except Exception:",
            "                pass",
            "    except Exception:",
            "        pass",
            "",
            "    try:",
            "        for _g_name in dir(store):",
            "            try:",
            "                _g = getattr(store, _g_name)",
            "                _unlock = getattr(_g, 'unlock_all', None)",
            "                if callable(_unlock):",
            "                    _unlock()",
            "            except Exception:",
            "                pass",
            "    except Exception:",
            "        pass",
            "",
            "    try:",
            "        if hasattr(store, 'gallery') and hasattr(store.gallery, 'unlocked_all'):",
            "            store.gallery.unlocked_all()",
            "    except Exception:",
            "        pass",
        ]

    def export_gallery_unlocker(self, detection=None):
        """Scrive il file Gallery Unlocker nella directory di output"""
        self.create_output_directory()
        gallery_path = self.output_dir / "wtmod_gallery.rpy"
        with open(gallery_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_gallery_unlocker(detection))
        return gallery_path

    def generate_devtools(self):
        """Genera il contenuto del file Dev Tools"""
        return """# Ren'Py WTForge - Dev Tools
# Generated automatically. Enables developer features at init priority 999.
# Delete this file to disable.

init 999 python:
    # Enable developer console (Shift+O or backtick)
    try:
        config.console = True
    except Exception:
        pass

    # Enable developer menu (Shift+D)
    try:
        config.developer = True
    except Exception:
        pass

    # Enable Quick Save (Q) and Quick Load (Alt+Q)
    try:
        config.has_quicksave = True
        config.has_autosave = True
    except Exception:
        pass

    # Force enable skipping of unseen/unread content
    try:
        config.allow_skipping = True
        _preferences.skip_unseen = True
    except Exception:
        pass

    # Force enable rollback (scroll wheel / page up)
    try:
        config.rollback_enabled = True
        config.hard_rollback_limit = -1
    except Exception:
        pass
"""

    def export_devtools(self):
        """Scrive il file Dev Tools nella directory di output"""
        self.create_output_directory()
        devtools_path = self.output_dir / "wtmod_devtools.rpy"
        with open(devtools_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_devtools())
        return devtools_path

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
