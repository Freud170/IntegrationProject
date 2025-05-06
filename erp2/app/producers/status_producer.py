import json
import os
import pika
import logging
from typing import Dict, Any, Optional

# Import our system interaction logger
from shared.logging.log_client import SystemInteractionLogger

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join('logs', 'status_producer.log'))
    ]
)
logger = logging.getLogger("erp2.status_producer")

# Initialize logger client
log_client = SystemInteractionLogger(
    service_name="erp2",
    rabbitmq_url=os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq/"),
    local_fallback_path="logs/local_system_logs.log"
)

def send_status_update(order_id: str, status: str):
    """
    Sends order status updates to the e-commerce system via RabbitMQ.
    
    Args:
        order_id: ID of the order being updated
        status: New status of the order (e.g., "Processed", "Shipped", "Cancelled")
    """
    try:
        # Connect to RabbitMQ
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=os.getenv("RABBITMQ_HOST", "rabbitmq"),
                port=int(os.getenv("RABBITMQ_PORT", "5672")),
                credentials=pika.PlainCredentials(
                    username=os.getenv("RABBITMQ_USER", "guest"),
                    password=os.getenv("RABBITMQ_PASS", "guest")
                )
            )
        )
        channel = connection.channel()
        
        # Ensure queue exists
        channel.queue_declare(queue='order_status', durable=True)
        
        # Prepare message
        message = {
            "order_id": order_id,
            "status": status
        }
        
        # Publish message
        channel.basic_publish(
            exchange='',
            routing_key='order_status',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
                content_type='application/json'
            )
        )
        
        logger.info(f"Sent status update for order {order_id}: {status}")
        
        # Log the interaction
        log_client.log_interaction_sync(
            target_system="ecommerce",
            interaction_type="RabbitMQ",
            message=message,
            status="success"
        )
        
        # Close connection
        connection.close()
        return True
        
    except Exception as e:
        error_message = f"Error sending status update: {str(e)}"
        logger.error(error_message)
        
        # Log the failed interaction
        log_client.log_interaction_sync(
            target_system="ecommerce",
            interaction_type="RabbitMQ",
            message={"order_id": order_id, "status": status},
            status="error",
            error_message=error_message
        )
        return False

# Async version for future use
async def send_status_update_async(order_id: str, status: str):
    """
    Async wrapper for send_status_update - for future implementation
    """
    # This is a placeholder for future async implementation
    # For now, we'll just call the sync version
    return send_status_update(order_id, status)