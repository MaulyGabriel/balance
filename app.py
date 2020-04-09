from communication import Communication
from recognition import Recognition
from loguru import logger
import multiprocessing as mp
import json

global actions

actions = [0]


class App:

    def __init__(self):
        self.config_json = self.read_config()

        self.r = Recognition(config=self.config_json)
        self.c = Communication(config=self.config_json, code_recognition=self.r)

        self.station = self.config_json['project']['station_id']
        self.carts = mp.Array('i', self.r.create_list(self.config_json['carts']['total']))

        self.connection = self.c.data_call()

        self.QRBE1 = self.c.create_digit('QRBE1,{}'.format(self.station))

    @staticmethod
    def read_config():
        with open('./config.json') as j:
            config = json.load(j)

        return config


if __name__ == '__main__':
    logger.info('Start application...')

    app = App()

    def send_b1():
        actions[0] = 1
        app.c.send_broadcast(connection=app.connection, message=app.QRBE1, actions=actions)


    try:

        app.connection.open()

        app.c.read_data(connection=app.connection, actions=actions)

        app.r.reader(carts=app.carts, actions=actions, callback=send_b1)

    except Exception as e:
        logger.error(e)
        logger.info('End application.')
