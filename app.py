from loguru import logger
from recognition import Recognition
from communication import Communication
import multiprocessing as mp


class App:

    def __init__(self):
        self.station_id = 1
        self.total_cart = 2
        self.receive, self.send = mp.Pipe()

        # [0]-Status camera  [1]-Send truck  [2]-Send package
        self.actions = mp.Array('i', [0])

        self.c = Communication(port='/dev/ttyUSB0', rate=115200)

        self.r = Recognition(
            station_id=self.station_id,
            camera=0,
            image_size=480,
            show_image=True,
            limit=self.total_cart,
            use_rasp=False,
            pattern_code='x'
        )

        self.carts = mp.Array('i', self.r.create_list(self.total_cart))

    def recognition_service(self):
        self.r.reader(carts=self.carts, actions=self.actions, plot=self.send)

    def communication_service(self):
        self.c.read_protocol(actions=self.actions, plot=self.receive)


if __name__ == '__main__':

    logger.info('Start application...')
    app = App()
    recognition_process = mp.Process(target=app.recognition_service, args=())
    communication_process = mp.Process(target=app.communication_service, args=())

    try:
        communication_process.start()
        recognition_process.start()

        communication_process.join()
        recognition_process.join()

    except KeyboardInterrupt:
        recognition_process.terminate()
        communication_process.terminate()
        logger.info('End application.')
