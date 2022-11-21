#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Explanation:

This script collects the Recorded Future Fusion Files
and publishes them into Sumo Logic

Usage:
    $ python  rfslfusion [ options ]

Style:
    Google Python Style Guide:
    http://google.github.io/styleguide/pyguide.html

    @name           rfslfusion
    @version        1.5.0
    @author-name    Wayne Schmidt
    @author-email   wschmidt@sumologic.com
    @license-name   Apache
    @license-url    https://www.apache.org/licenses/LICENSE-2.0
"""

__version__ = '1.5.0'
__author__ = "Wayne Schmidt (wschmidt@sumologic.com)"

import argparse
import configparser
import datetime
import os
import sys
import requests

sys.dont_write_bytecode = 1

PARSER = argparse.ArgumentParser(description="""
Tool to collect Recorded Future threat intel and publish to Sumo Logic
""")

PARSER.add_argument('-c', metavar='<cfgfile>', dest='CONFIG', help='specify a config file')

PARSER.add_argument("-v", type=int, default=0, metavar='<verbose>', \
                    dest='verbose', help="specify level of verbose output")

ARGS = PARSER.parse_args(args=None if sys.argv[1:] else ['--help'])

SRCTAG = 'recordedfuture'

CURRENT = datetime.datetime.now()
DSTAMP = CURRENT.strftime("%Y%m%d")
TSTAMP = CURRENT.strftime("%H%M%S")

LSTAMP = DSTAMP + '.' + TSTAMP

URLBASE = 'https://api.recordedfuture.com/v2/fusion/files/?path='

if os.name == 'nt':
    VARTMPDIR = os.path.join ( "C:", "Windows", "Temp" )
else:
    VARTMPDIR = os.path.join ( "/", "var", "tmp" )

CACHED = os.path.join(VARTMPDIR, SRCTAG, DSTAMP)
SRCURL = 'UNSET'

if ARGS.CONFIG:
    CFGFILE = os.path.abspath(ARGS.CONFIG)
    CONFIG = configparser.ConfigParser()
    CONFIG.optionxform = str
    CONFIG.read(CFGFILE)
    if ARGS.verbose > 8:
        print(dict(CONFIG.items('Default')))

    if CONFIG.has_option("Default", "MAPKEY"):
        MAPKEY = CONFIG.get("Default", "MAPKEY")
        os.environ['MAPKEY'] = MAPKEY

    if CONFIG.has_option("Default", "SRCURL"):
        SRCURL = CONFIG.get("Default", "SRCURL")
        os.environ['SRCURL'] = SRCURL

    if CONFIG.has_option("Default", "CACHED"):
        CACHED = os.path.abspath(CONFIG.get("Default", "CACHED"))

try:
    MAPKEY = os.environ['MAPKEY']
    SRCURL = os.environ['SRCURL']
except KeyError as myerror:
    print(f'Environment Variable Not Set :: {myerror.args[0]}')

def main():
    """
    This is the wrapper for the retreival and the publish modules.
    """
    if ARGS.verbose > 3:
        print(f'local_cache_directory: {CACHED}')


    for fusionkey in dict(CONFIG.items('FusionFiles')):
        fusionvalue = CONFIG.get("FusionFiles", fusionkey)
        fusionfile = retrieve_item(fusionkey, fusionvalue)
        if SRCURL != 'UNSET':
            publish_item(fusionfile)

def retrieve_item(fusionkey, fusionpath):
    """
    This retrieves the files from the Recorded Future website
    """

    target_http = f'{URLBASE}{fusionpath}'

    os.makedirs(CACHED, exist_ok=True)

    target_file = os.path.abspath(os.path.join(CACHED,fusionkey))

    if ARGS.verbose > 3:
        print(f'downloading: {target_http}')

    session = requests.Session()
    headers = {'X-RFToken': MAPKEY, 'X-RF-User-Agent' : 'SumoLogic+v1.0'}
    body = session.get(target_http, headers=headers)
    getresults = body.text

    if ARGS.verbose > 3:
        print(f'persisting: {target_file}')

    with open(target_file, mode="w", encoding='utf8') as outputfile:
        if ARGS.verbose > 7:
            print(f'starting: {fusionkey}')
        outputfile.write(getresults)
        if ARGS.verbose > 7:
            print(f'finished: {fusionkey}')

    return target_file

def publish_item(fusion_source):
    """
    This is the wrapper for publishing the files from Recorded Future to SumoLogic
    """

    headers = {'Content-Type':'txt/csv'}
    session = requests.Session()

    if ARGS.verbose > 3:
        print(f'preparing: {fusion_source}')

    with open(fusion_source, mode='r', encoding='utf8') as outputfile:
        fusion_payload = (outputfile.read().encode('utf-8'))

    with open(fusion_source, mode='r', encoding='utf8') as outputfile:
        fusion_schema = (outputfile.readline().encode('utf-8'))

    if ARGS.verbose > 3:
        print(f'publishing: {fusion_source}')

    filebase = os.path.splitext(os.path.basename(fusion_source))[0]

    fusion_file_category = f'recordedfuture/fusion/files/{filebase}'
    headers['X-Sumo-Category'] = fusion_file_category
    postresponse = session.post(SRCURL, fusion_payload, headers=headers).status_code

    if ARGS.verbose > 7:
        print(f'source_category: {str(fusion_file_category)}')
        print(f'upload_response: {str(postresponse)}')

    with open(fusion_source, mode='r', encoding='utf8') as outputfile:
        fusion_schema = (outputfile.readline().encode('utf-8'))

    fusion_schema_category = f'recordedfuture/fusion/schema/{filebase}'
    headers['X-Sumo-Category'] = fusion_schema_category
    postresponse = session.post(SRCURL, fusion_schema, headers=headers).status_code

    if ARGS.verbose > 7:
        print(f'source_category: {str(fusion_schema_category)}')
        print(f'upload_response: {str(postresponse)}')

if __name__ == '__main__':
    main()
