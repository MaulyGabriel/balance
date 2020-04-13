from database import DataBase
from loguru import logger
import pandas as pd


def show_data():
    db = DataBase('cache.db')
    db.consult()
    df = pd.DataFrame(db.packages, columns=['id', 'package'])
    logger.success(df)


if __name__ == '__main__':
    show_data()
