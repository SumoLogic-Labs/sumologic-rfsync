#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=R0912
# pylint: disable=C0413
# pylint: disable=W0123
# pylint: disable=E0401
# pylint: disable=R0914
# pylint: disable=R0904
# pylint: disable=R1732
# pylint: disable=W3101

"""
Explanation:

    This downloads Recorded Future Data and publishes this into Sumo Logic lookup files.
    The initial Sumo Logic environment setup is done with Terraform.

Usage:
    $ python  rflslookups [ options ]

Style:
    Google Python Style Guide:
    http://google.github.io/styleguide/pyguide.html

    @name           rflslookups
    @version        6.6.0
    @author-name    Wayne Schmidt
    @author-email   wayne.kirk.schmidt@gmail.com
    @license-name   Apache
    @license-url    https://www.apache.org/licenses/LICENSE-2.0
"""

__version__ = '6.6.0'
__author__ = "Wayne Schmidt (wayne.kirk.schmidt@gmail.com)"

import argparse
import configparser
import datetime
import time
import os
import sys
import json
import glob
import shutil
import http
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from filesplit.split import Split

sys.dont_write_bytecode = True

### import sumologic

PARSER = argparse.ArgumentParser(description="""
Download and Publish Recorded Future Data into Sumo Logic Lookup Files
""")

PARSER.add_argument('-c', metavar='<cfgfile>', dest='CONFIG', \
                    default='default', help='specify a config file')
PARSER.add_argument("-v", type=int, default=0, metavar='<verbose>', \
                    dest='verbose', help="specify level of verbose output")

ARGS = PARSER.parse_args()

CURRENTDIR = os.path.abspath(os.path.dirname(__file__))
CMDNAME = os.path.splitext(os.path.basename(__file__))[0]

CFGNAME = f'{CMDNAME}.cfg'

DELAY_TIME = 9

FILELIMIT = 90 * 1024 * 1024

LINELIMIT = 60000

if ARGS.CONFIG == 'default':
    CFGFILE = os.path.abspath(os.path.join(CURRENTDIR, CFGNAME ))
else:
    CFGFILE = os.path.abspath(ARGS.CONFIG)

DEFAULTMAP = ('domain', 'hash', 'ip', 'url', 'vulnerability')

SRCTAG = 'recordedfuture'

URLBASE = 'https://api.recordedfuture.com/v2'
URLTAIL = 'risklist?format=csv%2Fsplunk'

if os.name == 'nt':
    CACHED = os.path.join("C:", "Windows", "Temp" , SRCTAG)
else:
    CACHED = os.path.join("/", "var", "tmp", SRCTAG)

PUBLISH = {}
CFGDICT = {}

CURRENT = datetime.datetime.now()
DSTAMP = CURRENT.strftime("%Y%m%d")
TSTAMP = CURRENT.strftime("%H%M%S")

PURPOSE = 'lookups'

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

    if config.has_option("Default", "recorded_future_cache_dir"):
        CFGDICT['recorded_future_cache_dir'] = \
           f'{config.get("Default", "recorded_future_cache_dir")}/{PURPOSE}'
    else:
        CFGDICT['recorded_future_cache_dir'] = \
           f'{CACHED}/{PURPOSE}'

    if config.has_option("Default", "recorded_future_map_list"):
        CFGDICT['recorded_future_map_list'] = \
            config.get("Default", "recorded_future_map_list").split(',')
    else:
        CFGDICT['recorded_future_map_list'] = DEFAULTMAP

    if config.has_option("Default", "sumologic_access_id"):
        CFGDICT['sumologic_access_id'] = config.get("Default", "sumologic_access_id")

    if config.has_option("Default", "sumologic_access_key"):
        CFGDICT['sumologic_access_key'] = config.get("Default", "sumologic_access_key")

    if config.has_option("Default", "recorded_future_access_key"):
        CFGDICT['recorded_future_access_key'] = config.get("Default", "recorded_future_access_key")

    if config.has_option("Default", "source-url"):
        CFGDICT['source-url'] = config.get("Default", "source-url")

    for defaultmap in DEFAULTMAP:
        cfgkey = f'lookuptable-rf-{defaultmap}-id'
        if config.has_option("Default", cfgkey):
            CFGDICT[cfgkey] = config.get("Default", cfgkey)

    return CFGDICT

def recordedfuture_download():
    """
    Download Recorded Future Maps
    """
    session = requests.Session()

    if os.path.exists(CFGDICT['recorded_future_cache_dir']):
        if ARGS.verbose > 7:
            print(f'Scrubbing_Cache_Directory: {CFGDICT["recorded_future_cache_dir"]}')
        shutil.rmtree(CFGDICT['recorded_future_cache_dir'])

    os.makedirs(CFGDICT['recorded_future_cache_dir'], exist_ok=True)

    for map_token in CFGDICT['recorded_future_map_list']:
        if "/" in map_token:
            map_name, list_name = map_token.split ('/')
        else:
            map_name = map_token
            list_name = 'default'

        httppath = f'{URLBASE}/{map_name}/{URLTAIL}/{list_name}'
        csv_name = f'{map_name}.{list_name}.{"csv"}'
        csv_file = os.path.join(CFGDICT['recorded_future_cache_dir'], csv_name)
        category = f'{SRCTAG}/{"map"}/{map_name}/{list_name}'

        if list_name == 'default':
            category = f'{SRCTAG}/{"map"}/{map_name}'

        PUBLISH[csv_file] = category

        headers = {
            'X-RFToken': CFGDICT['recorded_future_access_key'],
            'X-RF-User-Agent' : 'SumoLogic+v1.0'
        }
        if ARGS.verbose > 4:
            print(f'Retrieving: {httppath}')
        body = session.get(httppath, headers=headers)
        getresults = body.text

        if ARGS.verbose > 4:
            print(f'Persisting: {csv_file}')
        with open(csv_file, mode="w", encoding='utf8') as outputfile:
            outputfile.write(getresults)

def sumologic_populate():
    """
    Create collector and source for Recorded Future Content
    """
    source = sumologic.SumoApiClient(CFGDICT['sumologic_access_id'], \
        CFGDICT['sumologic_access_key'])

    for map_token in CFGDICT['recorded_future_map_list']:

        targetfile = f'{CFGDICT["recorded_future_cache_dir"]}/{map_token}.default.csv'
        filesize = os.path.getsize(targetfile)

        lookupfileid = CFGDICT[f'lookuptable-rf-{map_token}-id']
        result = source.truncate_lookup_table(lookupfileid)
        if ARGS.verbose > 20:
            print(f'Lookup_File_Id: {lookupfileid}\nTruncate_Results: {result}')

        if filesize <= FILELIMIT:
            if ARGS.verbose > 2:
                print(f'Lookup_File_Id: {lookupfileid} Uploading_Source_File: {targetfile}')
            source = sumologic.SumoApiClient(CFGDICT['sumologic_access_id'], \
                CFGDICT['sumologic_access_key'])
            result = source.upload_lookup_csv(lookupfileid, targetfile, merge='true')
            jobid = result['id']
            if ARGS.verbose > 9:
                print(f'Import_Lookup_Job: {jobid}')
            time.sleep(DELAY_TIME)
            status = source.upload_lookup_csv_status(jobid)
            if ARGS.verbose > 9:
                print(f'Import_Lookup_Job: {status["status"]}')
            while ( status['status'] != 'Success' and status['status'] != 'PartialSuccess' ):
                status = source.upload_lookup_csv_status(jobid)
                if ARGS.verbose > 9:
                    print(f'Import_Lookup_Job: {status["status"]}')
                if ARGS.verbose > 29:
                    print(f'Import_Lookup_Job_Details:\n{status}')
                time.sleep(DELAY_TIME)
        else:
            split_dir = os.path.splitext(targetfile)[0]
            os.makedirs(split_dir, exist_ok=True)
            filesplit = Split(targetfile, split_dir )
            filesplit.bylinecount(linecount=LINELIMIT, includeheader=True)
            for csv_file in sorted(glob.glob(glob.escape(split_dir) + "/*.csv")):
                if ARGS.verbose > 2:
                    print(f'Lookup_File_Id: {lookupfileid} Uploading_Source_File: {csv_file}')
                source = sumologic.SumoApiClient(CFGDICT['sumologic_access_id'], \
                    CFGDICT['sumologic_access_key'])
                result = source.upload_lookup_csv(lookupfileid, csv_file, merge='true')
                jobid = result['id']
                if ARGS.verbose > 9:
                    print(f'Import_Lookup_Job: {jobid}')
                time.sleep(DELAY_TIME)
                status = source.upload_lookup_csv_status(jobid)
                if ARGS.verbose > 9:
                    print(f'Import_Lookup_Job: {status["status"]}')
                while status['status'] != 'Success':
                    status = source.upload_lookup_csv_status(jobid)
                    if ARGS.verbose > 9:
                        print(f'Import_Lookup_Job: {status["status"]}')
                    if ARGS.verbose > 29:
                        print(f'Import_Lookup_Job_Details:\n{status}')
                    time.sleep(DELAY_TIME)

###########################################################

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

    def post(self, method, data=None, headers=None, params=None):
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

    def truncate_lookup_table(self, table_id, adminmode=False):
        """
        truncate a specific lookup table
        """
        headers = {'isAdminMode': str(adminmode)}
        results = self.post(f'/v1/lookupTables/{table_id}/truncate', headers=headers)
        return results.json()

    def post_file(self, method, params, headers=None):
        """
        implements a post file
        """
        post_params = {'merge': params['merge']}
        file_data = open(params['file_name'], 'rb').read()
        files = {'file': (params['file_name'], file_data)}
        results = requests.post(self.endpoint + method, files=files, params=post_params,
                auth=(self.session.auth[0], self.session.auth[1]), headers=headers)
        if 400 <= results.status_code < 600:
            results.reason = results.text
        results.raise_for_status()
        return results

    def upload_lookup_csv(self, table_id, file_name, merge='false'):
        """
        populates a lookup file from a CSV file
        """
        params={'file_name': file_name, 'merge': merge }
        results = self.post_file(f'/v1/lookupTables/{table_id}/upload', params)
        return results.json()

    def upload_lookup_csv_status(self, jobid):
        """
        checks on the status of a lookup file upload job
        """
        results = self.get(f'/v1/lookupTables/jobs/{jobid}/status')
        return results.json()

###########################################################

def lambda_handler(event=None,context=None):
    """
    Functionality will work either being called by a lambda or standalone script
    """

    if ARGS.verbose > 4:
        print(f'ConfigFile: {CFGFILE}')

    initialize_variables()

    if ARGS.verbose > 9:
        print(f'Script_Event: {event}')
        print(f'Script_Context: {context}')

    recordedfuture_download()
    sumologic_populate()

if __name__ == '__main__':
    lambda_handler()
