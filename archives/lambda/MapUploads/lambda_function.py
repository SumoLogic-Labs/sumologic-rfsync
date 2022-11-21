"""
Lambda to download and upload map files
"""
import configparser
import datetime
import os
import sys
import requests

sys.dont_write_bytecode = 1

DEFAULTMAP = []
DEFAULTMAP.append('ip')
MAPLIST = DEFAULTMAP

FILE = {}
HTTP = {}
SUMO = {}

VERBOSE = 0

SRCTAG = 'recordedfuture'

CURRENTDIR = os.path.abspath(os.path.dirname(__file__))
CFGFILE = os.path.abspath(os.path.join(CURRENTDIR, 'recorded_future.cfg'))

CURRENT = datetime.datetime.now()
DSTAMP = CURRENT.strftime("%Y%m%d")
TSTAMP = CURRENT.strftime("%H%M%S")

LSTAMP = DSTAMP + '.' + TSTAMP

URLBASE = 'https://api.recordedfuture.com/v2'
URLTAIL = 'risklist?format=csv%2Fsplunk'

if os.name == 'nt':
    CACHED = os.path.join ( "C:", "Windows", "Temp" )
else:
    CACHED = os.path.join ( "/", "var", "tmp" )

CACHED = os.path.join(CACHED, SRCTAG, DSTAMP)
SRCURL = 'UNSET'

CONFIG = configparser.ConfigParser()
CONFIG.optionxform = str
CONFIG.read(CFGFILE)

if CONFIG.has_option("Default", "MAPKEY"):
    MAPKEY = CONFIG.get("Default", "MAPKEY")
    os.environ['MAPKEY'] = MAPKEY

if CONFIG.has_option("Default", "MAPLIST"):
    MAPLIST = CONFIG.get("Default", "MAPLIST").split(',')

if CONFIG.has_option("Default", "SRCURL"):
    SRCURL = CONFIG.get("Default", "SRCURL")

if CONFIG.has_option("Default", "CACHED"):
    CACHED = os.path.abspath(CONFIG.get("Default", "CACHED"))

for token in MAPLIST:
    if "/" in token:
        map_name, LIST_NAME = token.split ('/')
    else:
        map_name = token
        LIST_NAME = 'default'

    http_value = f'{URLBASE}/{map_name}/{URLTAIL}/{LIST_NAME}'
    HTTP[token] = http_value

    file_name = f'{SRCTAG}.{"risklist"}.{map_name}.{LIST_NAME}.{"csv"}'
    file_value = os.path.join(CACHED, file_name)
    FILE[token] = file_value

    sumo_value = f'{SRCTAG}/{"map"}/{map_name}/{LIST_NAME}'
    if LIST_NAME == 'default':
        sumo_value = f'{SRCTAG}/{"map"}/{map_name}'
    SUMO[token] = sumo_value

try:
    MAPKEY = os.environ['MAPKEY']
except KeyError as myerror:
    print(f'Environment Variable Not Set :: {myerror.args[0]}')

def retrieve_mapitem(retrievetarget):
    """
    This retrieves the mapitem from Recorded Future
    """
    target_http = HTTP[retrievetarget]
    target_file = FILE[retrievetarget]

    if VERBOSE > 4:
        print(f'retrieving: {retrievetarget} from: {target_http}' )

    session = requests.Session()
    headers = {'X-RFToken': MAPKEY, 'X-RF-User-Agent' : 'SumoLogic+v1.0'}
    body = session.get(target_http, headers=headers)
    getresults = body.text

    with open(target_file, mode="w", encoding='utf8') as outputfile:
        outputfile.write(getresults)

def publish_mapitem(publishtarget):
    """
    This publishes the mapitem to Sumo Logic
    """
    target_file = FILE[publishtarget]
    target_sumo = SUMO[publishtarget]

    if VERBOSE > 6:
        print(f'publishing: {publishtarget} to: {target_sumo}')

    with open(target_file, mode='r', encoding='utf8') as outputfile:
        rf_map_payload = (outputfile.read().encode('utf-8'))

        headers = {'Content-Type':'txt/csv'}
        session = requests.Session()

        headers['X-Sumo-Category'] = target_sumo
        _postresponse = session.post(SRCURL, rf_map_payload, headers=headers).status_code

        if VERBOSE > 2:
            print(f'web_response: {_postresponse}')

def lambda_handler(event=None,context=None):
    """
    General Logic should work when called by a lambda or standalone script
    """
    if VERBOSE > 8:
        print(f'event: {event}')
        print(f'context: {context}')

    if VERBOSE > 4:
        print(f'creating: {CACHED}')
    os.makedirs(CACHED, exist_ok=True)

    for maplistitem in MAPLIST:
        retrieve_mapitem(maplistitem)

        if SRCURL != 'UNSET':
            publish_mapitem(maplistitem)

if __name__ == '__main__':
    lambda_handler()
