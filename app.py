from communication import Communication
from recognition import Recognition
from config import Config
from loguru import logger
import multiprocessing as mp
import json


class App:

    def __init__(self):
        self.config_json = self.read_config()

        self.actions = mp.Array('i', [0])
        self.receive_truck, self.send_truck = mp.Pipe()

        self.c = Communication(config=self.config_json)
        self.r = Recognition(config=self.config_json, communication=self.c)

        self.config_station = Config(config=self.config_json)

        self.station = self.config_json['project']['station_id']
        self.carts = mp.Array('i', self.r.create_list(self.config_json['carts']['total']))

    @staticmethod
    def read_config():
        with open('./config.json') as j:
            config = json.load(j)

        return config

    def recognition_service(self):
        self.r.reader(carts=self.carts, actions=self.actions, plot_truck=self.send_truck)

    def communication_service(self):
        self.c.read_protocol(actions=self.actions, plot_truck=self.receive_truck, station=self.station)


if __name__ == '__main__':
    logger.info('Start application...')

    app = App()

    if app.station == '':
        app.config_station.set_configuration()

    communication_process = mp.Process(target=app.communication_service, args=())
    recognition_process = mp.Process(target=app.recognition_service, args=())

    try:
        communication_process.start()
        recognition_process.start()

        communication_process.join()
        recognition_process.join()

    except KeyboardInterrupt as e:
        logger.error(e)
        recognition_process.terminate()
        communication_process.terminate()
        logger.info('End application.')
