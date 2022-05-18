#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Checks to see if necessary modules exist
"""
import os
import sys

modulelist = [
    'argparse', 'configparser', 'datetime', 'os',
    'sys', 'json', 'pandas', 'requests'
]

ISSUES = 0

currentdir = os.path.abspath(os.path.dirname(__file__))
modulecfg = f'{currentdir}/requirements.txt'

if os.path.exists(modulecfg):
    with open ( modulecfg, "r", encoding='utf8') as cfgobject:
        modulelist = cfgobject.readlines()

for module in modulelist:
    module = module.rstrip()
    print('# Module # {}'.format(module))
    try:
        __import__(module)
    except ImportError:
        print(f'### Issue ### ToFix ### pip3 install {module}')
        ISSUES = ISSUES + 1
print(f'# Report # {ISSUES} Issues')
