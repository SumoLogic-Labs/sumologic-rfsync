#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Explanation:

This script collects demo events from Recorded Future
It puts files into a local directory cache.
Finally, it provides several means to publish to Sumo Logic.

Usage:
    $ python  demoprep [ options ]

Style:
    Google Python Style Guide:
    http://google.github.io/styleguide/pyguide.html

    @name           demoprep
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
import urllib.request
import requests

sys.dont_write_bytecode = 1

PARSER = argparse.ArgumentParser(description="""
A tool to manage collecting sample demo data from Recorded Future and publish to Sumo Logic.
""")

PARSER.add_argument('-k', metavar='<apikey>', dest='APIKEY', help='set API key')

PARSER.add_argument('-d', metavar='<cachedir>', dest='CACHED', help='set directory')

PARSER.add_argument('-c', metavar='<cfgfile>', dest='CONFIG', help='set config file')

PARSER.add_argument('-s', metavar='<srcurl>', dest='SRCURL', help='set HTTPS endpoint')

PARSER.add_argument('-m', metavar='<maplist>', dest='MAPLIST', \
                    action='append', help='set specific maps')

PARSER.add_argument("-v", type=int, default=0, metavar='<verbose>', \
                    dest='verbose', help="more verbose")

ARGS = PARSER.parse_args(args=None if sys.argv[1:] else ['--help'])

DEFAULTMAP = ('domain', 'hash', 'ip', 'url', 'vulnerability')
MAPLIST = DEFAULTMAP

FILEMAP = {}
WEBMAP = {}

SRCTAG = 'recordedfuture'

CURRENT = datetime.datetime.now()
DSTAMP = CURRENT.strftime("%Y%m%d")
TSTAMP = CURRENT.strftime("%H%M%S")

LSTAMP = DSTAMP + '.' + TSTAMP

RANGE = "10000"

URLBASE = 'https://api.recordedfuture.com/v2'
URLTAIL = 'demoevents?limit=' + RANGE

CACHED = os.path.join('/var/tmp/', SRCTAG, DSTAMP)

if ARGS.CONFIG:
    CFGFILE = os.path.abspath(ARGS.CONFIG)
    CONFIG = configparser.ConfigParser()
    CONFIG.optionxform = str
    CONFIG.read(CFGFILE)
    if ARGS.verbose > 9:
        print(dict(CONFIG.items('Default')))

    if CONFIG.has_option("Default", "APIKEY"):
        APIKEY = CONFIG.get("Default", "APIKEY")
        os.environ['APIKEY'] = APIKEY

    if CONFIG.has_option("Default", "MAPLIST"):
        MAPLIST = CONFIG.get("Default", "MAPLIST")

    if CONFIG.has_option("Default", "SRCURL"):
        SRCURL = CONFIG.get("Default", "SRCURL")

    if CONFIG.has_option("Default", "CACHED"):
        CACHED = os.path.abspath(CONFIG.get("Default", "CACHED"))

if ARGS.SRCURL:
    SRCURL = ARGS.SRCURL

if ARGS.APIKEY:
    os.environ['APIKEY'] = ARGS.APIKEY

if ARGS.CACHED:
    CACHED = os.path.abspath(ARGS.CACHED)

if ARGS.MAPLIST:
    MAPLIST = ARGS.MAPLIST

for mapname in MAPLIST:

    if mapname == 'all':
        for mapitem in DEFAULTMAP:
            filename = f'{"rf.demoevents"}.{mapitem}.{"txt"}'
            dstfile = os.path.join(CACHED, filename)
            FILEMAP[mapitem] = dstfile
            WEBMAP[mapitem] = SRCURL

    if mapname != 'all':
        filename = f'{"rf.demoevents"}.{mapitem}.{"txt"}'
        dstfile = os.path.join(CACHED, filename)
        FILEMAP[mapname] = dstfile
        WEBMAP[mapname] = SRCURL

try:
    APIKEY = os.environ['APIKEY']
except KeyError as myerror:
    print(f'Environment Variable Not Set :: {myerror.args[0]}')

def main():
    """
    This is the wrapper for the retreival and the publish modules.
    """

    if ARGS.verbose > 3:
        print(f'local_cache_directory: {CACHED}')

    for targetkey, targetfile in FILEMAP.items():
        retrieve_and_publish(targetkey, targetfile)

def retrieve_and_publish(targetkey, targetfile):
    """
    This retrieves the files from the Recorded Future website
    """
    if ARGS.verbose > 1:
        print(f'download_maps: {targetkey}')
        print(f'download_file: {targetfile}')

    maptarget = f'{URLBASE}/{targetkey}/{URLTAIL}'
    if ARGS.verbose > 2:
        print(f'using: {maptarget}')

    os.makedirs(CACHED, exist_ok=True)

    if ARGS.verbose > 2:
        print(f'downloading: {targetkey}')

    url = maptarget
    headers = {'Content-Type':'txt/plain'}
    session = requests.Session()
    sumo_category = SRCTAG + '/' + 'demoevents' + '/' + targetkey
    headers['X-Sumo-Category'] = sumo_category

    req = urllib.request.Request(url, None, {'X-RFToken': APIKEY})
    with urllib.request.urlopen(req) as res:
        output = res.read().decode("utf-8")
        with open(targetfile, mode="w", encoding='utf8') as outputfile:
            for line in output.splitlines():
                outputfile.write(line)
                outputfile.write('\n')
    if ARGS.verbose > 2:
        print(f'publishing: {SRCURL}')

    with open(targetfile, mode="r", encoding='utf8') as inputfile:
        rf_map_payload = (inputfile.read().encode('utf-8'))
        postresponse = session.post(SRCURL, rf_map_payload, headers=headers).status_code
        print(f'source_category: {sumo_category}')
        print(f'upload_response: {postresponse}')

if __name__ == '__main__':
    main()
