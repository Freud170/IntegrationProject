# Basis-Python-Image verwenden
FROM python:3.11-slim

# Arbeitsverzeichnis im Container
WORKDIR /app

# Abhängigkeiten kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Anwendungscode in das Image kopieren
COPY . .

# Wichtige Ports freigeben
EXPOSE 8000  # Für E-Commerce
EXPOSE 8001  # Für ERP

# Startbefehl je nach Framework (hier FastAPI mit uvicorn)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
