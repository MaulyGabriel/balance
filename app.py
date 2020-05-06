from digi.xbee.util import utils
from communication import Communication
from recognition import Recognition
from timer import TimerProcess
from database import DataBase
from package import Package
from loguru import logger
import multiprocessing as mp
import controller
import os

global commands

commands = list()


class App:

    def __init__(self):
        self.db = DataBase(data_base='cache.db')
        self.camera, self.communication = self.read_config()
        self.timer_process = TimerProcess()

        self.r = Recognition(config=self.camera, db=self.db)
        self.c = Communication(config=self.communication, code_recognition=self.r, timer_process=self.timer_process,
                               db=self.db)

        self.station = self.camera.station_id
        self.carts = mp.Array('i', self.r.create_list(12))

        self.connection = self.c.data_call()

        self.QRBE1 = self.c.create_digit('QRBE1,{}'.format(self.station))

    @staticmethod
    def read_config():
        db = DataBase(data_base='/home/madruga/developer/projects/config/config.db')

        camera = controller.consult_camera(db)

        communication = controller.consult_communication(db)

        return camera, communication

    def check_database(self):
        db = os.path.exists('./cache.db')

        if not db:
            self.db.create_data_base()
            self.db.create_table()


if __name__ == '__main__':
    logger.info('Start application...')

    app = App()
    app.check_database()


    def check_cache():

        packages = app.db.consult()

        logger.error(packages)

        return packages, len(packages['id']) > 0


    def check_package(package):

        for item in commands:

            if item.package == package:
                return True

        return False


    def callback_package():
        send_command = len(commands) == 0

        packages, have_cache = check_cache()

        if have_cache:

            for i, p in zip(packages['id'], packages['package']):

                if not check_package(package=p):
                    commands.append(Package(id_package=i, package=p))

        if not check_package(package=app.r.b2):
            commands.append(Package(id_package=0, package=app.r.b2))

        if send_command:
            app.timer_process.start_process(app.c.control_process, [app.connection, app.QRBE1, commands])


    def apply_configuration():

        try:
            app.connection.set_parameter("HP", utils.hex_string_to_bytes(app.communication.preamble))
        except Exception as e:
            logger.error(e)


    try:

        app.connection.open()

        apply_configuration()

        app.c.read_data(connection=app.connection, commands=commands)

        app.r.reader(carts=app.carts, callback=callback_package, commands=commands)

    except Exception as e:
        logger.error(e)
        logger.info('End application.')
