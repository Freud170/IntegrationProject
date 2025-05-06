from fastapi import APIRouter, Query, HTTPException, Body
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from .logger import async_logger
from .models import LogEntry, LogRequest

router = APIRouter(prefix="/logs", tags=["logs"])

# Import der App aus main.py (damit app.api:app verfügbar ist)
import importlib
try:
    main_module = importlib.import_module('.main', 'app')
    app = main_module.app
except (ImportError, AttributeError):
    # Fallback: Eine leere FastAPI App erstellen, falls die Import nicht funktioniert
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)

@router.post("/", status_code=201, response_model=Dict[str, str])
async def create_log_entry(log_request: LogRequest):
    """
    Erstellt einen neuen Log-Eintrag über die REST-API.
    
    Diese Methode kann von Services verwendet werden, die keine RabbitMQ-Verbindung haben
    oder aus anderen Gründen die REST-API zum Loggen nutzen möchten.
    """
    try:
        await async_logger.log_interaction(
            source_system=log_request.source_system,
            target_system=log_request.target_system,
            interaction_type=log_request.interaction_type,
            message=log_request.message,
            status=log_request.status,
            error_message=log_request.error_message
        )
        return {"status": "success", "message": "Log-Eintrag erfolgreich erstellt"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Erstellen des Log-Eintrags: {str(e)}")

@router.get("/", response_model=List[LogEntry])
async def get_logs(
    limit: int = Query(100, description="Maximale Anzahl der zurückzugebenden Logs"),
    source_system: Optional[str] = Query(None, description="Filter für Quellsystem"),
    target_system: Optional[str] = Query(None, description="Filter für Zielsystem"),
    interaction_type: Optional[str] = Query(None, description="Filter für Interaktionstyp")
):
    """
    Ruft die Logs aus dem System ab mit optionalen Filtern.
    """
    try:
        logs = await async_logger.get_logs(
            limit=limit,
            filter_source=source_system,
            filter_target=target_system,
            filter_type=interaction_type
        )
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Logs: {str(e)}")

@router.get("/stats", response_model=Dict[str, Any])
async def get_log_statistics():
    """
    Gibt einfache Statistiken über die protokollierten Interaktionen zurück.
    """
    try:
        # Alle Logs abrufen (mit höherem Limit für Statistik)
        logs = await async_logger.get_logs(limit=10000)
        
        # Statistik berechnen
        stats = {
            "total_interactions": len(logs),
            "by_source": {},
            "by_target": {},
            "by_type": {},
            "by_status": {},
            "latest_timestamp": logs[0]["timestamp"] if logs else None
        }
        
        for log in logs:
            source = log.get("source_system", "unknown")
            target = log.get("target_system", "unknown")
            interaction_type = log.get("interaction_type", "unknown")
            status = log.get("status", "unknown")
            
            stats["by_source"][source] = stats["by_source"].get(source, 0) + 1
            stats["by_target"][target] = stats["by_target"].get(target, 0) + 1
            stats["by_type"][interaction_type] = stats["by_type"].get(interaction_type, 0) + 1
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Statistiken: {str(e)}")

@router.delete("/", status_code=200, response_model=Dict[str, str])
async def clear_logs():
    """
    Löscht alle Logs (nur für Testzwecke).
    In einer Produktionsumgebung würde diese Funktion weitere Sicherheitsmaßnahmen erfordern.
    """
    try:
        # Leere Datei erstellen (überschreibt bestehende)
        with open(async_logger.log_file_path, 'w') as f:
            pass
        return {"status": "success", "message": "Logs wurden gelöscht"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Löschen der Logs: {str(e)}")