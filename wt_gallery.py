#!/usr/bin/env python3
"""
Ren'Py WTForge - Gallery Analyzer
Scans decompiled Ren'Py scripts to detect common gallery systems.
"""

import re
from pathlib import Path


class WTGalleryAnalyzer:
    """Analizza gli script .rpy decompilati per rilevare sistemi galleria"""

    def __init__(self, game_dir):
        self.game_dir = Path(game_dir)
        self.award_manager = False
        self.gallery_objects = []
        self.persistent_vars = []
        self.other_patterns = []

    def analyze(self):
        """Scansione degli script e ritorno del report"""
        rpy_files = self._collect_rpy_files()
        text = self._read_scripts(rpy_files)
        self._detect_award_manager(text)
        self._detect_gallery_objects(text)
        self._detect_persistent_vars(text)
        return self._report()

    def _collect_rpy_files(self):
        """Raccoglie tutti i file .rpy escludendo quelli del tool"""
        rpy_files = []
        if not self.game_dir.exists():
            return rpy_files
        for rpy_file in self.game_dir.rglob('*.rpy'):
            if 'wtmod' in rpy_file.parts:
                continue
            if rpy_file.name.lower() in ('gui.rpy', 'screens.rpy', 'options.rpy', 'images.rpy'):
                continue
            rpy_files.append(rpy_file)
        return rpy_files

    def _read_scripts(self, rpy_files):
        """Legge il contenuto degli script in un unico testo"""
        parts = []
        for rpy_file in rpy_files:
            try:
                parts.append(rpy_file.read_text(encoding='utf-8'))
            except Exception:
                pass
        return '\n'.join(parts)

    def _detect_award_manager(self, text):
        """Rileva la presenza di award_manager"""
        if 'award_manager' in text:
            self.award_manager = True

    def _detect_gallery_objects(self, text):
        """Rileva oggetti Ren'Py Gallery: var = Gallery(...)"""
        pattern = re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*Gallery\s*\(', re.MULTILINE)
        for match in pattern.finditer(text):
            name = match.group(1)
            if name not in self.gallery_objects:
                self.gallery_objects.append(name)

    def _detect_persistent_vars(self, text):
        """Rileva variabili persistenti collegate a galleria/CG/Unlock"""
        keywords = ('gallery', 'cg', 'unlock', 'seen', 'album', 'photo', 'image', 'scene')
        all_refs = re.findall(r'persistent\.([a-zA-Z_][a-zA-Z0-9_]*)', text)
        candidates = {}
        for var in set(all_refs):
            if any(k in var.lower() for k in keywords):
                candidates[var] = {'name': var, 'shape': 'unknown'}

        for var in candidates:
            pattern = re.compile(r'persistent\.' + re.escape(var) + r'\s*=\s*([^#\n]+)', re.MULTILINE)
            match = pattern.search(text)
            if match:
                rhs = match.group(1).strip()
                if rhs.startswith('set'):
                    candidates[var]['shape'] = 'set'
                elif rhs.startswith('dict') or rhs == '{}' or ':' in rhs.split('#')[0]:
                    candidates[var]['shape'] = 'dict'
                elif rhs.startswith('['):
                    candidates[var]['shape'] = 'list'
                elif rhs.startswith('{'):
                    candidates[var]['shape'] = 'set'
                elif rhs in ('True', 'False'):
                    candidates[var]['shape'] = 'bool'

        self.persistent_vars = list(candidates.values())

    def _report(self):
        """Restituisce il report di rilevamento"""
        return {
            'award_manager': self.award_manager,
            'gallery_objects': self.gallery_objects,
            'persistent_vars': self.persistent_vars,
            'other_patterns': self.other_patterns,
        }
