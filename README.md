# IntegrationProject

 Integration von eCommerce, ERP und CRM über REST, gRPC und RabbitMQ

## E-Commerce Service (FastAPI)

Dieses Projekt stellt eine einfache REST-Schnittstelle bereit, um Produkte und Bestellungen zu verwalten.  
Zusätzlich empfängt der Service Statusupdates über RabbitMQ.

---

### Voraussetzungen

- Docker
- Docker Compose

(Keine lokale Python- oder Datenbankinstallation notwendig.)

---

### Projektstruktur

- **FastAPI-Service** (`/app`)
- **Postgres-Datenbank**
- **RabbitMQ-Server**

Alles wird über Docker Compose automatisch gestartet.

---

### Installation & Start

1. Projekt klonen oder herunterladen:

    ```bash
    git clone <repository-url>
    cd <repository-ordner>
    ```

2. Container bauen und starten:

    ```bash
    docker-compose up --build
    ```

3. API verfügbar unter:
    <http://localhost:8000/>

4. RabbitMQ Web-Oberfläche verfügbar unter:
    <http://localhost:15672> (Benutzer: guest, Passwort: guest)

### Wichtige Befehle

| Aktion                         | Befehl |
|---------------------------------|--------|
| Projekt starten                | `docker-compose up --build` |
| Projekt stoppen                | `docker-compose down` |
| Alle Container + Volumes löschen (sauber) | `docker-compose down -v` |
| Nur Images neu bauen           | `docker-compose build` |

---

### Verfügbare REST-Endpunkte

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| `POST`  | `/products` | Produkt anlegen |
| `GET`   | `/products` | Alle Produkte abrufen |
| `POST`  | `/orders` | Bestellung aufgeben |
| `GET`   | `/orders/{order_id}` | Bestellung nach ID abrufen |

---

### Hinweise

- Vor dem Aufgeben einer Bestellung muss ein Produkt existieren (`product_id`).
- RabbitMQ wird verwendet, um Statusänderungen an Bestellungen zu empfangen.
## CRM
TODO

## ERP
TODO
