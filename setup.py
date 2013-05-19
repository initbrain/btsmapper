#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement

import os
from setuptools import setup, find_packages

from btsmapper import NAME, VERSION, AUTHOR, CONTACT

CURRENT_DIR = os.path.dirname(__file__)

README_PATH = os.path.join(CURRENT_DIR, 'README.txt')
if os.path.exists(README_PATH):
    with open(README_PATH) as readme:
        README = readme.read().strip()
else:
    README = ''

REQUIREMENTS_PATH = os.path.join(CURRENT_DIR, 'requirements.txt')
if os.path.exists(REQUIREMENTS_PATH):
    with open(REQUIREMENTS_PATH) as requirements:
        REQUIREMENTS = requirements.read().strip()
else:
    REQUIREMENTS = ''

setup(
    name=NAME,
    version=VERSION,
    description="GSM Base Transceiver Stations Mapping tool via Nokia 3310 and Nokia Debug function",
    long_description=README,
    author=AUTHOR,
    author_email=CONTACT,
    url='http://www.free-knowledge.net',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
    entry_points={
        'console_scripts': [
            'btsmapper_bootstrap = btsmapper.interface.install:main',
            'btsmapper = btsmapper.interface.gui:main'
            #'btsmapper_cli = btsmapper.interface.cli:main' #TODO
        ]
    },
    data_files=[
        ('btsmapper/images/', ['btsmapper/images/icone.png',
                    'btsmapper/images/logo_gpl_v3.png',
                    'btsmapper/images/logo_april.png',
                    'btsmapper/images/a_propos.png',
                    'btsmapper/images/poi.png',
                    'btsmapper/images/bts.png',
                    'btsmapper/images/sfr.png',
                    'btsmapper/images/orange.png']),
        ('btsmapper/core/', ['btsmapper/core/modules.json',
                             'btsmapper/core/nhm5_587.txt',
                             'btsmapper/core/gammurc',
                             'btsmapper/core/results.db'])
    ]
)

os.system('btsmapper_bootstrap')
