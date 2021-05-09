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
    @version        1.5.0
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
import os
import sys
import requests

sys.dont_write_bytecode = 1

PARSER = argparse.ArgumentParser(description="""
A tool to manage how to collect from Recorded Future and publish to Sumo Logic.
""")

PARSER.add_argument('-k', metavar='<apikey>', dest='APIKEY', help='set API key')

PARSER.add_argument('-d', metavar='<cachedir>', dest='CACHED', help='set directory')

PARSER.add_argument('-c', metavar='<cfgfile>', dest='CONFIG', help='set config file')

PARSER.add_argument('-s', metavar='<srcurl>', dest='SRCURL', help='set HTTPS endpoint')

PARSER.add_argument('-m', metavar='<maplist>', dest='MAPLIST', \
                    action='append', help='set specific maps')

PARSER.add_argument("-a", "--autosource", action='store_true', default=False, \
                    dest='AUTOSOURCE', help="make automatic categories for maps")

PARSER.add_argument("-i", "--initialize", action='store_true', default=False, \
                    dest='INITIALIZE', help="initialize config file")

PARSER.add_argument("-v", type=int, default=0, metavar='<verbose>', \
                    dest='verbose', help="more verbose")

ARGS = PARSER.parse_args()

DEFAULTMAP = ('domain', 'hash', 'ip', 'url', 'vulnerability')
MAPLIST = DEFAULTMAP

FILEMAP = dict()
WEBMAP = dict()

SRCTAG = 'recordedfuture'

CURRENT = datetime.datetime.now()
DSTAMP = CURRENT.strftime("%Y%m%d")
TSTAMP = CURRENT.strftime("%H%M%S")

LSTAMP = DSTAMP + '.' + TSTAMP

URLBASE = 'https://api.recordedfuture.com/v2'
URLTAIL = 'risklist?format=csv%2Fsplunk'

CACHED = os.path.join('/var/tmp/', SRCTAG, DSTAMP)

def initialize_config_file():
    """
    Initialize configuration file, write output, and then exit
    """

    starter_config='/var/tmp/recorded_future.initial.cfg'
    config = configparser.RawConfigParser()
    config.optionxform = str

    config.add_section('Default')

    cached_input = input ("Please enter your Cache Directory: \n")
    config.set('Default', 'CACHED', cached_input )

    apikey_input = input ("Please enter your API Secret: \n")
    config.set('Default', 'APIKEY', apikey_input )

    source_input = input ("Please enter the URL of the Sumologic Source: \n")
    config.set('Default', 'SRCURL', source_input )

    with open(starter_config, 'w') as configfile:
        config.write(configfile)
    print('Complete! Written: {}'.format(starter_config))
    sys.exit()

if ARGS.INITIALIZE:
    initialize_config_file()

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
            filename = '%s_%s.%s.%s' % ('rf', 'risklist', mapitem, 'csv')
            dstfile = os.path.join(CACHED, filename)
            FILEMAP[mapitem] = dstfile
            WEBMAP[mapitem] = SRCURL

    if mapname != 'all':
        filename = '%s_%s.%s.%s' % ('rf', 'risklist', mapname, 'csv')
        dstfile = os.path.join(CACHED, filename)
        FILEMAP[mapname] = dstfile
        WEBMAP[mapname] = SRCURL

try:
    APIKEY = os.environ['APIKEY']
except KeyError as myerror:
    print('Environment Variable Not Set :: {} '.format(myerror.args[0]))

def main():
    """
    This is the wrapper for the retreival and the publish modules.
    """

    if ARGS.verbose > 3:
        print('CACHED: {}'.format(CACHED))

    if ARGS.verbose > 7:
        print('DATASTRUCTURES:')
        print(FILEMAP)
        print(WEBMAP)

    for targetkey, targetfile in FILEMAP.items():
        retrieve_mapitem(targetkey, targetfile)

    for targetkey, localfile in FILEMAP.items():
        if targetkey in WEBMAP:
            sumologicurl = WEBMAP[targetkey]
            if SRCURL != 'UNSET':
                publish_mapitem(localfile, sumologicurl)

def retrieve_mapitem(targetkey, targetfile):
    """
    This retrieves the files from the Recorded Future website
    """
    if ARGS.verbose > 1:
        print('KEYNAME: ' + targetkey)
        print('FILENAME:' + targetfile)

    maptarget = '%s/%s/%s' % (URLBASE, targetkey, URLTAIL)

    session = requests.Session()
    headers = {'X-RFToken': APIKEY, 'X-RF-User-Agent' : 'SumoLogic+v1.0'}
    body = session.get(maptarget, headers=headers)
    getresults = body.text

    os.makedirs(CACHED, exist_ok=True)

    if ARGS.verbose > 2:
        print("Starting: " +  targetkey)

    with open(targetfile, mode="w") as outputfile:
        outputfile.write(getresults)

    if ARGS.verbose > 2:
        print("Finished: " + targetkey)

def publish_mapitem(localfile, sumologicurl):
    """
    This is the wrapper for publishing the files from Recorded Future to SumoLogic
    """
    if ARGS.verbose > 3:
        print('LOCALFILE: ' + localfile)

    with open(localfile, mode='r') as outputfile:

        rf_map_header = (outputfile.readline().encode('utf-8').strip())
        rf_map_payload = (outputfile.read().encode('utf-8'))

        headers = {'Content-Type':'txt/csv'}
        session = requests.Session()

        mymapfile = os.path.splitext(os.path.basename(localfile))[0]
        mymapname = mymapfile.split('.')[1]

        if ARGS.AUTOSOURCE:
            sumo_category = SRCTAG + '/' + 'map' + '/' + mymapname
        else:
            sumo_category = SRCTAG + '/' + 'feed'
        headers['X-Sumo-Category'] = sumo_category
        postresponse = session.post(sumologicurl, rf_map_payload, headers=headers).status_code
        if ARGS.verbose > 5:
            print('SUMOLOGIC_HTTPS: {}'.format(sumologicurl))
            print('SOURCE_CATEGORY: {}'.format(str(sumo_category)))
            print('UPLOAD_RESPONSE: {}'.format(str(postresponse)))

        sumo_category = SRCTAG + '/' + 'schema' + '/' + mymapname
        headers['X-Sumo-Category'] = sumo_category
        postresponse = session.post(sumologicurl, rf_map_header, headers=headers).status_code
        if ARGS.verbose > 5:
            print('SUMOLOGIC_HTTPS: {}'.format(sumologicurl))
            print('SOURCE_CATEGORY: {}'.format(str(sumo_category)))
            print('UPLOAD_RESPONSE: {}'.format(str(postresponse)))

if __name__ == '__main__':
    main()
