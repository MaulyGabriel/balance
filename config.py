from communication import Communication
from imutils.video import VideoStream
from recognition import Recognition
from time import time, sleep
from loguru import logger
import imutils
import json
import cv2


class Config:

    def __init__(self, port, rate):
        self.config_json = self.read_config_json()
        self.my_low_address = ''
        self.c = Communication(port, rate)
        self.pattern = 'QRCONF'
        self.config_ok = 'QROK,*2B\r\n'
        self.station = ''
        self.r = Recognition(
            camera=self.config_json['camera']['usb'],
            image_size=self.config_json['camera']['size_image'],
            show_image=bool(self.config_json['camera']['show_image']),
            limit=0,
            use_rasp=bool(self.config_json['camera']['raspberry']),
            pattern_code=self.config_json['project']['pattern'],
            communication=self.c
        )
        self.show_image = False

    def read_station(self):

        try:
            camera = VideoStream(usePiCamera=False, resolution=(
                self.config_json['camera']['resolution']['width'], self.config_json['camera']['resolution']['height']),
                                 framerate=self.config_json['camera']['fps']).start()

            sleep(0.8)

            while True:
                frame = camera.read()
                frame = imutils.resize(frame, width=self.config_json['camera']['size_image'])
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                code = self.r.scanner(frame)

                if code != '':
                    if code.split('-')[0].upper() == self.config_json['project']['pattern']:
                        if code.split('-')[1].upper():
                            self.station = code.split('-')[1].upper()
                            self.write_config()
                            break

                if bool(self.config_json['camera']['show_image']):
                    cv2.imshow('Config', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

            cv2.destroyAllWindows()
            camera.stop()

        except Exception as e:
            logger.error(e)

    def get_low_address(self):

        device = self.c.data_call()

        try:
            device.open()
            if device.get_64bit_addr() is None:
                logger.error('Address not found :( .')
            else:
                self.my_low_address = device.get_64bit_addr()
        except Exception as e:
            logger.error(e)
        finally:
            if device is not None and device.is_open():
                device.close()

    def write_config(self):
        with open('config.txt', 'w') as file:
            file.write('id_cam:{}'.format(self.station))

    def send_address(self, message):

        connection = self.c.data_call()
        connection.open()

        stop = False

        while True:

            try:

                connection.send_data_broadcast(message.encode('utf-8'))
                request = connection.read_data()

                if request is None:
                    pass
                else:
                    request = str(request.data.decode('utf-8'))

                    if request[:4] == self.config_ok[:4]:
                        if self.c.verify_digit(information=request):
                            stop = True
                        else:
                            logger.error('Error check sum.')

            except Exception as e:
                logger.error(e)

            if stop:
                break

        connection.close()

    def read_config(self):

        with open('config.txt') as file:
            for content in file:

                if content.split(':')[1] == '':
                    logger.info('Not configuration')
                else:
                    self.station = content.split(':')[1]

        return self.station

    @staticmethod
    def read_config_json():
        with open('./config.json') as j:
            config = json.load(j)

        return config

    def set_configuration(self):

        logger.success('Start configuration...')

        # 1 - Read camera id
        self.read_station()

        init_time = time()

        # 2 - Get my low address
        self.get_low_address()

        # 3 - Send my camera id and low address
        send_identifier = '{},{},{}'.format(self.pattern, self.my_low_address, self.station)
        send_identifier = self.c.create_digit(information=send_identifier)

        self.send_address(message=send_identifier)

        logger.success('End configuration: {} s'.format(round(time() - init_time, 2)))
