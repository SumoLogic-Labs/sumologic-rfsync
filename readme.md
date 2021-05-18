Sumo Logic Recorded Future Integration
======================================

We show how to integrate [Recorded Future](https://www.recordedfuture.com/) feeds with [Sumo Logic](https://www.sumologic.com/) products:

* [Sumo Logic Continuous Intelligence Platform - Recorded Future Integration Steps](doc/readme.md)

* [Sumo Logic Cloud SIEM Enterprise - Recorded Future Integration Steps](doc/readme.md)

Features
========

| Product Name   | Recorded Future Feeds Support        | Ad Hoc Enrichment |
|:---------------|:-------------------------------------|:------------------|
| [Sumo Logic CIP](https://www.sumologic.com/brief/continuous-intelligence-platform-overview/) | All Recorded Future feeds | [Browser Plugin](https://chrome.google.com/webstore/detail/recorded-future/cdblaggcibgbankgilackljdpdhhcine?hl=en)    |
| [Sumo Logic CSE](https://www.sumologic.com/solutions/cloud-siem-enterprise/) | All Recorded Future feeds except vulnerability | Within the SIEM   |

| Recorded Future Feeds    |
|:-------------------------|
| ip - ip addresses        |
| hash - file hashes       |
| domain - DNS domains     |
| url - web URLS           |
| vulnerability - CVE list |

ScreenShots
===========

| Sumo Logic Content Screen Shot Name  |
|:-------------------------------------|
| [Recorded Future Overview](content/screenshots/Recorded_Future_Overview.png) |
| [Recorded Future Domain Map](content/screenshots/Recorded_Future_Domain_Map.png) |
| [Recorded Future Hash Map](content/screenshots/Recorded_Future_Hash_Map.png) |
| [Recorded Future Ip Map](content/screenshots/Recorded_Future_IP_Map.png) |
| [Recorded Future URL Map](content/screenshots/Recorded_Future_URL_Map.png ) |
| [Recorded Future Vuln Map](content/screenshots/Recorded_Future_Vulnerability_Map.png) |

| Recorded Future Browser Plugin       |
|:-------------------------------------|
| [Recorded Future Browser Plugin IP1](content/screenshots/Recorded-Future-Example-001_IP.png) |
| [Recorded Future Browser Plugin IP2](content/screenshots/Recorded-Future-Example-002_IP.png) |
| [Recorded Future Browser Plugin Hash](content/screenshots/Recorded-Future-Example-003_Hash.png) |
| [Recorded Future Browser Plugin URL](content/screenshots/Recorded-Future-Example-004_URL.png) |
| [Recorded Future Browser Plugin Vulnerability](content/screenshots/Recorded-Future-Example-005_Vulnerability.png) |
| [Recorded Future Browser Plugin Domain](content/screenshots/Recorded-Future-Example-006_Domain.png) |
| [Recorded Future Browser Plugin IP Site Detail](content/screenshots/Recorded-Future-Example-007_IP-Site-Lookup.png) |

Content
=======
| Content Name                         |
|:-------------------------------------|
| [Recorded Future Overview](content/Recorded_Future_Content.json)        |

Installation
============

| Video Name                           |
|:-------------------------------------|
| [CIP Installation Video](media/Sumo_Logic-Recorded_Future-CIP-Integration.mp4) |
| [CSE Installation Video](media/Sumo_Logic-Recorded_Future-CSE-Integration.mp4) |

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
