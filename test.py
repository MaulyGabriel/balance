from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress
from loguru import logger
from time import sleep
import serial
import json


def send_message(port, rate):
    device = XBeeDevice(port, rate)

    try:

        device.open()

        logger.info('64-bit address: {}'.format(device.get_64bit_addr()))
        logger.info('16-bit address: {}'.format(device.get_16bit_addr()))
        logger.info('Node identifier: {}'.format(device.get_node_id()))
        logger.info('Firmware version: {}'.format(device.get_firmware_version()))
        logger.info('Hardware version: {}'.format(device.get_hardware_version()))
        logger.info('Role: {}'.format(device.get_role()))

    except Exception as e:
        logger.error(e)

    finally:

        if device is not None and device.is_open():
            device.close()
            logger.success('Close connection')


def open_connection(port):
    board = serial.Serial(port, baudrate=9600, timeout=1)

    return board


def send_command():
    code = '213\n'

    conn = open_connection(port='/dev/ttyUSB0')

    while True:
        conn.write(code.encode('utf-8'))
        logger.info(code)
        sleep(3)


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


def read_config(name):

    with open('./config.json') as j:
        config = json.load(j)

    print(config['config']['camera'])


if __name__ == '__main__':
    read_config(name='./config.json')
