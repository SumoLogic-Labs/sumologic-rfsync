Sumo Logic Recorded Future CIP Integration
==========================================

This covers how to setup the integration for the CIP, inicluding the dependencies.

Installing the Project
======================

First things first, we need to download the script and dependencies we need to use.

Please follow these quick steps to get this installed.

(https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CIP_project_prep.md "Install the Scripts")

Installing the Collectors
=========================

Now, to the configuring your Sumo Logic environment, with the final step deciding how to 

You can run Recorded Future integration by uploading to a HTTP hosted collector or an installed collector.

Each of the two requires the script we downloaded just previously and then edit the configuration file with your preferences.

The following sections focus on how to set up the collectors, and configuring Sumo Logic to accept the data.

Sumo Logic Preparation Work
===========================

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
| _sourceCategory = recordedfuture/cached/ip |
| _sourceCategory = recordedfuture/cached/hash |
| _sourceCategory = recordedfuture/cached/url |
| _sourceCategory = recordedfuture/cached/vunlerability |
| _sourceCategory = recordedfuture/cached/domain |

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

![Step01](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CIP_steps/sl.step1.png "Collection Management")

    2. Add a collector by clicking on add collectors.  We start with an installed collector.

![Step02](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CIP_steps/sl.step2.png "Add Collector")

    3. There are two types of collectors: hosted and installed.  

       We will choose installed for the 1st collector

![Step03](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CIP_steps/sl.step3.png "Choose Type - Installed")

    4. The installed collector needs to have the software running on the host you choose. 

       Please pick the right OS type to install the right package.

![Step04](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CIP_steps/sl.step4.png "Select Installation Package")

    5. The installed collector needs to establish connection to sumologic.  

       We want to create an access key for this collector.

![Step05](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CIP_steps/sl.step5.png "Navigate to Access Key")

    6. Create a name for the key. 

       If only for Recorded Future, then a suggestion for the name of the key: recordedfuture

       This will have a accesskey ID and the access key string.  

       SAVE BOTH strings as we will use this in our installation process.

![Step06](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CIP_steps/sl.step6.png "Access Key Details")

    7. The instaled collector should be running and have a green status connection. 

       We want to confirm the collector is running, and communicating with Sumo Logic.

![Step07](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CIP_steps/sl.step7.png "Verify Installed Collector")

    8. Now click on the collector to either add sources or script actions. 

       We choose sources now and will choose scripted actions later.

![Step08](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CIP_steps/sl.step8.png "Add Sources")

    9. Choose local files for the sources. 

       You will be asked for a path to specific files, and the source category.

![Step09](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CIP_steps/sl.step9.png "Choose Source Type - Local Files")

    10. Now specify the path to the files, and the source category. 

       By default the directory the files are cached into is under the home directory of the user running it.

       Default: $USER_HOME_DIR/var/tmp/recordedfuture/<YYYYMMDD>

       If running as root, this will put the directory into /var/tmp/recordedfuture.

![Step10](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CIP_steps/sl.step10.png "Specify Path for Files")

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
| domain | recordedfuture/cached/domain | $USERDIR/var/tmp/recordedfuture/`*`/`*domain*` |
| hash | recordedfuture/cached/hash | $USERDIR/var/tmp/recordedfuture/`*`/`*hash*` |
| ip | recordedfuture/cached/ip | $USERDIR/var/tmp/recordedfuture/`*`/`*ip*` |
| url | recordedfuture/cached/url | $USERDIR/var/tmp/recordedfuture/`*`/`*url`* |
| vulnerability | recordedfuture/cached/vunlerability | $USERDIR/var/tmp/recordedfuture/`*`/`*vuln*` |

          Suggested Settings for Consolidated Installed Collector Sources:

| Threat Map          | Source Category | Regular Path Expression |
|:------------------- |:----------------|:------------------------|
| all | recordedfuture/cached/consolidated | $USERDIR/var/tmp/recordedfuture/`*`/`*` |

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
