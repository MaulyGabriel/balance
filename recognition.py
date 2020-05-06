from imutils.video import VideoStream
from time import localtime, sleep
from loguru import logger
from pyzbar import pyzbar
import threading
import pandas as pd
import numpy as np
import imutils
import cv2


class Recognition:

    def __init__(self, config, db):
        self.config = config
        self.package_log = list()
        self.truck_log = list()
        self.cart_log = list()
        self.hour_log = list()
        self.b2 = ''
        self.db = db
        self.timer = None
        self.total_cart = 12

    @staticmethod
    def create_list(size):

        array = list(np.zeros([size]))
        array = list(map(lambda x: int(x), array))

        return array

    @staticmethod
    def scanner(frame):

        code = ''

        image = pyzbar.decode(frame)

        for data in image:
            text = data.data.decode('utf-8')
            code = '{}'.format(text)

        return code

    @staticmethod
    def get_format_date():

        date = localtime()

        year, month, day, hour, minutes, seconds = date[0], date[1], date[2], date[3], date[4], date[5]

        def verify_number(number):
            if len(str(number)) == 1:
                number = '0{}'.format(number)

            return number

        year = str(year)
        year = year[2:]
        day = verify_number(day)
        month = verify_number(month)
        hour = verify_number(hour)
        minutes = verify_number(minutes)
        seconds = verify_number(seconds)

        format_data = '{}/{}/{}-{}:{}:{}'.format(day, month, year, hour, minutes, seconds)

        return format_data

    def clear_b2(self):
        self.b2 = ''

    def start_camera(self):

        camera = VideoStream(
            usePiCamera=True,
            resolution=(self.config.width, self.config.height),
            framerate=self.config.fps).start()

        sleep(0.8)

        return camera

    def process_frame(self, frame):

        frame = imutils.resize(frame, self.config.resize_image)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        return frame

    def check_cache(self):
        packages = self.db.consult()
        return len(packages['id']) > 0

    def send_cache(self, callback, commands):

        have_cache = self.check_cache()
        have_commands = len(commands) == 0

        if have_cache and have_commands:
            callback()

        self.timer.cancel()
        self.timer = None

    def save_logs(self):

        logs = {

            'number_truck': self.package_log,
            'total_cart': self.cart_log,
            'cart_recognition': self.truck_log,
            'day': self.hour_log,
        }

        self.package_log = list()
        self.cart_log = list()
        self.truck_log = list()
        self.hour_log = list()

        df = pd.DataFrame(logs)
        with open('logs.csv', 'a') as f:
            df.to_csv(f, index=False, header=False)

        logger.success('Logs saved.')

    def reader(self, carts, callback, commands):

        camera = self.start_camera()

        truck = 0

        status_truck = 0

        while True:

            try:

                frame = camera.read()
                frame = self.process_frame(frame=frame)

                code = self.scanner(frame)

                if code != '':

                    cart = code.split('-')

                    if cart[0].upper() != "QRCODE0":

                        if cart[0].upper() == "CAM".upper():
                            truck = cart[1]
                            status_truck = 1

                        if truck == 0:
                            truck = 0
                            status_truck = 0

                        try:

                            new_code = cart[0]

                            if int(new_code) in carts[:]:
                                pass
                            else:
                                logger.info('Truck: {}, Code: {}'.format(truck, new_code))
                                carts[0:self.total_cart - 1] = carts[1:self.total_cart]
                                carts[self.total_cart - 1] = int(cart[0])
                        except Exception as e:
                            logger.error(e)

                    elif cart[0].upper() == "QRCODE0":

                        total_identify = self.total_cart - carts[:].count(0)

                        if total_identify == 0:
                            pass
                        else:
                            codes_carts = ''

                            aux_cart = carts[:]

                            for c in aux_cart:

                                if c != 0:
                                    codes_carts += ',{}'.format(c)
                                else:
                                    pass

                            format_package = 'QRBE2,{},{}{}'.format(
                                truck,
                                total_identify,
                                codes_carts
                            )

                            self.package_log.append(truck)
                            self.cart_log.append(total_identify)
                            self.truck_log.append(status_truck)
                            self.hour_log.append(self.get_format_date())

                            self.save_logs()

                            truck = 0
                            self.b2 = format_package
                            carts[:] = self.create_list(size=self.total_cart)

                            callback()

                    else:
                        pass
                else:
                    pass

                    if self.timer is None:
                        logger.info('INIT TIMER CACHE')
                        self.timer = threading.Timer(120, self.send_cache, [callback, commands])
                        self.timer.start()

                if bool(int(self.config.show_image)):
                    cv2.imshow('Solinftec', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                else:
                    pass
            except Exception as e:
                logger.error(e)

        camera.stop()
        cv2.destroyAllWindows()
