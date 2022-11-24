Sumo Logic Recorded Future CIP Integration
==========================================

This covers how to setup the integration for the CIP, including the dependencies.

Overview
========

Number of Steps: 9

Duration: 10 - 15 minutes

System-Requisites:
==================
	+ working python 3.6 or higher installation
	+ working terraform package

Data-Input:
===========
	+ Recorded Future API KEY
	+ Sumo Logic API name
	+ Sumo Logic API KEY
	+ Sumo Logic Deployment Region String
	+ Sumo Logic Deployment Organization ID
	+ Sumo Logic - Recorded Future Cached Directory Target

Resources:
==========
	+ some 1 - 2 Gbytes of local space
	+ recommended 2 - 4 Gbytes of memory

Sumo Logic Preparation
======================

    1. Navigate to the Administration and Security Management Page in your organization
        + Record the Sumo Logic Organization ID ( in the Administration / Account page )
        + Record the Sumo Logic Deployment Location ( from the login URL )

    2. Create Sumo Logic API key.

       We suggest keeping this key separate from other API keys and name this: recordedfuture

       When this is done, it will show the accesskey ID and the access key string.
       SAVE BOTH strings as we will use this in our installation process.

        + Sumo Logic API name
        + Sumo Logic API KEY

Installation Steps
==================

You will need to use Python 3.6 or higher and the modules listed in the dependency section.  

The steps are as follows: 

    1. Download and install python 3.6 or higher from python.org. Append python3 to the LIB and PATH env.

    2. Download and install terraform from developer.hashicorp.com. 
       The instructions can be found here https://developer.hashicorp.com/terraform/downloads

    3. Download and install git for your platform if you don't already have it installed.
       It can be downloaded from https://git-scm.com/downloads
    
    4. Clone the git repository for Recorded Future / Sumo Logic Integration. 

       prompt> git clone git@github.com:SumoLogic-Labs/sumologic-rfsync.git

       Open a shell prompt and change directory to the base of the git repository you have cloned. 

    5. Change to the terraform directory. Confirm you have terraform installed and initialize terraform

       prompt> cd <repository>/bin/terraform

       prompt> which terraform

       prompt> terraform --version

       prompt> terraform init

    5. Now, run terraform! This will evaluate all of the terraform files in the directory and configure your environment.

       The easiest way to do this is run the shell script: rfsyncprep.startup.ksh

       This will prompt you for the information below, so be prepared to have the information ready.

	+ Recorded Future API KEY
	+ Sumo Logic API name
	+ Sumo Logic API KEY
	+ Sumo Logic Deployment Region String
	+ Sumo Logic Deployment Organization ID
	+ Sumo Logic - Recorded Future Cached Directory Target

       Once this is done you will have a configured Sumo Logic environment!
       Also, you will have the coniguration file you need to upload Recorded Future Data into Sumo Logic. 

        + /var/tmp/recordedfuture/config/rfslconfig.cfg - your configuration file

        + /var/tmp/recordedfuture/config/rfslconfig.vars - helper file for terraform

    6. Next, let's confirm we have a python installed, it is the right version, and we have a working environment.

       prompt> which python3
       /usr/local/bin/python3

       prompt> python3 --version
       Python 3.9.7

       prompt> cd <repository>/bin
       prompt> <repository>/bin/scripts/envcheck.py 

       Please install any python modules that the script may ask you to install.

    7. Now! Run the publishing script and see that you have imported data into Sumo Logic. 

       prompt> <repository>/bin/scripts/rfslsync.py -v 20 -c <configuration_file>

       example: 

       prompt> <repository>/bin/scripts/rfslpublish.py -v 20 -c /var/tmp/recordedfuture/config/rfslconfig.cfg

    8. Next, you can run the following scripts

        + <repository>/bin/scripts/rfslpublish.py - Publishes the Recorded Future data into Sumo Logic

        + <repository>/bin/scripts/rfsllookups.py - Uploads Recorded Future data into Sumo Logic lookup files

        + <repository>/bin/scripts/rfslsamples.py - Publishes Recorded Future demo data into Sumo Logic

    9.  Next use the build_lambda script to create the necessary zip files to install into AWS if you wish.

       prompt> <repository>/scripts/bin/build_lambda.sh rfslpublish - builds the basic publish lambda function zipfile

       prompt> <repository>/scripts/bin/build_lambda.sh rfsllookups - builds the data upload into lookup file lambda function zipfile

       prompt> <repository>/scripts/bin/build_lambda.sh rfslsamples - builds the demo events download lambda function zipfile

 
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
