#!/usr/bin/env python3
"""
Ren'Py WTForge - Choice Effect Extractor
Estrae gli effetti (variabili modificate) dal blocco dopo ogni scelta di menu.
Inspirato a UCD_FlagExtractor di Universal Choice Descriptor.
"""

import ast
import re
from pathlib import Path


def compile_wildcard(pattern, full=True, case_sensitive=True):
    """
    Converte un pattern wildcard in regex compilato.
    Supporta:
        *   -> qualsiasi sequenza di caratteri (\\w e .)
        ?   -> un carattere
        ~x  -> case-insensitive
    """
    if not pattern:
        return None
    s = pattern
    s = s.replace("*", r"[\w.]*")
    s = s.replace("?", r"\w")
    if s.startswith("~"):
        s = "(?i)" + s[1:]
    if full:
        s += "$"
    flags = re.IGNORECASE if s.startswith("(?i)") else 0
    s = s.replace("(?i)", "")
    return re.compile("^" + s, flags)


class WTVariableFilter:
    """Filtro include/exclude per variabili, basato su wildcard."""

    def __init__(self, include=None, exclude=None):
        self.include_patterns = include or []
        self.exclude_patterns = exclude or []
        self._include = [compile_wildcard(p) for p in self.include_patterns if p]
        self._exclude = [compile_wildcard(p) for p in self.exclude_patterns if p]

    def is_relevant(self, var):
        """Ritorna True se la variabile è inclusa e non esclusa."""
        # Se include non è vuoto, la var deve matchare almeno un pattern include
        if self._include:
            if not any(p.match(var) for p in self._include if p):
                return False
        if self._exclude:
            if any(p.match(var) for p in self._exclude if p):
                return False
        return True

    def score(self, effects):
        """Somma i valori degli effetti rilevanti."""
        return sum(
            e.get('value', 0) or 0
            for e in effects
            if self.is_relevant(e.get('var', ''))
        )

    def filtered_effects(self, effects):
        """Ritorna solo gli effetti rilevanti."""
        return [e for e in effects if self.is_relevant(e.get('var', ''))]

    def concise_hint(self, effects, max_items=3):
        """Costruisce un hint breve con le variabili rilevanti più significative."""
        relevant = self.filtered_effects(effects)
        if not relevant:
            return ''
        # Ordina per impatto assoluto decrescente, poi per nome
        relevant = sorted(relevant, key=lambda e: (-abs(e.get('value', 0) or 0), e.get('var', '')))
        parts = []
        for e in relevant[:max_items]:
            var = e['var']
            val = e.get('value') or 0
            if val > 0:
                parts.append(f"{var} +{val}")
            elif val < 0:
                parts.append(f"{var} {val}")
            else:
                parts.append(var)
        return ', '.join(parts)

    def to_dict(self):
        return {
            'include': self.include_patterns,
            'exclude': self.exclude_patterns,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(d.get('include', []), d.get('exclude', []))


class WTChoiceEffectExtractor:
    """Estrae gli effetti di una scelta di menu dal codice sorgente .rpy."""

    # Assegnamenti: $ var = val, var += val, persistent.x = y, a, b = (1, 2), etc.
    _ASSIGN_RE = re.compile(
        r'^\s*(?:\$\s+)?'
        r'(?P<vars>(?:[a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*)'
        r'(?:\s*[,=]\s*[a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*)*)'
        r'\s*(?P<op>\+|-|\*\*|\*|//|/|%)?(?<!=)=(?!=)'
        r'\s*(?P<rhs>.+?)?\s*$'
    )

    # Chiamate funzione stile $ change_relationship("fiona", 1)
    _FUNC_RE = re.compile(
        r'^\s*(?:\$\s+)?'
        r'(?P<func>[a-zA-Z_]\w*)'
        r'\s*\(\s*'
        r'(?P<args>[^)]*)'
        r'\s*\)\s*$'
    )

    # if/elif/else a livello Ren'Py (con o senza $)
    _IF_RE = re.compile(r'^(?:\$\s+)?if\s+(.+?)\s*:\s*$')
    _ELIF_RE = re.compile(r'^(?:\$\s+)?elif\s+(.+?)\s*:\s*$')
    _ELSE_RE = re.compile(r'^(?:\$\s+)?else\s*:\s*$')

    # Control flow
    _JUMP_RE = re.compile(r'^jump\s+([a-zA-Z_]\w*)\s*$')
    _CALL_RE = re.compile(r'^call\s+([a-zA-Z_]\w*)\s*$')
    _RETURN_RE = re.compile(r'^return\b')
    _MENU_RE = re.compile(r'^menu\b.*:\s*$')
    _LABEL_RE = re.compile(r'^label\s+([a-zA-Z_]\w*)\s*:\s*$')
    _BLOCK_HEADER_RE = re.compile(
        r'^(?:init\s+-?\d+\s+)?(?:python|screen|image|transform|style)\s*(?::|$)'
    )

    def __init__(self, files=None):
        self.files = files or []
        self._file_cache = {}
        self._seen_labels = set()

    def _get_file_lines(self, file_path):
        if file_path in self._file_cache:
            return self._file_cache[file_path]
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception:
            lines = []
        self._file_cache[file_path] = lines
        return lines

    def _strip_comment(self, s):
        """Rimuove un commento inline se non è dentro una stringa."""
        # Approssimativo: togli il primo # che non è tra apici
        in_quote = None
        for i, c in enumerate(s):
            if c in ('"', "'"):
                if in_quote is None:
                    in_quote = c
                elif in_quote == c and (i == 0 or s[i - 1] != '\\'):
                    in_quote = None
            elif c == '#' and in_quote is None:
                return s[:i].strip()
        return s.strip()

    def extract(self, lines, start_index, base_indent, current_file=None):
        """Estrae effetti e route dal blocco che inizia a start_index."""
        self._seen_labels = set()
        return self._extract_block(lines, start_index, base_indent, current_file)

    def _extract_block(self, lines, start_index, base_indent, current_file=None):
        effects = []
        routes = []
        i = start_index
        n = len(lines)
        # stack di (body_indent, condition)
        if_stack = []

        while i < n:
            line = lines[i]
            raw = line.rstrip('\n')
            stripped = raw.lstrip()
            if not stripped or stripped.startswith('#'):
                i += 1
                continue
            indent = len(raw) - len(stripped)

            if indent <= base_indent:
                break

            text = self._strip_comment(stripped)

            # Stop espliciti
            if self._RETURN_RE.match(text) or self._MENU_RE.match(text):
                break

            m_label = self._LABEL_RE.match(text)
            if m_label and indent <= base_indent + 4:
                # Nuova label: fine blocco scelta
                break

            # Salta blocchi multilinea python/init/screen
            if self._BLOCK_HEADER_RE.match(text) and text.endswith(':'):
                block_indent = indent
                i += 1
                while i < n:
                    nl = lines[i].rstrip('\n')
                    ns = nl.lstrip()
                    if not ns or ns.startswith('#'):
                        i += 1
                        continue
                    ni = len(nl) - len(ns)
                    if ni <= block_indent:
                        break
                    i += 1
                continue

            # If / elif / else
            m_if = self._IF_RE.match(text)
            m_elif = self._ELIF_RE.match(text)
            m_else = self._ELSE_RE.match(text)
            if m_if or m_elif or m_else:
                cond = m_if.group(1) if m_if else (m_elif.group(1) if m_elif else 'else')
                # rimuovi commenti interni alla condizione
                cond = cond.split('#')[0].strip()

                # Determina l'indent del corpo
                body_indent = indent + 4
                j = i + 1
                while j < n:
                    nl = lines[j].rstrip('\n')
                    ns = nl.lstrip()
                    if ns and not ns.startswith('#'):
                        body_indent = max(body_indent, len(nl) - len(ns))
                        break
                    j += 1

                # Se siamo nello stesso blocco if di livello superiore, aggiorna condizione
                if if_stack:
                    top_if_indent = if_stack[-1][0] - 4
                    if indent == top_if_indent:
                        if_stack[-1] = (body_indent, cond)
                    elif indent > top_if_indent:
                        if_stack.append((body_indent, cond))
                    else:
                        while if_stack and (if_stack[-1][0] - 4) >= indent:
                            if_stack.pop()
                        if_stack.append((body_indent, cond))
                else:
                    if_stack.append((body_indent, cond))
                i += 1
                continue

            # Se indent diminuisce rispetto al corpo dell'if, poppa gli if
            while if_stack and indent < if_stack[-1][0]:
                if_stack.pop()

            condition = if_stack[-1][1] if if_stack else None

            # Jump: seguiamo label una volta sola e registriamo la route
            m_jump = self._JUMP_RE.match(text)
            if m_jump:
                target = m_jump.group(1)
                routes.append({'kind': 'jump', 'label': target, 'condition': condition})
                extra = self._follow_label(target, current_file)
                if extra:
                    # Applichiamo la condizione corrente a quelli seguiti
                    for e in extra:
                        e['condition'] = condition or e.get('condition')
                    effects.extend(extra)
                break

            # Call: seguiamo label, registriamo la route e poi continuiamo
            m_call = self._CALL_RE.match(text)
            if m_call:
                target = m_call.group(1)
                routes.append({'kind': 'call', 'label': target, 'condition': condition})
                extra = self._follow_label(target, current_file)
                if extra:
                    for e in extra:
                        e['condition'] = condition or e.get('condition')
                    effects.extend(extra)
                i += 1
                continue

            # Assegnamenti
            m = self._ASSIGN_RE.match(text)
            if m:
                varnames = m.group('vars')
                op_symbol = m.group('op')
                op = (op_symbol + '=') if op_symbol is not None else '='
                rhs = (m.group('rhs') or '').strip()
                if rhs:
                    # Separa i target per , o =
                    targets = [v.strip() for v in re.split(r'[,=]', varnames) if v.strip()]
                    values = self._split_values(rhs, len(targets))
                    for t, v in zip(targets, values):
                        eff_value = self._compute_value(op, v)
                        effects.append({
                            'var': t,
                            'op': op,
                            'value': eff_value,
                            'condition': condition,
                            'raw': f"{t} {op} {v}",
                        })
                i += 1
                continue

            # Chiamate funzione con numero finale
            fm = self._FUNC_RE.match(text)
            if fm:
                eff = self._parse_function_call(fm.group('func'), fm.group('args'), condition)
                if eff:
                    effects.append(eff)
                i += 1
                continue

            i += 1

        return {'effects': effects, 'routes': routes}

    def _split_values(self, rhs, n_targets):
        """Prova a dividere rhs in n valori per assegnazioni multiple."""
        if n_targets <= 1:
            return [rhs]
        # Prova a interpretare come tuple/list
        for wrapped in (rhs, f"({rhs})"):
            try:
                parsed = ast.literal_eval(wrapped.strip())
                if isinstance(parsed, (tuple, list)) and len(parsed) == n_targets:
                    return [repr(v) for v in parsed]
            except Exception:
                pass
        # Fallback: restituisci rhs a tutti (male, ma accettabile)
        return [rhs] * n_targets

    def _compute_value(self, op, raw_value):
        """Torna un punteggio numerico per il filtro; None se non valutabile."""
        raw = raw_value.strip()
        if not raw:
            return None

        # Valore letterale
        try:
            val = ast.literal_eval(raw)
        except Exception:
            return None

        if val is True:
            val = 1
        elif val is False:
            val = -1
        elif not isinstance(val, (int, float)):
            # stringhe, liste, etc. non danno punteggio
            return 0

        # Assegnazioni dirette (v = True / 5) e += contribuiscono positivamente
        if op is None or op.startswith('+') or op == '=':
            return val
        if op.startswith('-'):
            return -val
        # Operatori moltiplicativi/di confronto non sono stimabili staticamente
        return None

    def _parse_function_call(self, func, args, condition):
        """Estrae un effetto da chiamate tipo change_relationship('fiona', 1)."""
        str_args = re.findall(r'[\'\"]([a-zA-Z_][a-zA-Z0-9_]*)[\'\"]', args)
        nums = re.findall(r'-?\d+', args)

        if not nums:
            return None

        try:
            value = int(nums[-1])
        except ValueError:
            return None

        if 'relationship' in func:
            if not str_args:
                return None
            name = f'rel_{str_args[0]}'
        elif str_args:
            # change_stat("love") o change_anything("name")
            name = str_args[0]
        else:
            name = func

        return {
            'var': name,
            'op': '+=' if value >= 0 else '-=',
            'value': value,
            'condition': condition,
            'raw': f'{func}({args})',
        }

    def _follow_label(self, label, current_file):
        """Segue jump/call a una label una sola volta per evitare loop."""
        if label in self._seen_labels:
            return []
        self._seen_labels.add(label)

        files_to_search = []
        if current_file:
            files_to_search.append(current_file)
        for f in self.files:
            if f != current_file:
                files_to_search.append(f)

        for f in files_to_search:
            lines = self._get_file_lines(f)
            for idx, line in enumerate(lines):
                if re.match(rf'^\s*label\s+{re.escape(label)}\s*:', line.lstrip()):
                    base_indent = len(line) - len(line.lstrip())
                    res = self._extract_block(lines, idx + 1, base_indent, current_file=f)
                    return res.get('effects', res)
        return []
