#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Explanation:

This script collects files from the Recorded Future website.
It puts files into a local directory cache.
Finally, it provides several means to publish to Sumo Logic.

Usage:
    $ python  rfslsync [ options ]

Style:
    Google Python Style Guide:
    http://google.github.io/styleguide/pyguide.html

    @name           rfslsync
    @version        3.0.0
    @author-name    Wayne Schmidt
    @author-email   wschmidt@sumologic.com
    @license-name   Apache
    @license-url    https://www.apache.org/licenses/LICENSE-2.0
"""

__version__ = '3.0.0'
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

PARSER.add_argument('-k', metavar='<apikey>', dest='MAPKEY', help='specify the API key')

PARSER.add_argument('-d', metavar='<cachedir>', dest='CACHED', help='specify the directory')

PARSER.add_argument('-c', metavar='<cfgfile>', dest='CONFIG', help='specify a config file')

PARSER.add_argument('-s', metavar='<srcurl>', dest='SRCURL', help='specify the publishing endpoint')

PARSER.add_argument('-m', metavar='<maplist>', dest='MAPLIST', \
                    action='append', help='specify specific maps')

PARSER.add_argument("-f", default='csv', metavar="<format>", dest='FORMAT', \
                    help="specify map format ( csv or json. default csv )")

PARSER.add_argument("-v", type=int, default=0, metavar='<verbose>', \
                    dest='verbose', help="specify level of verbose output")

PARSER.add_argument("-u", action='store_true', default=False, \
                    dest='UNIFIED', help="unify schema and payload")

ARGS = PARSER.parse_args(args=None if sys.argv[1:] else ['--help'])

DEFAULTMAP = []
DEFAULTMAP.append('ip')
MAPLIST = DEFAULTMAP

FILE = {}
HTTP = {}
SUMO = {}

SRCTAG = 'recordedfuture'

CURRENT = datetime.datetime.now()
DSTAMP = CURRENT.strftime("%Y%m%d")
TSTAMP = CURRENT.strftime("%H%M%S")

LSTAMP = DSTAMP + '.' + TSTAMP

URLBASE = 'https://api.recordedfuture.com/v2'
URLTAIL = 'risklist?format=csv%2Fsplunk'

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

    if CONFIG.has_option("Default", "MAPLIST"):
        MAPLIST = CONFIG.get("Default", "MAPLIST").split(',')

    if CONFIG.has_option("Default", "SRCURL"):
        SRCURL = CONFIG.get("Default", "SRCURL")

    if CONFIG.has_option("Default", "CACHED"):
        CACHED = os.path.abspath(CONFIG.get("Default", "CACHED"))

if ARGS.SRCURL:
    SRCURL = ARGS.SRCURL

if ARGS.MAPKEY:
    os.environ['MAPKEY'] = ARGS.MAPKEY

if ARGS.CACHED:
    CACHED = os.path.abspath(ARGS.CACHED)

if ARGS.MAPLIST:
    MAPLIST = ARGS.MAPLIST

for MYMAP in MAPLIST:
    if "/" in MYMAP:
        mapname, LIST_NAME = MYMAP.split ('/')
    else:
        mapname = MYMAP
        LIST_NAME = 'default'

    http_value = f'{URLBASE}/{mapname}/{URLTAIL}&list={LIST_NAME}'
    HTTP[MYMAP] = http_value

    file_name = f'{SRCTAG}.{"risklist"}.{mapname}.{LIST_NAME}.{"csv"}'
    file_value = os.path.join(CACHED, file_name)
    FILE[MYMAP] = file_value

    sumo_value = f'{SRCTAG}/{"map"}/{mapname}/{LIST_NAME}'
    if LIST_NAME == 'default':
        sumo_value = f'{SRCTAG}/{"map"}/{mapname}'
    SUMO[MYMAP] = sumo_value

try:
    MAPKEY = os.environ['MAPKEY']
except KeyError as myerror:
    print(f'Environment Variable Not Set :: {myerror.args[0]}')

def main():
    """
    This is the wrapper for the retreival and the publish modules.
    """

    if ARGS.verbose > 3:
        print(f'local_cache_directory: {CACHED}')

    for token in MAPLIST:
        if ARGS.verbose > 3:
            print(f'TOKEN: {token}')
        if ARGS.verbose > 7:
            print(f'TOKEN_HTTP: {HTTP[token]}')
            print(f'TOKEN_FILE: {FILE[token]}')
            print(f'TOKEN_SUMO: {SUMO[token]}')

        retrieve_mapitem(token)
        if SRCURL != 'UNSET':
            publish_mapitem(token)

def retrieve_mapitem(token):
    """
    This retrieves the files from the Recorded Future website
    """

    target_http = HTTP[token]
    target_file = FILE[token]

    if ARGS.verbose > 3:
        print(f'downloading: {target_http}')

    session = requests.Session()
    headers = {'X-RFToken': MAPKEY, 'X-RF-User-Agent' : 'SumoLogic+v1.0'}
    body = session.get(target_http, headers=headers)
    getresults = body.text

    os.makedirs(CACHED, exist_ok=True)

    if ARGS.verbose > 3:
        print(f'persisting: {target_file}')

    with open(target_file, mode="w", encoding='utf8' ) as outputfile:
        if ARGS.verbose > 7:
            print(f'starting: {token}')
        outputfile.write(getresults)
        if ARGS.verbose > 7:
            print(f'finished: {token}')

def publish_mapitem(token):
    """
    This is the wrapper for publishing the files from Recorded Future to SumoLogic
    """

    target_file = FILE[token]
    target_sumo = SUMO[token]

    if ARGS.verbose > 3:
        print(f'preparing: {target_file}')

    with open(target_file, mode='r', encoding='utf8') as outputfile:
        rf_map_header = (outputfile.readline().encode('utf-8').strip())
        rf_map_payload = (outputfile.read().encode('utf-8'))

    with open(target_file, mode='r', encoding='utf8') as outputfile:
        rf_map_complete = (outputfile.read().encode('utf-8'))

    if ARGS.verbose > 3:
        print(f'publishing: {target_sumo}')

    headers = {'Content-Type':'txt/csv'}
    session = requests.Session()

    headers['X-Sumo-Category'] = target_sumo
    if ARGS.UNIFIED:
        postresponse = session.post(SRCURL, rf_map_complete, headers=headers).status_code
    else:
        postresponse = session.post(SRCURL, rf_map_payload, headers=headers).status_code

    if ARGS.verbose > 7:
        print(f'source_category: {str(target_sumo)}')
        print(f'upload_response: {str(postresponse)}')

    target_sumo = target_sumo.replace("map","schema")
    headers['X-Sumo-Category'] = target_sumo
    postresponse = session.post(SRCURL, rf_map_header, headers=headers).status_code

    if ARGS.verbose > 7:
        print(f'source_category: {str(target_sumo)}')
        print(f'upload_response: {str(postresponse)}')

if __name__ == '__main__':
    main()
