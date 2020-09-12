#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Explanation:

This script will retrieve enriched information from Recorded Future
And send the information to Sumo Logic

Usage:
    $ python  rfslenrich [ options ]

Style:
    Google Python Style Guide:
    http://google.github.io/styleguide/pyguide.html

    @name           rfslenrich
    @version        1.0.0
    @author-name    Wayne Schmidt
    @author-email   wschmidt@sumologic.com
    @license-name   GNU GPL
    @license-url    http://www.gnu.org/licenses/gpl.html
"""

__version__ = '1.0.0'
__author__ = "Wayne Schmidt (wschmidt@sumologic.com)"

import argparse
import configparser
import datetime
import json
import os
import sys
import requests

sys.dont_write_bytecode = 1

PARSER = argparse.ArgumentParser(description="""
A tool to manage enriched information from Recorded Future and publish to Sumo Logic.
""")

PARSER.add_argument('-k', metavar='<key>', dest='key', help='set API key')
PARSER.add_argument('-c', metavar='<cfg>', dest='cfg', help='set config file')
PARSER.add_argument('-u', metavar='<url>', dest='url', help='set url: <urlname>')
PARSER.add_argument('-m', metavar='<map>', dest='map', help='set map: <mapname>')
PARSER.add_argument('-i', metavar='<item>', dest='item', help='set item: <itemname>')
PARSER.add_argument("-v", type=int, default=0, metavar='<verbose>', \
                    dest='verbose', help="more verbose")

URLLIST = ''
ARGS = PARSER.parse_args()
DEFAULTMAP = ('domain', 'hash', 'ip', 'url', 'vulnerability')
FIELDSLIST = ('analystNotes', 'counts', 'enterpriseLists', 'entity', 'metrics', \
              'relatedEntities', 'risk', 'sightings', 'timestamps')

SRCTAG = 'recordedfuture'
CURRENT = datetime.datetime.now()
DSTAMP = CURRENT.strftime("%Y%m%d")
TSTAMP = CURRENT.strftime("%H%M%S")
LSTAMP = DSTAMP + '.' + TSTAMP
URLBASE = 'https://api.recordedfuture.com/v2'

if ARGS.cfg:
    CFGFILE = os.path.abspath(ARGS.cfg)
    CONFIG = configparser.ConfigParser()
    CONFIG.read(CFGFILE)

    APIKEY = json.loads(CONFIG.get("Default", "APIKEY"))
    os.environ['APIKEY'] = APIKEY

    URLNAME = json.loads(CONFIG.get("Default", "URLNAME"))
    os.environ['URLNAME'] = URLNAME

if ARGS.url:
    os.environ['SRCURL'] = ARGS.url
if ARGS.item:
    os.environ['RFITEM'] = ARGS.item
if ARGS.map:
    os.environ['RFMAP'] = ARGS.map
if ARGS.key:
    os.environ['APIKEY'] = ARGS.key

try:
    APIKEY = os.environ['APIKEY']
    SRCURL = os.environ['SRCURL']
    RFMAP = os.environ['RFMAP']
    RFITEM = os.environ['RFITEM']
except KeyError as myerror:
    print('Environment Variable Not Set :: {} '.format(myerror.args[0]))

def main():
    """
    This is the wrapper for the retreival and the publish modules.
    """

    if ARGS.verbose > 4:
        print('APIKEY: {}'.format(APIKEY))
        print('RFMAP: {}'.format(RFMAP))
        print('RFITEM: {}'.format(RFITEM))
        print('SRCURL: {}'.format(SRCURL))

    rfdata = retrieve_mapitem(APIKEY, RFMAP, RFITEM)
    publish_mapitem(rfdata, SRCURL)

def retrieve_mapitem(my_key, my_map, my_item):
    """
    This retrieves the files from the Recorded Future website
    """
    separator = '%2C'
    fields = separator.join(FIELDSLIST)
    maptarget = '%s/%s/%s?fields=%s&metadata=false' % (URLBASE, my_map, my_item, fields)

    session = requests.Session()
    headers = {'X-RFToken': my_key, 'X-RF-User-Agent' : 'SumoLogic+v1.0'}
    body = session.get(maptarget, headers=headers)
    results = body.text

    return results

def publish_mapitem(payload, sumologicurl):
    """
    This is the wrapper for publishing the files from Recorded Future to SumoLogic
    """

    if ARGS.verbose > 2:
        print('SUMOLOGIC: {}'.format(sumologicurl))

    if ARGS.verbose > 4:
        print('PAYLOAD: {}'.format(payload))

    headers = {'Content-Type':'application/json'}
    session = requests.Session()
    postresponse = session.post(sumologicurl, payload, headers=headers).status_code

    if ARGS.verbose > 6:
        print('RESPONSE: {}'.format(postresponse))

if __name__ == '__main__':
    main()
