from communication import Communication
from recognition import Recognition
from config import Config
from loguru import logger
import multiprocessing as mp


class App:

    def __init__(self):
        self.total_cart = 12
        self.size_image = 480
        self.camera = 0
        # rasp -> port='/dev/ttyAMA0'
        self.port = '/dev/ttyUSB0'
        self.rate = 115200
        self.show_image = True
        self.use_rasp = False
        self.actions = mp.Array('i', [0])
        self.pattern_code = 'QRCONF'.upper()
        self.receive_truck, self.send_truck = mp.Pipe()
        self.c = Communication(port=self.port, rate=self.rate)
        self.config = Config(port=self.port, rate=self.rate)
        self.station = self.config.read_config()
        self.r = Recognition(
            camera=self.camera,
            image_size=self.size_image,
            show_image=self.show_image,
            limit=self.total_cart,
            use_rasp=self.use_rasp,
            pattern_code=self.pattern_code,
            communication=self.c
        )
        self.carts = mp.Array('i', self.r.create_list(self.total_cart))

    def recognition_service(self):
        self.r.reader(carts=self.carts, actions=self.actions, plot_truck=self.send_truck)

    def communication_service(self):
        self.c.read_protocol(actions=self.actions, plot_truck=self.receive_truck, station=self.station)


if __name__ == '__main__':

    logger.info('Start application...')
    app = App()

    if app.station == '':
        app.config.set_configuration()

    communication_process = mp.Process(target=app.communication_service, args=())
    recognition_process = mp.Process(target=app.recognition_service, args=())

    try:
        communication_process.start()
        recognition_process.start()

        communication_process.join()
        recognition_process.join()

    except Exception as e:
        logger.error(e)
        recognition_process.terminate()
        communication_process.terminate()
        logger.info('End application.')
