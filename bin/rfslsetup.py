#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=W0123
# pylint: disable=E0401
# pylint: disable=R0914
# pylint: disable=R0904

"""
Explanation:

This installs a Recorded Future environment into a Sumo Logic environment
Starting with collecting the threat intelligence maps, it populates sources,
creates indices, creates lookups, and uploads content to the organization.

Usage:
    $ python  rfslsetup [ options ]

Style:
    Google Python Style Guide:
    http://google.github.io/styleguide/pyguide.html

    @name           rfslsetup
    @version        6.0.0
    @author-name    Wayne Schmidt
    @author-email   wschmidt@sumologic.com
    @license-name   Apache 2.0
    @license-url    http://www.gnu.org/licenses/gpl.html
"""

__version__ = '6.0.0'
__author__ = "Wayne Schmidt (wschmidt@sumologic.com)"

import argparse
import configparser
import datetime
import time
import json
import os
import sys
import http
import glob
import shutil
import requests
from filesplit.split import Split
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

sys.dont_write_bytecode = 1

PARSER = argparse.ArgumentParser(description="""
Unified Script to create a complete Recorded Future - Sumo Logic Integration
""")

PARSER.add_argument('-c', metavar='<cfgfile>', dest='CONFIG', \
                    default='default', help='specify a config file')
PARSER.add_argument('-s', metavar='<steps>', dest='STEPKEY', \
                    default='complete', help='specify script steps')
PARSER.add_argument("-v", type=int, default=0, metavar='<verbose>', \
                    dest='verbose', help="specify level of verbose output")

ARGS = PARSER.parse_args()

STEPLIST = {}
STEPLIST['ingest'] = [ 'ingest' ]
STEPLIST['download'] = [ 'download' ]
STEPLIST['publish'] = [ 'download', 'publish' ]
STEPLIST['fusion'] = [ 'fusion' ]
STEPLIST['lookups'] = [ 'download', 'lookups' ]
STEPLIST['indices'] = [ 'indices' ]
STEPLIST['content'] = [ 'content' ]
STEPLIST['demo'] = [ 'demo' ]
STEPLIST['complete'] = [ 'ingest', 'download', 'publish', 'fusion', \
                         'lookups', 'indices', 'content' ]
STEPLIST['basic'] = [ 'download', 'lookups']

CURRENTDIR = os.path.abspath(os.path.dirname(__file__))
CMDNAME = os.path.splitext(os.path.basename(__file__))[0]

CFGNAME = f'{CMDNAME}.cfg'

DELAY_TIME = 1

if ARGS.CONFIG == 'default':
    CFGFILE = os.path.abspath(os.path.join(CURRENTDIR, CFGNAME ))
else:
    CFGFILE = os.path.abspath(ARGS.CONFIG)

DEFAULTMAP = []
DEFAULTMAP.append('ip')

MAPLIST = DEFAULTMAP

SRCTAG = 'recordedfuture'

FILEMAP = {}
WEBMAP = {}
IDMAP = {}

URLBASE = 'https://api.recordedfuture.com/v2'
URLTAIL = 'risklist?format=csv%2Fsplunk'

if os.name == 'nt':
    CACHED = os.path.join("C:", "Windows", "Temp" , SRCTAG)
else:
    CACHED = os.path.join("/", "var", "tmp", SRCTAG)

FILELIMIT = 80 * 1024 * 1024

LINELIMIT = 40000

CFGDICT = {}
FUSION = {}
LOOKUPS = {}
PUBLISH = {}

CURRENT = datetime.datetime.now()
DSTAMP = CURRENT.strftime("%Y%m%d")
TSTAMP = CURRENT.strftime("%H%M%S")

def prepare_ingest():
    """
    Create collector and source for Recorded Future Content
    """
    source = SumoApiClient(CFGDICT['SUMOUID'], CFGDICT['SUMOKEY'])

    rfcollector = f'{SRCTAG}_collector'
    rfsource = f'{SRCTAG}_source'

    buildcollector = 'yes'
    buildsource = 'yes'

    collist = source.get_collectors()
    for colitem in collist:
        mycollectorname = colitem['name']
        mycollectorid = colitem['id']
        if mycollectorname == rfcollector:
            buildcollector = 'no'
            rfcollectorid = mycollectorid
        srclist = source.get_sources(mycollectorid)
        for srcitem in srclist:
            mysrcname = srcitem['name']
            _mysrcid = srcitem['id']
            if mysrcname == rfsource:
                buildsource = 'no'
                CFGDICT["SRCURL"] = srcitem['url']

    if buildcollector == 'yes':
        collectorresults = source.create_collector(rfcollector)
        rfcollectorid = collectorresults['id']
    if buildsource == 'yes':
        sourceresults = source.create_source(rfcollectorid, rfsource)
        CFGDICT["SRCURL"] = sourceresults['url']

def prepare_content():
    """
    Create Indices from Map content
    """
    source = SumoApiClient(CFGDICT['SUMOUID'], CFGDICT['SUMOKEY'])
    results = source.get_personal_folder()

    personaldirid = results['id']
    if ARGS.verbose > 4:
        print(f'PersonalFolderId: {results["id"]}')

    contentfile = os.path.abspath(f'{CURRENTDIR}/content/{SRCTAG}_content.json')
    with open(contentfile, 'r', encoding='utf8') as contentobject:
        jsoncontent = json.load(contentobject)

    buildit = 'yes'
    for item in results['children']:
        contentname = item['name']
        contentid = item['id']
        if contentname == f'{SRCTAG}_content':
            if ARGS.verbose > 9:
                print(f'ExistingItem: {contentid} - {contentname}')
            result = source.delete_content_job(contentid)
            jobid = result['id']
            if ARGS.verbose > 9:
                print(f'Delete_Content_Job: {jobid}')
            time.sleep(DELAY_TIME)

    if buildit == 'yes':
        result = source.start_import_job(personaldirid, jsoncontent)
        jobid = result['id']
        status = source.check_import_job_status(personaldirid, jobid)
        if ARGS.verbose > 9:
            print(f'Import_Content_Job: {status["status"]}')
        while status['status'] == 'InProgress':
            status = source.check_import_job_status(personaldirid, jobid)
            if ARGS.verbose > 9:
                print(f'Import_Content_Job: {status["status"]}')
                time.sleep(DELAY_TIME)

def prepare_indices():
    """
    Create Indices from Map content
    """
    source = SumoApiClient(CFGDICT['SUMOUID'], CFGDICT['SUMOKEY'])
    results = source.get_personal_folder()

    personaldirid = results['id']
    if ARGS.verbose > 4:
        print(f'PersonalFolderId: {results["id"]}')

    contentfile = os.path.abspath(f'{CURRENTDIR}/content/{SRCTAG}_indices.json')
    with open(contentfile, 'r', encoding='utf8') as contentobject:
        jsoncontent = json.load(contentobject)

    buildit = 'yes'
    for item in results['children']:
        contentname = item['name']
        contentid = item['id']
        if contentname == f'{SRCTAG}_indices':
            if ARGS.verbose > 9:
                print(f'ExistingItem: {contentid} - {contentname}')
            result = source.delete_content_job(contentid)
            jobid = result['id']
            if ARGS.verbose > 9:
                print(f'Delete_Indices_Job: {jobid}')
            time.sleep(DELAY_TIME)

    if buildit == 'yes':
        result = source.start_import_job(personaldirid, jsoncontent)
        jobid = result['id']
        status = source.check_import_job_status(personaldirid, jobid)
        if ARGS.verbose > 9:
            print(f'Import_Indices_Job: {status["status"]}')
        while status['status'] == 'InProgress':
            status = source.check_import_job_status(personaldirid, jobid)
            if ARGS.verbose > 9:
                print(f'Import_Indices_Job: {status["status"]}')
                time.sleep(DELAY_TIME)

def prepare_lookups():
    """
    Create Lookup Files
    """
    source = SumoApiClient(CFGDICT['SUMOUID'], CFGDICT['SUMOKEY'])
    results = source.get_personal_folder()

    personaldirid = results['id']
    if ARGS.verbose > 4:
        print(f'PersonalFolderId: {results["id"]}')

    buildit = 'yes'
    lookupdirname = f'{SRCTAG}_lookups'

    for item in results['children']:
        contentname = item['name']
        contentid = item['id']
        if contentname == lookupdirname:
            if ARGS.verbose > 9:
                print(f'ExistingItem: {contentid} - {contentname}')
            result = source.delete_content_job(contentid)
            jobid = result['id']
            if ARGS.verbose > 9:
                print(f'Delete_Lookup_Job: {jobid}')
            time.sleep(DELAY_TIME)

    if buildit == 'yes':
        lookupdirid = source.create_folder(lookupdirname,personaldirid)["id"]
    if ARGS.verbose > 4:
        print(f'LookupDirId: {lookupdirid}')
        print(f'LookupDirName: {lookupdirname}')

    create_lookup_stubs(source, lookupdirid)
    upload_lookup_data(source)

def create_lookup_stubs(source, lookupdirid):
    """
    Create Lookup File Stubs
    """
    for rfcsvmap in glob.glob(glob.escape(CFGDICT['CACHED']) + "/*.default.csv"):
        jsonname = os.path.basename(rfcsvmap).replace(".default.csv", ".json")
        jsonfile = os.path.join(CURRENTDIR, "json", jsonname)
        if ARGS.verbose > 4:
            print(f'Creating_Lookup_Using: {jsonfile}')
        results = source.create_lookup(lookupdirid, jsonfile )
        lookupfileid = results["id"]
        lookupfilename = results["name"]
        LOOKUPS[lookupfilename] = lookupfileid

def upload_lookup_data(source):
    """
    Upload the lookup file data
    """
    source.session.headers = None

    for lookupkey, lookupfileid in LOOKUPS.items():
        targetfile = f'{CFGDICT["CACHED"]}/{lookupkey}.default.csv'
        filesize = os.path.getsize(targetfile)
        if filesize <= FILELIMIT:
            if ARGS.verbose > 2:
                print(f'Lookup_File_Id: {lookupfileid} Uploading_Source_File: {targetfile}')
            _result = source.populate_lookup(lookupfileid, targetfile)
        else:
            split_dir = os.path.splitext(targetfile)[0]
            os.makedirs(split_dir, exist_ok=True)
            filesplit = Split(targetfile, split_dir )
            filesplit.bylinecount(linecount=LINELIMIT, includeheader=True)
            for csv_file in glob.glob(glob.escape(split_dir) + "/*.csv"):
                if ARGS.verbose > 2:
                    print(f'Lookup_File_Id: {lookupfileid} Uploading_Source_File: {csv_file}')
                _result = source.populate_lookup_merge(lookupfileid, csv_file)

def prepare_fusion():
    """
    Download Main Maps
    """
    session = requests.Session()

    fusionurl = 'https://api.recordedfuture.com/v2/fusion/files/?path='

    for fkey, fvalue in FUSION.items():
        target_http = f'{fusionurl}{fvalue}'
        target_name = f'{"fusion"}.{fkey}'
        target_file = os.path.abspath(os.path.join(CFGDICT['CACHED'],target_name))

        if ARGS.verbose > 3:
            print(f'Downloading: {target_http}')

        headers = {'X-RFToken': CFGDICT['MAPKEY'], 'X-RF-User-Agent' : 'SumoLogic+v1.0'}
        body = session.get(target_http, headers=headers)
        getresults = body.text

        if ARGS.verbose > 3:
            print(f'Persisting: {target_file}')

        with open(target_file, mode="w", encoding='utf8') as outputfile:
            outputfile.write(getresults)

        headers = {'Content-Type':'txt/csv'}

        with open(target_file, mode='r', encoding='utf8') as outputfile:
            fusion_payload = (outputfile.read().encode('utf-8'))

        filebase = os.path.splitext(os.path.basename(target_file))[0]
        fusion_file_category = f'recordedfuture/fusion/files/{filebase}'

        if ARGS.verbose > 3:
            print(f'publishing: {fusion_file_category}')

        headers['X-Sumo-Category'] = fusion_file_category
        postresponse = session.post(CFGDICT['SRCURL'], fusion_payload, headers=headers).status_code

        if ARGS.verbose > 7:
            print(f'source_category: {str(fusion_file_category)}')
            print(f'upload_response: {str(postresponse)}')

def prepare_download():
    """
    Download Recorded Future Maps
    """
    session = requests.Session()

    os.makedirs(CFGDICT['CACHED'], exist_ok=True)
    os.chdir(CFGDICT['CACHED'])
    for csvmap in glob.glob("*.csv"):
        removecsv = os.path.abspath(csvmap)
        if ARGS.verbose > 7:
            print(f'Scrubbing_File: {removecsv}')
        os.remove(removecsv)

    os.chdir(CFGDICT['CACHED'])
    for csvdir in glob.glob("*.default"):
        removedir = os.path.abspath(csvdir)
        if ARGS.verbose > 7:
            print(f'Scrubbing_Directories: {removedir}')
        shutil.rmtree(removedir)

    for map_token in CFGDICT['MAPLIST'].split(","):
        if "/" in map_token:
            map_name, list_name = map_token.split ('/')
        else:
            map_name = map_token
            list_name = 'default'

        httppath = f'{URLBASE}/{map_name}/{URLTAIL}/{list_name}'
        csv_name = f'{map_name}.{list_name}.{"csv"}'
        csv_file = os.path.join(CFGDICT['CACHED'], csv_name)
        category = f'{SRCTAG}/{"map"}/{map_name}/{list_name}'

        if list_name == 'default':
            category = f'{SRCTAG}/{"map"}/{map_name}'

        PUBLISH[csv_file] = category

        headers = {'X-RFToken': CFGDICT['MAPKEY'], 'X-RF-User-Agent' : 'SumoLogic+v1.0'}
        if ARGS.verbose > 4:
            print(f'Retrieving: {httppath}')
        body = session.get(httppath, headers=headers)
        getresults = body.text

        if ARGS.verbose > 4:
            print(f'Persisting: {csv_file}')
        with open(csv_file, mode="w", encoding='utf8') as outputfile:
            outputfile.write(getresults)

def prepare_publish():
    """
    Publish the results
    """
    session = requests.Session()

    for csv_file, category in PUBLISH.items():
        with open(csv_file, mode='r', encoding='utf8') as inputfile:
            rf_map_payload = (inputfile.read().encode('utf-8'))

        headers = {'Content-Type':'txt/csv'}
        headers['X-Sumo-Category'] = category
        if ARGS.verbose > 4:
            print(f'Publishing: {category}')
        postresponse = session.post(CFGDICT['SRCURL'], rf_map_payload, headers=headers).status_code

        if ARGS.verbose > 8:
            print(f'Web_Status: {postresponse}')

def initialize_variables():
    """
    Define and read configuration file, validating config file entries
    """
    if os.path.exists(CFGFILE):
        config = configparser.RawConfigParser()
        config.optionxform = str
        config.read(CFGFILE)
    else:
        print(f'ConfigFile: {CFGFILE} Missing! Exiting.')
        sys.exit()

    if ARGS.verbose > 8:
        print(dict(config.items('Default')))

    config.read(CFGFILE)

    if config.has_option("Default", "CACHED"):
        CFGDICT['CACHED'] = config.get("Default", "CACHED")
    else:
        CFGDICT['CACHED'] = CACHED

    if config.has_option("Default", "SUMOUID"):
        CFGDICT['SUMOUID'] = config.get("Default", "SUMOUID")

    if config.has_option("Default", "SUMOKEY"):
        CFGDICT['SUMOKEY'] = config.get("Default", "SUMOKEY")

    if config.has_option("Default", "SUMONAME"):
        CFGDICT['SUMONAME'] = config.get("Default", "SUMONAME")

    if config.has_option("Default", "MAPKEY"):
        CFGDICT['MAPKEY'] = config.get("Default", "MAPKEY")

    if config.has_option("Default", "MAPLIST"):
        CFGDICT['MAPLIST'] = config.get("Default", "MAPLIST")

    if config.has_option("Default", "SRCURL"):
        CFGDICT['SRCURL'] = config.get("Default", "SRCURL")

    for fusionkey in dict(config.items('FusionFiles')):
        fusionvalue = config.get("FusionFiles", fusionkey)
        FUSION[fusionkey] = fusionvalue

    return CFGDICT

class SumoApiClient():
    """
    General Sumo Logic API Client Class
    """

    def __init__(self, access_id, access_key, endpoint=None, cookie_file='cookies.txt'):
        """
        Initializes the Sumo Logic object
        """

        self.retry_strategy = Retry(
            total=10,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        self.adapter = HTTPAdapter(max_retries=self.retry_strategy)

        self.session = requests.Session()

        self.session.mount("https://", self.adapter)
        self.session.mount("http://", self.adapter)

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

    def delete_collector(self, item_id, adminmode=False):
        """
        delete a collector
        """
        headers = {'isAdminMode': str(adminmode).lower()}
        url = '/v1/collectors/' + str(item_id) + '/delete'
        body = self.delete(url, headers=headers).text
        results = json.loads(body)
        return results

    def delete_content_job(self, item_id, adminmode=False):
        """
        deletes content
        """
        headers = {'isAdminMode': str(adminmode).lower()}
        url = '/v2/content/' + str(item_id) + '/delete'
        body = self.delete(url, headers=headers).text
        results = json.loads(body)
        return results

    def delete_content_job_status(self, item_id, job_id, adminmode=False):
        """
        checks on the delete job status
        """
        headers = {'isAdminMode': str(adminmode).lower()}
        url = '/v2/content/' + str(item_id) + '/delete/' + str(job_id) + '/status'
        body = self.get(url, headers=headers)
        results = json.loads(body)
        return results

    def start_export_job(self, myself):
        """
        This starts an export job by passing in the content ID
        """
        url = "/v2/content/" + str(myself) + "/export"
        body = self.post(url, data=str(myself)).text
        results = json.loads(body)
        return results

    def check_export_job_status(self, myself,jobid):
        """
        This starts an export job by passing in the content ID
        """
        url = "/v2/content/" + str(myself) + "/export/" + str(jobid) + "/status"
        time.sleep(DELAY_TIME)
        body = self.get(url).text
        results = json.loads(body)
        return results

    def check_export_job_result(self, myself,jobid):
        """
        This starts an export job by passing in the content ID
        """
        url = "/v2/content/" + str(myself) + "/export/" + str(jobid) + "/result"
        time.sleep(DELAY_TIME)
        body = self.get(url).text
        results = json.loads(body)
        return results

    def start_import_job(self, folderid, content, adminmode=False, overwrite=False):
        """
        This starts an import job by passing in the content ID and content
        """
        headers = {'isAdminMode': str(adminmode).lower()}
        params = {'overwrite': str(overwrite).lower()}
        url = "/v2/content/folders/" + str(folderid) + "/import"
        time.sleep(DELAY_TIME)
        body = self.post(url, content, headers=headers, params=params).text
        results = json.loads(body)
        return results

    def check_import_job_status(self, folderid, jobid, adminmode=False):
        """
        This checks on the status of an import content job
        """
        headers = {'isAdminMode': str(adminmode).lower()}
        url = "/v2/content/folders/" + str(folderid) + "/import/" + str(jobid) + "/status"
        time.sleep(DELAY_TIME)
        body = self.get(url, headers=headers).text
        results = json.loads(body)
        return results

    def get_collectors(self):
        """
        Using an HTTP client, this uses a GET to retrieve all collector information.
        """
        url = "/v1/collectors"
        body = self.get(url).text
        results = json.loads(body)['collectors']
        return results

    def get_collector(self, myselfid):
        """
        Using an HTTP client, this uses a GET to retrieve single collector information.
        """
        url = "/v1/collectors/" + str(myselfid)
        body = self.get(url).text
        results = json.loads(body)['collector']
        return results

    def create_collector(self, collector_name):
        """
        Using an HTTP client, this creates a collector
        """
        _object_type = 'collector'
        jsonpayload = {
            "api.version":"v1",
            "collector":{
                "name": collector_name,
                "timeZone":"Etc/UTC",
                "fields":{
                },
                "collectorType":"Hosted",
                "collectorVersion":""
            }
        }
        url = "/v1/collectors"
        body = self.post(url, jsonpayload).text
        results = json.loads(body)['collector']
        return results

    def get_sources(self, parentid):
        """
        Using an HTTP client, this uses a GET to retrieve for all sources for a given collector
        """
        url = "/v1/collectors/" + str(parentid) + '/sources'
        body = self.get(url).text
        results = json.loads(body)['sources']
        return results

    def get_source(self, parentid, myselfid):
        """
        Using an HTTP client, this uses a GET to retrieve a given source for a given collector
        """
        url = "/v1/collectors/" + str(parentid) + '/sources/' + str(myselfid)
        body = self.get(url).text
        results = json.loads(body)['sources']
        return results

    def create_source(self, parentid, source_name):
        """
        Using an HTTP client, this creates a source for a collector
        """
        _object_type = 'source'
        jsonpayload = {
            "api.version": "v1",
            "source":{
                "name": f'{source_name}' ,
                "description": f'hosted source for {source_name}',
                "category": f'{source_name}_category',
                "encoding":"UTF-8",
                "sourceType":"HTTP",
                "automaticDateParsing": True,
                "multilineProcessingEnabled": True,
                "useAutolineMatching": True,
                "forceTimeZone": False,
                "messagePerRequest": False
            }
        }
        url = "/v1/collectors/" + str(parentid) + "/sources"
        body = self.post(url, jsonpayload).text
        results = json.loads(body)['source']
        return results

def lambda_handler(event=None,context=None):
    """
    General Logic should work when called by a lambda or standalone script
    """

    if ARGS.verbose > 4:
        print(f'ConfigFile: {CFGFILE}')

    initialize_variables()

    os.makedirs(CFGDICT['CACHED'], exist_ok=True)

    if ARGS.verbose > 9:
        print(f'Script_Event: {event}')
        print(f'Script_Context: {context}')

    if ARGS.verbose > 4:
        print(f'STEPLIST: {STEPLIST[ARGS.STEPKEY]}')

    for step_name in STEPLIST[ARGS.STEPKEY]:
        if ARGS.verbose > 2:
            print(f'Process_Step_Name: {step_name}')
        eval( 'prepare_' + step_name + "()")

if __name__ == '__main__':
    lambda_handler()
