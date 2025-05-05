from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class LogRequest(BaseModel):
    """
    Modell für eine Log-Anfrage über die REST-API.
    """
    source_system: str
    target_system: str
    interaction_type: str
    message: Dict[str, Any]
    status: str = "success"
    error_message: Optional[str] = None

class LogEntry(BaseModel):
    """
    Modell für einen Log-Eintrag, wie er in der Datei gespeichert wird.
    """
    timestamp: datetime
    source_system: str
    target_system: str
    interaction_type: str
    message: Dict[str, Any]
    status: str
    error_message: Optional[str] = None