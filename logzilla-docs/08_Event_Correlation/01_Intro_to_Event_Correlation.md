<!-- @@@title:Intro to Event Correlation@@@ -->


Event Correlation Methods
---
Event correlation generally includes the following concepts:

* Event triggers (when to correlate)
* Event filters (what to correlate)
* Event pairing (associations between multiple events)
* Event suppression (what to ignore)
* Time-based (window of time before something becomes important, or no longer important)

Event Correlation in LogZilla
---
LogZilla's forwarding rules can be used to send matched events to a well-known tool called SEC (Simple Event Correlator). SEC is already installed with LogZilla along with some sample rules to help you get started.

<iframe style="display: block; margin-left: auto; margin-right: auto;" width="560" height="315" src="https://www.youtube.com/embed/4eNEvCIbbic" title="Intro to Event Correlation | LogZilla University" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>


Flow
---
SEC is traditionally used as a pre-processor for systems where a log message would be sent to SEC before coming into LogZilla. However, because LogZilla is so scalable, SEC is not able to process such a large number of events.

Instead, we allow users to create forwarding rules to send only matched events needed for correlation. Sending only the events you actually care about greatly reduces the amount of strain put on the SEC tool.

This method also has the added bonus of being able to correlate events from more than just syslog messages (e.g.: SNMP Traps, etc.).

Traditional Method
---
`Syslog Daemon --> SEC --> Log Tool`
Scalable Method
---
`<Syslog, SNMP Traps, Webhooks, Files, any unstructured data, etc. --> LogZilla --> SEC`


About SEC
---
SEC was written by Risto Vaarandi and is available from the <a href="https://github.com/simple-evcorr/sec">SEC Github Page</a> as well as Debian-based Repositories (via apt-get)
