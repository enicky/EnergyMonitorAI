
from rabbitmq_client import RMQConnection, MandatoryError
from rabbitmq_client.connection import DeclarationError

import logging, coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install("DEBUG", logger=logger)

class RabbitMqConnectionClass(RMQConnection):
    logPrefix= '[RabbitMqConnectionClass]'
    ready = False
    def __init__(self, connection_parameters=None):
        super().__init__(connection_parameters)
       
    def handle_on_ready(self, callback):
        self._on_ready_callback = callback
        
    def on_ready(self):
        
        logger.info(f'{self.logPrefix} on_ready')
        self.ready = True
        self._on_ready_callback()
        return super().on_ready()
    
    
    def on_close(self, permanent=False):
        logger.info(f'{self.logPrefix} on_close')
        return super().on_close(permanent)    
        
    def on_error(self, error: MandatoryError | DeclarationError):
        logger.info(f'{self.logPrefix} on_error {error}')
        return super().on_error(error)