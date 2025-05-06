# app/rabbitmq.py

import aio_pika
import asyncio
import os
from app.crud import update_order_status

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")

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

    channel = await connection.channel()
    queue = await channel.declare_queue("order_status", durable=True)

    print(" [*] Waiting for status updates. To exit press CTRL+C")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                payload = message.body.decode()
                print(f" [x] Received {payload}")
                
                try:
                    order_id, new_status = payload.strip().split(",")
                    await update_order_status(order_id, new_status)
                    print(f" [✔] Updated order {order_id} to status {new_status}")
                except Exception as e:
                    print(f" [!] Error processing message: {e}")