"""
Lambda to pull down demo events
"""
import configparser
import datetime
import os
import sys
import urllib.request
import requests

sys.dont_write_bytecode = 1

DEFAULTMAP = ['domain', 'hash', 'ip', 'url', 'vulnerability']
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

VERBOSE = 0

CURRENTDIR = os.path.abspath(os.path.dirname(__file__))
CFGFILE = os.path.abspath(os.path.join(CURRENTDIR, 'recorded_future.cfg'))

CONFIG = configparser.ConfigParser()
CONFIG.optionxform = str
CONFIG.read(CFGFILE)
if VERBOSE > 9:
    print(dict(CONFIG.items('Default')))

if CONFIG.has_option("Default", "MAPKEY"):
    MAPKEY = CONFIG.get("Default", "MAPKEY")
    os.environ['MAPKEY'] = MAPKEY

if CONFIG.has_option("Default", "MAPLIST"):
    MAPLIST = CONFIG.get("Default", "MAPLIST").split(",")
    print(MAPLIST)

if CONFIG.has_option("Default", "SRCURL"):
    SRCURL = CONFIG.get("Default", "SRCURL")

if CONFIG.has_option("Default", "CACHED"):
    CACHED = os.path.abspath(CONFIG.get("Default", "CACHED"))

for mapname in MAPLIST:

    if mapname == 'all':
        for mapitem in DEFAULTMAP:
            filename = f'{"rf_demoevents"}.{mapitem}.{"txt"}'
            dstfile = os.path.join(CACHED, filename)
            FILEMAP[mapitem] = dstfile
            WEBMAP[mapitem] = SRCURL

    if mapname != 'all':
        filename = f'{"rf_demoevents"}.{mapname}.{"txt"}'
        dstfile = os.path.join(CACHED, filename)
        FILEMAP[mapname] = dstfile
        WEBMAP[mapname] = SRCURL

try:
    MAPKEY = os.environ['MAPKEY']
except KeyError as myerror:
    print(f'Environment Variable Not Set :: {myerror.args[0]}')

def retrieve_and_publish(targetkey, targetfile):
    """
    This retrieves the files from the Recorded Future website
    """
    if VERBOSE > 1:
        print(f'download_maps: {targetkey}')
        print(f'download_file: {targetfile}')

    maptarget = f'{URLBASE}/{targetkey}/{URLTAIL}'
    if VERBOSE > 2:
        print(f'using: {maptarget}')

    os.makedirs(CACHED, exist_ok=True)

    if VERBOSE > 2:
        print(f'downloading: {targetkey}')

    url = maptarget
    headers = {'Content-Type':'txt/plain'}
    session = requests.Session()
    sumo_category = SRCTAG + '/' + 'demoevents' + '/' + targetkey
    headers['X-Sumo-Category'] = sumo_category

    req = urllib.request.Request(url, None, {'X-RFToken': MAPKEY})
    with urllib.request.urlopen(req) as res:
        output = res.read().decode("utf-8")
        with open(targetfile, mode="w", encoding='utf8') as outputfile:
            for line in output.splitlines():
                outputfile.write(line)
                outputfile.write('\n')
    if VERBOSE > 2:
        print(f'publishing: {SRCURL}')

    with open(targetfile, mode="r", encoding='utf8') as inputfile:
        rf_map_payload = (inputfile.read().encode('utf-8'))
        postresponse = session.post(SRCURL, rf_map_payload, headers=headers).status_code
        if VERBOSE > 2:
            print(f'source_category: {sumo_category}')
            print(f'upload_response: {postresponse}')

def lambda_handler(event=None,context=None):
    """
    This is the wrapper for the retreival and the publish modules.
    """

    if VERBOSE > 3:
        print(f'local_cache_directory: {CACHED}')

    if VERBOSE > 9:
        print(f'event: {event}')
        print(f'context: {context}')

    for targetkey, targetfile in FILEMAP.items():
        retrieve_and_publish(targetkey, targetfile)

if __name__ == '__main__':
    lambda_handler()
