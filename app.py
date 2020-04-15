from communication import Communication
from recognition import Recognition
from database import DataBase
from package import Package
from loguru import logger
import multiprocessing as mp
import json
import os

global commands

commands = list()


class App:

    def __init__(self):
        self.config_json = self.read_config()

        self.r = Recognition(config=self.config_json)
        self.c = Communication(config=self.config_json, code_recognition=self.r)

        self.station = self.config_json['project']['station_id']
        self.carts = mp.Array('i', self.r.create_list(self.config_json['carts']['total']))

        self.connection = self.c.data_call()

        self.QRBE1 = self.c.create_digit('QRBE1,{}'.format(self.station))

        self.db = DataBase(data_base='cache.db')

    @staticmethod
    def read_config():
        with open('./config.json') as j:
            config = json.load(j)

        return config

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
        app.db.consult()

        return len(app.db.packages) > 0


    def check_package(package):

        for item in commands:

            if item.package == package:
                return True

        return False

    def callback_package():

        logger.debug('CALLBACK')

        send_command = len(commands) == 0

        app.db.consult()

        if check_cache():

            for i, p in zip(app.db.packages['id'], app.db.packages['package']):

                if not check_package(package=p):
                    logger.debug('HAVE CACHE')
                    commands.append(Package(id=i, package=p))

        if not check_package(package=app.r.b2):
            commands.append(Package(id=0, package=app.r.b2))

        if send_command:
            app.c.send_broadcast(connection=app.connection, message=app.QRBE1, commands=commands)

    try:

        app.connection.open()

        app.c.read_data(connection=app.connection, commands=commands, qrbe1=app.QRBE1)

        app.r.reader(carts=app.carts, callback=callback_package)

    except Exception as e:
        logger.error(e)
        logger.info('End application.')
