import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
import aiofiles

class AsyncLogger:
    """
    Asynchroner Logger für die Protokollierung von Service-Interaktionen.
    Schreibt die Logs in eine Datei und unterstützt asynchronen Zugriff.
    """
    def __init__(self, log_dir: str = "logs", log_file: str = "system_interactions.log"):
        self.log_dir = log_dir
        self.log_file = log_file
        self.log_file_path = os.path.join(log_dir, log_file)
        self.ensure_log_directory()
        
    def ensure_log_directory(self):
        """Stellt sicher, dass das Log-Verzeichnis existiert."""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            print(f"Log-Verzeichnis {self.log_dir} erstellt")
            
    async def log_interaction(self, source_system: str, target_system: str, interaction_type: str, 
                             message: Dict[str, Any], status: str = "success", 
                             error_message: Optional[str] = None):
        """
        Protokolliert eine Interaktion zwischen zwei Systemen asynchron in der Log-Datei.
        
        :param source_system: Das System, von dem die Interaktion ausging
        :param target_system: Das Zielsystem der Interaktion
        :param interaction_type: Art der Interaktion (z.B. 'REST', 'gRPC', 'RabbitMQ')
        :param message: Die Nachricht/Daten, die ausgetauscht wurden
        :param status: Status der Interaktion ('success' oder 'error')
        :param error_message: Fehler-Nachricht, falls Status 'error' ist
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "source_system": source_system,
            "target_system": target_system,
            "interaction_type": interaction_type,
            "message": message,
            "status": status
        }
        
        if error_message:
            log_entry["error_message"] = error_message
            
        # Formatieren als JSON-Zeile
        log_line = json.dumps(log_entry) + "\n"
        
        # Asynchron in die Datei schreiben
        async with aiofiles.open(self.log_file_path, mode='a', encoding='utf-8') as file:
            await file.write(log_line)
            await file.flush()  # Sicherstellen, dass die Daten sofort geschrieben werden
            
        print(f"Interaktion protokolliert: {source_system} -> {target_system}")
        
    async def get_logs(self, limit: int = 100, filter_source: Optional[str] = None, 
                      filter_target: Optional[str] = None, filter_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Liest die letzten 'limit' Log-Einträge aus der Datei.
        Mit optionalen Filtern für Quellsystem, Zielsystem und Interaktionstyp.
        
        :return: Liste der Log-Einträge
        """
        logs = []
        
        # Prüfen, ob Log-Datei existiert
        if not os.path.exists(self.log_file_path):
            return logs
            
        try:
            async with aiofiles.open(self.log_file_path, mode='r', encoding='utf-8') as file:
                lines = await file.readlines()
                
                # Reversed, um die neuesten zuerst zu bekommen
                for line in reversed(lines):
                    if not line.strip():
                        continue
                        
                    try:
                        log_entry = json.loads(line)
                        
                        # Filter anwenden, wenn angegeben
                        if filter_source and log_entry.get("source_system") != filter_source:
                            continue
                        if filter_target and log_entry.get("target_system") != filter_target:
                            continue
                        if filter_type and log_entry.get("interaction_type") != filter_type:
                            continue
                            
                        logs.append(log_entry)
                        
                        # Limit prüfen
                        if len(logs) >= limit:
                            break
                    except json.JSONDecodeError:
                        print(f"Fehler beim Dekodieren der Log-Zeile: {line}")
                        continue
        except Exception as e:
            print(f"Fehler beim Lesen der Logs: {str(e)}")
            
        return logs

# Singleton-Instanz des Loggers erstellen
async_logger = AsyncLogger()