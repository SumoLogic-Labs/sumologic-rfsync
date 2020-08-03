Sumo Logic Recorded Future Integration
======================================

This script, config files, and instructions allow a client of Recorded Future to add their data into Sumo Logic.

Installing the Project
======================

The scripts are command line based, designed to be used within a batch script or DevOPs tool such as Cher or Ansible.
Script are python3 scripts. The complete list of the python modules are provided to aid people using a pip install.

You will need to use Python 3.6 or higher and the modules listed in the dependency section.  

The steps are as follows: 

    1. Download and install python 3.6 or higher from python.org. Append python3 to the LIB and PATH env.

    2. Download and install git for your platform if you don't already have it installed.
       It can be downloaded from https://git-scm.com/downloads
    
    3. Open a new shell/command prompt. It must be new since only a new shell will include the new python 
       path that was created in step 1. Cd to the folder where you want to install the scripts.
    
    4. Execute the following command to install pipenv, which will manage all of the library dependencies:
    
        sudo -H pip3 install pipenv 
 
    5. Clone this repo using the following command:
    
       git clone git@github.com:wks-sumo-logic/sumologic-rfsync.git

    This will create a new folder
    
    6. Change into the folder. Type the following to install all the package dependencies 
       (this may take a while as this will download all of the libraries that it uses):

        pipenv install
        
Setting up the Sumo Logic Recorded Future Integration
=====================================================

Designed to be completed in minimal steps, the integration can be setup easily.

Please refer to these configuration instructions located:

[Configuring your Sumo Logic Recorded Future Integration](doc/readme.md)

Dependencies
============

See the contents of "pipfile"

Script Names and Purposes
=========================

Scripts and Functions:

    1. rfslsync.py - This is the main script. It collects files, optionally saves them, and pushes them.

    2. rfslsync.sh - This is a wrapper script to launch the download script as part of a scripted action.

    3. sl-updates-24h.query - This could be used to monitor the age of the downloaded data
                   
To Do List:
===========

* Build an Ansible wrapper for script to automatically complete configuration

* extend the download/upload functions

* download gzipped data use for installed collector


License
=======

Copyright 2019 Wayne Kirk Schmidt

Licensed under the GNU GPL License (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    license-name   GNU GPL
    license-url    http://www.gnu.org/licenses/gpl.html

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Support
=======

Feel free to e-mail me with issues to: wschmidt@sumologic.com
I will provide "best effort" fixes and extend the scripts.
