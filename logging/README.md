# Logging Service

## Übersicht

Der Logging-Service protokolliert alle Interaktionen zwischen den Systemen (eCommerce, ERP, CRM) asynchron in einer zentralen Datei. Er bietet eine einheitliche Möglichkeit, alle Kommunikation zwischen den Services zu verfolgen und zu analysieren.

## Features

- **Asynchrone Protokollierung** aller Systeminteraktionen
- **Zentralisierte Log-Datei** für einfache Überwachung und Analyse
- **Mehrere Protokollierungswege**:
  - Via RabbitMQ (bevorzugt für asynchrone Services)
  - Via REST API (für Services ohne RabbitMQ)
- **Log-Abfrage und Filterung** über REST API
- **Statistiken** über Service-Kommunikation

## Technologie-Stack

- Python 3.13
- FastAPI (REST API)
- RabbitMQ (Nachrichtenverarbeitung)
- aio-pika (Async RabbitMQ Client)

## Verzeichnisstruktur

```
logging/
  ├── app/                     # Hauptanwendungscode
  │   ├── api.py               # REST API Endpunkte
  │   ├── logger.py            # Core Logger-Implementierung
  │   ├── main.py              # FastAPI App und Startup
  │   ├── models.py            # Pydantic-Datenmodelle
  │   └── rabbitmq_consumer.py # RabbitMQ Nachrichtenverarbeitung
  ├── logs/                    # Log-Dateien (Container-Volume)
  ├── Dockerfile               # Docker-Container-Definition
  ├── docker-compose.yml       # Docker Compose Konfiguration
  └── requirements.txt         # Python Dependencies
```

## Verwendung

### Deployment

```bash
cd logging
docker-compose up -d
```

### Logs einsehen

```bash
# Alle Logs anzeigen
curl http://localhost:8002/logs

# Gefiltert nach Quellsystem
curl http://localhost:8002/logs?source_system=ecommerce

# Statistiken abrufen
curl http://localhost:8002/logs/stats
```

### Von anderen Services verwenden

Fügen Sie den Log-Client zu Ihrem Service hinzu:

```python
from shared.logging.log_client import SystemInteractionLogger

# Für asynchrone Services
logger = SystemInteractionLogger(service_name="ecommerce", 
                                local_fallback_path="logs/local_fallback.log")

# Im asynchronen Kontext verwenden
await logger.log_interaction(
    target_system="erp",
    interaction_type="REST",
    message={"order_id": "12345", "status": "shipped"},
    status="success"
)

# Im synchronen Kontext verwenden
logger.log_interaction_sync(
    target_system="crm",
    interaction_type="RabbitMQ",
    message={"customer_id": "C54321", "action": "update_profile"},
    status="success"
)
```

## API-Referenz

### REST-Endpunkte

- `GET /logs` - Protokollierte Interaktionen abfragen mit optionaler Filterung
- `POST /logs` - Neuen Log-Eintrag erstellen
- `GET /logs/stats` - Log-Statistiken abrufen
- `DELETE /logs` - Logs löschen (nur für Testzwecke)

### RabbitMQ-Queues

- `system_interactions_logs` - Queue für alle System-Interaktions-Logs