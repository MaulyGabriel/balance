from loguru import logger


def show_version():
    version = open('version.txt', 'r')

    for i in version:
        logger.info('{}'.format(i))

    version.close()


if __name__ == '__main__':
    show_version()
