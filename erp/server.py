import grpc
from concurrent import futures
import logging

from erp.services.order_service import OrderProcessor
import erp.protos.order_pb2 as order_pb2
import erp.protos.order_pb2_grpc as order_pb2_grpc

# Logger Setup
logging.basicConfig(filename="./logs/erp.log", level=logging.INFO)

class OrderService(order_pb2_grpc.OrderServiceServicer):
    def __init__(self):
        self.processor = OrderProcessor()

    def ProcessOrder(self, request, context):
        logging.info(f"Order erhalten: {request.order_id} mit Menge {request.quantity}")

        try:
            # Hier m\u00fcsste man eigentlich auch das Produkt ID mit\u00fcbergeben (sp\u00e4ter verbessern)
            shipping_date, order_status = self.processor.process_order(
                request.order_id, "product_001", request.quantity
            )

            return order_pb2.OrderResponse(
                shipping_date=shipping_date,
                order_status=order_status
            )

<<<<<<< Updated upstream
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return order_pb2.OrderResponse()
=======
        self.publish_status_update(request.order_id, order_status)

        return OrderResponse(
            shipping_date=shipping_date,
            order_status=order_status
        )

    def publish_status_update(self, order_id, status):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq", port=5672))
        channel = connection.channel()
        channel.queue_declare(queue='order_status_update', durable=True)

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
>>>>>>> Stashed changes

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    order_pb2_grpc.add_OrderServiceServicer_to_server(OrderService(), server)
    server.add_insecure_port('[::]:50051')
    logging.info("gRPC Server l\u00e4uft auf Port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
<<<<<<< Updated upstream
=======
    logging.basicConfig(level=logging.INFO)
>>>>>>> Stashed changes
    serve()
