import asyncio
import json
import aio_pika
from app import crud
from app.models import CustomerCreate

async def consume_order_updates():
    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("order_updates", durable=True)
        
        async for message in queue:
            async with message.process():
                try:
                    print("Nachricht empfangen")
                    # JSON-Daten aus der Nachricht extrahieren
                    data = json.loads(message.body)
                    
                    # Kundeninformationen extrahieren
                    customer_data = data.get("customer")

                    if customer_data:
                        # Validieren und erstellen des Kundenobjekts
                        customer = CustomerCreate(**customer_data)
                        await crud.create_customer(customer)
                        print(f"Kunde {customer.name} erfogreich erstellt")
                    else:
                        print("Fehler: Keine Kundeninformationen in der Nachricht gefunden")
                except Exception as e:
                    print(f"Fehler beim Verabreiten: {e}")

# Consumer der Nachrichten von RabbitMQ
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(consume_order_updates())