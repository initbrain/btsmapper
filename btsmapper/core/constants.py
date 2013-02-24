# -*- coding: utf-8 -*-

import os
import inspect
import btsmapper

BTSMAPPER_PATH = os.path.dirname(inspect.getfile(btsmapper))
CONFIG_PATH = os.path.join(BTSMAPPER_PATH, 'config')