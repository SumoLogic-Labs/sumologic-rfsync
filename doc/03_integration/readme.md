Sumo Logic Recorded Future Integration
======================================

This document will walk through specific steps in deployment options.


Installing the Script and Modules
=================================

1. First install python3 on the host you setup the installed collector.

If this is the only implementation of python3 then use the Pipfile to install only the necessary python modules.

Setting up the Directory and Configuration File
===============================================

1. Next, please confgure the user that will run the script to have
   access to the directory the script will cache the threat maps.

Default:

`$USER`/var/tmp/recordedfuture/*YYYYMMDD*/

The script will not remove the downloaded files.
Archiving, backups, and file system maintenance must be considered.

Later versions will support data management. 
That said, it is important to decide how best to manage the data/space.

2. Download the script and sample configuration file.

The best way to do this is to clone the github project.

https://github.com/wks-sumo-logic/sumologic-rfsync

When downloaded and unpacked, the directory structure will be:

`/var/tmp/rfslsync/bin/rfslsync.py`

`/var/tmp/rfslsync/bin/rfslsync.sh`

`/var/tmp/rfslsync/bin/rfslsync.qry`

`/var/tmp/rfslsync/etc/rfslsync.cfg`

`/var/tmp/rfslsync/log/output.log`

Confirm you can run the following command:

`prompt> ./bin/rfslsync.py -h`

If you are able to run the command, then we can configure the script.

Add the following information into the configuration file.

* Recorded Future API Key
* Directory to cache the threat intelligence maps
* [optional] the list of Web URL for publishing Directory to cache the threat intelligence maps

Sample of the configuration file used for the script is:

`[Default]`

`APIKEY = "please-insert-your-recorded-future-api-key"`

`MAPLIST = [ "domain", "hash", "ip", "vulnerability", "url" ]`

`URLLIST = [ "all#https://collectors.jp.sumologic.com/receiver/v1/http/sumologic-hosted-collector==" ]`

Setting up the download Script
==============================

Sumologic supports the ability to run a script of your choosing, called a scripted action.
We will put that script into a local directory on the install collector host.

That script, coupled with the query is how Sumo Logic will pull the Recorded Future files.
A script sample is located in the bin directory of the git project, and is called:

* rfslsync.sh

Steps to set up the hosted collector would be:

1) cd /var/tmp and create the directory required

* umask 022

* mkdir -p /var/tmp/rfslsync/bin

* mkdir -p /var/tmp/rfslsync/etc

2) Confirm the path to the rfsync.sh script. <git-repository-dir>/bin/rflsync.sh

3) Confirm the path to the rfslsync.cfg config file. <git-repository-dir>/etc/rfslsync.cfg

4) Copy and Edit the files required for the scripted action:

* cp <git-repository-dir>/bin/rfslsync.sh /var/tmp/rfslsync/bin/rfslsync.sh

* cp <git-repository-dir>/bin/rfslsync.py /var/tmp/rfslsync/bin/rfslsync.py

* cp <git-repository-dir>/etc/rfslsync.cfg /var/tmp/rfslsync/etc/rfslsync.cfg

5) Confirm the contents of the wrapper script is correct /var/tmp/rfslsync/rfslsync.sh

   * cmdname

   * cfgname

6) Confirm the script can be executed.

The next step is setting up the scripted action, and optionally setup the query to monitor the downloads

Setting up the Scripted Action
==============================

![Step1](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/03_integration/steps/sl.step1.png "Navigate to the Installed Collector")

1) Go to the installed collector you have setup, and add a scripted action.
   The action is a command/script that can run as a command based on a query.

![Step2](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/03_integration/steps/sl.step2.png "Click on Add Scripted Action")

2) When adding the scripted action, we need to specify the type of script,
   the full path of the script, and the directory this will run in.

![Step3](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/03_integration/steps/sl.step3.png "Fill in Values")

3) This is an example of the filled in values. 

| Key Name p          | Hosted Collector URL                                  |
|:------------------- |:------------------------------------------------------|
| Script Action Name | download-recorded-future-maps |
| Script Description | Download Threat Intelligence from Recorded Future |
| Path to script | /var/tmp/rfslsync/bin/rfslsync.sh |
| Directory for script | /var/tmp/rfslsync |
| Script type | /bin/bash |

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
