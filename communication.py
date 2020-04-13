from digi.xbee.devices import XBeeDevice
from database import DataBase
from loguru import logger
import threading


class Communication:

    def __init__(self, config, code_recognition):
        self.config = config
        self.code = code_recognition
        self.count_send = 0
        self.db = DataBase(data_base='cache.db')

    def data_call(self):

        device = XBeeDevice(self.config['serial']['port'], self.config['serial']['baudrate'])

        return device

    def send_broadcast(self, connection, message, actions):

        if actions[0] == 1:

            if self.count_send == 3:
                self.db.insert(self.code.b2)
                logger.debug('Saved cache')
                self.count_send = 0
                actions[0] = 0
            else:
                try:
                    connection.send_data_broadcast(message.encode('utf-8'))
                except Exception as e:
                    logger.error('Error callback: {}'.format(e))

                logger.success('Send: {}'.format(message))
                self.count_send += 1
                threading.Timer(self.config['serial']['timeout'], self.send_broadcast,
                                [connection, message, actions]).start()
        else:
            logger.debug('Sleep: {}'.format(self.count_send))

    def read_data(self, connection, actions):

        def data_receive_callback(xbee_message):
            answer = xbee_message.data.decode('utf-8')

            if xbee_message.is_broadcast:
                pass
            else:

                if answer[:6] == 'QRIPDA':
                    if self.verify_digit(answer):
                        logger.debug('Receive: {}'.format(answer))
                        connection.send_data(xbee_message.remote_device,
                                             self.create_digit(self.code.b2).encode('utf-8'))

                elif answer[:4] == 'QROK':
                    if self.verify_digit(answer):
                        logger.debug('Receive: {}'.format(answer))
                        actions[0] = 0
                        self.count_send = 0
                        self.code.clear_b2()

        connection.add_data_received_callback(data_receive_callback)

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

        validated_information = '{}{}\r\n'.format(information, validated_information.upper())

        return validated_information.upper()

    def verify_digit(self, information):

        result = self.create_digit(information=information.strip()[:-3])

        if information.strip()[-2:] == result.strip()[-2:]:
            return True
        else:
            return False
