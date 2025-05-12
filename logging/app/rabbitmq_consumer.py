import json
import asyncio
import logging
from typing import Optional, Dict, Any
import aio_pika
from aio_pika import ExchangeType
from .logger import async_logger

class LoggingRabbitMQConsumer:
    """
    RabbitMQ-Konsument für den Logging-Service.
    Empfängt Nachrichten von allen Services und protokolliert sie zentral.
    """
    
    def __init__(self, rabbitmq_url: str = "amqp://guest:guest@rabbitmq/"):
        """
        Initialisiert den RabbitMQ-Konsumenten.
        
        :param rabbitmq_url: URL zur RabbitMQ-Instanz
        """
        self.rabbitmq_url = rabbitmq_url
        self.connection = None
        self.channel = None
        self._ready = asyncio.Event()
        self._stopping = False
        self._reconnect_delay = 5.0  # Verzögerung in Sekunden vor dem Wiederverbinden
        self._logger = logging.getLogger("logging_service.rabbitmq")
        self.exchange = None
        self.queue = None
    
    async def connect(self) -> None:
        """Stellt eine Verbindung zu RabbitMQ her."""
        try:
            self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=10)
            self._ready.set()
            self._logger.info("Verbindung zu RabbitMQ hergestellt")
        except Exception as e:
            self._logger.error(f"Fehler beim Verbinden mit RabbitMQ: {str(e)}")
            self._ready.clear()
            if not self._stopping:
                asyncio.create_task(self._reconnect())
    
    async def _reconnect(self) -> None:
        """Versucht, die Verbindung zu RabbitMQ wiederherzustellen."""
        await asyncio.sleep(self._reconnect_delay)
        await self.connect()
    
    async def setup_queues(self) -> None:
        """Richtet die Warteschlangen für das Logging ein."""
        await self._ready.wait()
        
        # Declare fanout exchange for logging events and bind a durable queue
        self.exchange = await self.channel.declare_exchange(
            "logging_exchange",
            ExchangeType.FANOUT,
            durable=True
        )
        self.queue = await self.channel.declare_queue(
            "logging_events",
            durable=True
        )
        await self.queue.bind(self.exchange)
    
    async def consume_logs(self) -> None:
        """
        Verarbeitet eingehende Lognachrichten von allen Services.
        """
        await self._ready.wait()
        
        # Consume log envelope events
        queue = self.queue
        
        async def process_message(message: aio_pika.IncomingMessage) -> None:
            """
            Verarbeitet eine eingehende Nachricht und protokolliert sie.
            
            :param message: Die eingehende RabbitMQ-Nachricht
            """
            async with message.process():
                try:
                    # Each message is already a log envelope
                    body = message.body.decode('utf-8')
                    log_data = json.loads(body)
                    # Forward into file-based async_logger
                    await async_logger.log_interaction(
                        source_system=log_data.get('source_system', 'unknown'),
                        target_system=log_data.get('target_system', 'unknown'),
                        interaction_type=log_data.get('interaction_type', 'unknown'),
                        message=log_data.get('payload', {}),
                        status=log_data.get('status', 'SUCCESS'),
                        error_message=log_data.get('error_message')
                    )
                    self._logger.debug(f"Logged event: {log_data.get('source_system')} -> {log_data.get('target_system')}")
                except Exception as e:
                    self._logger.error(f"Error processing log envelope: {e}")
        
        # Nachrichten asynchron verarbeiten
        await queue.consume(process_message)
        self._logger.info("Log-Konsument gestartet")
    
    async def start(self) -> None:
        """Startet den RabbitMQ-Konsumenten."""
        await self.connect()
        await self.setup_queues()
        await self.consume_logs()
    
    async def stop(self) -> None:
        """Stoppt den RabbitMQ-Konsumenten."""
        self._stopping = True
        if self.connection:
            await self.connection.close()
        self._logger.info("RabbitMQ-Konsument gestoppt")

# Erstellen einer Singleton-Instanz
rabbitmq_consumer = LoggingRabbitMQConsumer()