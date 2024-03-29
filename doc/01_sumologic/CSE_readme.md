Configuring the Cloud SIEM Enterprise
=====================================

The Cloud SIEM Enterprise can be done from the SIEM UI.

Installation Steps
==================

This article shows how to install and setup Recorded Future API and TAXII feeds to use with CSE.

Recorded Future provides contextual Threat Intelligence through indicator lookups via a cloud-accessible API. 

CSE provides an Insight Action that allows lookup of extracted Insight Artifacts. 

The lookup result is added as enrichment to Insight and/or Signals. 

You can also bring in Recorded Future TAXII feeds into CSE, enriching data used to create Signals based on IP, Domain, Hash, or URL.

API Integration Enabling the API in Recorded Future
===================================================

*	Navigate to menu > user settings > API Access > Generate new API token

![Step01](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CSE_steps/cse.step.1.png "Generate API Token")
 
*	Now Setup an Insight Action configuration

![Step02](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CSE_steps/cse.step.2.png "Insight Action Config")

To enrich both Insights and Signals that are part of Insights ensure both Enrichment checkboxes are checked.
Insight Notification Type "When created" checkbox triggers this action on every Insight at creation time

NOTE: Please consult with your Recorded Future account manager regarding licensed API usage.

* 	Artifacts (required)

Record fields that are subject to lookup in RF is controlled via Artifacts. 
Currently supported Artifacts are: "IP Address", "Domain", "URL", and "Hash" (artifact names are case sensitive).

![Step03](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CSE_steps/cse.step.3.png "Feed List")

*	Enrichment

Artifact lookup results are shown in a list under the enrichment name "Recorded Future".
 
![Step04](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CSE_steps/cse.step.4.png "Enrichment")

Artifact lookup results are shown in a list under the enrichment name "Recorded Future".

| RF API Fields 2019-08-03  |
|:--------------------------|
|	**analystNotes**        |
|	counts              |
|	**entity**              |
|	**intelCard**           |
|	metrics             |
|	relatedEntites      |
|	**risk**                |
|	**sightings**           |
|	**threatLists**         |
|	**timestamps**          |

Bold fields are included in Insight and Signal enrichment via the CSE Insight Action.

*	Custom Headers

JASK uses a custom User-Agent header to aid in potential troubleshooting. 

Current User-Agent header should be:

	*	SumoLogicCSE-Enrichment+v1.0

	*	TAXII Feed Integration

Go to https://<tenant>portal.jask.ai/config/integrations/intelligence

Click on "ADD" 
	
![Step05](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CSE_steps/cse.step.5.customer.headers.png "Map List")

Enter your credentials on the next screen:

	* Name = Recorded Future

	* Discovery URL: https://api.recordedfuture.com/taxii/

	* Username: <service account username>

	* Password: <API_KEY>

	* Certification: NOT NEEDED

	* Subscription ID: NOT NEEDED

	* Polling Interval: Please see the link below for best practices.

[Polling_Interval](https://support.recordedfuture.com/hc/en-us/articles/115010401968-Risk-List-Download-Recommendations)

![Step06](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CSE_steps/cse.step.6.png "Map List")

*	Click "Update"

Context Actions
===============

Context Actions allow an analyst to easily investigate IOCs in an external system anytime in their investigation process. 

Recorded Future makes this accessible with their deep-link to intelligence cards.

1.	To Set this up in CSE navigate to Configuration > Context Actions and click add.

2.	Add a context action for an IP address using this URL: https://app.recordedfuture.com/live/sc/entity/ip:{{value}}
 
![Step07_1](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CSE_steps/cse.step.7.1.png "IP-Address")

3.	Add a context action for a Hash using this URL: https://app.recordedfuture.com/live/sc/entity/hash:{{value}}
 
![Step07_2](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CSE_steps/cse.step.7.2.png "Hash")

4. 	Add a context action for a URL using this URL: https://app.recordedfuture.com/live/sc/entity/url:{{value}}

![Step07_3](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CSE_steps/cse.step.7.3.png "URL")
 
5. 	Add a context action for a domain using this URL: https://app.recordedfuture.com/live/sc/entity/idn:{{value}}
 
![Step07_4](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CSE_steps/cse.step.7.4.png "Domain")

6.	This context actions can now be used inside CSE. An example of a hash lookup:
 
![Step07_5](https://github.com/wks-sumo-logic/sumologic-rfsync/blob/master/doc/01_sumologic/CSE_steps/cse.step.7.5.png "Hash")

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

