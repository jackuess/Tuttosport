from collections import deque
import logging
import logging.handlers
from math import cos, sin
import sys

import settings

BRIGHT = '\033[1m'
WHITE_ON_GREEN = BRIGHT + '\033[37m\033[42m'
BLACK_ON_WHITE = BRIGHT + '\033[30m\033[47m'
BROWN = BRIGHT + '\033[43m'
RESET = '\033[0m'


class SyslogFormatter(logging.Formatter):
    def format(self, record):
        return 'feedfetcher:[%d]: %s - %s' % (record.process,
                                              record.levelname,
                                              record.message)


class SportFormatter(logging.Formatter):
    _x = 0
    colors = [WHITE_ON_GREEN, WHITE_ON_GREEN,
              BLACK_ON_WHITE, BLACK_ON_WHITE]
    amp = 3
    flag_height = 22

    @classmethod
    def get_x(cls):
        x = cls._x
        cls._x += 1
        cls._x = cls._x % cls.flag_height
        return x

    def format(self, record):
        x = self.get_x()
        offset = int(self.amp*sin(x*0.5))
        s = super(SportFormatter, self).format(record)
        r = '%s%s%s' % (self.colors[x%4],
                        ('  %s' % s).ljust(80-offset, ' '),
                        RESET)
        if x == (self.flag_height-1):
            # Add the stick
            r += '\n%s%s%s' % (BROWN, '  \n'*8, RESET)
        return r


def create_logger(name):
    '''Creates a logger that logs to:

        - Standard out on level DEBUG
        - Email on level ERROR

    Returns:
        A logging.Logger instance
    '''
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(SportFormatter())
    stdout_handler.setLevel(logging.DEBUG)
    logger.addHandler(stdout_handler)

    syslog_handler = logging.handlers.SysLogHandler(address='/dev/log')
    syslog_handler.setFormatter(SyslogFormatter())
    syslog_handler.setLevel(logging.DEBUG)
    logger.addHandler(syslog_handler)

    if len(settings.logging['toaddrs']) > 0:
        email_handler = logging.handlers.SMTPHandler(**settings.logging)
        email_handler.setLevel(logging.ERROR)
        logger.addHandler(email_handler)

    return logger


class Logging(object):
    def __init__(self):
        self.logger = create_logger(
            '%s.%s' % (__name__, self.__class__.__name__))
