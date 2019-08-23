#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Explanation: gets a list of csv files from the recorded futures website

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

import urllib.request
import sys

RFD = dict()
RFD['ip'] = 'ip'
RFD['domain'] = 'domain'
RFD['url'] = 'url'
RFD['hash'] = 'hash'
RFD['vulnerability'] = 'vulnerability'

URLBASE = 'https://api.recordedfuture.com/v2'
URLTAIL = 'risklist?format=csv%2Fsplunk'

TOKEN = '1b89670de448468ab765ec7976b2a7a7'

for target, url in RFD.items():

    filesep = '_'
    filelist = ('rf', target, 'risklist')
    dstfile = filesep.join(filelist)

    urlsep = '/'
    urllist = (URLBASE, target, URLTAIL)
    url = urlsep.join(urllist)

    print(dstfile, url)

    request = urllib.request.Request(url, None, {'X-RFToken': TOKEN})
    results = urllib.request.urlopen(request)

    print("Starting Risklist: " +  dstfile)
    with open(dstfile, mode="wb") as outputfile:
        outputfile.write(results.read())
    print("Finished Risklist: " + dstfile)

sys.exit()
