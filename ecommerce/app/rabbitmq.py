# app/rabbitmq.py

import aio_pika
import asyncio
import os
import json
from app.crud import update_order_status, get_order_details
from aio_pika import ExchangeType

# import central logging client
from app.log_client import SystemInteractionLogger

# instantiate logger
log_client = SystemInteractionLogger(service_name="ecommerce")

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")

async def publish_order_update(order_id, order_date, total_amount, status, customer_id):
    """
    Publishes an order update message to the "order_updates" queue.
    """
    try:
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        channel = await connection.channel()

        exchange = await channel.declare_exchange(
            "order_updates_exchange",
            ExchangeType.FANOUT,
            durable=True
        )

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

        await exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode()),
            routing_key=""
        )
        print(f" [✔] Published order update: {message}")
        # emit a log event for publish
        await log_client.log_interaction(
            target_system="order_updates_exchange",
            interaction_type="publish_order_update",
            message=message,
            status="SUCCESS"
        )
        await connection.close()
    except Exception as e:
        print(f" [!] Error publishing order update: {e}")
        # log error
        await log_client.log_interaction(
            target_system="order_updates_exchange",
            interaction_type="publish_order_update",
            message={"error": str(e)},
            status="ERROR"
        )

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
                    # emit a log event for consume
                    await log_client.log_interaction(
                        target_system="order_updates_exchange",
                        interaction_type="consume_status_update",
                        message=status_data,
                        status="SUCCESS"
                    )
                except Exception as e:
                    print(f"Error processing order update: {e}")