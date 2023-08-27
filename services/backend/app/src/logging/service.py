import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import pathlib

from src.config import APP_SRC_FOLDER_ABS


class AppLogFormatter(logging.Formatter):
    """Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629"""

    grey     = '\x1b[38;21m'
    blue     = '\x1b[38;5;39m'
    yellow   = '\x1b[38;5;226m'
    red      = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset    = '\x1b[0m'

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_logger(filename: str = 'log.txt') -> logging.Logger:
    logdir = os.path.join(pathlib.Path(__file__).parent.resolve(), 'logs')

    if not os.path.exists(logdir):
        os.makedirs(logdir)

    formatter = AppLogFormatter(
        '%(asctime)s | %(name)s |  %(levelname)s: %(message)s',
        # '%Y-%m-%d %H:%M:%S'
    )

    # stdout
    log_stream_handler = logging.StreamHandler()
    log_stream_handler.setFormatter(formatter)
    log_stream_handler.setLevel(logging.INFO)

    # file
    log_file_handler = RotatingFileHandler(
        filename=os.path.join(logdir, f"log.txt"),
        maxBytes=1000000,   # 1MB
        backupCount=100,
    )

    ## To use a new log file for each launch instead
    # log_file_handler = logging.FileHandler(
    #     filename=os.path.join(logdir, f"{filename}.txt"),
    # )
    log_file_handler.setFormatter(formatter)
    log_file_handler.setLevel(logging.DEBUG)

    logging.basicConfig(
        handlers=[
            log_file_handler,
            log_stream_handler,
        ],
        encoding='utf-8',
        level=logging.INFO
    )

    return logging.getLogger()


timestamp = datetime.now().strftime('%Y%m%d_%H%M%S%f')
logger = get_logger(filename=timestamp)
