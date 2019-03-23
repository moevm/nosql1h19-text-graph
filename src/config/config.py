from logutils.colorize import ColorizingStreamHandler
import logging


class ColorHandler(ColorizingStreamHandler):
    def __init__(self, *args, **kwargs):
        super(ColorHandler, self).__init__(*args, **kwargs)
        self.level_map = {
                logging.DEBUG: (None, 'blue', False),
                logging.INFO: (None, 'green', False),
                logging.WARNING: (None, 'yellow', False),
                logging.ERROR: (None, 'red', False),
                logging.CRITICAL: ('red', 'white', True),
        }


class Config:
    LOGGING_CONFIG = {
        'handlers': {
            'console': {
                '()': ColorHandler,
                'level': 'DEBUG',
                'formatter': 'brief',
                'stream': 'ext://sys.stdout'
            }
        },
        'formatters': {
            'brief': {
                'class': 'logging.Formatter',
                'format': '%(levelname)s: %(message)s'
            }
        },
        'version': 1,
        'loggers': {
            'root': {
                'handlers': ['console'],
                'level': 'DEBUG'
            }
        },
    }


