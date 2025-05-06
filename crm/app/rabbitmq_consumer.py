import asyncio
import json
import aio_pika
from app import crud

RABBITMQ_URL = "amqp://guest:guest@rabbitmq/"

# Consumer für Bestellungen
async def consume_order_updates():

    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        order_queue = await channel.declare_queue("order_updates", durable=True)
        print(" [*] Waiting for order updates. To exit press CTRL+C")

        async for message in order_queue:
            async with message.process():
                try:
                    print(f" [x] Received order: {message.body.decode()}")
                    order_data = json.loads(message.body)

                    # Bestellung in der Datenbank hinzufügen
                    await crud.create_customer_order(order_data)

                    print(f" [✔] Order added successfully for customer {order_data['customer_id']}")
                except Exception as e:
                    print(f" [!] Error processing order: {e}")

# Consumer für Bestellstatus-Updates
async def consume_status_updates():

    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        status_queue = await channel.declare_queue("order_status_updates", durable=True)
        print(" [*] Waiting for status updates. To exit press CTRL+C")

        async for message in status_queue:
            async with message.process():
                try:
                    print(f" [x] Received status update: {message.body.decode()}")
                    status_data = json.loads(message.body)

                    # Status der Bestellung in der Datenbank aktualisieren
                    await crud.update_order_status(status_data["order_id"], status_data["status"])

                    print(f" [✔] Status updated for order {status_data['order_id']}")
                except Exception as e:
                    print(f" [!] Error processing status update: {e}")

# Loop für die Consumer
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(consume_order_updates())
    loop.create_task(consume_status_updates())
    loop.run_forever()