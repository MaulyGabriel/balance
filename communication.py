from digi.xbee.devices import XBeeDevice
from loguru import logger
from time import sleep


class Communication:

    def __init__(self, port, rate):
        self.port = port
        self.rate = rate
        self.status_camera = 'STATUS_CAMERA,*7E\r\n'
        self.status_truck = 'SEND_TRUCK,*34\r\n'
        self.status_package = 'SEND_PACKAGE,*35\r\n'

    def data_call(self):

        device = XBeeDevice(self.port, self.rate)

        return device

    def read_protocol(self, actions, plot):

        connection = self.data_call()

        try:

            connection.open()

            while True:

                message = connection.read_data()

                if message is None:
                    pass
                else:

                    message = str(message.data.decode('utf-8'))

                    if self.verify_digit(message):

                        if actions[0]:
                            actions[0] = 0
                            logger.debug('Send status')
                            # self.send_message(connection=connection, message='CAMERA_OK')
                        elif actions[0] == 1:

                            truck = plot.recv()
                            logger.debug(truck)
                            # self.send_message(connection=connection, message=truck)
                            # actions[0] = 0
                        elif message[:] == self.status_package:
                            actions[0] = 2
                            sleep(0.5)
                            package = plot.recv()
                            logger.debug(package)
                            # self.send_message(connection=connection, message=package)
                            # actions[0] = 0
                        else:
                            pass

        except Exception as e:
            logger.error('Error in connection: {}'.format(e))

        connection.close()

    def send_message(self, connection, message):

        try:
            message = self.create_digit(information=message)

            if self.verify_digit(information=message):
                connection.send_data_broadcast(message.encode('utf-8'))
            else:
                logger.error('Message error')

        except Exception as e:
            logger.error(e)

    @staticmethod
    def create_digit(information):

        information = str(information)
        information = information.upper()

        information += ','

        verify_digit = 0

        for digit in str(information):
            verify_digit ^= ord(digit)

        validated_information = ''
        hexadecimal = hex(verify_digit)
        len_hexadecimal = len(hexadecimal)

        if len_hexadecimal == 3:
            validated_information = '0' + hexadecimal[2]
        elif len_hexadecimal == 4:
            validated_information = hexadecimal[2:4]
        else:
            logger.error('Unable to generate validation')

        validated_information = '{}*{}\r\n'.format(information, validated_information.upper())

        return validated_information.upper()

    def verify_digit(self, information):

        position = information.find('*')

        result = self.create_digit(information[:position - 1])

        if information[position + 1:] == result[position + 1:]:
            return True
        else:
            return False
