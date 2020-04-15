from digi.xbee.devices import XBeeDevice
from database import DataBase
from loguru import logger
from timer import TimerProcess
import threading


class Communication:

    def __init__(self, config, code_recognition):
        self.config = config
        self.code = code_recognition
        self.count_send = 0
        self.db = DataBase('cache.db')
        self.timer_process = TimerProcess(self.config['serial']['timeout'])

    def data_call(self):

        device = XBeeDevice(self.config['serial']['port'], self.config['serial']['baudrate'])

        return device

    def send_broadcast(self, connection, message, commands):

        if self.count_send == 3:
            if commands[0].id == 0:
                self.db.insert(commands[0].package)
                logger.debug('Saved cache')
            self.count_send = 0

            '''
            if len(commands) > 0:
                self.send_broadcast(connection=connection, message=message, commands=commands)
            '''

        else:
            try:
                connection.send_data_broadcast(message.encode('utf-8'))
            except Exception as e:
                logger.error('Error callback: {}'.format(e))

            logger.success('Send: {}'.format(message))

            self.count_send += 1

            self.timer_process.start_process(self.send_broadcast, [connection, message, commands])

            logger.debug('Sleep: {}'.format(self.count_send))

    def read_data(self, connection, commands, qrbe1):

        def data_receive_callback(xbee_message):
            answer = xbee_message.data.decode('utf-8')

            if xbee_message.is_broadcast:
                pass
            else:

                if answer[:6] == 'QRIPDA':
                    if self.verify_digit(answer):
                        logger.debug('Receive: {}'.format(answer))

                        connection.send_data(xbee_message.remote_device,
                                             self.create_digit(commands[0].package).encode('utf-8'))

                        logger.success('SEND: {}'.format(commands[0].package))

                elif answer[:4] == 'QROK':
                    if self.verify_digit(answer):
                        logger.debug('Receive: {}'.format(answer))

                        self.timer_process.stop_process()

                        if commands[0].id != 0:
                            self.db.delete(id_package=commands[0].id)

                        self.count_send = 0
                        self.code.clear_b2()

                        logger.error('Antes: {}'.format(len(commands)))
                        commands.pop(0)
                        logger.error('Depois: {}'.format(len(commands)))

                        if len(commands) > 0:
                            self.send_broadcast(connection=connection, message=qrbe1, commands=commands)

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
