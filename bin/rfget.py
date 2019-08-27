#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Explanation: gets a list of csv files from the Recorded Future website
Publish this to the SumoLogic website.

Usage:
    $ python  rfget [ options ]

Style:
    Google Python Style Guide:
    http://google.github.io/styleguide/pyguide.html

    @name           rfget
    @version        0.8.00
    @author-name    Wayne Schmidt
    @author-email   wschmidt@sumologic.com
    @license-name   GNU GPL
    @license-url    http://www.gnu.org/licenses/gpl.html
"""

__version__ = 0.80
__author__ = "Wayne Schmidt (wschmidt@sumologic.com)"

import argparse
import datetime
import os
import configparser
import json
import requests
import urllib.request
import sys

sys.dont_write_bytecode = 1

PARSER = argparse.ArgumentParser(description="""

This script retrieves Recorded Future Data and saves then into a local cache.

""")

PARSER.add_argument('-w', metavar='<weburl>', dest='weburl', help='specify hosted weburl')
PARSER.add_argument('-k', metavar='<apikey>', dest='apikey', help='specify API key')
PARSER.add_argument('-r', metavar='<rfmaps>', dest='rfmaps', default='all', help='specify rfmap')
PARSER.add_argument('-o', metavar='<outputdir>', dest='outputdir', help='specify output directory')
PARSER.add_argument('-c', metavar='<cfgfile>', dest='cfgfile', help='specify a config file')

ARGS = PARSER.parse_args()

if ARGS.cfgfile:
    CFGFILE = os.path.abspath(ARGS.cfgfile)
    CONFIG = configparser.ConfigParser()
    CONFIG.read(CFGFILE)
    WEBURL = json.loads(CONFIG.get("Default", "WEBURL"))
    os.environ['WEBURL'] = WEBURL
    APIKEY = json.loads(CONFIG.get("Default", "APIKEY"))
    os.environ['APIKEY'] = APIKEY
    RFMAPS = json.loads(CONFIG.get("Default", "RFMAPS"))
    os.environ['RFMAPS'] = RFMAPS
else:
    if ARGS.weburl:
        os.environ["WEBURL"] = ARGS.weburl
    if ARGS.apikey:
        os.environ["APIKEY"] = ARGS.apikey
    if ARGS.rfmaps:
        os.environ["RFMAPS"] = ARGS.rfmaps

SRCTAG = 'recordedfuture'

CURRENT = datetime.datetime.now()
DSTAMP = CURRENT.strftime("%Y%m%d")
TSTAMP = CURRENT.strftime("%H%M%S")
LSTAMP = DSTAMP + '.' + TSTAMP

URLBASE = 'https://api.recordedfuture.com/v2'
URLTAIL = 'risklist?format=csv%2Fsplunk'

try:
    WEBURL = os.environ['WEBURL']
    APIKEY = os.environ['APIKEY']
    RFMAPS = os.environ['RFMAPS']
except KeyError as myerror:
    print('Environment Variable Not Set :: {} '.format(myerror.args[0]))

RFITEMLIST = list()
RFITEMLIST = ('ip', 'domain', 'url', 'hash', 'vulnerability')
RFITEMLIST = [ 'ip' ]

def main():
    """
    This is the wrapper for the retreival and the publish modules.
    """

    for rfitem in RFITEMLIST:
        if RFMAPS in (rfitem, 'all'):
            print(rfitem)
            slrfmap = retrieve_rfitem(rfitem)
            publish_to_sumologic(slrfmap)

def retrieve_rfitem(rfitem):
    """
    This retrieves the files from the Recorded Future website
    """
    targeturl = '%s/%s/%s' % (URLBASE, rfitem, URLTAIL)
    getrequest = urllib.request.Request(targeturl, None, {'X-RFToken': APIKEY})
    getresults = urllib.request.urlopen(getrequest)

    if ARGS.outputdir:
        persist_rfitem(getresults, rfitem)

def persist_rfitem(getresults, rfitem):
    """
    This persists the Recoorded Future files to a local directory
    """
    basedir = os.path.abspath((os.path.join(ARGS.outputdir)))
    csvdir = '%s/%s/%s' % (basedir, SRCTAG, DSTAMP)
    os.makedirs(csvdir, exist_ok=True)

    filename = '%s_%s_%s.%s' % ('rf', rfitem, 'risklist', 'csv')
    dstfile = os.path.join(csvdir, filename)
    print("Starting: " +  dstfile)
    with open(dstfile, mode="wb") as outputfile:
        outputfile.write(getresults.read())
    print("Finished: " + dstfile)

if __name__ == '__main__':
    main()
