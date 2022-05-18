Sumo Logic Recorded Future Integration
======================================

Sumo Logic is proud to partner with Recorded Future to provide integration between these two platforms.

This integration allows Recorded Future's comprehensive threat intelligence to enhance Sumo Logic queries.

The result? On the fly ability to lookup/enhance events with threat intelligence to better respond to events.

Configuring the Feed: Getting started!
======================================

Let's get started! Integrating [Recorded Future](https://www.recordedfuture.com/) feeds with [Sumo Logic](https://www.sumologic.com/) products, please follow the steps:

*    [Recorded Future Integration with Sumo Logic Integration Steps](doc/readme.md) 

in the order listed.

Current Integrations
====================

| Product Name   | Recorded Future Feeds Support        | Ad Hoc Enrichment |
|:---------------|:-------------------------------------|:------------------|
| [Sumo Logic CIP](https://www.sumologic.com/brief/continuous-intelligence-platform-overview/) | All Recorded Future feeds | [Browser Plugin](https://chrome.google.com/webstore/detail/recorded-future/cdblaggcibgbankgilackljdpdhhcine?hl=en)    |
| [Sumo Logic CSE](https://www.sumologic.com/solutions/cloud-siem-enterprise/) | All Recorded Future feeds except vulnerability | Within the SIEM   |

Current Data Feeds
==================

| Recorded Future Feeds           |
|:--------------------------------|
| ip - ip addresses               |
| hash - file hashes              |
| domain - DNS domains            |
| url - web URLS                  |
| vulnerability - CVE list        |

| Recorded Future Fusion Files    |
|:--------------------------------|
| Public Fusion Files             |
| Personal Fusion Files           |

Included Sumo Logic Content
===========================

The following content is provided so you can monitor your Recorded Future feed, as well as base new content on these examples.

| Content Name                         |
|:-------------------------------------|
| [Recorded Future Index Consolidated Content](content/Recorded_Future_Content.json)        |
| [Recorded Future Index Individual Queries](content/queries/)        |

Features:
=========

- [x] Support for AWS Lambda, EC2, and installed collector support for data collection ( both Windows and Linux )

- [x] Support for getting Recorded Future Demo Events, Threat Intelligence and curated Fusion Files

- [x] Support for creating Sumo Logic lookup files as well as Sumo Logic index for correlation

- [x] Included Sumo Logic content; dashboards showing the health of your threat intelligence feed

- [x] Support for actions and response using Sumo Logic webhooks

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
