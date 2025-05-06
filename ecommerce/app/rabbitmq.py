# app/rabbitmq.py

import aio_pika
import asyncio
import os
import json
from app.crud import update_order_status, get_order_details  # Import the missing function

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")

async def publish_order_update(order_id, order_date, total_amount, status):
    """
    Publishes an order update message to the "order_updates" queue.
    """
    try:
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        channel = await connection.channel()
        
        message = {
            "OrderID": order_id,
            "OrderDate": order_date,
            "TotalAmount": total_amount,
            "Status": status
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

    channel = await connection.channel()
    queue = await channel.declare_queue("order_status_update", durable=True)

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

                    # Fetch additional order details from the database
                    order_details = await get_order_details(order_id)
                    await publish_order_update(
                        order_id=order_details["OrderID"],
                        order_date=order_details["OrderDate"],
                        total_amount=order_details["TotalAmount"],
                        status=new_status
                    )
                except Exception as e:
                    print(f" [!] Error processing message: {e}")