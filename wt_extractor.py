#!/usr/bin/env python3
"""
Ren'Py WTForge - Extractor Module
Gestisce l'estrazione dei file .rpa e la decompilazione dei file .rpyc
"""

import os
import sys
import subprocess
from pathlib import Path


class WTExtractor:
    def __init__(self, game_path, output_dir=None):
        """
        Inizializza l'estrattore
        
        Args:
            game_path: Percorso al gioco (.app o cartella)
            output_dir: Directory di output (default: game_path/game)
        """
        self.game_path = Path(game_path)
        self.output_dir = Path(output_dir) if output_dir else self._find_game_dir()
        self.script_dir = Path(__file__).parent
        self.unren_tools = self.script_dir / "UnRen Tools"
        
    def _find_game_dir(self):
        """Trova la directory game del gioco Ren'Py"""
        # Controlla se è un .app (macOS)
        if self.game_path.suffix == '.app':
            game_dir = self.game_path / "Contents" / "Resources" / "autorun" / "game"
            if game_dir.exists():
                return game_dir
        
        # Controlla se è una cartella con directory game
        game_dir = self.game_path / "game"
        if game_dir.exists():
            return game_dir
            
        # Se non trova game, assume che il percorso sia già la directory game
        return self.game_path
    
    def extract_rpa_files(self, progress_callback=None):
        """
        Estrae tutti i file .rpa nella directory game
        
        Args:
            progress_callback: Funzione callback per aggiornare progresso (current, total)
            
        Returns:
            bool: True se estrazione completata con successo
        """
        rpa_files = list(self.output_dir.glob("*.rpa"))
        
        if not rpa_files:
            print("Nessun file .rpa trovato")
            return True
            
        print(f"Trovati {len(rpa_files)} file .rpa da estrarre")
        
        rpatool_path = self.unren_tools / "rpatool"
        
        for i, rpa_file in enumerate(rpa_files):
            if progress_callback:
                progress_callback(i + 1, len(rpa_files))
                
            print(f"Estrazione di {rpa_file.name}...")
            
            try:
                result = subprocess.run(
                    [sys.executable, str(rpatool_path), '-x', str(rpa_file), '-o', str(self.output_dir)],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    print(f"Errore nell'estrazione di {rpa_file.name}: {result.stderr}")
                    return False
                    
            except Exception as e:
                print(f"Errore durante l'estrazione: {e}")
                return False
                
        print("Estrazione completata")
        return True
    
    def decompile_rpyc_files(self, progress_callback=None):
        """
        Decompila tutti i file .rpyc nella directory game
        
        Args:
            progress_callback: Funzione callback per aggiornare progresso (current, total)
            
        Returns:
            bool: True se decompilazione completata con successo
        """
        # Trova tutti i file .rpyc
        rpyc_files = []
        for rpyc_file in self.output_dir.rglob("*.rpyc"):
            # Escludi file di sistema
            if not any(x in rpyc_file.name.lower() for x in ['gui', 'screens', 'options', 'images']):
                rpyc_files.append(rpyc_file)
        
        if not rpyc_files:
            print("Nessun file .rpyc trovato da decompilare")
            return True
            
        print(f"Trovati {len(rpyc_files)} file .rpyc da decompilare")
        
        # Aggiungi decompiler al Python path
        decompiler_dir = self.unren_tools / "decompiler"
        if str(decompiler_dir) not in sys.path:
            sys.path.insert(0, str(decompiler_dir))
        
        unrpyc_path = self.unren_tools / "unrpyc.py"
        
        # Decomplila in batches per evitare problemi con troppi argomenti
        batch_size = 50
        for i in range(0, len(rpyc_files), batch_size):
            batch = rpyc_files[i:i + batch_size]
            
            if progress_callback:
                progress_callback(i + len(batch), len(rpyc_files))
            
            try:
                result = subprocess.run(
                    [sys.executable, str(unrpyc_path), '-c'] + [str(f) for f in batch],
                    capture_output=True,
                    text=True,
                    cwd=str(self.output_dir)
                )
                
                if result.returncode != 0:
                    print(f"Errore nella decompilazione: {result.stderr}")
                    return False
                    
            except Exception as e:
                print(f"Errore durante la decompilazione: {e}")
                return False
                
        print("Decompilazione completata")
        return True
    
    def get_rpy_files(self):
        """
        Restituisce la lista dei file .rpy per l'analisi
        
        Returns:
            list: Lista di Path dei file .rpy
        """
        rpy_files = []
        for rpy_file in self.output_dir.rglob("*.rpy"):
            # Escludi file di sistema e il tool stesso
            if not any(x in rpy_file.name.lower() for x in ['gui', 'screens', 'options', 'images', 'wtmod']):
                rpy_files.append(rpy_file)
        return rpy_files


if __name__ == "__main__":
    # Test del modulo
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python wt_extractor.py <percorso_gioco>")
        sys.exit(1)
        
    game_path = sys.argv[1]
    extractor = WTExtractor(game_path)
    
    print(f"Directory di output: {extractor.output_dir}")
    
    # Estrazione
    extractor.extract_rpa_files()
    
    # Decompilazione
    extractor.decompile_rpyc_files()
    
    # Lista file .rpy
    rpy_files = extractor.get_rpy_files()
    print(f"\nFile .rpy trovati: {len(rpy_files)}")
    for rpy in rpy_files[:5]:  # Mostra primi 5
        print(f"  - {rpy.name}")
