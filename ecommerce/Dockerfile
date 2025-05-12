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
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# 5. Port öffnen (nur informativ)
EXPOSE 8000

# 6. Startbefehl
# 7. Initialize the database before starting the application
ENTRYPOINT ["./entrypoint.sh"]