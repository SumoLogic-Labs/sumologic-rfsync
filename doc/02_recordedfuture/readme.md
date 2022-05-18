Sumo Logic Recorded Future Integration
======================================

This document will walk through specific steps in deployment options.

Recorded Future Steps
=====================

Key for Recorded Future is to contact them to register for your threat feeds.
Specify the threat feeds, the granularity of feed, and the frequency of updates.

From this you should have the following items:

1. List of threat feeds you want. Below is a sample of the size of the uncompressed CSV files

| Threat Map          | Size in Kbytes  | Size in Lines | Sample File Name |
|:------------------- |:----------------|:--------------|:-----------------|
| domain | 18076 | 25632 | rf_domain_risklist.csv |
| hash | 91124 | 100001 | rf_hash_risklist.csv |
| ip | 15696 | 14127 | rf_ip_risklist.csv |
| url | 143160 | 100001 | rf_url_risklist.csv |
| vulnerability | 23748 | 43684 | rf_vulnerability_risklist.csv |

2. As part of the registration, you will obtain an API key. Please save this key.
   Test your access using this key, to ensure you are able to download the threat maps.

   https://api.recordedfuture.com/v2/

   You will be prompted for your API token here.

Other Useful Resources:

https://api.recordedfuture.com/index.html

When successful, you will be using this information as well as other information 
in a configuration file to automate your download and publish to Sumo Logic.

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
