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
    $ python rflslookups.py -c <cfgfile> [options]

Style:
    Google Python Style Guide:
    http://google.github.io/styleguide/pyguide.html

    @license-name   Apache
    @license-url    https://www.apache.org/licenses/LICENSE-2.0
"""

__version__ = '7.0.0'
__author__ = "Patrick Kinsella (patrick.kinsella@recordedfuture.com)"

import argparse
import configparser
import os
import csv
import json
import http
import requests
from io import StringIO
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

PARSER = argparse.ArgumentParser(description="Download and Publish Recorded Future Data into Sumo Logic Lookup Files")
PARSER.add_argument('-c', metavar='<cfgfile>', dest='cfgfile', \
                    required=True, help='specify a config file')
PARSER.add_argument("-v", type=int, default=0, metavar='<verbose>', \
                    dest='verbose', help="specify level of verbose output")
ARGS = PARSER.parse_args()

MAX_BYTES_PER_CHUNK = 90000000

class RFSLLookups:
    def __init__(self, cfgfile):
        if os.path.exists(cfgfile):
            config = configparser.RawConfigParser()
            config.optionxform = str
            config.read(cfgfile)
        else:
            raise ValueError(f"Config file '{cfgfile}' not found!")
        if ARGS.verbose > 8:
            print('Config:')
            for key, val in dict(config.items('Default')).items():
                print(f'    {key} = {val}')
        self.ioc_types = ['domain', 'hash', 'ip', 'url', 'vulnerability']
        self.sumologic_access_id = config.get("Default", "sumologic_access_id")
        self.sumologic_access_key = config.get("Default", "sumologic_access_key")
        self.recordedfuture_access_key = config.get("Default", "recorded_future_access_key")
        self.source_url = config.get("Default", "source-url")
        self.lookup_ids = {}
        for ioc_type in self.ioc_types:
            self.lookup_ids[ioc_type] = config.get("Default", f'lookuptable-rf-{ioc_type}-id')
        self.sumo_api_client = SumoApiClient(self.sumologic_access_id, self.sumologic_access_key)
        self.session = requests.Session()
        self.headers = {
                'X-RFToken': self.recordedfuture_access_key,
                'User-Agent' : 'SumoLogic/1.0'
        }
        self.risklists = {}

    def recordedfuture_download(self):
        """
        Download Recorded Future Maps
        """
        for ioc_type in self.ioc_types:
            url = f'https://api.recordedfuture.com/v2/{ioc_type}/risklist'
            params = {'format': 'csv/splunk',
                      'list': 'default'}
            if ARGS.verbose > 4:
                print(f'Retrieving: {url}')

            body = self.session.get(url, headers=self.headers, params=params)
            try:
                body.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print(f'{ioc_type} risklist not available: {err}')
                continue
            self.risklists[ioc_type] = body.text

            if ARGS.verbose > 4:
                print(f'Retrieved: {url}')


    def split_csv(self, csv_file, ioc_type):
        """
        Split CSV file into chunks
        """
        reader = csv.DictReader(csv_file)
        rows = list(reader)
        output_buffer = StringIO()
        writer = csv.DictWriter(output_buffer, fieldnames=reader.fieldnames)
        i = 0
        chunks = []
        while i < len(rows):
            total_bytes = writer.writeheader()
            while total_bytes < MAX_BYTES_PER_CHUNK and i < len(rows):
                row = rows[i]
                i += 1
                total_bytes += writer.writerow(row)
            output_buffer.seek(0)
            chunks.append(output_buffer.read())
            output_buffer.seek(0)
            output_buffer.truncate()

        if ARGS.verbose > 4:
            chunks_term = 'chunk' if len(chunks) == 1 else 'chunks'
            print(f'Split {ioc_type} risklist into {len(chunks)} {chunks_term}')
        return chunks

    def sumologic_populate(self):
        """
        Create collector and source for Recorded Future Content
        """
        for ioc_type in self.risklists.keys():
            if ARGS.verbose > 4:
                print(f'Truncating {ioc_type} lookup table')
            self.sumo_api_client.truncate_lookup_table(self.lookup_ids[ioc_type])
            lookupfileid = self.lookup_ids[ioc_type]
            risklist_as_file = StringIO(self.risklists[ioc_type])
            chunks = self.split_csv(risklist_as_file, ioc_type)
            risklist_as_file.close()
            for idx, chunk in enumerate(chunks):
                if ARGS.verbose > 4:
                    print(f'Uploading {ioc_type} risklist chunk {idx+1} of {len(chunks)}')
                self.sumo_api_client.upload_lookup_csv(lookupfileid, chunk, merge=True)

###########################################################

class SumoApiClient:
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
        results.raise_for_status()
        if results.ok and ARGS.verbose > 4:
            print(f'Truncate success, job ID: {results.json()["id"]}')
        return results.json()

    def upload_lookup_csv(self, table_id, file_content, merge=False):
        """
        populates a lookup file from a CSV file
        """
        params = {'merge': merge}
        files = {'file': file_content}
        headers = {'Accept': 'application/json'}
        results = requests.post(self.endpoint + f'/v1/lookupTables/{table_id}/upload', files=files, params=params,
                auth=(self.session.auth[0], self.session.auth[1]), headers=headers)
        results.raise_for_status()
        if results.ok and ARGS.verbose > 4:
            print(f'Upload success, job ID: {results.json()["id"]}')
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
    controller = RFSLLookups(ARGS.cfgfile)
    controller.recordedfuture_download()
    controller.sumologic_populate()

if __name__ == '__main__':
    lambda_handler()
