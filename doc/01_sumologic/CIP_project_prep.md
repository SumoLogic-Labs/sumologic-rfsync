To prepare our ptoject to use the API solution
==============================================

To use Recorded Future with Sumo Logic CIP, we need to download the project and its dependencies

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
 
    5. Clone this repo using the following command:
    
       git clone git@github.com:wks-sumo-logic/sumologic-rfsync.git

    This will create a new folder
    
    6. Change into the folder. Type the following to install all the package dependencies 
       (this may take a while as this will download all of the libraries that it uses):

        pipenv install
        
Now, we can go back to configuring our collectors and turning on our script!

Script Names and Purposes
=========================

Scripts and Functions:

    1. rfslsync.py - This is the main script. It collects files, optionally saves them, and pushes them.

    2. rfslsync.sh - This is a wrapper script to launch the download script as part of a scripted action.

    3. rfslenrich.py - this can return data to enrich data, and is another example of the RF API at work.
                   
License
=======

Copyright 2020 Wayne Kirk Schmidt

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
