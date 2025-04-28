import pika
import json
import logging

def send_status_update(order_id: str, status: str):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()
        channel.queue_declare(queue='order_status')

        message = {
            "order_id": order_id,
            "status": status
        }

        channel.basic_publish(
            exchange='',
            routing_key='order_status',
            body=json.dumps(message)
        )

        logging.info(f"Status Update f\u00fcr Order {order_id}: {status} gesendet.")

        connection.close()

    except Exception as e:
        logging.error(f"Fehler beim Senden der Nachricht: {str(e)}")
