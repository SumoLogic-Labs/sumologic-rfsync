SumoLogic Recorded Future Integration
=====================================

This document will walk through specific steps in deployment options.


Installing the Script and Modules
=================================

1. First install python3 on the host you setup the installed collector.

If this is the only implementation of python3 then use the Pipfile to 
install only the necessary python modules.

Setting up the Directory and Configuration File
===============================================

1. Next, please confgure the user that will run the script to have
   access to the directory the script will cache the threat maps.

Default:

`$USER`/var/tmp/recordedfuture/*YYYYMMDD*/

The script will not remove the downloaded files, so archiving, backups,
and file system maintenance are important items to consider.

While later versions will implement a switch to compress/remove older
threat intelligence maps, this choice is left to you how best to manage space.

2. Download the script and sample configuration file.

the easiest way to do this is to download the github project either by 
cloning the project or downloading a zip file.

https://github.com/wks-sumo-logic/sumologic-rfsync

When downloaded and unpacked, the directory structure will be:

./bin/rfslsync.py
./bin/sl-updates-24h.query
./etc/rfslsync.cfg

Confirm you can run the following command:

prompt> ./bin/rfslsync.py -h

If you are able to run the command, then we can configure the script.

Add the following information into the configuration file.

* Recorded Future API Key
* Directory to cache the threat intelligence maps
* [optional] the list of Web URL for publishing Directory to cache the threat intelligence maps

Sample of the configuration file used for the script is:

`
[Default]
APIKEY = "please-insert-your-recorded-future-api-key"
MAPLIST = [ "domain", "hash", "ip", "vulnerability", "url" ]
URLLIST = [ "all#https://collectors.jp.sumologic.com/receiver/v1/http/registered-sumologic-collector-url==" ]
`


Setting up Scripted Action
==========================



Setting up Scheduled Query
==========================

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
/Users/wschmidt/Downloads/sumologictoolbox-master/Pipfile
