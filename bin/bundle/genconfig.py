#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Explanation:

This will walk the client through a set of questions to create a config file.

Usage:
    $ python  genconfig [ options ]

Style:
    Google Python Style Guide:
    http://google.github.io/styleguide/pyguide.html

    @name           genconfig
    @version        1.9.0
    @author-name    Wayne Schmidt
    @author-email   wschmidt@sumologic.com
    @license-name   GNU GPL
    @license-url    http://www.gnu.org/licenses/gpl.html
"""

__version__ = '1.9.0'
__author__ = "Wayne Schmidt (wschmidt@sumologic.com)"

import argparse
import configparser
import datetime
import os
import sys
import urllib.request

sys.dont_write_bytecode = 1

PARSER = argparse.ArgumentParser(description="""
Generates a Sumo Logic/Recorded Future Integration Config File
""")

PARSER.add_argument('-c', metavar='<cfgfile>', dest='CONFIG', \
                    default='rfslsetup.initial.cfg', help='specify a config file')

PARSER.add_argument("-i", "--initialize", action='store_true', default=False, \
                    dest='INITIALIZE', help="initialize config file")

ARGS = PARSER.parse_args(args=None if sys.argv[1:] else ['--help'])

DEFAULTMAP = []
DEFAULTMAP.append('ip')
MAPLIST = DEFAULTMAP
FUSION = {}

SRCTAG = 'recordedfuture'

CURRENT = datetime.datetime.now()
DSTAMP = CURRENT.strftime("%Y%m%d")
TSTAMP = CURRENT.strftime("%H%M%S")

LSTAMP = DSTAMP + '.' + TSTAMP

if os.name == 'nt':
    VARTMPDIR = os.path.join ( "C:\\", "Windows", "Temp" )
else:
    VARTMPDIR = os.path.join ( "/", "var", "tmp" )

CACHED = os.path.join(VARTMPDIR, SRCTAG, DSTAMP)
SRCURL = 'UNSET'

def collect_config_info(config):
    """
    Collect information to populate the config file with
    """

    config.add_section('Default')

    cached_input = input ("Please enter your Cache Directory: \n")
    config.set('Default', 'CACHED', cached_input )

    apikey_input = input ("Please enter your Recorded Future API Key: \n")
    config.set('Default', 'MAPKEY', apikey_input )

    sumo_uid_input = input ("Please enter your Sumo Logic API Key Name: \n")
    config.set('Default', 'SUMOUID', sumo_uid_input )

    sumo_key_input = input ("Please enter your Sumo Logic API Key String: \n")
    config.set('Default', 'SUMOKEY', sumo_key_input )

    sumo_region_input = input ("Please enter your Sumo Logic Deployment Location: \n")
    config.set('Default', 'SUMOEND', sumo_region_input )

    sumo_org_id = input ("Please enter your Sumo Logic Organization ID: \n")
    sumo_org_name = sumo_region_input + '_' + sumo_org_id
    config.set('Default', 'SUMONAME', sumo_org_name )

    source_input = input ("Please enter your Sumo Logic Hosted Source URL: \n")
    config.set('Default', 'SRCURL', source_input )

    map_list_input = input ("Please enter your Recorded Future Maps to Retrieve: \n")
    config.set('Default', 'MAPLIST', map_list_input )

    print('Please enter the Fusion files you may have, one path at a time.')
    print('When you enter "DONE" at any time, then the collection is done.')

    config.add_section('FusionFiles')

    fusion_path_input = ''
    while fusion_path_input != 'DONE':

        fusion_path_input = input ("Fusion_Path: \n")

        fusion_path = urllib.request.unquote(fusion_path_input)

        fusion_category = os.path.basename(fusion_path)

        FUSION[fusion_category] = fusion_path_input

    FUSION.pop('DONE')

    for fusion_key, fusion_value in FUSION.items():
        config.set('FusionFiles', fusion_key, fusion_value )

def persist_config_file(config):
    """
    This is a wrapper to persist the configutation files
    """

    if ARGS.CONFIG:
        starter_config = os.path.abspath(ARGS.CONFIG)
    else:
        starter_config = os.path.join(VARTMPDIR, "recorded_future.cfg")

    with open(starter_config, 'w', encoding='utf8') as configfile:
        config.write(configfile)

    print(f'Written script config: {starter_config}')

def display_config_file():
    """
    This is a wrapper to display the configuration file
    """
    cfg_file = os.path.abspath(ARGS.CONFIG)
    if os.path.exists(cfg_file):
        my_config = configparser.ConfigParser()
        my_config.optionxform = str
        my_config.read(cfg_file)
        print(f'### Contents: {cfg_file} ###\n')
        for cfgitem in dict(my_config.items('Default')):
            cfgvalue = my_config.get('Default', cfgitem)
            print(f'{cfgitem} = {cfgvalue}')
    else:
        print(f'Unable to find: {cfg_file}')

def main():
    """
    This is a wrapper for the configuration file generation routine
    """

    if ARGS.INITIALIZE is False:

        display_config_file()

    else:

        config = configparser.RawConfigParser()
        config.optionxform = str

        collect_config_info(config)

        persist_config_file(config)

if __name__ == '__main__':
    main()
