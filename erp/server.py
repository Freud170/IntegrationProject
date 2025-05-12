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

from protos.order_pb2 import OrderResponse, OrderStatusUpdateRequest
from google.protobuf.empty_pb2 import Empty
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
        # declare fanout exchange for order status updates
        channel.exchange_declare(exchange='order_updates_exchange', exchange_type='fanout', durable=True)

        message = {
            "order_id": order_id,
            "status": status
        }

        # publish to the exchange with empty routing key for fanout
        channel.basic_publish(
            exchange='order_updates_exchange',
            routing_key='',
            body=json.dumps(message)
        )

        connection.close()

        logging.info(f"Published status update for order {order_id}: {status}")

    def UpdateOrderStatus(self, request: OrderStatusUpdateRequest, context) -> Empty:
        """
        Receives order status updates via gRPC and publishes to RabbitMQ exchange.
        """
        try:
            self.publish_status_update(request.order_id, request.status)
            return Empty()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return Empty()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_OrderServiceServicer_to_server(OrderService(), server)
    server.add_insecure_port('[::]:50052')
    logging.info("gRPC server running on port 50052")
    server.start()
    # Graceful shutdown on SIGTERM
    import signal
    def _sigterm_handler(signum, frame):
        logging.info("SIGTERM received, stopping gRPC server...")
        server.stop(0)
    signal.signal(signal.SIGTERM, _sigterm_handler)
    server.wait_for_termination()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    serve()
