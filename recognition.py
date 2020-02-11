from imutils.video import VideoStream
from loguru import logger
from time import localtime, sleep
from pyzbar import pyzbar
import numpy as np
import imutils
import cv2


class Recognition:

    def __init__(self, station_id, camera, image_size, show_image, limit, use_rasp, pattern_code):
        self.station_id = station_id
        self.camera = camera
        self.limit = limit
        self.use_rasp = use_rasp
        self.show_image = show_image
        self.image_size = image_size
        self.pattern_code = pattern_code
        self.package_ok = 'QRBE2'
        self.package_send = 'QRBE3'

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

        format_data = '{}{}{},{}{}{}'.format(day, month, year, hour, minutes, seconds)

        return format_data

    def reader(self, carts, actions, plot_truck, plot_carts):

        if self.use_rasp is True:
            camera = VideoStream(usePiCamera=True, resolution=(1280, 720), framerate=65).start()
        else:
            camera = VideoStream(src=self.camera).start()

        sleep(0.8)

        truck = ''

        while True:

            frame = camera.read()
            frame = imutils.resize(frame, self.image_size)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            code = self.scanner(frame)

            if code != '':

                if actions[0] == 0:

                    cart = code.split('-')

                    # our code?
                    if cart[0] != self.pattern_code:

                        # code is truck ?
                        if cart[0] == 'CAM':
                            logger.debug('Truck: OK')
                            truck = cart[1]

                        # add code in package case not exist
                        try:
                            if int(cart[0]) in carts[:]:
                                pass
                            else:
                                logger.info('Add cart in package')
                                carts[0:self.limit - 1] = carts[1:self.limit]
                                carts[self.limit - 1] = int(cart[0])
                        except ValueError:
                            pass
                        except IndexError:
                            pass

                        total_identify = self.limit - carts[:].count(0)

                        if total_identify == self.limit:
                            format_package = '{},{},{},{},{}'.format(
                                self.package_ok,
                                self.station_id,
                                truck,
                                total_identify,
                                self.get_format_date()
                            )

                            logger.info('Send trucks')
                            plot_truck.send(format_package)

                elif actions[0] == 1:

                    final_message = ''

                    for c in carts[:]:

                        if c != 0:
                            final_message += '\n{},{}'.format(self.package_send, c)
                        else:
                            pass

                    logger.info('Send carts')
                    plot_carts.send(final_message)

                    logger.info('Clear package')
                    carts[:] = self.create_list(size=self.limit)

            if self.show_image is True:
                cv2.imshow('Image', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            else:
                # camera on
                pass

    cv2.destroyAllWindows()
