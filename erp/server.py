import aio_pika
import grpc
from concurrent import futures
import logging
from datetime import datetime
import pika
import sys
import os
import json

# Add the protos directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'protos'))

from protos.order_pb2 import OrderResponse
from protos.order_pb2_grpc import OrderServiceServicer, add_OrderServiceServicer_to_server

class OrderService(OrderServiceServicer):
    def __init__(self):
        self.stock_db = {
            "product_001": {"name": "Product 1", "stock": 100},
            "product_002": {"name": "Product 2", "stock": 50}
        }

    def ProcessOrder(self, request, context):
        product = self.stock_db.get(request.product_id)
        if not product:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Product not found")
            return OrderResponse()

        if product['stock'] < request.quantity:
            context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            context.set_details("Insufficient stock")
            return OrderResponse()

        product['stock'] -= request.quantity
        shipping_date = datetime.now().strftime("%Y-%m-%d")
        order_status = 2 # Shipped

        self.publish_status_update(request.order_id, order_status)

        return OrderResponse(
            shipping_date=shipping_date,
            order_status=order_status
        )

    def publish_status_update(self, order_id, status):
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()
        channel.exchange = channel.declare_exchange("order_updates_exchange", aio_pika.ExchangeType.FANOUT, durable=True)

        message = {
            "order_id": order_id,
            "status": status
        }

        channel.basic_publish(
            exchange='',
            routing_key='order_status_update',
            body=json.dumps(message)
        )

        connection.close()

        logging.info(f"Published status update for order {order_id}: {status}")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_OrderServiceServicer_to_server(OrderService(), server)
    server.add_insecure_port('[::]:50052')
    logging.info("gRPC server running on port 50052")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    serve()
