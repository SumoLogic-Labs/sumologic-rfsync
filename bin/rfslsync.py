#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Explanation:

This will collect CSV files from the Recorded Future website
save this into a cache, and then Publish this to the SumoLogic website.

This script allows the client to choose how to publish as well.

Usage:
    $ python  rfslsync [ options ]

Style:
    Google Python Style Guide:
    http://google.github.io/styleguide/pyguide.html

    @name           rfslsync
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
import pprint
import re
import os
import sys
import urllib.request

sys.dont_write_bytecode = 1

PARSER = argparse.ArgumentParser(description="""

This script connects Recorded Future to SumoLogic in the following manner.
Retrieves the information from Recorded Future in CSV format
Pushes the files to Sumologic hosted Web collector.

""")

PARSER.add_argument('-k', metavar='<key>', dest='key', help='set API key')
PARSER.add_argument('-d', metavar='<dir>', dest='dir', help='set directory')
PARSER.add_argument('-c', metavar='<cfg>', dest='cfg', help='set config file')
PARSER.add_argument('-u', metavar='<url>', nargs='*', dest='url', help='set url: <map#urlname>')
PARSER.add_argument('-m', metavar='<map>', nargs='*', dest='map', default=['all'], help='set maps')
PARSER.add_argument('-v', '--verbose', help='verbose', action="store_true")

ARGS = PARSER.parse_args()
DEFAULTMAP = ('domain', 'hash', 'ip', 'url', 'vulnerability')
FILEMAP = dict()
WEBMAP = dict()
SRCTAG = 'recordedfuture'
CURRENT = datetime.datetime.now()
DSTAMP = CURRENT.strftime("%Y%m%d")
TSTAMP = CURRENT.strftime("%H%M%S")
LSTAMP = DSTAMP + '.' + TSTAMP
URLBASE = 'https://api.recordedfuture.com/v2'
URLTAIL = 'risklist?format=csv%2Fsplunk'
CSVDIR = 'unset'
MAPLIST = DEFAULTMAP

if ARGS.cfg:
    CFGFILE = os.path.abspath(ARGS.cfg)
    CONFIG = configparser.ConfigParser()
    CONFIG.read(CFGFILE)

    APIKEY = json.loads(CONFIG.get("Default", "APIKEY"))
    os.environ['APIKEY'] = APIKEY

    URLLIST = json.loads(CONFIG.get("Default", "URLLIST"))
    MAPLIST = json.loads(CONFIG.get("Default", "MAPLIST"))
    if CONFIG.has_option('Default', 'CSVDIR'):
        CSVDIR = os.path.abspath(json.loads(CONFIG.get("Default", "CSVDIR")))
else:
    if ARGS.url:
        URLLIST = ARGS.url
    if ARGS.map:
        MAPLIST = ARGS.map
    if ARGS.key:
        os.environ['APIKEY'] = ARGS.key
    if ARGS.dir:
        BASEDIR = os.path.abspath((os.path.join(ARGS.dir)))
        CSVDIR = os.path.abspath(ARGS.dir)

if CSVDIR == 'unset':
    HOMEDIR = os.path.abspath((os.path.expanduser('~')))
    BASEDIR = os.path.abspath((os.path.join(HOMEDIR, 'var', 'tmp')))

    CSVDIR = '%s/%s/%s' % (BASEDIR, SRCTAG, DSTAMP)

for mapname in MAPLIST:
    if mapname == 'all':
        for mapitem in DEFAULTMAP:
            filename = '%s_%s_%s.%s' % ('rf', mapitem, 'risklist', 'csv')
            dstfile = os.path.join(CSVDIR, filename)
            FILEMAP[mapitem] = dstfile
    if mapname != 'all':
        filename = '%s_%s_%s.%s' % ('rf', mapname, 'risklist', 'csv')
        dstfile = os.path.join(CSVDIR, filename)
        FILEMAP[mapname] = dstfile

if URLLIST is not None:
    for urlname in URLLIST:
        if ARGS.verbose:
            print('PRIOR-URLNAME: ' + urlname)
        matchObject = re.search(r"^(\w+\#.*)", urlname)
        if not matchObject:
            urlname = 'all' + '#' + urlname
        if ARGS.verbose:
            print('AFTER-URLNAME: ' + urlname)
        (targetmap, targeturl) = urlname.split('#')
        if targetmap == 'all':
            for mapname in DEFAULTMAP:
                if mapname in FILEMAP:
                    WEBMAP[mapname] = targeturl
        if targetmap != 'all':
            if targetmap in FILEMAP:
                WEBMAP[targetmap] = targeturl

try:
    APIKEY = os.environ['APIKEY']
except KeyError as myerror:
    print('Environment Variable Not Set :: {} '.format(myerror.args[0]))

def main():
    """
    This is the wrapper for the retreival and the publish modules.
    """

    if ARGS.verbose:
        print('DATASTRUCTURES:')
        pprint.pprint(FILEMAP)
        pprint.pprint(WEBMAP)

    if ARGS.verbose:
        print('CSVDIR: ' + CSVDIR)

    for targetkey, targetfile in FILEMAP.items():
        retrieve_mapitem(targetkey, targetfile)

    for targetkey, localfile in FILEMAP.items():
        sumologicurl = WEBMAP[targetkey]
        publish_mapitem(localfile, sumologicurl)


def retrieve_mapitem(targetkey, targetfile):
    """
    This retrieves the files from the Recorded Future website
    """
    if ARGS.verbose:
        print('FILEKEY: ' + targetkey)
        print('FILEFILE:' + targetfile)

    maptarget = '%s/%s/%s' % (URLBASE, targetkey, URLTAIL)
    getrequest = urllib.request.Request(maptarget, None, {'X-RFToken': APIKEY})
    getresults = urllib.request.urlopen(getrequest)

    os.makedirs(CSVDIR, exist_ok=True)

    if ARGS.verbose:
        print("Starting: " +  targetkey)

    with open(targetfile, mode="wb") as outputfile:
        outputfile.write(getresults.read())

    if ARGS.verbose:
        print("Finished: " + targetkey)

def publish_mapitem(localfile, sumologicurl):
    """
    This is the wrapper for publishing the files from Recorded Future to SumoLogic
    """
    if ARGS.verbose:
        print('LOCALFILE: ' + localfile)
        print('SUMOLOGIC: ' + sumologicurl)

    with open(localfile, mode='r') as outputfile:
        slrfmap8 = (outputfile.read().encode('utf-8'))
        postrequest = urllib.request.Request(sumologicurl, slrfmap8, {'Content-Type':'txt/csv'})
        postresponse = urllib.request.urlopen(postrequest)
        if ARGS.verbose:
            print('RESPONSE: ' + str(postresponse.status) )

if __name__ == '__main__':
    main()
