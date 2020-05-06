from digi.xbee.devices import XBeeDevice
from loguru import logger
from time import sleep


class Communication:

    def __init__(self, config, code_recognition, timer_process, db):
        self.config = config
        self.code = code_recognition
        self.count_send = 0
        self.db = db
        self.timer_process = timer_process

    def data_call(self):

        device = XBeeDevice(self.config.port, self.config.baudrate)

        return device

    def control_process(self, connection, message, commands):

        while self.timer_process.interruption or len(commands) > 0:
            self.send_broadcast(connection, message, commands)
            sleep(self.config.timeout)

    def send_broadcast(self, connection, message, commands):

        if self.count_send == 3:
            if len(commands) > 0:
                if commands[0].id == 0:
                    if not commands[0].package == '':
                        self.db.insert(commands[0].package)
                    self.timer_process.stop_process()
                self.count_send = 0
                commands.pop(0)
        else:
            try:
                connection.send_data_broadcast(message.encode('utf-8'))
                logger.debug('SEND: {}'.format(message))
            except Exception as e:
                logger.error('Error callback: {}'.format(e))

            self.count_send += 1

    def read_data(self, connection, commands):

        def data_receive_callback(xbee_message):
            answer = xbee_message.data.decode('utf-8')

            if xbee_message.is_broadcast:
                pass
            else:

                if answer[:6] == 'QRIPDA':
                    if self.verify_digit(answer):
                        if len(commands) > 0:
                            connection.send_data(xbee_message.remote_device,
                                                 self.create_digit(commands[0].package).encode('utf-8'))

                            logger.success('RECEIVE: {}'.format(answer))

                elif answer[:4] == 'QROK':
                    if self.verify_digit(answer):
                        self.timer_process.stop_process()

                        logger.success('RECEIVE: {}'.format(answer))

                        if commands[0].id != 0:
                            self.db.delete(id_package=commands[0].id)

                        self.count_send = 0
                        self.code.clear_b2()

                        commands.pop(0)

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
