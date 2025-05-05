import logging
import asyncio
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router as logs_router
from .rabbitmq_consumer import rabbitmq_consumer

# Konfiguration des Loggings für den Service selbst
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Ausgabe in die Konsole
        logging.FileHandler(os.path.join('logs', 'logging_service.log'))  # Ausgabe in eine Datei
    ]
)

logger = logging.getLogger("logging_service")

# FastAPI App initialisieren
app = FastAPI(
    title="Logging Service",
    description="Zentraler Logging-Service für die Protokollierung aller System-Interaktionen",
    version="1.0.0"
)

# CORS-Middleware hinzufügen (für die Web-UI falls benötigt)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In der Produktion einschränken
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API-Router einbinden
app.include_router(logs_router)

@app.on_event("startup")
async def startup_event():
    """
    Wird beim Start des Services ausgeführt.
    Initialisiert RabbitMQ-Konsumenten und andere Hintergrundaufgaben.
    """
    logger.info("Logging-Service wird gestartet...")
    
    # RabbitMQ-Konsumenten im Hintergrund starten
    asyncio.create_task(rabbitmq_consumer.start())
    
    logger.info("Logging-Service erfolgreich gestartet!")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Wird beim Herunterfahren des Services ausgeführt.
    Beendet RabbitMQ-Verbindungen und andere Ressourcen.
    """
    logger.info("Logging-Service wird heruntergefahren...")
    
    # RabbitMQ-Konsumenten stoppen
    await rabbitmq_consumer.stop()
    
    logger.info("Logging-Service erfolgreich heruntergefahren!")

@app.get("/")
async def root():
    """
    Einfacher Health-Check-Endpunkt.
    """
    return {"status": "online", "service": "logging"}