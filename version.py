from loguru import logger
import json


class Version:

    def __init__(self):
        self.config_json = self.read_config_json()

    @staticmethod
    def read_config_json():
        with open('./config.json') as j:
            config = json.load(j)

        return config

    def show_version(self):
        logger.info('{}'.format(self.config_json['project']))


if __name__ == '__main__':
    v = Version()
    v.show_version()
