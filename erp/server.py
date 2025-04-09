# 2. erp/server.py (Person B - gRPC Server + RabbitMQ Producer)

import grpc
from concurrent import futures
import order_pb2
import order_pb2_grpc
import pika
import json
import logging

logging.basicConfig(filename="../erp/logs/erp.log", level=logging.INFO)

class OrderService(order_pb2_grpc.OrderServiceServicer):
    def ProcessOrder(self, request, context):
        logging.info(f"Processing Order: {request}")
        # Bestellung verarbeiten (Lagerbestand reduzieren etc.)

        # Nachricht an RabbitMQ senden (Lieferstatus)
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='order_status')
        status_update = {"order_id": request.order_id, "status": "shipped"}
        channel.basic_publish(exchange='', routing_key='order_status', body=json.dumps(status_update))

        return order_pb2.OrderResponse(shipping_date="2025-04-15", order_status="shipped")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    order_pb2_grpc.add_OrderServiceServicer_to_server(OrderService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()