import json
import asyncio
import logging
from typing import Dict, Any, Optional
import aio_pika
import requests
from datetime import datetime

class SystemInteractionLogger:
    """
    Client für den zentralen Logging-Service.
    
    Diese Klasse kann von allen Services verwendet werden, um ihre Interaktionen
    asynchron zu protokollieren, entweder über RabbitMQ oder REST API.
    """
    
    def __init__(
            self,
            service_name: str,
            rabbitmq_url: str = "amqp://guest:guest@rabbitmq/",
            logging_api_url: str = "http://logging:8002/logs",
            local_fallback_path: Optional[str] = None
        ):
        """
        Initialisiert den Logging-Client.
        
        :param service_name: Name des Services (z.B. 'ecommerce', 'erp', 'crm')
        :param rabbitmq_url: URL zur RabbitMQ-Instanz
        :param logging_api_url: URL zur REST API des Logging-Services
        :param local_fallback_path: Optionaler Pfad für lokale Logs, falls RabbitMQ und REST nicht verfügbar sind
        """
        self.service_name = service_name
        self.rabbitmq_url = rabbitmq_url
        self.logging_api_url = logging_api_url
        self.local_fallback_path = local_fallback_path
        
        # RabbitMQ-Verbindung
        self.connection = None
        self.channel = None
        
        # Logger für interne Zwecke
        self.logger = logging.getLogger(f"{service_name}_log_client")
        
        if local_fallback_path:
            # Lokalen Handler für Fallback einrichten
            file_handler = logging.FileHandler(local_fallback_path)
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(file_handler)
    
    async def connect_rabbitmq(self):
        """
        Stellt eine Verbindung zu RabbitMQ her.
        """
        try:
            self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
            self.channel = await self.connection.channel()
            
            # Deklariere die Queue
            await self.channel.declare_queue("system_interactions_logs", durable=True)
            
            return True
        except Exception as e:
            self.logger.error(f"Fehler beim Verbinden mit RabbitMQ: {str(e)}")
            return False
    
    async def log_interaction(
            self,
            target_system: str,
            interaction_type: str,
            message: Dict[str, Any],
            status: str = "success",
            error_message: Optional[str] = None
        ) -> bool:
        """
        Protokolliert eine Systeminteraktion asynchron.
        
        :param target_system: Zielsystem der Interaktion
        :param interaction_type: Art der Interaktion (z.B. 'REST', 'gRPC', 'RabbitMQ')
        :param message: Nachrichteninhalt
        :param status: Status der Interaktion ('success', 'error')
        :param error_message: Optionale Fehlermeldung
        :return: True, wenn das Logging erfolgreich war
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "source_system": self.service_name,
            "target_system": target_system,
            "interaction_type": interaction_type,
            "message": message,
            "status": status
        }
        
        if error_message:
            log_entry["error_message"] = error_message
            
        # Versuche zuerst RabbitMQ
        try:
            if not self.connection or self.connection.is_closed:
                await self.connect_rabbitmq()
                
            if self.channel and not self.channel.is_closed:
                await self.channel.default_exchange.publish(
                    aio_pika.Message(
                        body=json.dumps(log_entry).encode('utf-8'),
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                    ),
                    routing_key="system_interactions_logs"
                )
                return True
        except Exception as e:
            self.logger.warning(f"RabbitMQ Logging fehlgeschlagen, versuche REST API: {str(e)}")
        
        # Wenn RabbitMQ fehlschlägt, versuche REST API
        try:
            response = requests.post(
                self.logging_api_url,
                json=log_entry,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 201:
                return True
            else:
                self.logger.warning(f"REST API Logging fehlgeschlagen mit Status {response.status_code}")
        except Exception as e:
            self.logger.warning(f"REST API Logging fehlgeschlagen: {str(e)}")
            
        # Wenn alles fehlschlägt, lokales Logging als Fallback
        if self.local_fallback_path:
            self.logger.info(f"Fallback: Lokales Logging für {interaction_type} zu {target_system}")
            self.logger.info(json.dumps(log_entry))
            return True
            
        return False
        
    def log_interaction_sync(
            self,
            target_system: str,
            interaction_type: str,
            message: Dict[str, Any],
            status: str = "success",
            error_message: Optional[str] = None
        ) -> bool:
        """
        Synchrone Version des Loggings für nicht-async Kontext.
        
        Nutzt die REST API, da RabbitMQ asyncio benötigt.
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "source_system": self.service_name,
            "target_system": target_system,
            "interaction_type": interaction_type,
            "message": message,
            "status": status
        }
        
        if error_message:
            log_entry["error_message"] = error_message
            
        # Versuche REST API für synchrones Logging
        try:
            response = requests.post(
                self.logging_api_url,
                json=log_entry,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 201:
                return True
            else:
                self.logger.warning(f"REST API Logging fehlgeschlagen mit Status {response.status_code}")
        except Exception as e:
            self.logger.warning(f"REST API Logging fehlgeschlagen: {str(e)}")
            
        # Lokales Logging als Fallback
        if self.local_fallback_path:
            self.logger.info(f"Fallback: Lokales Logging für {interaction_type} zu {target_system}")
            self.logger.info(json.dumps(log_entry))
            return True
            
        return False
    
    async def close(self):
        """
        Schließt die RabbitMQ-Verbindung.
        """
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            self.logger.info("RabbitMQ-Verbindung geschlossen")