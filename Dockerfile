# Verwende als Basis ein schlankes Python-Image
FROM python:3.13-slim

# Arbeitsverzeichnis erstellen
WORKDIR /integration

# Anforderungen für alle Projekte kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Häufig verwendete Abhängigkeiten oder geteilten Code (falls vorhanden) kopieren
COPY shared/ shared/

# Einzelne Projektordner für die Dienste bereitstellen (z.B. CRM, Ecommerce, ERP)
COPY crm/ /integration/crm
COPY ecommerce/ /integration/ecommerce
COPY erp/ /integration/erp

# Optional: Zusatztools installieren (falls benötigt)
# INSTALLIEREN, BEISPIEL: RUN apt-get update && apt-get install ...

# Öffne Ports (informativ)
EXPOSE 8000 8001 8002

# Setze ein Beispiel-Startkommando, falls alle Dienste initialisiert werden sollen
CMD ["echo", "Docker Setup für Integration fertig. Bitte Docker-Compose verwenden."]
