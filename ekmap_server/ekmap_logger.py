import logging
from .ekmap_common import *

class eKLogger():

    def log(msg):
        _logger = logging.getLogger(LOGGER_NAME)
        _logger.setLevel(logging.INFO)
            
        fileHandler = logging.FileHandler(LOGGER_DIR)
        formatter = logging.Formatter(LOGGER_FORMAT)
        fileHandler.setFormatter(formatter)

        _logger.addHandler(fileHandler)
        _logger.info(msg)

        _logger.removeHandler(fileHandler)