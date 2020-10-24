Configuring the Cloud SIEM Enterprise
=====================================

The Cloud SIEM Enterprise can be done from the SIEM UI.

Installation Steps
==================

    1. Navigate to the collection management page in your organization

![Step01](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CSE_steps/cse.step1.png "Collection Management")

    2. Add a collector by clicking on add collectors.  We start with an installed collector.

![Step02](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CSE_steps/cse.step2.png "Add Collector")

    3. There are two types of collectors: hosted and installed.  

       We will choose installed for the 1st collector

![Step03](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CSE_steps/cse.step3.png "Choose Type - Installed")

    4. The installed collector needs to have the software running on the host you choose. 

       Please pick the right OS type to install the right package.

![Step04](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CSE_steps/cse.step4.png "Select Installation Package")

    5. The installed collector needs to establish connection to sumologic.  

       We want to create an access key for this collector.

![Step05](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CSE_steps/cse.step5.png "Navigate to Access Key")

    6. Create a name for the key. 

       If only for Recorded Future, then a suggestion for the name of the key: recordedfuture

       This will have a accesskey ID and the access key string.  

       SAVE BOTH strings as we will use this in our installation process.

![Step06](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CSE_steps/cse.step6.png "Access Key Details")

    7. The instaled collector should be running and have a green status connection. 

       We want to confirm the collector is running, and communicating with Sumo Logic.

![Step07](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CSE_steps/cse.step7.png "Verify Installed Collector")

    8. Now click on the collector to either add sources or script actions. 

       We choose sources now and will choose scripted actions later.

![Step08](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CSE_steps/cse.step8.png "Add Sources")

    9. Choose local files for the sources. 

       You will be asked for a path to specific files, and the source category.

![Step09](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CSE_steps/cse.step9.png "Choose Source Type - Local Files")

    10. Now specify the path to the files, and the source category. 

       By default the directory the files are cached into is under the home directory of the user running it.

       Default: $USER_HOME_DIR/var/tmp/recordedfuture/<YYYYMMDD>

       If running as root, this will put the directory into /var/tmp/recordedfuture.

![Step10](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CSE_steps/cse.step10.png "Specify Path for Files")

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
