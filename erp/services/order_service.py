import logging
from erp.producers.status_producer import send_status_update

class OrderProcessor:
    def __init__(self):
        self.stock_db = {
            "product_001": 100,
            "product_002": 50
        }  # Dummy Lagerbestand

    def process_order(self, order_id: str, product_id: str, quantity: int) -> (str, str):
        if product_id not in self.stock_db:
            logging.error(f"Product {product_id} not found!")
            raise ValueError("Produkt nicht gefunden.")

        if self.stock_db[product_id] < quantity:
            logging.warning(f"Nicht genug Bestand f\u00fcr {product_id}.")
            order_status = "cancelled"
            shipping_date = "n/a"
        else:
            self.stock_db[product_id] -= quantity
            logging.info(f"Bestand f\u00fcr {product_id} reduziert auf {self.stock_db[product_id]}")
            order_status = "shipped"
            shipping_date = "2025-05-01"  # Dummy Lieferdatum

        # Sende Statusupdate via RabbitMQ
        send_status_update(order_id, order_status)

        return shipping_date, order_status
