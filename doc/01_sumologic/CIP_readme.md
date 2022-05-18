Sumo Logic Recorded Future CIP Integration
==========================================

This covers how to setup the integration for the CIP, inicluding the dependencies.

Installing the Project
======================

You will need to use Python 3.6 or higher and the modules listed in the dependency section.  

The steps are as follows: 

    1. Download and install python 3.6 or higher from python.org. Append python3 to the LIB and PATH env.

    2. Download and install git for your platform if you don't already have it installed.
       It can be downloaded from https://git-scm.com/downloads
    
    3. Open a new shell/command prompt. It must be new since only a new shell will include the new python 
       path that was created in step 1. Cd to the folder where you want to install the scripts.
    
    4. Execute the following command to install pipenv, which will manage all of the library dependencies:
    
        sudo -H pip3 install pipenv 
 
    5. Clone this repository, which will create a new folder.
    
    6. Change into the folder. Type the following to install all the package dependencies 
       (this may take a while as this will download all of the libraries that it uses):

        pipenv install
        
Now, we can go back to configuring our collectors and turning on our script!

Script
======

    1. rfslsync.py - This is the main script. It collects files, optionally saves them, and pushes them.

    2. rfslsync.sh - This is a wrapper script to launch the download script as part of a scripted action.

Installing the Collectors
=========================

You can choose to have a hosted or an installed collector ingest your Recorded Future data.

The following shows how to set up the collectors, and configure Sumo Logic to accept the feed.

    1. Configure collectors for your deployments, along with sources.

[Installing Collectors](https://help.sumologic.com/01Start-Here/Quick-Start-Tutorials/Set-Up-Sumo-Logic-Tutorial/Part-1%3A-Install-a-Collector)
[Configure Hosted Collector](https://help.sumologic.com/03Send-Data/Hosted-Collectors/Configure-a-Hosted-Collector)

An overview of the installation is we setup an installed collector, sources, and create an access key.
The collector and the access key are used to securely establish communication to Sumologic.
The sources are definitions for your data, where you want the files to show up in your Sumo Logic query.

An installed collector is required; this allows you run the integration script the easiest.
The hosted collector allows you to republish to other sources if you need it giving you flexibility.

    2.1. Implement an installed collector for your deployment.

This is where we will run the script to download the Recorded Future threat intelligence files.
Our script we use will be a python3 script, so for now it is recommended to have a Linux build
with the latest python3 and python modules to install the script.

Later support will be for Windows and other operating systems using a binary created from Pyinstaller.

    2.2. Choose a source category or Categories for the threat intelligence. 

| Suggested Cached Source Categories |
|:-------------------------------------------------------------------|
| _sourceCategory = recordedfuture/map/ip |
| _sourceCategory = recordedfuture/map/hash |
| _sourceCategory = recordedfuture/map/url |
| _sourceCategory = recordedfuture/map/vunlerability |
| _sourceCategory = recordedfuture/map/domain |

    3.1. You can also optionally to setup a hosted HTTP collector. 

As an example, navigating to the following URL.

https://service.jp.sumologic.com/ui/#/collection/collection

and then choose to add a collector. You will be prompted to add sources as well.

when done, you can see there is a unique URL for each of the sources you have created.

We will use this URL to optionally publish to Sumologic as well.

https://collectors.jp.sumologic.com/receiver/v1/http/<unique_url_generated_by_sumologic>

    3.2. Choose a source category or Categories for the threat intelligence. 

| Suggested Hosted Source Categories |
|:-------------------------------------------------------------------|
| _sourceCategory = recordedfuture/hosted/ip |
| _sourceCategory = recordedfuture/hosted/hash |
| _sourceCategory = recordedfuture/hosted/url |
| _sourceCategory = recordedfuture/hosted/vunlerability |
| _sourceCategory = recordedfuture/hosted/domain |

Installation Steps
==================

    1. Navigate to the collection management page in your organization

    2. Add a collector by clicking on add collectors.  We start with an installed collector.

    3. There are two types of collectors: hosted and installed.  

       We will choose installed for the 1st collector

    4. The installed collector needs to have the software running on the host you choose. 

       Please pick the right OS type to install the right package.

    5. The installed collector needs to establish connection to sumologic.  

       We want to create an access key for this collector.

    6. Create a name for the key. 

       If only for Recorded Future, then a suggestion for the name of the key: recordedfuture

       This will have a accesskey ID and the access key string.  

       SAVE BOTH strings as we will use this in our installation process.

    7. The instaled collector should be running and have a green status connection. 

       We want to confirm the collector is running, and communicating with Sumo Logic.

    8. Now click on the collector to either add sources or script actions. 

       We choose sources now and will choose scripted actions later.

    9. Choose local files for the sources. 

       You will be asked for a path to specific files, and the source category.

    10. Now specify the path to the files, and the source category. 

       By default the directory the files are cached into is under the home directory of the user running it.

       Default: $USER_HOME_DIR/var/tmp/recordedfuture/<YYYYMMDD>

       If running as root, this will put the directory into /var/tmp/recordedfuture.

    11. The installed collector will be running software, so we need to enable this feature.

        We need to add this into the resources for the installed collector.

         "enableActionSource=true"
         "enableScriptSource=true"

        We will be using the Script Source to regularly start the download script.

        Adding this to the user.properties files and then stopping and restarting the collector.

        When working with a Unix/Mac collector, then stop and start the collector
   
         prompt# <sumo_logic_collector_install_directory>/collector stop
  
        wait for 5 seconds
      
         prompt# <sumo_logic_collector_install_directory>/collector start

Suggested Settings
===================

Suggested Settings for Individual Installed Collector Sources:

| Threat Map          | Source Category | Regular Path Expression |
|:------------------- |:----------------|:------------------------|
| domain | recordedfuture/map/domain | $USERDIR/var/tmp/recordedfuture/`*`/`*domain*` |
| hash | recordedfuture/map/hash | $USERDIR/var/tmp/recordedfuture/`*`/`*hash*` |
| ip | recordedfuture/map/ip | $USERDIR/var/tmp/recordedfuture/`*`/`*ip*` |
| url | recordedfuture/map/url | $USERDIR/var/tmp/recordedfuture/`*`/`*url`* |
| vulnerability | recordedfuture/map/vunlerability | $USERDIR/var/tmp/recordedfuture/`*`/`*vuln*` |

          Suggested Settings for Consolidated Installed Collector Sources:

| Threat Map          | Source Category | Regular Path Expression |
|:------------------- |:----------------|:------------------------|
| all | recordedfuture/map/consolidated | $USERDIR/var/tmp/recordedfuture/`*`/`*` |

Suggested Settings for Individual Hosted Collector Sources:

| Threat Map          | Source Category | Hosted Collector URL    |
|:------------------- |:----------------|:------------------------|
| domain | recordedfuture/hosted/domain | https://collectors.jp.sumologic.com/receiver/v1/http/uniqueurl |
| hash | recordedfuture/hosted/hash | https://collectors.jp.sumologic.com/receiver/v1/http/uniqueurl |
| ip | recordedfuture/hosted/ip | https://collectors.jp.sumologic.com/receiver/v1/http/uniqueurl |
| url | recordedfuture/hosted/url | https://collectors.jp.sumologic.com/receiver/v1/http/uniqueurl |
| vulnerability | recordedfuture/hosted/vunlerability | https://collectors.jp.sumologic.com/receiver/v1/http/uniqueurl |

Suggested Settings for Consolidated Hosted Collector Sources:

| Threat Map          | Source Category | Hosted Collector URL    |
|:------------------- |:----------------|:------------------------|
| all | recordedfuture/hosted/consolidated | https://collectors.jp.sumologic.com/receiver/v1/http/uniqueurl |

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
