from flask import jsonify
from .rabbitmqconnectionclass import RabbitMqConnectionClass
from rabbitmq_client import RMQProducer, ExchangeParams, PublishParams, QueueParams, QueueBindParams
import pika
import json
import logging, coloredlogs
import time

import functools
from concurrent.futures import ThreadPoolExecutor
import asyncio

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger = logger)

def force_async(fn):
    '''
    turns a sync function to async function using threads
    '''
    from concurrent.futures import ThreadPoolExecutor
    import asyncio
    pool = ThreadPoolExecutor()

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        future = pool.submit(fn, *args, **kwargs)
        return asyncio.wrap_future(future)  # make it awaitable

    return wrapper


class RabbitHandler(object):
    _ready = False
    _logPrefix = '[RabbitHandler]'
    __instance = None
    _queue_name = 'test_queue'
    _exchange_name = 'test_exchange'
    _routing_key = 'test.*'
    _routing_name = 'test.*'
    
    @staticmethod
    def getInstance():
        logger.debug(f'[RabbitHandler:getInstance] has been called -> {RabbitHandler.__instance}')
        if RabbitHandler.__instance == None:
            RabbitHandler()
        return RabbitHandler.__instance
    
    @property
    def is_ready(self):
        return self._ready
    
    
    def __init__(self) -> None:
        logger.debug(f'[RabbitHandler:__init__] lets see what happens')
        if RabbitHandler.__instance != None:
            raise Exception('This class is a singleton')
        else:
            RabbitHandler.__instance = self      
            self.creds = pika.PlainCredentials("ai", "Aveve2008")
            self.connection_parameters = pika.ConnectionParameters(host='192.168.1.181', port=5672, credentials=self.creds)
            self.connection = RabbitMqConnectionClass(connection_parameters=self.connection_parameters)      
            logger.debug(f'{self._logPrefix} registering handle_on_ready')
            self.connection.handle_on_ready(self.on_ready)      
        logger.debug('[RabbitHandler:__init__] finished init ')
            
    
    async def prepare_connections(self):
        logger.debug(f'[RabbitHandler:prepare_connections] start preparing connections')    
        self.connection.start()
    
    def on_exchange_ready(self):
        logger.debug(f'[RabbitHandler:on_exchange_ready] exchange has been declared')    
        self._exchange_ready = True
        self.connection.declare_queue(QueueParams(self._queue_name), self.on_queue_ready)
    
    def on_queue_ready(self, x):
        logger.debug(f'[RabbitHandler:on_queue_ready] queue is ready => {x}')
        self._queue_ready = True
        self.connection.bind_queue(QueueBindParams(
                    queue=self._queue_name, 
                    exchange=self._exchange_name, 
                    routing_key=self._routing_key), 
                self.on_queue_binding)
    
    def on_queue_binding(self, x):
        logger.debug(f'[RabbitHandler:on_queue_binding] queue binding has been setup -> {x}')    
        self._queue_binding_ready = True
        self.producer = RMQProducer(connection_parameters=self.connection_parameters)
        self.producer.start()
        while not self.producer.ready:
            logger.debug(f'{self._logPrefix} Producer wasnt ready yet. Sleep for 2 seconds.')
            time.sleep(2)
        logger.debug(f'{self._logPrefix} producer became ready.')
        self._ready = True
            
    def on_ready(self):
        #self._ready = True
        logger.debug(f'{self._logPrefix} handling onready of connection')
        self.connection.declare_exchange(ExchangeParams(self._exchange_name), self.on_exchange_ready)     
    
    def publish_message(self, object_to_send):
        logger.debug(f'{self._logPrefix} start sending object to RabbitMQ -> {self._ready}')
        if self._ready :
            self.producer.basic_publish(json.dumps(object_to_send), self._exchange_name, self._routing_name)
        else:
            logger.debug(f'{self._logPrefix} not ready yet')
        # self.producer.publish(json.dumps(object_to_send), 
        #                       exchange_params=ExchangeParams(exchange="ai_exchange"),
        #                       routing_key='ai.create.model',
        #                       )
    
    def disconnect(self):
        if not self.producer is None:
            self.producer.stop()
            
        if not self.connection is None:
            self.connection.stop()
            