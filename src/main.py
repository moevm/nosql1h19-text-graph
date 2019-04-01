import logging.config

from config.config import Config


if __name__ == "__main__":
    logging.config.dictConfig(Config.LOGGING_CONFIG)
    logger = logging.getLogger('root')
    logger.info('Starting app...')
