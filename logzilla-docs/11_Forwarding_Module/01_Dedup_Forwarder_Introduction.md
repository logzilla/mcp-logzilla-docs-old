<!-- @@@title:Dedup Forwarder Introduction@@@ -->


# Preduplication Engine 

LogZilla's preduplication™ engine enables events to be forwarded and is a vital component for large network data management. This module allows customers to specify a "hold timer" (and optional match of specific events) which will forward a single event to a downstream receiver along with metadata about the number of times it happened in a given time period.

##### LogZilla Pre-Dup™ Algorithm and Process

![LogZilla Dedup Module](@@path/images/predup-engine-tm-1080x608.jpg)

In large networks, this capability saves companies millions due to the fact that when things go wrong, Network Devices, Firewalls, Servers, and Applications all generate more events more often. Because the original design for syslog was UDP-based, it also means they will send the same event repeatedly in the hopes that "something" is listening.

Take the following real-world "event storm" example:

##### Event Storm
![Duplex Storm](@@path/images/duplex_storm.jpg)

As seen, almost 1 Billion events were generated in a very short time. 

On the right side, LogZilla shows 70k to 90k of the same events being generated every minute. 

By using the LogZilla forwarding module, companies can still generate the information needed by downstream receivers without fear of degrading performance of those systems. 

In the case of the event storm above, the downstream receivers would have **received 4 events instead of 308,642**, but those 4 events would have had a count of the number of times the event was generated. 

# Forwarding Options

LogZilla NEO can forward events as a log or a trap, no matter how that event came into the system. For example, an incoming log can be sent as an SNMP Trap and an incoming SNMP Trap can be forwarded as a log. The same holds true for any incoming event type such as direct API inserts, webhooks, piped text, etc.







