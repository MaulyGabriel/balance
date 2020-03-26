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

        self.c = Communication(port=self.config_json['serial']['port'], rate=self.config_json['serial']['baudrate'])
        self.config_station = Config(port=self.config_json['serial']['port'],
                                     rate=self.config_json['serial']['baudrate'])

        self.station = self.config_station.read_config()

        self.r = Recognition(
            camera=self.config_json['camera']['usb'],
            image_size=self.config_json['camera']['size_image'],
            show_image=bool(int(self.config_json['camera']['show_image'])),
            limit=self.config_json['carts']['total'],
            use_rasp=bool(int(self.config_json['camera']['raspberry'])),
            pattern_code=self.config_json['project']['pattern'],
            communication=self.c
        )
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
