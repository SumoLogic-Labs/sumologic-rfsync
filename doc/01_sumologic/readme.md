SumoLogic Recorded Future Integration
=====================================

This document will walk through specific steps in deployment options.


Installing the Collectors
=========================

You can run Recorded Future integration by uploading 
to a HTTP hosted collector or an installed collector.

Each of the two will require to download the script 
from the github, and set up the configuration file.

The sections below will talk about setting up the 
collectors, and configuring SumoLogic to accept the data.

SumoLogic Preparation Work
==========================

    1. Configure collectors for your deployments, along with sources.

[Installing Collectors](https://help.sumologic.com/01Start-Here/Quick-Start-Tutorials/Set-Up-Sumo-Logic-Tutorial/Part-1%3A-Install-a-Collector)
[Configure Hosted Collector](https://help.sumologic.com/03Send-Data/Hosted-Collectors/Configure-a-Hosted-Collector)

An overview of the installation is we setup an installed collector, sources, and create an access key.
The collector and the access key are used to securely establish communication to Sumologic.
The sources are definitions for your data, where you want the files to show up in your SumoLogic query.

An installed collector is required; this allows you run the integration script the easiest.
The hosted collector allows you to republish to other sources if you need it giving you flexibility.

    2.1. Implement an installed collector for your deployment.

This is where we will run the script to download the Recorded Future threat intelligence files.
Our script we use will be a python3 script, so for now it is recommended to have a Linux build
with the latest python3 and python modules to install the script.

Later support will be for Windows and other operating systems using a binary created from Pyinstaller.



    2.2. Choose a source category or Categories for the threat intelligence. Examples:

           _sourceCategory = recordedfutures/cached/ip
           _sourceCategory = recordedfutures/cached/hash
           _sourceCategory = recordedfutures/cached/url
           _sourceCategory = recordedfutures/cached/vunlerability
           _sourceCategory = recordedfutures/cached/domain

    3.1. You can also optionally to setup a hosted HTTP collector. 

       As an example, navigating to the following URL.

       https://service.jp.sumologic.com/ui/#/collection/collection

       and then choose to add a collector. You will be prompted to add sources as well.

       when done, you can see there is a unique URL for each of the sources you have created.
       We will use this URL to optionally publish to Sumologic as well.

       https://collectors.jp.sumologic.com/receiver/v1/http/<unique_url_generated_by_sumologic>

    3.2. Choose a source category or Categories for the threat intelligence. Examples:

           _sourceCategory = recordedfutures/hosted/ip
           _sourceCategory = recordedfutures/hosted/hash
           _sourceCategory = recordedfutures/hosted/url
           _sourceCategory = recordedfutures/hosted/vunlerability
           _sourceCategory = recordedfutures/hosted/domain


Installation Steps
==================

[Step-1: SumoLogic Preparation](01_sumologic/readme.md)

[Step-2: Recorded Future Preparation](02_recordedfuture/readme.md)

[Step-3: Integration Setup](03_integration/readme.md)




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
