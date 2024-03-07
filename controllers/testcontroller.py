from flask_restful import Resource
from dapr.clients import DaprClient
import json

import logging, coloredlogs
logger = logging.getLogger(__name__)
coloredlogs.install('DEBUG', logger=logger)


class TestController(Resource):
    def __init__(self) -> None:
        logger.debug(f'CTOR of TestController ...')
        super().__init__()
        
    def get(self):
        logger.debug(f'TestController get request')
        with DaprClient() as client:
            logger.debug('Starting to publish event to ai.listmodels')
            result = client.publish_event('pubsub', topic_name='ai.listmodels', data=json.dumps({"request": "list_ai_models"}))
            logger.debug(f'Result from publishing event = {result.headers}')
            