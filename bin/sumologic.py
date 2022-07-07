#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=W0123
# pylint: disable=E0401
# pylint: disable=R0914
# pylint: disable=R0904

"""
    @name           sumologic.py
    @version        6.0.0
    @author-name    Wayne Schmidt
    @author-email   wschmidt@sumologic.com
    @license-name   Apache 2.0
    @license-url    http://www.gnu.org/licenses/gpl.html
"""

__version__ = '6.0.0'
__author__ = "Wayne Schmidt (wschmidt@sumologic.com)"

import time
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

##########
##########        self.session.headers = None

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
        results = self.post_file('/v1/lookupTables/%s/upload' % table_id, params)
        return results.json()

    def upload_lookup_csv_status(self, jobid):
        """
        checks on the status of a lookup file upload job
        """
        results = self.get('/v1/lookupTables/jobs/%s/status' % jobid)
        return results.json()

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
        time.sleep(DELAY_TIME)
        body = self.get(url, headers=headers).text
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
