from digi.xbee.devices import XBeeDevice


def send_message(port, rate):
    device = XBeeDevice(port, rate)

    try:

        device.open()

        while True:
            message = input('Type the command '
                            '\n[0] - STATUS_CAMERA'
                            '\n[1] - SEND_TRUCK'
                            '\n[2] - SEND_PACKAGE\n: '
                            )

            message = int(message)

            if message == 0:
                device.send_data_broadcast('STATUS_CAMERA,*7E\r\n'.encode('utf-8'))
            elif message == 1:
                device.send_data_broadcast('SEND_TRUCK,*34\r\n'.encode('utf-8'))
            elif message == 2:
                device.send_data_broadcast('SEND_PACKAGE,*35\r\n'.encode('utf-8'))
            else:
                pass

    except Exception as e:
        print(e)


if __name__ == '__main__':
    send_message(port='/dev/ttyUSB0', rate=115200)
