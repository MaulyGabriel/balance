from loguru import logger
import sqlite3
import io


class DataBase:

    def __init__(self, data_base):
        self.db = data_base

    def open_connection(self):

        conn = sqlite3.connect(self.db)
        return conn

    def create_data_base(self):
        try:
            conn = sqlite3.connect(self.db)
            conn.close()
            logger.success('Data base created')
        except Exception as e:
            logger.error(e)

    def create_table(self):

        conn = self.open_connection()

        cursor = conn.cursor()

        cursor.execute(
            "CREATE TABLE package(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, package TEXT NOT NULL, data NOT NULL DEFAULT CURRENT_TIMESTAMP);")

        logger.success('Table created')
        conn.close()

    def insert(self, package):

        conn = self.open_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO package(id, package) VALUES(NULL, '{}');".format(package))

        conn.commit()

        logger.success('Data inserted.')

        conn.close()

    def consult(self):

        packages = {'id': list(), 'package': list(), 'data': list()}

        conn = self.open_connection()

        cursor = conn.cursor()

        cursor.execute("SELECT id, package, data FROM package;")

        cache = cursor.fetchall()

        if len(cache) > 0:

            for p in cache:
                packages['id'].append(p[0])
                packages['package'].append(p[1])
                packages['data'].append(p[2])

        conn.close()

        return packages

    def delete(self, id_package):
        conn = self.open_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM package WHERE id={}".format(id_package))
        conn.commit()
        logger.success('Data deleted')
        conn.close()

    def consult_data(self, sql):

        try:
            conn = self.open_connection()

            cursor = conn.cursor()

            cursor.execute(sql)

            cache = cursor.fetchall()

            conn.close()

            if len(cache) > 0:
                return cache

            return None

        except Exception as e:
            logger.error('Consult: {}'.format(e))

    def backup(self, name):

        conn = self.open_connection()

        with io.open('{}.sql'.format(name), 'w') as f:
            for row in conn.iterdump():
                f.write('%s\n' % row)

        logger.success('Backup created')
        conn.close()
