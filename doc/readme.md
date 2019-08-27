SumoLogic Recorded Futures Integration
======================================

This document will walk through specific steps in deployment options.


Installing the Collectors
=========================

You can run Recorded Futures integration by uploading 
to a HTTP hosted collector or an installed collector.

Each of the two will require to download the script 
from the github, and set up the configuration file.

The sections below will talk about setting up the 
collectors, and configuring SumoLogic to accept the data.

SumoLogic Preparation Work
==========================
    1. Choose a source category for the threat intelligence. Examples:

           _sourceCategory = recordedfutures/ip
           _sourceCategory = recordedfutures/hash
           _sourceCategory = recordedfutures/url
           _sourceCategory = recordedfutures/vunlerability
           _sourceCategory = recordedfutures/domain

Recorded Futures Preparation Work
=================================


    1. Please obtain a Recorded Futues API key from Recorded Futures.
       For reference this web page should help with the subscription process.

           https://www.recordedfuture.com/api-announcement/

    2. Once you have the API key, then place this into the configuration file.
       Please see an example of the configuration file format here:

           https://github.com/wks-sumo-logic/sumologic-rfsync/tree/master/etc

    3. Confirm ths list of threat intelligence maps you have requested.
       Edit the configuration file if required to reflect your subscription.

    4. confirm you have read about the download best practices:

           https://go.recordedfuture.com/applying-threat-intelligence

Hosted Collector Installation
=============================

Installed Collector Installation
================================

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
