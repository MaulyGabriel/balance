from digi.xbee.devices import XBeeDevice
from loguru import logger
import threading

global actions

actions = [1]

def data_call():
    device = XBeeDevice('/dev/ttyUSB0', 115200)

    return device


def send_broadcast(connection, message, actions):

    if actions[0] == 1:
        connection.send_data_broadcast(message.encode('utf-8'))
        logger.success(message)
        threading.Timer(15, send_broadcast, [connection, message, actions]).start()
    else:
        logger.info('SLEEP')


def read_data(connection, actions):

    def data_receive_callback(xbee_message):
        answer = xbee_message.data.decode('utf-8')

        logger.success(answer)

        connection.send_data_async(xbee_message.remote_device, 'QRBE2'.encode('utf-8'))
        logger.success('TEST UNICAST')

        actions[0] = 0

    connection.add_data_received_callback(data_receive_callback)


if __name__ == '__main__':

    device = data_call()

    try:
        device.open()

        read_data(connection=device, actions=actions)

        send_broadcast(connection=device, message='QRBE1', actions=actions)


    except Exception as e:
        logger.error(e)
