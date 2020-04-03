from communication import Communication
from loguru import logger
import json


class Test:

    def __init__(self):
        self.config = ''

    def read_config(self):

        with open('./config.json') as j:
            self.config = json.load(j)


if __name__ == '__main__':
    t = Test()
    t.read_config()

    c = Communication(config=t.config)

    s = 'CD'
    s = c.create_digit(s)

    c.verify_digit(information=s)

    logger.info(s)

