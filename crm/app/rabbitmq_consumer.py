import asyncio
import json
import os
import aio_pika
from aio_pika import ExchangeType
# import local log_client
from app.log_client import SystemInteractionLogger
from app import crud

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")

# instantiate logger client
log_client = SystemInteractionLogger(service_name="crm")

async def consume_order_updates():
    connection = await aio_pika.connect_robust(RABBITMQ_URL, timeout=None)
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            "order_updates_exchange",
            ExchangeType.FANOUT,
            durable=True
        )
        # Eigene CRM-Queue deklarieren und an Exchange binden
        order_queue = await channel.declare_queue("crm_order_updates", durable=True)
        await order_queue.bind(exchange)

        # Nachrichten aus der gebundenen Queue verarbeiten
        async for message in order_queue:
            async with message.process():
                try:
                    print(f"Bestellung Empfangen: {message.body.decode()}")
                    order_data = json.loads(message.body)

                    # Bestellung in der Datenbank hinzufügen
                    await crud.create_customer_order(order_data)

                    print(f"Bestellung wurde Kunde zugewiesen {order_data['customer_id']}")
                    # emit log event for consume
                    await log_client.log_interaction(
                        target_system="order_updates_exchange",
                        interaction_type="consume_order_update",
                        message=order_data,
                        status="SUCCESS"
                    )
                except Exception as e:
                    print(f"Fehler bei der Bearbeitung {e}")

#Consumer für Status-Updates
async def consume_status_updates():
    connection = await aio_pika.connect_robust(RABBITMQ_URL,timeout=None)
    async with connection:
        channel = await connection.channel()

        exchange = await channel.declare_exchange("order_updates_exchange", aio_pika.ExchangeType.FANOUT, durable=True)

        status_queue = await channel.declare_queue("crm_order_status", durable=True)
        await status_queue.bind(exchange)

        async for message in status_queue:
            async with message.process():
                try:
                    print(f" Stsus Update Empfangen: {message.body.decode()}")
                    status_data = json.loads(message.body)

                    # Status der Bestellung in der Datenbank aktualisieren
                    await crud.update_order_status(status_data["order_id"], status_data["status"])

                    print(f" Status Update erfolgreich: {status_data['order_id']}")
                    # emit log event for status consume
                    await log_client.log_interaction(
                        target_system="order_updates_exchange",
                        interaction_type="consume_status_update",
                        message=status_data,
                        status="SUCCESS"
                    )
                except Exception as e:
                    print(f" Fehler: {e}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(consume_order_updates())
    loop.create_task(consume_status_updates())
    loop.run_forever()