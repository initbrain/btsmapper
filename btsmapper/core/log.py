# -*- coding: utf-8 -*-

import logging
import sys


class ColorFormatter(logging.Formatter):
    """
    A logging formatter that colors messages depending on their level.
    """
    _color_map = {
        'DEBUG': '\033[22;32m',
        'INFO': '\033[01;34m',
        'WARNING': '\033[22;35m',
        'ERROR': '\033[22;31m',
        'CRITICAL': '\033[01;31m'
    }

    def _colorize(self, level, message):
        return '{0}{1}\033[0;0m'.format(
            self._color_map[level],
            message
        )

    def format(self, record):
        """
        Overrides the default :func:`logging.Formatter.format` to add colors to
        the :obj:`record`'s :attr:`levelname` and :attr:`name` attributes.
        """
        return record.msg  # PATCH OBS
        #        level_length = len(record.levelname)

#        if record.levelname in self._color_map:
#            record.msg = self._colorize(record.levelname, record.msg)
#            record.levelname = '['+self._colorize(record.levelname, record.levelname)+']'
#            record.name = '\033[37m\033[1m{0}\033[0;0m'.format(record.name)
#        return super(ColorFormatter, self).format(record)


# prepare formatters
console_formatter = ColorFormatter(
    fmt='%(levelname)s %(message)s', #[%(asctime)s] %(name)s # PATCH OBS
    datefmt='%Y-%m-%d %H:%M:%S'
)

# prepare handlers
handlers = []

## console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(console_formatter)
console_handler.setLevel(logging.DEBUG)
handlers.append(console_handler)

# configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
for handler in handlers:
    root_logger.addHandler(handler)

# configure external loggers (third party libs, etc...)
external_loggers = (
    'requests',
    )
for logger_name in external_loggers:
    external_logger = logging.getLogger(logger_name)
    external_logger.setLevel(logging.WARNING)
