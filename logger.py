import logging


def setup_logger():
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)

    err_handler = logging.FileHandler('error.log')
    err_handler.setLevel(logging.ERROR)
    err_handler.setFormatter(formatter)
    err_handler.addFilter(lambda x: x.levelno == logging.ERROR)

    info_handler = logging.FileHandler('info.log')
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)
    info_handler.addFilter(lambda x: x.levelno < logging.ERROR)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    logger.addHandler(err_handler)
    logger.addHandler(info_handler)
    logger.addHandler(console_handler)
