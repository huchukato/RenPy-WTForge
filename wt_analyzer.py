#!/usr/bin/env python3
"""
Ren'Py WTForge - Analyzer Module
Analizza i file .rpy per trovare scelte e variabili
Basato sul codice originale di fergz
"""

import os
import re
import io
from pathlib import Path
from collections import defaultdict


class WTAnalyzer:
    def __init__(self):
        """Inizializza l'analizzatore"""
        # Configurazione
        self.vars_to_check = ['cheat', 'harem', 'developer', 'brawlerStoryFight', 
                              'minigames', 'name', 'bios', '()', 'persistent', 'renpy', 
                              'achievement', 'config', '_preferences', 'imagebutton', 
                              'guideSuggestedPage', 'phone_call', 'timer_range', 'swypes', 'swyper']
        
        self.blocks_to_check = ['init', 'python']
        self.ifelse = ['if', 'else', 'elif']
        self.dont_extract_points_from = ['False', 'True', 'if', 'else', 'elif']
        
        # Colori per evidenziazione
        self.color_positive = '#00b894'  # verde
        self.color_negative = '#d63031'  # rosso
        self.color_neutral = '#0984e3'   # blu
        
        # Dati analizzati
        self.variables = {}  # {var_name: {info}}
        self.choices = []    # Lista di tutte le scelte trovate
        
    def match_choice(self, line):
        """Verifica se la linea è una scelta"""
        return re.compile(r"\".*\".*:").match(line) is not None
    
    def match_normal_variable(self, line):
        """Verifica se la linea è una variabile normale"""
        return re.compile(r"\$\ ?[a-zA-Z_.]+ ?\-?\+?= ?\d").match(line) is not None
    
    def match_bracket_variable(self, line):
        """Verifica se la linea è una variabile con parentesi"""
        return re.compile(r"\$\ ?[a-zA-Z_.]+ ?\(-?\d\)").match(line) is not None
    
    def match_setter_var(self, line):
        """Verifica se la linea è una variabile setter"""
        return (re.compile(r"\$ ?[a-zA-Z0-9_.]+ ?= ?True?").match(line) is not None or 
                re.compile(r"\$ ?[a-zA-Z0-9_.]+ ?= ?False?").match(line) is not None or 
                re.compile(r"\$ ?[a-zA-Z0-9_.]+ ?= ?-?\d").match(line) is not None)
    
    def match_function_call(self, line):
        """Verifica se la linea è una chiamata a funzione con argomento numerico finale"""
        return (re.compile(r"\$ ?[a-zA-Z_][a-zA-Z0-9_]*\([^)]*-?\d+\)").match(line) is not None and
                not any(s in line for s in self.vars_to_check))

    def match_variables(self, line):
        """Verifica se la linea contiene variabili da estrarre"""
        return ((self.match_normal_variable(line) or self.match_bracket_variable(line) or 
                 self.match_setter_var(line) or self.match_function_call(line)) and 
                not any(s in line for s in self.vars_to_check))
    
    def is_number(self, x):
        """Verifica se x è un numero"""
        return re.match("-?[0-9]+([.][0-9]+)?$", x) is not None
    
    def cleanup_variable(self, variable):
        """Pulisce la variabile rimuovendo commenti"""
        temp = variable
        if '#' in temp:
            hash_index = temp.index('#')
            temp = temp[:hash_index]
        return temp
    
    def get_bool_score(self, vars):
        """Calcola score da variabili booleane: True=+1, False=-1"""
        score = 0
        has_bool = False
        for var in vars:
            if '= True' in var or '=True' in var:
                score += 1
                has_bool = True
            elif '= False' in var or '=False' in var:
                score -= 1
                has_bool = True
        return score if has_bool else None

    def get_func_call_score(self, line):
        """Estrae il valore numerico finale da una chiamata a funzione"""
        m = re.search(r',?\s*(-?\d+)\s*\)\s*$', line)
        if m:
            return int(m.group(1))
        # Solo un argomento numerico: func(5) o func(-3)
        m = re.search(r'\(\s*(-?\d+)\s*\)', line)
        if m:
            return int(m.group(1))
        return 0

    def get_num_from_list(self, vars):
        """Calcola il punteggio totale da una lista di variabili"""
        num = 0
        for i in vars:
            if i.startswith('jump:'):
                continue
            clean = i.lstrip(':')
            # Chiamate a funzione: score dall'ultimo argomento numerico
            if self.match_function_call(clean):
                num += self.get_func_call_score(clean)
                continue
            if any(s in i for s in self.dont_extract_points_from) or self.match_setter_var(i):
                continue
            stripped = i.replace(':$', '').replace(')', '').replace('(', '+').replace('$', '').replace('=', '').strip().split(' ')
            try:
                if len(stripped) == 3:
                    num += int(stripped[-2] + stripped[-1])  # $ asdf += 3
                elif len(stripped) == 2:
                    num = num - int(stripped[1]) if '-' in stripped[0] else num + int(stripped[1])  # $ asdf+= 2
                elif len(stripped) == 1:  # $ asd+=3 // $ dk(1)
                    l = '-' + stripped[0].split('-')[-1] if '-' in stripped[0] else stripped[0].split('+')[-1]
                    if self.is_number(l):
                        num += int(l)
            except (ValueError, IndexError):
                continue
        return num
    
    def extract_variable_name(self, var_line):
        """Estrae il nome della variabile da una linea"""
        clean = var_line.lstrip(':').strip()
        
        # Chiamate a funzione: $ func_name("arg", number) o $ func_name(number)
        m = re.match(r'\$ ?([a-zA-Z_][a-zA-Z0-9_]*)\(', clean)
        if m:
            func_name = m.group(1)
            # Primo argomento stringa (es. "alice") -> usalo come parte del nome
            str_arg = re.search(r'["\']([a-zA-Z_][a-zA-Z0-9_]*)["\']', clean)
            if str_arg:
                arg = str_arg.group(1)
                # change_relationship("alice") -> rel_alice
                if 'relationship' in func_name:
                    return f'rel_{arg}'
                # change_stat("love") o change_anything("name") -> usa la stringa come nome
                return arg
            return func_name
        
        # Variabili normali: rimuovi $, =, +, -, parentesi
        cleaned = clean.replace('$', '').replace('=', '').replace('+', '').replace('-', '')
        cleaned = cleaned.replace('(', '').replace(')', '').strip()
        parts = cleaned.split()
        if parts:
            return parts[0]
        return cleaned
    
    def generate_hint_text(self, var_info, jump_label=None):
        """Genera l'hint text automatico dalle variabili (es. 'rel_alice +1, ch2sharing +1')"""
        parts = []
        for v in var_info:
            val = v['value']
            sign = '+' if val >= 0 else ''
            parts.append(f"{v['name']} {sign}{val}")
        if jump_label:
            parts.append(f">> {jump_label}")
        return ', '.join(parts)

    def read_if_statement(self, data, indent):
        """Legge le variabili in un blocco if"""
        vars = []
        for value in data:
            cur_ind = len(value) - len(value.lstrip())
            exact_line = value.strip()
            if cur_ind != indent:
                break
            else:
                if any(exact_line.startswith(s) for s in self.ifelse):
                    break
                else: 
                    if self.match_variables(exact_line): 
                        vars.append(':' + exact_line)
        if len(vars):
            return vars
        else:
            return None
    
    def match_jump(self, line):
        """Verifica se la linea è un jump"""
        return re.match(r'^jump\s+\w+', line) is not None

    def extract_jump_label(self, line):
        """Estrae il label da un jump"""
        m = re.match(r'^jump\s+(\w+)', line)
        return m.group(1) if m else None

    def predict_label_choices(self, data, label):
        """Legge le variabili nel label di destinazione del jump (come fergz)"""
        full_label = 'label ' + label + ':\n'
        vars = []
        try:
            label_index = data.index(full_label)
            to_check = data[label_index + 1:]
            for line in to_check:
                stripped = line.strip()
                if (any(stripped.startswith(b) for b in self.blocks_to_check) or
                        'jump' in stripped or
                        self.match_choice(stripped) or
                        any(stripped.startswith(s) for s in self.ifelse)):
                    break
                if self.match_variables(stripped) and not any(s in stripped for s in self.vars_to_check):
                    vars.append(stripped)
            return vars if vars else None
        except Exception:
            return None

    def read_until_choice(self, data, start_index):
        """Legge le variabili dopo una scelta fino alla prossima scelta"""
        vars = []
        try:
            if data[0].strip():
                ind_to_check = len(data[0]) - len(data[0].lstrip())
            else:
                for j in data:
                    if j.strip():
                        ind_to_check = len(j) - len(j.lstrip())
                        break
        except:
            return []
            
        for index, line in enumerate(data):
            exact_line = line.strip()
            cur_ind = len(line) - len(line.lstrip())
            
            if (exact_line.startswith('"') and self.match_choice(exact_line)) or \
               (exact_line.startswith('label') and exact_line.endswith(':') and cur_ind != ind_to_check) or \
               (any(exact_line.startswith(s) for s in self.blocks_to_check) and exact_line.endswith(':')):
                break
            elif any(exact_line.startswith(s) for s in self.ifelse) and cur_ind == ind_to_check and \
                 not any(s in exact_line for s in self.vars_to_check):
                if len(vars) and any(vars[-1].startswith(s) for s in self.ifelse):
                    vars.remove(vars[-1])
                vars.append(exact_line)
                if data[index + 1].strip():
                    ind = len(data[index + 1]) - len(data[index + 1].lstrip())
                else:
                    for j in data:
                        if j.strip():
                            ind = len(j) - len(j.lstrip())
                            break
                if_vars = self.read_if_statement(data[index + 1:], ind)
                try:                
                    vars += if_vars if if_vars else []
                except:
                    if (exact_line.startswith('else') or exact_line.startswith('elif')) and exact_line in vars:
                        vars.remove(exact_line)
            elif self.match_variables(exact_line) and not any(data[index-1].strip().startswith(s) for s in self.ifelse) \
                 and not exact_line in vars:
                if ':' + exact_line not in vars and cur_ind == ind_to_check:
                    if len(vars) and any(vars[-1].startswith(s) for s in self.ifelse):
                        vars.pop()               
                    vars.append(self.cleanup_variable(exact_line))   
            elif cur_ind != ind_to_check and self.match_variables(exact_line) and \
                 (exact_line not in vars and ':' + exact_line not in vars):
                break
            elif self.match_jump(exact_line) and cur_ind == ind_to_check:
                label = exact_line.split()[-1]
                if 'jump:jump ' + label not in vars and not any(v.startswith('jump:') for v in vars):
                    label_vars = self.predict_label_choices(data, label)
                    if label_vars:
                        vars += label_vars
                    else:
                        vars.append('jump:' + exact_line)
        return vars
    
    def analyze_file(self, file_path):
        """Analizza un singolo file .rpy"""
        try:
            with io.open(file_path, 'r', encoding='utf-8') as f:
                data = f.readlines()
        except:
            return
        
        for index, line in enumerate(data):
            exact_line = line.strip()
            if exact_line.startswith('"') and self.match_choice(exact_line):
                vars = self.read_until_choice(data[index + 1:], index + 1)
                if len(vars) and any(vars[-1].startswith(s) for s in self.ifelse):
                    vars.pop()

                # Calcola punteggio e variabili (anche se vars è vuoto → jump-only)
                score = self.get_num_from_list(vars) if vars else 0
                bool_score = self.get_bool_score(vars) if vars else None
                if score == 0 and bool_score is not None:
                    score = bool_score

                var_info = []
                jump_label = None
                for var in vars:
                    if var.startswith('jump:'):
                        jump_label = self.extract_jump_label(var[5:])
                        continue
                    clean = var.lstrip(':')
                    var_name = self.extract_variable_name(clean)
                    var_value = self.get_num_from_list([clean])
                    if var_value == 0 and self.match_setter_var(clean):
                        if '= True' in clean or '=True' in clean:
                            var_value = 1
                        elif '= False' in clean or '=False' in clean:
                            var_value = -1
                    var_info.append({
                        'name': var_name,
                        'original_line': clean,
                        'value': var_value
                    })
                    if var_name not in self.variables:
                        self.variables[var_name] = {
                            'display_name': var_name,
                            'description': '',
                            'occurrences': 0
                        }
                    self.variables[var_name]['occurrences'] += 1

                hint_text = self.generate_hint_text(var_info, jump_label)

                raw_choice = exact_line.strip('"').rstrip(':')
                # Rimuovi condizione if ... (es. "testo" if var == False)
                if '" if ' in raw_choice:
                    raw_choice = raw_choice.split('" if ')[0].strip('"').strip("'")

                choice_data = {
                    'file': str(file_path),
                    'line': index + 1,
                    'choice_text': raw_choice,
                    'variables': var_info,
                    'total_score': score,
                    'is_best': score > 0,
                    'hint_text': hint_text,
                    'hint_text_custom': None
                }
                self.choices.append(choice_data)
    
    def analyze_directory(self, directory):
        """Analizza tutti i file .rpy in una directory"""
        rpy_files = list(Path(directory).rglob("*.rpy"))
        
        # Escludi file di sistema e cartella wtmod generata da WTForge
        exclude_files = ['gui.rpy', 'screens.rpy', 'options.rpy', 'images.rpy', 'gallery.rpy']
        rpy_files = [f for f in rpy_files
                     if f.name not in exclude_files
                     and 'wtmod' not in f.parts]
        
        print(f"Analisi di {len(rpy_files)} file .rpy...")
        
        for rpy_file in rpy_files:
            self.analyze_file(rpy_file)
        
        print(f"Trovate {len(self.choices)} scelte")
        print(f"Trovate {len(self.variables)} variabili uniche")
        
        return self.choices, self.variables
    
    def get_best_choices(self):
        """Restituisce le scelte migliori per ogni gruppo"""
        # Raggruppa scelte per contesto (file + linee vicine)
        best_choices = []
        for choice in self.choices:
            if choice['is_best']:
                best_choices.append(choice)
        return best_choices


if __name__ == "__main__":
    # Test del modulo
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python wt_analyzer.py <directory_game>")
        sys.exit(1)
        
    game_dir = sys.argv[1]
    analyzer = WTAnalyzer()
    
    choices, variables = analyzer.analyze_directory(game_dir)
    
    print(f"\nVariabili trovate:")
    for var_name, var_info in variables.items():
        print(f"  {var_name}: {var_info['occurrences']} occorrenze")
    
    print(f"\nPrime 5 scelte:")
    for choice in choices[:5]:
        print(f"  {choice['choice_text']} (score: {choice['total_score']})")
