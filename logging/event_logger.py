import asyncio
import aio_pika
import logging
import os
import json
from datetime import datetime

# Logging-Konfiguration
logging.basicConfig(
    filename="logs/system_interactions.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

# Stelle sicher, dass das Logs-Verzeichnis existiert
os.makedirs("logs", exist_ok=True)

# Konfigurationsvariablen
RABBITMQ_URL = "amqp://guest:guest@rabbitmq/"
QUEUE_NAMES = ["order_updates", "order_status_update"]

async def monitor_rabbitmq_queues():
    """
    Überwacht die existierenden RabbitMQ-Queues und protokolliert alle Nachrichten.
    """
    # Versuche, eine Verbindung herzustellen (mit Wiederholungsversuchen)
    connection = None
    while connection is None:
        try:
            connection = await aio_pika.connect_robust(RABBITMQ_URL)
            logging.info(f"Mit RabbitMQ verbunden: {RABBITMQ_URL}")
            print(f" [✓] Mit RabbitMQ verbunden: {RABBITMQ_URL}")
        except Exception as e:
            print(f" [!] RabbitMQ-Verbindung fehlgeschlagen: {e}, wiederhole in 5 Sekunden...")
            await asyncio.sleep(5)
    
    # Channel erstellen
    channel = await connection.channel()
    
    # Überwachungsaufgaben für alle angegebenen Queues erstellen
    tasks = []
    for queue_name in QUEUE_NAMES:
        queue = await channel.declare_queue(
            queue_name, 
            durable=True,
            passive=True  # Nur prüfen, ob die Queue existiert, nicht erstellen
        )
        task = asyncio.create_task(
            monitor_queue(queue, queue_name)
        )
        tasks.append(task)
    
    print(f" [*] Überwache {len(tasks)} RabbitMQ-Queues. Zum Beenden Strg+C drücken")
    
    # Auf alle Überwachungsaufgaben warten
    await asyncio.gather(*tasks)

async def monitor_queue(queue, queue_name):
    """
    Überwacht eine bestimmte Queue und protokolliert alle empfangenen Nachrichten.
    """
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                body = message.body.decode()
                log_message = f"Queue: {queue_name}, Nachricht: {body}"
                print(f" [x] {log_message}")
                logging.info(log_message)
                
                # Versuche, strukturierte JSON-Daten zu protokollieren
                try:
                    json_data = json.loads(body)
                    # Protokolliere formatierte JSON-Daten
                    logging.info(f"JSON-Daten aus {queue_name}:\n{json.dumps(json_data, indent=2, ensure_ascii=False)}")
                except json.JSONDecodeError:
                    # Keine JSON-Daten, protokolliere als Rohtext
                    logging.info(f"Rohtext-Nachricht aus {queue_name}: {body}")

if __name__ == "__main__":
    print(" [*] Starte Logging-Service...")
    logging.info(f"Logging-Service gestartet - {datetime.now().isoformat()}")
    try:
        asyncio.run(monitor_rabbitmq_queues())
    except KeyboardInterrupt:
        print(" [!] Beende auf Benutzeranforderung")
        logging.info("Logging-Service wurde durch Benutzer beendet")
    except Exception as e:
        error_msg = f"Fehler im Logging-Service: {e}"
        print(f" [!] {error_msg}")
        logging.error(error_msg)