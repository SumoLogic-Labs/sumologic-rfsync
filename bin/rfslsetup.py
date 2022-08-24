#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=W0123
# pylint: disable=E0401
# pylint: disable=R0914
# pylint: disable=R0904
# pylint: disable=C0413

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
import glob
import shutil
import requests
from filesplit.split import Split

sys.dont_write_bytecode = True

import sumologic

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
STEPLIST['publish'] = [ 'download', 'ingest', 'publish' ]
STEPLIST['fusion'] = [ 'fusion' ]
STEPLIST['lookups'] = [ 'download', 'ingest', 'lookups' ]
STEPLIST['indices'] = [ 'indices' ]
STEPLIST['content'] = [ 'content' ]
STEPLIST['demo'] = [ 'demo' ]
STEPLIST['complete'] = [ 'ingest', 'download', 'publish', 'fusion', \
                         'lookups', 'indices', 'content' ]
STEPLIST['basic'] = [ 'download', 'lookups']

CURRENTDIR = os.path.abspath(os.path.dirname(__file__))
CMDNAME = os.path.splitext(os.path.basename(__file__))[0]

CFGNAME = f'{CMDNAME}.cfg'

DELAY_TIME = 9

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

FILELIMIT = 90 * 1024 * 1024

LINELIMIT = 60000

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
    source = sumologic.SumoApiClient(CFGDICT['SUMOUID'], CFGDICT['SUMOKEY'])

    rfcollector = f'{SRCTAG}_collector'
    rfsource = f'{SRCTAG}_source'

    buildcollector = 'yes'
    buildsource = 'yes'

    collist = source.get_collectors()
    if ARGS.verbose > 9:
        print(f'collector_list: {collist}')
    for colitem in collist:
        if colitem['name'] is not None:
            mycollectorname = colitem['name']
            mycollectorid = colitem['id']
            if mycollectorname == rfcollector:
                buildcollector = 'no'
                rfcollectorid = mycollectorid
        srclist = source.get_sources(mycollectorid)
        if ARGS.verbose > 9:
            print(f'colitem: {mycollectorname} source_list: {srclist}')
        for srcitem in srclist:
            if srcitem['name'] is not None:
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

    if ARGS.verbose > 9:
        print(f'{CFGDICT["SRCURL"]}')

def prepare_content():
    """
    Create Indices from Map content
    """
    source = sumologic.SumoApiClient(CFGDICT['SUMOUID'], CFGDICT['SUMOKEY'])
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
            status = source.delete_content_job_status(contentid, jobid)
            if ARGS.verbose > 9:
                print(f'Delete_Content_Job: {status["status"]}')
            while status['status'] == 'InProgress':
                status = source.delete_content_job_status(contentid, jobid)
                if ARGS.verbose > 9:
                    print(f'Delete_Content_Job: {status["status"]}')
                    time.sleep(DELAY_TIME)

    if buildit == 'yes':
        result = source.start_import_job(personaldirid, jsoncontent)
        jobid = result['id']
        print(f'Import_Content_Job: {jobid}')
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
    source = sumologic.SumoApiClient(CFGDICT['SUMOUID'], CFGDICT['SUMOKEY'])
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
            status = source.delete_content_job_status(contentid, jobid)
            if ARGS.verbose > 9:
                print(f'Delete_Indices_Job: {status["status"]}')
            while status['status'] == 'InProgress':
                status = source.delete_content_job_status(contentid, jobid)
                if ARGS.verbose > 9:
                    print(f'Delete_Indices_Job: {status["status"]}')
                    time.sleep(DELAY_TIME)

    if buildit == 'yes':
        result = source.start_import_job(personaldirid, jsoncontent)
        jobid = result['id']
        print(f'Import_Indices_Job: {jobid}')
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
    source = sumologic.SumoApiClient(CFGDICT['SUMOUID'], CFGDICT['SUMOKEY'])
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
            status = source.delete_content_job_status(contentid, jobid)
            if ARGS.verbose > 9:
                print(f'Delete_Lookup_Job: {status["status"]}')
            while status['status'] == 'InProgress':
                status = source.delete_content_job_status(contentid, jobid)
                if ARGS.verbose > 9:
                    print(f'Delete_Lookup_Job: {status["status"]}')
                    time.sleep(DELAY_TIME)

    if buildit == 'yes':
        lookupdirid = source.create_folder(lookupdirname,personaldirid)["id"]
    if ARGS.verbose > 4:
        print(f'LookupDirId: {lookupdirid}')
        print(f'LookupDirName: {lookupdirname}')

    create_lookup_stubs(source, lookupdirid)

    upload_lookup_data()

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

def upload_lookup_data():
    """
    Upload the lookup file data
    """

    for lookupkey, lookupfileid in LOOKUPS.items():
        targetfile = f'{CFGDICT["CACHED"]}/{lookupkey}.default.csv'
        filesize = os.path.getsize(targetfile)
        if filesize <= FILELIMIT:
            if ARGS.verbose > 2:
                print(f'Lookup_File_Id: {lookupfileid} Uploading_Source_File: {targetfile}')
            source = sumologic.SumoApiClient(CFGDICT['SUMOUID'], CFGDICT['SUMOKEY'])
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
                source = sumologic.SumoApiClient(CFGDICT['SUMOUID'], CFGDICT['SUMOKEY'])
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
