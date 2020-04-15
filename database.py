from loguru import logger
import sqlite3
import io


class DataBase:

    def __init__(self, data_base):
        self.db = data_base
        self.packages = {'id': list(), 'package': list(), 'data': list()}
        self.package = {'id': list(), 'package': list(), 'data': list()}

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

        print(package)

        cursor.execute("INSERT INTO package(id, package) VALUES(NULL, '{}');".format(package))

        conn.commit()

        logger.success('Data inserted.')

        conn.close()

    def consult(self):

        conn = self.open_connection()

        cursor = conn.cursor()

        cursor.execute("SELECT id, package, data FROM package;")

        cache = cursor.fetchall()

        if len(cache) > 0:

            for p in cache:
                self.packages['id'].append(p[0])
                self.packages['package'].append(p[1])
                self.packages['data'].append(p[2])

        conn.close()

    def consult_by_id(self, id_package):

        conn = self.open_connection()

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM package WHERE id={}".format(id_package))

        for i in cursor.fetchall():
            self.package = self.package = {'id': i[0], 'package': i[1], 'data': i[2]}

        conn.close()

    def consult_by_package(self, package):

        conn = self.open_connection()

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM package WHERE package LIKE '%{}%'".format(package))

        for i in cursor.fetchall():
            self.package = self.package = {'id': i[0], 'package': i[1], 'data': i[2]}

    def update(self, id_package, new_package):
        conn = self.open_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE package SET package='{}' WHERE id={}".format(new_package, id_package))
        conn.commit()
        logger.success('Data updated')
        conn.close()

    def delete(self, id_package):
        conn = self.open_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM package WHERE id={}".format(id_package))
        conn.commit()
        logger.success('Data deleted')
        conn.close()

    def show_information(self, name_table):

        conn = self.open_connection()
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info({})".format(name_table))
        columns = [c[1] for c in cursor.fetchall()]

        logger.info('Columns: {}'.format(columns))

        conn.close()

    def backup(self, name):

        conn = self.open_connection()

        with io.open('{}.sql'.format(name), 'w') as f:
            for row in conn.iterdump():
                f.write('%s\n' % row)

        logger.success('Backup created')
        conn.close()


if __name__ == '__main__':

    db = DataBase(data_base='cache.db')
    db.consult()
    print(db.packages)