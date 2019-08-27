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
    @version        0.8.00
    @author-name    Wayne Schmidt
    @author-email   wschmidt@sumologic.com
    @license-name   GNU GPL
    @license-url    http://www.gnu.org/licenses/gpl.html
"""

__version__ = 0.40
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

This script connects Recorded Future to SumoLogic in the following manner.
Retrieves the information from Recorded Future in CSV format
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
    This is the wrapper for the retreival and the publish modules.
    """

    starttime = datetime.datetime.now()

    for rfitem in RFITEMLIST:
        if RFMAPS in (rfitem, 'all'):
            sync_rfitem(rfitem)

    finaltime = datetime.datetime.now()
    totaltime = finaltime - starttime
    print(totaltime.total_seconds())

def sync_rfitem(rfitem):
    """
    This retrieves the files from Recorded Future API server
    """
    targeturl = '%s/%s/%s' % (URLBASE, rfitem, URLTAIL)
    getrequest = requests.get(targeturl, headers=({'X-RFToken': APIKEY}), stream=True)
    if getrequest.status_code == 200:
        getrequest.raw.decode_content = True
        info = {'fieldname': ('filename', getrequest.raw, getrequest.headers['Content-Type'])}
        requests.post(WEBURL, files=info)

    if ARGS.outputdir:
        persist_rfitem(getrequest, rfitem)

def persist_rfitem(getrequest, rfitem):
    """
    This persists the Recorded Future files to a local directory
    """
    basedir = os.path.abspath((os.path.join(ARGS.outputdir)))
    csvdir = '%s/%s/%s' % (basedir, SRCTAG, DSTAMP)
    os.makedirs(csvdir, exist_ok=True)

    filename = '%s_%s_%s.%s' % ('rf', rfitem, 'risklist', 'csv')
    dstfile = os.path.join(csvdir, filename)
    with open(dstfile, mode="wb") as outputfile:
        outputfile.write(getrequest.content)

if __name__ == '__main__':
    main()
