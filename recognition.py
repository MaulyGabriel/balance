from imutils.video import VideoStream
from time import localtime, sleep
from loguru import logger
from pyzbar import pyzbar
import pandas as pd
import numpy as np
import imutils
import cv2


class Recognition:

    def __init__(self, camera, image_size, show_image, limit, use_rasp, pattern_code, communication):
        self.camera = camera
        self.limit = limit
        self.use_rasp = use_rasp
        self.show_image = show_image
        self.image_size = image_size
        self.pattern_code = pattern_code
        self.c = communication
        self.package_log = list()
        self.truck_log = list()
        self.cart_log = list()
        self.hour_log = list()

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

    def reader(self, carts, actions, plot_truck):

        if self.use_rasp:
            camera = VideoStream(usePiCamera=self.use_rasp, resolution=(1640, 1232), framerate=65).start()
        else:
            camera = VideoStream(src=self.camera).start()

        sleep(0.8)

        truck = 0

        status_truck = 0

        while True:

            frame = camera.read()
            frame = imutils.resize(frame, self.image_size)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            code = self.scanner(frame)

            if code != '':

                cart = code.split('-')

                if actions[0] == 0:

                    # our code?
                    if cart[0].upper() != self.pattern_code:

                        # code is truck ?
                        if cart[0].upper() == 'CAM'.upper():
                            truck = cart[1]
                            status_truck = 1

                        if truck == 0:
                            truck = 0
                            status_truck = 0

                        # add code in  package
                        try:
                            if int(cart[0]) in carts[:]:
                                pass
                            else:
                                logger.info('Add cart in package: {}'.format(cart[0]))
                                carts[0:self.limit - 1] = carts[1:self.limit]
                                carts[self.limit - 1] = int(cart[0])
                        except ValueError:
                            pass
                        except IndexError:
                            pass

                    elif cart[0].upper() == self.pattern_code:

                        total_identify = self.limit - carts[:].count(0)

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

                            format_package = '{},{}{}'.format(
                                truck,
                                total_identify,
                                codes_carts
                            )

                            self.package_log.append(format_package.split(',')[0])
                            self.cart_log.append(total_identify)
                            self.truck_log.append(status_truck)
                            self.hour_log.append(self.get_format_date())

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

                            truck = 0
                            plot_truck.send(format_package)
                            carts[:] = self.create_list(size=self.limit)
                            actions[0] = 1

                    else:
                        pass
                else:
                    pass
            else:
                pass

            if self.show_image is True:
                cv2.imshow('Image', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            else:
                # camera on, send status
                pass

        camera.stop()
        cv2.destroyAllWindows()
