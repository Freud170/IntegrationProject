import grpc
import pika
import logging
import os
from concurrent import futures

# Set up logging to a file
logging.basicConfig(filename='event_logs.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

# RabbitMQ setup
def rabbitmq_listener():
    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))
    channel = connection.channel()
    channel.queue_declare(queue='events')

    def callback(ch, method, properties, body):
        logging.info(f"RabbitMQ Event: {body.decode()}")

    channel.basic_consume(queue='events', on_message_callback=callback, auto_ack=True)
    logging.info("RabbitMQ listener started.")
    channel.start_consuming()

# gRPC setup
class EventServiceServicer(grpc.Service):
    def LogEvent(self, request, context):
        logging.info(f"gRPC Event: {request.message}")
        return grpc.Empty()

def grpc_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # Replace `EventServiceServicer` and `add_EventServiceServicer_to_server` with actual service definitions
    # grpc.add_EventServiceServicer_to_server(EventServiceServicer(), server)
    grpc_port = os.getenv('GRPC_PORT', '50051')
    server.add_insecure_port(f'[::]:{grpc_port}')
    logging.info(f"gRPC server started on port {grpc_port}.")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    import threading

    # Start RabbitMQ listener in a separate thread
    rabbitmq_thread = threading.Thread(target=rabbitmq_listener, daemon=True)
    rabbitmq_thread.start()

    # Start gRPC server
    grpc_server()