Sumo Logic Recorded Future CIP Integration
==========================================

This covers how to setup the integration for the CIP, including the dependencies.

Overview
========

Number of Steps: 6

Duration: 10 - 15 minutes

Pre-Requisites:
	+ working python 3.6 or higher installation
	+ Recorded Future API KEY
	+ Sumo Logic Source HTTPS endpoint

Resources:
	+ some 1 - 2 Gbytes of local space
	+ recommended 2 - 4 Gbytes of memory

Summary Steps:
	+ <repository>/bin/envcheck.py
	+ <repository>/bin/genconfig.py
	+ <repository>/bin/rfslsync.py

Script Preparation
==================

You will need to use Python 3.6 or higher and the modules listed in the dependency section.  

The steps are as follows: 

    1. Download and install python 3.6 or higher from python.org. Append python3 to the LIB and PATH env.

    2. Download and install git for your platform if you don't already have it installed.
       It can be downloaded from https://git-scm.com/downloads
    
    3. Open a new shell/command prompt. It must be new since only a new shell will include the new python 
       path that was created in step 1. Cd to the folder where you want to install the scripts.
    
    4. Execute the following command to install pipenv, which will manage all of the library dependencies:
    
        sudo -H pip3 install pipenv 
 
Sumo Logic Preparation
======================

    1. Navigate to the Security Management Page in your organization

    2. Create Sumo Logic API key.

       We suggest keeping this key separate from other API keys and name this: recordedfuture

       When this is done, it will show the accesskey ID and the access key string.

       SAVE BOTH strings as we will use this in our installation process.

Specific Steps
==============

1. Clone the Github Repository

prompt> git clone git@github.com:SumoLogic-Labs/sumologic-rfsync.git

2. Confirm python3 exists and is newer than 3.6

prompt> which python3

/usr/local/bin/python3

prompt> python3 --version
Python 3.9.7

3. CD into the bin directory and validate the module install

prompt> cd <repository>/bin

prompt> ./envcheck.py 

4. Initialize the configuration file

prompt> ./genconfig.py -i

You will be prompted to answer all of the questions. 

NOTE: this creates a configuration file in /var/tmp suitable for both standalone and lambda scripts

NOTE: this will successfully run on Windows as well as Unix

5. Now, check the values of the configuration file

prompt> <repository>/bin/genconfig.py -c <configfile_file>

6. Test out this download process using this configuration file

prompt> <repository>/bin/rfslsync.py -v 6 -c <configuration_file>
 
Collector Reference
===================

You can choose to have a hosted or an installed collector ingest your Recorded Future data.

The script creates a hosted collector for you, though you can make your own if you choose.

[Installing Collectors](https://help.sumologic.com/01Start-Here/Quick-Start-Tutorials/Set-Up-Sumo-Logic-Tutorial/Part-1%3A-Install-a-Collector)
[Configure Hosted Collector](https://help.sumologic.com/03Send-Data/Hosted-Collectors/Configure-a-Hosted-Collector)

Suggested Settings
==================

| Threat Map          | Source Category | Regular Path Expression |
|:------------------- |:----------------|:------------------------|
| domain | recordedfuture/map/domain | $USERDIR/var/tmp/recordedfuture/`*`/`*domain*` |
| hash | recordedfuture/map/hash | $USERDIR/var/tmp/recordedfuture/`*`/`*hash*` |
| ip | recordedfuture/map/ip | $USERDIR/var/tmp/recordedfuture/`*`/`*ip*` |
| url | recordedfuture/map/url | $USERDIR/var/tmp/recordedfuture/`*`/`*url`* |
| vulnerability | recordedfuture/map/vunlerability | $USERDIR/var/tmp/recordedfuture/`*`/`*vuln*` |

License
=======

Copyright 2020 Wayne Kirk Schmidt
https://www.linkedin.com/in/waynekirkschmidt

Licensed under the Apache 2.0 License (the "License");

You may not use this file except in compliance with the License.
You may obtain a copy of the License at

    license-name   APACHE 2.0
    license-url    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Support
=======

Feel free to e-mail me with issues to: 

*    wschmidt@sumologic.com

*    wayne.kirk.schmidt@gmail.com

I will provide "best effort" fixes and extend the scripts.
