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

Then you will need to create the a local directory for the script to run.

`prompt> umask 022 ; mkdir -p /var/tmp/rfslsync/{bin,etc,log}`

Then copy the scripts from the bin directory into the bin directory you created.

`prompt> cp -p <repository>/bin/script/rfsl*.py /var/tmp/rfslsync/bin`

`prompt> cp -p <repository>/bin/script/rfsl*.sh /var/tmp/rfslsync/bin`

Now, confirm you can run the following command:

`prompt> /var/tmp/rfslsync/bin/rfslsync.py -h`

If you are able to run the command, then we can configure the script.

Next? We need a configuration file that contains at least:

* Recorded Future API Key
* Directory to cache the threat intelligence maps
* [optional] the list of Web URL for publishing Directory to cache the threat intelligence maps

The best way to accomplish this is to run the genconfig.py script in the bin directory.

`prompt> <repository>/bin/script/genconfig.py -i -c /var/tmp/rfslsync/etc/rfslsync.cfg`

Using this script, it will prompt you for all of information it will need to run all lambdas/scripts.

Checkpoint!
===========

When done, the directory structure should look like the following:

`/var/tmp/rfslsync/bin/rfslsync.py`

`/var/tmp/rfslsync/bin/rfslsync.sh`

`/var/tmp/rfslsync/etc/rfslsync.cfg`

If we have these files, then we should be ready to configure the scripted action.

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
