import os
from ai.pr import PR
from controllers.aihandler import AiHandler
from controllers.filehandler import FileHandler

from flask import Flask
from flask_restful import  Api

from business.rabbithandler import RabbitHandler
from helpers.customformatter import CustomFormatter

import coloredlogs, logging, time
import asyncio
#logging.basicConfig(level=logging.INFO)
logging.getLogger("pika").setLevel(logging.WARNING)
logging.getLogger('rabbitmq_client').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger = logger)


UPLOAD_FOLDER = 'files'


async def main():
    logger.info(f'[main] pre rabbithandler instance')
    rabbitHandler = RabbitHandler.getInstance()
    logger.info(f'[main] pre prepare connections')
    await rabbitHandler.prepare_connections()
    logger.info(f'[main] start waiting for connections to become ready ')
    while not rabbitHandler.is_ready:
        logger.debug(f'[main] rabbithandler is not ready yet')
        time.sleep(2)
    
    logger.info(f'[main] rabbithandler is ready')

    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    api = Api(app)
            
    api.add_resource(FileHandler, "/files")
    api.add_resource(AiHandler, "/ai")

    app.run(debug=False)    

if  __name__ == "__main__":
    asyncio.run(main())