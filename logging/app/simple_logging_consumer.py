import pika
import os
import logging

RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://user:password@rabbitmq/")
QUEUE_NAME = "system_interactions_logs"
LOGFILE = os.path.join(os.path.dirname(__file__), "..", "logs.txt")

os.makedirs(os.path.dirname(LOGFILE), exist_ok=True)

# Logging-Konfiguration
logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), "..", "logs", "system_interactions.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def callback(ch, method, properties, body):
    message = body.decode("utf-8")
    with open(LOGFILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")
    logging.info("Nachricht empfangen: %s", message)
    print("Nachricht geloggt:", message)

def main():
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)
    print("Warte auf Nachrichten...")
    channel.start_consuming()

if __name__ == "__main__":
    main()
