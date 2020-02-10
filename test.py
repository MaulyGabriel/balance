from digi.xbee.devices import XBeeDevice


def send_message(port, rate):
    device = XBeeDevice(port, rate)

    try:

        device.open()

        while True:
            message = input('Type the command '
                            '\n[1] - STATUS_CAMERA'
                            '\n[2] - SEND_TRUCK'
                            '\n[3] - SEND_PACKAGE\n: '
                            )

            message = int(message)

            if message == 1:
                device.send_data_broadcast('STATUS_CAMERA,*7E\r\n'.encode('utf-8'))
            elif message == 2:
                device.send_data_broadcast('SEND_TRUCK,*34\r\n'.encode('utf-8'))
            elif message == 3:
                device.send_data_broadcast('SEND_PACKAGE,*35\r\n'.encode('utf-8'))
            else:
                pass

    except Exception as e:
        print(e)
        device.close()

    device.close()


if __name__ == '__main__':

    try:
        send_message(port='/dev/ttyUSB0', rate=115200)
    except KeyboardInterrupt:
        print('End application')
