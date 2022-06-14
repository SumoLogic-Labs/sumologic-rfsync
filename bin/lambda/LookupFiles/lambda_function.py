"""
Lambda to process lookup files
"""
import json
import os
import sys
import configparser
import http
import glob
import requests
from filesplit.split import Split

sys.dont_write_bytecode = 1

VERBOSE = 0

CURRENTDIR = os.path.abspath(os.path.dirname(__file__))
CFGFILE = os.path.abspath(os.path.join(CURRENTDIR, 'recorded_future.cfg'))

CONFIG = configparser.ConfigParser()
CONFIG.optionxform = str
CONFIG.read(CFGFILE)

if VERBOSE > 8:
    print(dict(CONFIG.items('Default')))

DEFAULTMAP = []
DEFAULTMAP.append('ip')
MAPLIST = DEFAULTMAP

FILEMAP = {}
WEBMAP = {}
IDMAP = {}

URLBASE = 'https://api.recordedfuture.com/v2'
URLTAIL = 'risklist?format=csv%2Fsplunk'

if os.name == 'nt':
    CACHED = os.path.join ( "C:", "Windows", "Temp" )
else:
    CACHED = os.path.join ( "/", "var", "tmp" )

FILELIMIT = 50 * 1024 * 1024

LINELIMIT = 30000

CONFIG.read(CFGFILE)

if CONFIG.has_option("Default", "CACHED"):
    CACHED = CONFIG.get("Default", "CACHED")
    os.environ['CACHED'] = CACHED

if CONFIG.has_option("Default", "SUMOUID"):
    SUMOUID = CONFIG.get("Default", "SUMOUID")
    os.environ['SUMOUID'] = SUMOUID

if CONFIG.has_option("Default", "SUMOKEY"):
    SUMOKEY = CONFIG.get("Default", "SUMOKEY")
    os.environ['SUMOKEY'] = SUMOKEY

if CONFIG.has_option("Default", "SUMONAME"):
    SUMONAME = CONFIG.get("Default", "SUMONAME")
    os.environ['SUMONAME'] = SUMONAME

if CONFIG.has_option("Default", "MAPKEY"):
    MAPKEY = CONFIG.get("Default", "MAPKEY")
    os.environ['MAPKEY'] = MAPKEY

if CONFIG.has_option("Default", "MAPLIST"):
    MAPLIST = CONFIG.get("Default", "MAPLIST")
    os.environ['MAPLIST'] = MAPLIST

try:

    SUMOUID = os.environ['SUMOUID']
    SUMOKEY = os.environ['SUMOKEY']
    SUMONAME = os.environ['SUMONAME']
    MAPKEY = os.environ['MAPKEY']
    MAPLIST = os.environ['MAPLIST']

except KeyError as myerror:

    print(f'Environment Variable Not Set :: {myerror.args[0]}')

def prepare_maplist():
    """
    Populate all of the mapnames to use as output files
    """
    for mapname in MAPLIST.split(','):
        mapname = mapname.replace("/", ".")
        filename = f'{mapname}.{"csv"}'
        os.makedirs(CACHED, exist_ok=True)
        dstfile = os.path.join(CACHED, filename)
        FILEMAP[mapname] = dstfile
        if VERBOSE > 2:
            print(f'map: {mapname:20} file: {dstfile}')

def download_mapitem(targetkey, targetfile):
    """
    Download all of the maps into output files
    """
    maptarget = f'{URLBASE}/{targetkey}/{URLTAIL}'
    if VERBOSE > 2:
        print(f'syncing: {targetkey:16} using: {maptarget}')

    session = requests.Session()
    headers = {'X-RFToken': MAPKEY, 'X-RF-User-Agent' : 'SumoLogic+v1.0'}
    body = session.get(maptarget, headers=headers)
    getresults = body.text

    with open(targetfile, mode="w", encoding='utf8') as outputfile:
        outputfile.write(getresults)

def create_lookup_files(source,childlist,lookupdirid):
    """
    Create the Lookup file definitions
    """
    for targetkey, targetfile in FILEMAP.items():
        if targetkey not in childlist:
            lookupjsonfile = targetfile.replace("csv", "json")
            lookupjsonfile = os.path.join(".", os.path.basename(lookupjsonfile))
            result = source.create_lookup(lookupdirid, lookupjsonfile )
            lookupfileid = result['id']
            lookupfilename = result['name']
            if VERBOSE > 2:
                print(f'CREATE id: {lookupfileid} name: {lookupfilename}')
            IDMAP[targetkey] = lookupfileid
        else:
            IDMAP[targetkey] = childlist[targetkey]

def upload_lookup_data(source):
    """
    Upload the lookup file data
    """
    source.session.headers = None

    for targetkey, targetfile in FILEMAP.items():
        filesize = os.path.getsize(targetfile)
        lookupfileid = IDMAP[targetkey]
        if filesize <= FILELIMIT:
            if VERBOSE > 2:
                print(f'UPLOAD id: {lookupfileid} file: {targetfile}')
            _result = source.populate_lookup(lookupfileid, targetfile)
        else:
            split_dir = os.path.splitext(targetfile)[0]
            os.makedirs(split_dir, exist_ok=True)
            filesplit = Split(targetfile, split_dir )
            filesplit.bylinecount(linecount=LINELIMIT, includeheader=True)
            for csv_file in glob.glob(glob.escape(split_dir) + "/*.csv"):
                if VERBOSE > 2:
                    print(f'UPLOAD id: {lookupfileid} file: {csv_file}')
                _result = source.populate_lookup_merge(lookupfileid, csv_file)

def prepare_lookup_data(source):
    """
    Populate the data structures
    """

    target_object = "myfolders"
    target_dict = {}
    target_dict["orgid"] = SUMONAME
    target_dict[target_object] = {}

    src_items = source.get_personal_folder()

    target_dict[target_object]['id'] = {}
    target_dict[target_object]['id'].update({'parent' : SUMONAME})
    target_dict[target_object]['id'].update({'dump' : src_items})
    parent_id = target_dict['myfolders']['id']['dump']['id']

    return target_dict, parent_id

def configure_lookups():
    """
    Driver logic for creating lookups
    """
    source = SumoApiClient(SUMOUID, SUMOKEY)
    target_dict, parent_id = prepare_lookup_data(source)

    createdir = 'yes'

    for folder in target_dict['myfolders']['id']['dump']['children']:
        if folder['name'] == 'recordedfuture':
            createdir = 'no'
            lookupdirname = folder['name']
            lookupdirid = folder['id']

    if createdir == 'yes':
        result = source.create_folder('recordedfuture', parent_id)
        lookupdirname = result['name']
        lookupdirid = result['id']
        if VERBOSE > 2:
            print(f'\nCREATE id: {lookupdirid} name: {lookupdirname}\n')

    result = source.get_folder(lookupdirid)
    childlist = {}
    for child in result['children']:
        childid = child['id']
        childname = child['name']
        childlist[childname] = childid

    create_lookup_files(source,childlist,lookupdirid)

    upload_lookup_data(source)

class SumoApiClient():
    """
    General Sumo Logic API Client Class
    """

    def __init__(self, access_id, access_key, endpoint=None, cookie_file='cookies.txt'):
        """
        Initializes the Sumo Logic object
        """

        self.session = requests.Session()
        self.session.auth = (access_id, access_key)
        self.session.headers = {'content-type': 'application/json', \
            'accept': 'application/json'}
        cookiejar = http.cookiejar.FileCookieJar(cookie_file)
        self.session.cookies = cookiejar
        if endpoint is None:
            self.endpoint = self._get_endpoint()
        elif len(endpoint) < 3:
            self.endpoint = 'https://api.' + endpoint + '.sumologic.com/api'
        else:
            self.endpoint = endpoint
        if self.endpoint[-1:] == "/":
            raise Exception("Endpoint should not end with a slash character")

    def _get_endpoint(self):
        """
        SumoLogic REST API endpoint changes based on the geo location of the client.
        It contacts the default REST endpoint and resolves the 401 to get the right endpoint.
        """
        self.endpoint = 'https://api.sumologic.com/api'
        self.response = self.session.get('https://api.sumologic.com/api/v1/collectors')
        endpoint = self.response.url.replace('/v1/collectors', '')
        return endpoint

    def delete(self, method, params=None, headers=None, data=None):
        """
        Defines a Sumo Logic Delete operation
        """
        response = self.session.delete(self.endpoint + method, \
            params=params, headers=headers, data=data)
        if response.status_code != 200:
            response.reason = response.text
        response.raise_for_status()
        return response

    def get(self, method, params=None, headers=None):
        """
        Defines a Sumo Logic Get operation
        """
        response = self.session.get(self.endpoint + method, \
            params=params, headers=headers)
        if response.status_code != 200:
            response.reason = response.text
        response.raise_for_status()
        return response

    def upload(self, method, headers=None, files=None):
        """
        Defines a Sumo Logic Post operation
        """
        response = self.session.post(self.endpoint + method, \
            headers=headers, files=files)
        if response.status_code != 200:
            response.reason = response.text
        response.raise_for_status()
        return response

    def post(self, method, data, headers=None, params=None):
        """
        Defines a Sumo Logic Post operation
        """
        response = self.session.post(self.endpoint + method, \
            data=json.dumps(data), headers=headers, params=params)
        if response.status_code != 200:
            response.reason = response.text
        response.raise_for_status()
        return response

    def put(self, method, data, headers=None, params=None):
        """
        Defines a Sumo Logic Put operation
        """
        response = self.session.put(self.endpoint + method, \
            data=json.dumps(data), headers=headers, params=params)
        if response.status_code != 200:
            response.reason = response.text
        response.raise_for_status()
        return response

    def create_folder(self, folder_name, parent_id, adminmode=False):
        """
        creates a named folder
        """
        headers = {'isAdminMode': str(adminmode)}
        jsonpayload = {
            'name': folder_name,
            'parentId': str(parent_id)
        }

        url = '/v2/content/folders'
        body = self.post(url, jsonpayload, headers=headers).text
        results = json.loads(body)
        return results

    def create_lookup(self, parent_id, jsonfile, adminmode=False):
        """
        creates a lookup file stub
        """
        headers = {'isAdminMode': str(adminmode)}

        with open (jsonfile, "r", encoding='utf8') as jsonobject:
            jsonpayload = json.load(jsonobject)
            jsonpayload['parentFolderId'] = parent_id

        url = '/v1/lookupTables'
        body = self.post(url, jsonpayload, headers=headers).text
        results = json.loads(body)
        return results

    def populate_lookup_merge(self, parent_id, csvfile):
        """
        populates a lookup file stub
        """

        with open(csvfile, "r", encoding='utf8') as fileobject:
            csvpayload = fileobject.read()

        files = { 'file' : ( csvfile, csvpayload ) }
        headers = {'merge': 'true' }

        url = '/v1/lookupTables/' + parent_id + '/upload'
        body = self.upload(url, headers=headers, files=files).text
        results = json.loads(body)
        return results

    def populate_lookup(self, parent_id, csvfile):
        """
        populates a lookup file stub
        """

        with open(csvfile, "r", encoding='utf8') as fileobject:
            csvpayload = fileobject.read()

        files = { 'file' : ( csvfile, csvpayload ) }

        url = '/v1/lookupTables/' + parent_id + '/upload'
        body = self.upload(url, files=files).text
        results = json.loads(body)
        return results

    def get_folder(self, folder_id, adminmode=False):
        """
        queries folders
        """
        headers = {'isAdminMode': str(adminmode).lower()}
        url = '/v2/content/folders/' + str(folder_id)
        body = self.get(url, headers=headers).text
        results = json.loads(body)
        return results

    def get_personal_folder(self):
        """
        get personal base folder
        """
        url = '/v2/content/folders/personal'
        body = self.get(url).text
        results = json.loads(body)
        return results

def lambda_handler(event=None,context=None):
    """
    General Logic should work when called by a lambda or standalone script
    """

    prepare_maplist()

    if VERBOSE > 9:
        print(f'event: {event}')
        print(f'context: {context}')

    for targetkey, targetfile in FILEMAP.items():
        download_mapitem(targetkey, targetfile)

    configure_lookups()

if __name__ == '__main__':
    lambda_handler()
