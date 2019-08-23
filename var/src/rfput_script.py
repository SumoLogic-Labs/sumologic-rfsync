#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Explanation: gets a list of csv files from the recorded futures website
Publish this to the SumoLogic website.

Usage:
    $ python  rfget [ options ]

Style:
    Google Python Style Guide:
    http://google.github.io/styleguide/pyguide.html

    @name           rfget
    @version        0.2.00
    @author-name    Wayne Schmidt
    @author-email   wschmidt@sumologic.com
    @license-name   GNU GPL
    @license-url    http://www.gnu.org/licenses/gpl.html
"""

__version__ = 0.40
__author__ = "Wayne Schmidt (wschmidt@sumologic.com)"

import argparse
import datetime
import os
import configparser
import json
import urllib.request
import sys

sys.dont_write_bytecode = 1

PARSER = argparse.ArgumentParser(description="""

This script connects Recorded Futures to SumoLogic in the following manner.
Retrieves the information from Recorded Futures in CSV format
Pushes the files to Sumologic hosted Web collector.

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

def main():
    """
    This is the wrapper for the retrieval and the publish modules.
    """
    print(WEBURL)
    targetdir = os.path.abspath('%s/%s/%s' % (ARGS.outputdir, SRCTAG, DSTAMP))
    print(targetdir)
    for targetfiles in os.listdir(targetdir):
        targetfile = os.path.join(targetdir, targetfiles)
        print(targetfile)
        with open(targetfile, mode='r') as outputfile:
            slrfmap8 = (outputfile.read().encode('utf-8'))
            postrequest = urllib.request.Request(WEBURL, slrfmap8, {'Content-Type':'txt/csv'})
            postresponse = urllib.request.urlopen(postrequest)

if __name__ == '__main__':
    main()
