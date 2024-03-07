from fastapi import FastAPI, UploadFile, File
from dapr.clients import DaprClient
import json
import logging, coloredlogs
import os

logger = logging.getLogger(__name__)
coloredlogs.install('DEBUG', logger=logger)



app = FastAPI()


@app.get('/test')
async def test_root():
    logger.debug('Start calling test route')
    PUBSUB_NAME = 'pubsub'
    TOPIC_NAME = 'ai.listmodels'
    with DaprClient() as client:
        result = client.publish_event(
            pubsub_name=PUBSUB_NAME,
            topic_name=TOPIC_NAME,
            data=json.dumps({"success": True}),
            data_content_type='application/json',
            
        )
        logger.debug(f'Published event ... result = {result.headers}')
        
        
@app.post('/upload')
async def upload(file: UploadFile = File(...)):
    logger.debug(f'Uploading file ... ')
    try:
        logger.debug('pre....')
        contents = file.file.read()
        upload_folder = os.getenv("UPLOAD_FOLDER", 'files')
        logger.debug(f'using upload folder {upload_folder}')
        file_name = os.path.join(upload_folder, file.filename)
        logger.debug(f'file name {file_name}')
        with open(file_name, 'wb') as f:
            f.write(contents)
    except Exception:
        logger.error('Error uploading file')
        return {"message": "There was an error uploading the file"}
    finally:
        logger.debug('closing file')
        file.file.close()
    logger.debug(f'Finished uploading file {file.filename}')
    return {"message": f"Successfully uploaded {file.filename}"}

@app.get('/startai')
async def start_ai_training():
    logger.debug('Start calling start training route')
    PUBSUB_NAME = 'pubsub'
    TOPIC_NAME = 'ai.start.training'
    with DaprClient() as client:
        result = client.publish_event(
            pubsub_name=PUBSUB_NAME,
            topic_name=TOPIC_NAME,
            data=json.dumps({"success": True}),
            data_content_type='application/json',
            
        )
        logger.debug(f'Published event ... result = {result.headers}')
        

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)        