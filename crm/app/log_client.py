import json
import logging
import aio_pika
from aio_pika import ExchangeType, Message
import requests
from datetime import datetime
import os
from typing import Dict, Any, Optional

class SystemInteractionLogger:
    """
    Client for the central Logging Service.
    Used by services to log interactions via RabbitMQ or REST API.
    """
    def __init__(
        self,
        service_name: str,
        rabbitmq_url: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq/"),
        logging_api_url: str = os.getenv("LOGGING_API_URL", "http://logging:8002/logs"),
        local_fallback_path: Optional[str] = None
    ):
        self.service_name = service_name
        self.rabbitmq_url = rabbitmq_url
        self.logging_api_url = logging_api_url
        self.local_fallback_path = local_fallback_path

        self.connection = None
        self.channel = None
        self.logger = logging.getLogger(f"{service_name}_log_client")

        if local_fallback_path:
            file_handler = logging.FileHandler(local_fallback_path)
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            self.logger.addHandler(file_handler)

    async def connect_rabbitmq(self) -> bool:
        try:
            self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
            self.channel = await self.connection.channel()
            return True
        except Exception as e:
            self.logger.error(f"Error connecting to RabbitMQ: {e}")
            return False

    async def log_interaction(
        self,
        target_system: str,
        interaction_type: str,
        message: Dict[str, Any],
        status: str = "success",
        error_message: Optional[str] = None
    ) -> bool:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "source_system": self.service_name,
            "target_system": target_system,
            "interaction_type": interaction_type,
            "payload": message,
            "status": status
        }
        if error_message:
            log_entry["error_message"] = error_message
        try:
            if not self.connection or self.connection.is_closed:
                await self.connect_rabbitmq()
            exchange = await self.channel.declare_exchange(
                "logging_exchange",
                ExchangeType.FANOUT,
                durable=True
            )
            await exchange.publish(
                Message(
                    body=json.dumps(log_entry).encode('utf-8'),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key="logging_events"
            )
            return True
        except Exception as e:
            self.logger.warning(f"RabbitMQ logging failed, trying REST: {e}")
        try:
            response = requests.post(
                self.logging_api_url,
                json=log_entry,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 201:
                return True
            self.logger.warning(f"REST logging failed status {response.status_code}")
        except Exception as e:
            self.logger.warning(f"REST logging failed: {e}")
        if self.local_fallback_path:
            self.logger.info(f"Logging locally: {log_entry}")
            return True
        return False
