from imutils.video import VideoStream
from time import localtime, sleep
from loguru import logger
from pyzbar import pyzbar
import pandas as pd
import numpy as np
import imutils
import cv2


class Recognition:

    def __init__(self, config):
        self.config = config
        self.package_log = list()
        self.truck_log = list()
        self.cart_log = list()
        self.hour_log = list()
        self.b2 = ''

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

        if bool(int(self.config['camera']['raspberry'])):
            camera = VideoStream(
                usePiCamera=bool(int(self.config['camera']['raspberry'])),
                resolution=(
                    self.config['camera']['resolution']['width'], self.config['camera']['resolution']['height']),
                framerate=self.config['camera']['fps']).start()
        else:
            camera = VideoStream(src=self.config['camera']['usb']).start()

        sleep(0.8)

        return camera

    def process_frame(self, frame):

        frame = imutils.resize(frame, self.config['camera']['size_image'])
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        return frame

    def reader(self, carts, actions, callback):

        logger.info('Recognition start')

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

                    if actions[0] == 0:

                        if cart[0].upper() != self.config['project']['pattern']:

                            if cart[0].upper() == 'CAM'.upper():
                                truck = cart[1]
                                status_truck = 1

                            if truck == 0:
                                truck = 0
                                status_truck = 0

                            try:
                                if int(cart[0]) in carts[:]:
                                    pass
                                else:
                                    logger.info('Truck: {}'.format(truck))
                                    logger.info('Add cart in package: {}'.format(cart[0]))
                                    carts[0:int(self.config['carts']['total']) - 1] = carts[1:int(
                                        self.config['carts']['total'])]
                                    carts[int(self.config['carts']['total']) - 1] = int(cart[0])
                            except Exception as e:
                                logger.error(e)

                        elif cart[0].upper() == self.config['project']['pattern']:

                            total_identify = int(self.config['carts']['total']) - carts[:].count(0)

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

                                logs = {

                                    'number_truck': self.package_log,
                                    'total_cart': self.cart_log,
                                    'cart_recognition': self.truck_log,
                                    'day': self.hour_log,
                                }

                                logger.debug(logs)

                                self.package_log = list()
                                self.cart_log = list()
                                self.truck_log = list()
                                self.hour_log = list()

                                df = pd.DataFrame(logs)
                                with open('logs.csv', 'a') as f:
                                    df.to_csv(f, index=False, header=False)

                                truck = 0
                                self.b2 = format_package
                                carts[:] = self.create_list(size=int(self.config['carts']['total']))

                                callback()

                        else:
                            pass
                    else:
                        pass
                else:
                    pass

                if bool(int(self.config['camera']['show_image'])):
                    cv2.imshow('Image', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                else:
                    pass
            except Exception as e:
                logger.error(e)

        camera.stop()
        cv2.destroyAllWindows()
