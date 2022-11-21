#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=W0123
# pylint: disable=E0401
# pylint: disable=R0914
# pylint: disable=R0904
# pylint: disable=R1732
# pylint: disable=W3101

"""
    @name           sumologic.py
    @version        6.6.0
    @author-name    Wayne Schmidt
    @author-email   wayne.kirk.schmidt@gmail.com
    @license-name   Apache
    @license-url    https://www.apache.org/licenses/LICENSE-2.0
"""

__version__ = '6.6.0'
__author__ = "Wayne Schmidt (wayne.kirk.schmidt@gmail.com)"

import json
import sys
import http
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

DELAY_TIME = 1

sys.dont_write_bytecode = True

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
