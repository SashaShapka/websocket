import logging.config
import sys


def setup_logging():
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'stream': sys.stdout,
                'formatter': 'default',
                'level': logging.INFO,
            },
        },
        'loggers': {
            'socket_logger': {
                'handlers': ['console'],
                'level': logging.INFO,
                'stream': sys.stdout,
                'propagate': False,
            },
        },
    }

    logging.config.dictConfig(logging_config)