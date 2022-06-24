Sumo Logic Recorded Future Integration
======================================

The installation of the Sumo Logic Recorded Future integration is easy.

There are in 3 easy steps:

    * Setup your Recorded Future Feed: API Key, Maps, Fusion Files.

    * Setup Continuous Intelligence Platform (CIP)

    * Setup Cloud SIEM Enterprise (CSE)

See our section on Sumo Logic Preparation to choose the right setup steps for you.

Setup Steps
===========

Let's start with a choice. We recommend configuring your CIP environment first and then setup CSE.

Why? The CSE does the best when the CIP environment is properly setup, feeding the SIEM with data.

Setup correctly, CIP records you feed to the SIEM can be enhanced with Recorded Future threat intelligence.

Planning:
=========

[Recorded Future Preparation](02_recordedfuture/readme.md)

Before you being, first step plan how you want to ingest the data into Sumo Logic. 

The next step ensures we have the right subscription and setup for Recorded Future.

The last step pulls all of this together, and makes your threat intelligence import automatic.

CIP Setup:
==========

[CIP::Step-by-Step::Howto: Sumo Logic CIP Preparation](01_sumologic/CIP_readme.md)

CSE Setup:
==========

[CSE::Step-by-Step::Howto: Sumo Logic CSE Preparation](01_sumologic/CSE_readme.md)

CIP Setup (Optional):
=====================

Probably the easiest way to download is to setup an AWS or Azure function using your API key.

But! There are options to download maps, and this shows how you can setup a local installed collector to also download maps.

[CIP::Step-By-Step::Howto: Sumo Logic Installed Collector](03_integration/readme.md)

After it is done! The Screen Shots
==================================

| Sumo Logic Content Screen Shot Name  |
|:-------------------------------------|
| [Recorded Future Overview](content/screenshots/Recorded_Future_Overview.png) |
| [Recorded Future Domain Map](content/screenshots/Recorded_Future_Domain.png) |
| [Recorded Future Hash Map](content/screenshots/Recorded_Future_Hash.png) |
| [Recorded Future Ip Map](content/screenshots/Recorded_Future_IP.png) |
| [Recorded Future URL Map](content/screenshots/Recorded_Future_URL.png ) |
| [Recorded Future Vulnerability Map](content/screenshots/Recorded_Future_Vulnerability.png) |

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
