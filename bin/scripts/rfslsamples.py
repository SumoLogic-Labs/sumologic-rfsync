#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Explanation:

    This doenloads Recorded Future demo events into Sumo Logic.
    The initial Sumo Logic environment setup is done with Terraform.

Usage:
    $ python  rfslsamples [ options ]

Style:
    Google Python Style Guide:
    http://google.github.io/styleguide/pyguide.html

    @name           rfslsamples
    @version        6.6.0
    @author-name    Wayne Schmidt
    @author-email   wayne.kirk.schmidt@gmail.com
    @license-name   Apache
    @license-url    https://www.apache.org/licenses/LICENSE-2.0
"""

__version__ = '6.0.0'
__author__ = "Wayne Schmidt (wayne.kirk.schmidt@gmail.com)"

import argparse
import configparser
import datetime
import os
import sys
import urllib.request
import requests

sys.dont_write_bytecode = True

PARSER = argparse.ArgumentParser(description="""
Download and Publish Script for Recorded Future Sample Events
""")

PARSER.add_argument('-c', metavar='<cfgfile>', dest='CONFIG', \
                    default='default', help='specify a config file')
PARSER.add_argument("-v", type=int, default=0, metavar='<verbose>', \
                    dest='verbose', help="specify level of verbose output")

ARGS = PARSER.parse_args()

CURRENTDIR = os.path.abspath(os.path.dirname(__file__))
CMDNAME = os.path.splitext(os.path.basename(__file__))[0]

CFGNAME = f'{CMDNAME}.cfg'

DELAY_TIME = 9

if ARGS.CONFIG == 'default':
    CFGFILE = os.path.abspath(os.path.join(CURRENTDIR, CFGNAME ))
else:
    CFGFILE = os.path.abspath(ARGS.CONFIG)

DEFAULTMAP = ('domain', 'hash', 'ip', 'url', 'vulnerability')
MAPLIST = DEFAULTMAP

SRCTAG = 'recordedfuture'

RANGE = "10000"

URLBASE = 'https://api.recordedfuture.com/v2'
URLTAIL = 'demoevents?limit=' + RANGE

if os.name == 'nt':
    CACHED = os.path.join("C:", "Windows", "Temp" , SRCTAG)
else:
    CACHED = os.path.join("/", "var", "tmp", SRCTAG)

CFGDICT = {}

CURRENT = datetime.datetime.now()
DSTAMP = CURRENT.strftime("%Y%m%d")
TSTAMP = CURRENT.strftime("%H%M%S")

PURPOSE = 'samples'

def initialize_variables():
    """
    Define and read configuration file, validating config file entries
    """
    if os.path.exists(CFGFILE):
        config = configparser.RawConfigParser()
        config.optionxform = str
        config.read(CFGFILE)
    else:
        print(f'ConfigFile: {CFGFILE} Missing! Exiting.')
        sys.exit()

    if ARGS.verbose > 8:
        print(dict(config.items('Default')))

    config.read(CFGFILE)

    if config.has_option("Default", "recorded_future_cache_dir"):
        CFGDICT['recorded_future_cache_dir'] = \
           f'{config.get("Default", "recorded_future_cache_dir")}/{PURPOSE}'
    else:
        CFGDICT['recorded_future_cache_dir'] = \
           f'{CACHED}/{PURPOSE}'

    if config.has_option("Default", "recorded_future_map_list"):
        CFGDICT['recorded_future_map_list'] = \
            config.get("Default", "recorded_future_map_list").split(',')
    else:
        CFGDICT['recorded_future_map_list'] = DEFAULTMAP

    if config.has_option("Default", "recorded_future_api_key"):
        CFGDICT['recorded_future_api_key'] = config.get("Default", "recorded_future_api_key")

    if config.has_option("Default", "source-url"):
        CFGDICT['source-url'] = config.get("Default", "source-url")

    return CFGDICT

def retrieve_and_publish():
    """
    This retrieves the files from the Recorded Future website
    """

    os.makedirs(CFGDICT['recorded_future_cache_dir'], exist_ok=True)

    for mapname in MAPLIST:
        urlsource = f'{URLBASE}/{mapname}/{URLTAIL}'
        filename = f'{"rf.demoevents"}.{mapname}.{"txt"}'
        targetfile = os.path.join(CACHED, filename)

        if ARGS.verbose > 2:
            print(f'downloading: {mapname}')

        headers = {'Content-Type':'txt/plain'}
        session = requests.Session()

        sumo_category = SRCTAG + '/' + 'demoevents' + '/' + mapname
        headers['X-Sumo-Category'] = sumo_category

        req = urllib.request.Request(urlsource, None, \
            {'X-RFToken': CFGDICT["recorded_future_api_key"]})

        if os.path.exists(targetfile):
            if ARGS.verbose > 2:
                print(f'Scrubbing_Demo_File: {targetfile}')
            os.remove(targetfile)

        with urllib.request.urlopen(req) as res:
            output = res.read().decode("utf-8")
            with open(targetfile, mode="w", encoding='utf8') as outputfile:
                for line in output.splitlines():
                    outputfile.write(line)
                    outputfile.write('\n')

        if ARGS.verbose > 2:
            print(f'publishing: {mapname} to: {sumo_category}')

        with open(targetfile, mode="r", encoding='utf8') as inputfile:
            rf_payload = (inputfile.read().encode('utf-8'))
            postresponse = session.post(CFGDICT["source-url"], \
                rf_payload, headers=headers).status_code

            print(f'source_category: {sumo_category}')
            print(f'upload_response: {postresponse}')

def lambda_handler(event=None,context=None):
    """
    Functionality will work either being called by a lambda or standalone script
    """

    if ARGS.verbose > 4:
        print(f'ConfigFile: {CFGFILE}')

    initialize_variables()

    if ARGS.verbose > 9:
        print(f'Script_Event: {event}')
        print(f'Script_Context: {context}')

    retrieve_and_publish()

if __name__ == '__main__':
    lambda_handler()
