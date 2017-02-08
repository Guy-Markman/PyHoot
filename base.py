# -*- coding: utf-8 -*-
# By Alon Bar-Lev @alonbl
"""Base module"""


import logging


class Base(object):
    """Base of all objects"""

    LOG_PREFIX = 'my'

    @property
    def logger(self):
        """Logger."""
        return self._logger

    def __init__(self):
        """Contructor."""
        self._logger = logging.getLogger(
            '%s.%s' % (
                self.LOG_PREFIX,
                self.__module__,
            ),
        )


def setup_logging(stream=None, level=logging.INFO):
    logger = logging.getLogger(Base.LOG_PREFIX)
    logger.propagate = False
    logger.setLevel(level)

    try:
        h = logging.StreamHandler(stream)
        h.setLevel(logging.DEBUG)
        h.setFormatter(
            logging.Formatter(
                fmt=(
                    '%(asctime)-15s '
                    '[%(levelname)-7s] '
                    '%(name)s::%(funcName)s:%(lineno)d '
                    '%(message)s'
                ),
            ),
        )
        logger.addHandler(h)
    except IOError:
        logging.warning('Cannot initialize logging', exc_info=True)

    return logger
