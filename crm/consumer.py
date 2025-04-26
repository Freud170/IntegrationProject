# 3. crm/consumer.py (Person C - RabbitMQ Consumer)

import pika
import json
import logging

#test

logging.basicConfig(filename="../crm/logs/crm.log", level=logging.INFO)

def consume_orders():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='order_created')

    def callback(ch, method, properties, body):
        order = json.loads(body)
        logging.info(f"Order received for CRM: {order}")

    channel.basic_consume(queue='order_created', on_message_callback=callback, auto_ack=True)
    print(' [*] CRM waiting for orders.')
    channel.start_consuming()

if __name__ == "__main__":
    consume_orders()