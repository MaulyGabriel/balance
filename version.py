from loguru import logger


class Version:

    def __init__(self):
        pass

    @staticmethod
    def show_version():
        with open('version.txt', 'r') as file:
            for content in file:
                logger.info('{}'.format(content))


if __name__ == '__main__':
    v = Version()
    v.show_version()
