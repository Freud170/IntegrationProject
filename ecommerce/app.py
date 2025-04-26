# 1. ecommerce/app.py (Person A - REST API + RabbitMQ Consumer)

from fastapi import FastAPI
import pika
import json
import logging
#huang
app = FastAPI()

# Logger Setup
logging.basicConfig(filename="../ecommerce/logs/ecommerce.log", level=logging.INFO)

@app.post("/order")
async def create_order(order: dict):
    logging.info(f"Order received: {order}")
    # Hier sollte die Bestellung verarbeitet und an ERP über gRPC geschickt werden
    return {"message": "Order accepted", "lieferdatum": "tbd", "lieferstatus": "pending"}

# RabbitMQ Consumer Setup
def consume_status_updates():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='order_status')

    def callback(ch, method, properties, body):
        message = json.loads(body)
        logging.info(f"Status Update received: {message}")

    channel.basic_consume(queue='order_status', on_message_callback=callback, auto_ack=True)
    print(' [*] Waiting for messages.')
    channel.start_consuming()