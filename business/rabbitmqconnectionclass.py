
from rabbitmq_client import RMQConnection, MandatoryError
from rabbitmq_client.connection import DeclarationError

import logging

class RabbitMqConnectionClass(RMQConnection):
    logPrefix= '[RabbitMqConnectionClass]'
    ready = False
    def __init__(self, connection_parameters=None):
        logging.info(f"{self.logPrefix} -> {connection_parameters}" )
        super().__init__(connection_parameters)
       
    def handle_on_ready(self, callback):
        self._on_ready_callback = callback
        
    def on_ready(self):
        logging.info(f'{self.logPrefix} on_ready')
        self.ready = True
        super().on_ready()
        self._on_ready_callback()
    
    
    def on_close(self, permanent=False):
        logging.info(f'{self.logPrefix} on_close')
        return super().on_close(permanent)    
        
    def on_error(self, error: MandatoryError | DeclarationError):
        logging.info(f'{self.logPrefix} on_error {error}')
        return super().on_error(error)