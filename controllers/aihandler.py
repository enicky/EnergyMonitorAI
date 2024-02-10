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

import logging, coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install('DEBUG', logger = logger)


import matplotlib
matplotlib.use('agg')

import matplotlib.pyplot as plt

class AiHandler(Resource):
    logPrefix = '[AiHandler]'
    def __init__(self) -> None:
        self._rabbit_handler = RabbitHandler.getInstance()
        self.trainer = PR()
        pass
    
    def post(self):       
        logPrefix= '[AiHandler:post]'
        currentUuid = uuid.uuid4()
        
        logger.info(f'[] json body {request.json} with currentUuid = {currentUuid}')
        method= request.json['method']
        
        if method == 'train':
            formatted_date = datetime.strftime(datetime.now(), '%Y%m%d_%H%M%S')
            model_file_name = f"models/model_epoch_{formatted_date}.pt"
            model_image_file_name =  f"model_x{formatted_date}"
            
            logger.info(f'{logPrefix} process train')
            x, train_loss_list, test_loss_list = self.trainer.process(currentUuid, model_file_name)
            plt.figure(figsize=(8, 6))
            
        # # Plotting the values after the loop ends
        #plt.figure(figsize=(8, 6))
            plt.plot(train_loss_list, label='Train Loss')
            plt.plot(test_loss_list, label='Test Loss')
            plt.xlabel('Iterations')
            plt.ylabel('Loss')
            plt.title('Loss Comparison - Stage Ivan Groffils')
            plt.legend()
            plt.grid(True)
            #plt.show()
            plt.savefig(f"models/{model_image_file_name}.png")
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
            logger.info(f'{logPrefix} Start Listing models ... current folder = {getcwd()}')
            onlyfiles = [f for f in listdir(modelsFolder) if isfile(join(modelsFolder, f))]
            logger.info(f'{logPrefix} onlyFiles: {onlyfiles}')
            return jsonify({
                'success' : True,
                'files' : onlyfiles
            })
        