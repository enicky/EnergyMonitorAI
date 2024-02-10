
from .datacontroller import DataController
from .modelcontroller import ModelController
from .ShallowRegressionLSTM import ShallowRegressionLSTM
from .sequencedataset import SequenceDataset
import pandas as pd
from torch.utils.data import DataLoader
import torch
import logging
from torch import nn
import sys
import logging, coloredlogs
logger = logging.getLogger(__name__)
coloredlogs.install('DEBUG', logger=logger)

target_sensor = "energy_power" 
forecast_follow = 21
period_between_each_row = "30min"
forecast_col = "Model forecast"
columns_features = ["bme_temp", "bme_hum", "hour", "day_of_week", "day_of_year"]
folder_path = "./files"
learning_rate = 0.001#5e-5
num_hidden_units = 16
model_train_epoch_count = 530
train_test_split_factor = 0.80
batch_size = 64
sequence_length = 30

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
#logger.info(device)
#logger.info(sys.version)
#logger.info(f'pd. __version__ == {pd.__version__}')
#logger.info(f'torch version {torch.__version__}')

class PR:
    def __init__(self) -> None:
        pass
    
    def process(self, uuid, model_filename):
        logPrefix= '[PR:process]'
        dataController = DataController(
            target_sensor,
            forecast_follow,
            period_between_each_row,
            forecast_col,
            folder_path,
            learning_rate,
            num_hidden_units,
            model_train_epoch_count,
            train_test_split_factor,
            batch_size,
            sequence_length,
            columns_features,
        )

        data = dataController.readData()

        data = dataController.prepareData(data)

        data = dataController.createFeaturesData(data)

        features = list(data.columns.difference([target_sensor]))
        logger.info(f'[update] features : {features}')
        shiftFollowColumn = f"{target_sensor}_follow{forecast_follow}"
        #logger.info(f'[main] shiftFollowColumn {shiftFollowColumn}')
        #logger.info(f'[main] len(data)= {len(data)}')
        data = dataController.createShiftColumn(data, shiftFollowColumn)
        #logger.info(f'[main] len(data)= {len(data)}')
        data_train, data_test = dataController.splitData(data)
        logger.info(f'[main] data_train {len(data_train)} and data_test {len(data_test)}' )
        dataController.scaleTransformData(data_train, shiftFollowColumn, "fit")

        data_train = dataController.scaleTransformData(
             data_train, shiftFollowColumn, "transform"
         )
        data_test = dataController.scaleTransformData(
             data_test, shiftFollowColumn, "transform"
         )

        torch.manual_seed(101)

        SeqData_train = SequenceDataset(
            data_train,
            target=shiftFollowColumn,
            features=features,
            sequence_length=sequence_length,
        )
        SeqData_test = SequenceDataset(
            data_test,
            target=shiftFollowColumn,
            features=features,
            sequence_length=sequence_length,
        )

        logger.info('[main] train_loader')
        train_loader = DataLoader(SeqData_train, batch_size=batch_size, shuffle=True, pin_memory=True)
        logger.info('[main] test_loader')
        self.test_loader = DataLoader(SeqData_test, batch_size=batch_size, shuffle=False, pin_memory=True)
        logger.info('[main] train_eval_loader')
        train_eval_loader = DataLoader(SeqData_train, batch_size=batch_size, shuffle=False, pin_memory = True)
        logger.info('[main] finished dataloaders ')
        self.model = ShallowRegressionLSTM(
            num_sensors=len(features), hidden_units=num_hidden_units
        )
        loss_function = nn.MSELoss()
        optimizer = torch.optim.Adam(self. model.parameters(), lr=learning_rate)

        modelController = ModelController(
            self.model, loss_function, optimizer, model_train_epoch_count
        )
        logger.info(f'{logPrefix} Start training model on {model_filename}')
        train_loss_list, test_loss_list = modelController.train_test_model(
            train_loader, self.test_loader, model_filename=model_filename
        )        
        return model_filename, train_loss_list, test_loss_list
        

        #data_train[forecast_col] = modelController.predict(train_eval_loader)
        #data_test[forecast_col] = modelController.predict(test_loader)
        
    def predict(self):
        
        self.model.load_state_dict(torch.load('models/model.pt'))
        self.model.eval()
        
        model_controller = ModelController(self.model, None, None, None)
        output = model_controller.predict(self.test_loader)
        logger.info(f'[pr:predict] output = {output}')