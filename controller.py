class Camera:

    def __init__(self, camera_id, station_id, show_image, resize_image, width, height, fps):
        self.id = camera_id
        self.station_id = station_id
        self.show_image = show_image
        self.resize_image = resize_image
        self.width = width
        self.height = height
        self.fps = fps

    def __repr__(self):
        return '<Camera> {} {}x{}'.format(self.station_id, self.width, self.height)


class Communication:

    def __init__(self, communication_id, port, baudrate, timeout, preamble):
        self.id = communication_id
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.preamble = preamble

    def __repr__(self):
        return '<Communication> {}:{}'.format(self.port, self.baudrate)


def consult_communication(db):
    communications = list()

    sql = 'SELECT * FROM communication'
    result = db.consult_data(sql)

    if result is None:
        return None

    for c in result:
        communications.append(
            Communication(communication_id=c[0], port=c[1], baudrate=c[2], timeout=c[3], preamble=c[4]))

    return communications


def consult_camera(db):
    cameras = list()

    sql = 'SELECT * FROM camera'
    result = db.consult_data(sql)

    if result is None:
        return None
    for c in result:
        cameras.append(
            Camera(camera_id=c[0], station_id=c[1], show_image=c[2], resize_image=c[3], width=c[4], height=c[5],
                   fps=c[6]))

    return cameras
