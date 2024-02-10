from typing import Union
from flask_restful import Resource
from flask import request, jsonify
import sys
from os import listdir, getcwd
from os.path import isfile, join
import uuid

from business.rabbithandler import RabbitHandler
sys.path.append('..')



from ai.pr import PR
from datetime import datetime

import logging



class AiHandler(Resource):
    logPrefix = '[AiHandler]'
    def __init__(self) -> None:
        self._rabbit_handler = RabbitHandler.getInstance()
        self.trainer = PR()
        pass
    
    def post(self):
        
        
        logPrefix= '[AiHandler:post]'
        currentUuid = uuid.uuid4()
        
        logging.info(f'[] json body {request.json} with currentUuid = {currentUuid}')
        method= request.json['method']
        
        if method == 'train':
            formatted_date = datetime.strftime(datetime.now(), '%Y%m%d_%H%M%S')
            model_file_name = f"models/model_epoch_{formatted_date}.pt"
            
            logging.info(f'{logPrefix} process train')
            #self.trainer.process(currentUuid, model_file_name)
            object_to_send = {
                'success' : True, 
                "method" : method, 
                'model_filename' : model_file_name,
                'processing_uuid' : str(currentUuid)
                }
            self._rabbit_handler.publish_message(object_to_send)
            return jsonify(object_to_send)
        if method == 'listmodels':
            modelsFolder = 'models'
            logging.info(f'{logPrefix} Start Listing models ... current folder = {getcwd()}')
            onlyfiles = [f for f in listdir(modelsFolder) if isfile(join(modelsFolder, f))]
            logging.info(f'{logPrefix} onlyFiles: {onlyfiles}')
            return jsonify({
                'success' : True,
                'files' : onlyfiles
            })
        