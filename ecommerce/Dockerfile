# Dockerfile

# 1. Basisimage
FROM python:3.13-slim

# 2. Arbeitsverzeichnis
WORKDIR /app

# 3. Abhängigkeiten kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Code kopieren
COPY app/ app/

# 5. Port öffnen (nur informativ)
EXPOSE 8000

# 6. Startbefehl
# 7. Initialize the database before starting the application
CMD ["sh", "-c", "python -c 'from app.db import init_db; import asyncio; asyncio.run(init_db())' && uvicorn app.main:app --host 0.0.0.0 --port 8000"]