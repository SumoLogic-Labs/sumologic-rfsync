#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Explanation:

    This doenloads Recorded Future Fusion files into Sumo Logic.
    The initial Sumo Logic environment setup is done with Terraform.

Usage:
    $ python  rfslfusion [ options ]

Style:
    Google Python Style Guide:
    http://google.github.io/styleguide/pyguide.html

    @name           rfslfusion
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
import shutil
import requests

sys.dont_write_bytecode = True

PARSER = argparse.ArgumentParser(description="""
Download and Publish Script for Recorded Future Fusion Data into Sumo Logic Source Categories
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

DEFAULTFUSION = ('domain', 'hash', 'ip', 'url', 'vulnerability')

SRCTAG = 'recordedfuture'

URLBASE = 'https://api.recordedfuture.com/v2'
URLTAIL = 'risklist?format=csv%2Fsplunk'

if os.name == 'nt':
    CACHED = os.path.join("C:", "Windows", "Temp" , SRCTAG)
else:
    CACHED = os.path.join("/", "var", "tmp", SRCTAG)

PUBLISH = {}
CFGDICT = {}

CURRENT = datetime.datetime.now()
DSTAMP = CURRENT.strftime("%Y%m%d")
TSTAMP = CURRENT.strftime("%H%M%S")

PURPOSE = 'fusion'

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

    if config.has_option("Default", "recorded_future_fusion_list"):
        CFGDICT['recorded_future_fusion_list'] = \
            config.get("Default", "recorded_future_fusion_list").split(',')
    else:
        CFGDICT['recorded_future_map_list'] = DEFAULTFUSION

    if config.has_option("Default", "recorded_future_access_key"):
        CFGDICT['recorded_future_access_key'] = config.get("Default", "recorded_future_access_key")

    if config.has_option("Default", "source-url"):
        CFGDICT['source-url'] = config.get("Default", "source-url")

    return CFGDICT

def download_and_publish():
    """
    Download Recorded Future Maps
    """

    if os.path.exists(CFGDICT['recorded_future_cache_dir']):
        if ARGS.verbose > 7:
            print(f'Scrubbing_Cache_Directory: {CFGDICT["recorded_future_cache_dir"]}')
        shutil.rmtree(CFGDICT['recorded_future_cache_dir'])
    os.makedirs(CFGDICT['recorded_future_cache_dir'], exist_ok=True)

    session = requests.Session()
    fusionurl = 'https://api.recordedfuture.com/v2/fusion/files/?path='

    for fvalue in CFGDICT['recorded_future_fusion_list']:
        target_http = f'{fusionurl}{fvalue}'
        target_name = f'{"fusion"}.{fvalue}'
        target_file = os.path.abspath(os.path.join(CFGDICT['recorded_future_cache_dir'],target_name))

        if ARGS.verbose > 3:
            print(f'Downloading: {target_http}')

        headers = {'X-RFToken': CFGDICT['recorded_future_access_key'], 'X-RF-User-Agent' : 'SumoLogic+v1.0'}
        body = session.get(target_http, headers=headers)
        getresults = body.text

        if ARGS.verbose > 3:
            print(f'Persisting: {target_file}')

        with open(target_file, mode="w", encoding='utf8') as outputfile:
            outputfile.write(getresults)

        headers = {'Content-Type':'txt/csv'}

        with open(target_file, mode='r', encoding='utf8') as outputfile:
            fusion_payload = (outputfile.read().encode('utf-8'))

        filebase = os.path.splitext(os.path.basename(target_file))[0]
        fusion_file_category = f'recordedfuture/fusion/files/{filebase}'

        if ARGS.verbose > 3:
            print(f'publishing: {fusion_file_category}')

        headers['X-Sumo-Category'] = fusion_file_category
        postresponse = session.post(CFGDICT['source-url'], fusion_payload, headers=headers).status_code

        if ARGS.verbose > 7:
            print(f'source_category: {str(fusion_file_category)}')
            print(f'upload_response: {str(postresponse)}')

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

    download_and_publish()

if __name__ == '__main__':
    lambda_handler()
