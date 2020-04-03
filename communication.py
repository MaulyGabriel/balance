from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress
from loguru import logger
from time import sleep


class Communication:

    def __init__(self, config):
        self.config = config

    def data_call(self):

        device = XBeeDevice(self.config['serial']['port'], self.config['serial']['baudrate'])

        return device

    def read_protocol(self, actions, plot_truck, station):

        connection = self.data_call()

        attempts_count = 1

        try:

            connection.open()

            while True:

                if actions[0] == 0:

                    message = connection.read_data()

                    if message is None:
                        pass
                    else:
                        pass
                        '''
                        message = str(message.data.decode('utf-8'))

                        if self.verify_digit(message):
                            logger.info('Receive: {}'.format(message))
                        '''

                elif actions[0] == 1:
                    truck = plot_truck.recv()

                    have_package = '{},{},{}'.format('QRBE1', station, connection.get_64bit_addr())
                    have_package = self.create_digit(have_package)
                    connection.send_data_broadcast(have_package.encode('utf-8'))

                    while True:

                        answer = connection.read_data()

                        if answer is None:
                            pass
                        else:
                            answer = answer.data.decode('utf-8')

                            if answer[:6] == 'QRIPDA':

                                if self.verify_digit(answer):

                                    remote_device = RemoteXBeeDevice(
                                        connection,
                                        XBee64BitAddress.from_hex_string(answer.split(',')[1])
                                    )

                                    final_message = 'QRBE2,{},{}'.format(attempts_count, truck)
                                    final_message = self.create_digit(final_message)

                                    connection.send_data(remote_device, final_message.encode('utf-8'))

                                    logger.success('Send unicast: {}'.format(final_message))

                                    while True:

                                        answer = connection.read_data()

                                        if answer is None:
                                            pass
                                        else:

                                            answer = answer.data.decode('utf-8')
                                            logger.success(answer)

                                            if answer[:4] == 'QROK':
                                                if self.verify_digit(answer):
                                                    logger.success('receive ok')
                                                    attempts_count = 0
                                                    actions[0] = 0
                                                    break
                                    '''
                                    if actions[0] == 0:
                                        break
            
                                    answer = connection.read_data()

                                    if answer is None:
                                        pass
                                    else:
                                        answer = answer.data.decode('utf-8')

                                        if answer[:4] == 'QROK':
                                            if self.verify_digit(answer):
                                                logger.success('receive ok')
                                                attempts_count = 0
                                                actions[0] = 0
                                                break
                                    
                                    while attempts_count != 0:

                                        final_message = 'QRBE2,{},{}'.format(attempts_count, truck)
                                        final_message = self.create_digit(final_message)

                                        connection.send_data(remote_device, final_message.encode('utf-8'))

                                        logger.success('Send unicast: {}'.format(final_message))

                                        answer = connection.read_data()

                                        if answer is None:
                                            pass
                                        else:
                                            answer = answer.data.decode('utf-8')

                                            if answer[:4] == 'QROK':
                                                if self.verify_digit(answer):
                                                    logger.success('receive ok')
                                                    attempts_count = 0
                                                    actions[0] = 0
                                                    break


                                        attempts_count += 1
                                                
                                        sleep(5)
                                        '''

                        if actions[0] == 0:
                            logger.success('Send QRB2 end terminate')
                            break

        except Exception as e:
            logger.error('Error in connection: {}'.format(e))

        finally:
            connection.close()

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
