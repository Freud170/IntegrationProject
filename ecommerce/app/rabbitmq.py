# app/rabbitmq.py

import aio_pika
import asyncio
import os
import json
from app.crud import update_order_status, get_order_details

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")

async def publish_order_update(order_id, order_date, total_amount, status, customer_id):
    """
    Publishes an order update message to the "order_updates" queue.
    """
    try:
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        channel = await connection.channel()

        await channel.declare_queue("order_updates", durable=True)

        # Map OrderStatus enum to integer values
        status_mapping = {
            "Processed": 1,
            "Shipped": 2,
            "Cancelled": 3
        }

        message = {
            "order_id": order_id,
            "order_date": order_date.isoformat(),
            "order_amount": total_amount,
            "order_status": status_mapping.get(status, 0),
            "customer_id": customer_id
        }

        await channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode()),
            routing_key="order_updates"
        )
        print(f" [✔] Published order update: {message}")
        await connection.close()
    except Exception as e:
        print(f" [!] Error publishing order update: {e}")

async def consume_order_status_updates():
    """
    Verbindet sich mit RabbitMQ und verarbeitet Statusupdate-Nachrichten für Bestellungen.
    Mit automatischen Verbindungsversuchen beim Start.
    """
    connected = False
    while not connected:
        try:
            connection = await aio_pika.connect_robust(RABBITMQ_URL)
            connected = True
        except Exception as e:
            print(f" [!] RabbitMQ not ready yet ({e}), retrying in 5 seconds...")
            await asyncio.sleep(5)  # 5 Sekunden warten und nochmal versuchen

    connection = await aio_pika.connect_robust(RABBITMQ_URL, timeout=None)
    async with connection:
        channel = await connection.channel()

        exchange = await channel.declare_exchange("order_updates_exchange", aio_pika.ExchangeType.FANOUT, durable=True)

        status_queue = await channel.declare_queue("ecommerce_order_status", durable=True)
        await status_queue.bind(exchange)

        async for message in status_queue:
            async with message.process():
                try:
                    print(f"Order update received: {message.body.decode()}")
                    status_data = json.loads(message.body)

                    await update_order_status(status_data["order_id"], status_data["status"])

                    print(f"Order {status_data['OrderID']} updated successfully.")
                except Exception as e:
                    print(f"Error processing order update: {e}")