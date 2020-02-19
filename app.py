from loguru import logger
from recognition import Recognition
from communication import Communication
import multiprocessing as mp


class App:

    def __init__(self):
        self.station_id = 1
        self.total_cart = 12
        self.receive_truck, self.send_truck = mp.Pipe()
        self.receive_carts, self.send_carts = mp.Pipe()
        self.actions = mp.Array('i', [0])
        # rasp -> port='/dev/ttyAMA0'
        self.c = Communication(port='/dev/ttyUSB0', rate=115200)

        self.r = Recognition(
            station_id=self.station_id,
            camera=1,
            image_size=480,
            show_image=True,
            limit=self.total_cart,
            use_rasp=False,
            pattern_code='x'.upper()
        )

        self.carts = mp.Array('i', self.r.create_list(self.total_cart))

    def recognition_service(self):
        self.r.reader(carts=self.carts, actions=self.actions, plot_truck=self.send_truck, plot_carts=self.send_carts)

    def communication_service(self):
        self.c.read_protocol(actions=self.actions, plot_truck=self.receive_truck, plot_carts=self.receive_carts)


if __name__ == '__main__':

    logger.info('Start application...')
    app = App()
    communication_process = mp.Process(target=app.communication_service, args=())
    recognition_process = mp.Process(target=app.recognition_service, args=())

    try:
        communication_process.start()
        recognition_process.start()

        communication_process.join()
        recognition_process.join()

    except KeyboardInterrupt:
        recognition_process.terminate()
        communication_process.terminate()
        logger.info('End application.')
