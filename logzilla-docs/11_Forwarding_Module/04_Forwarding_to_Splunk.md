<!-- @@@title:Forwarding to Splunk@@@ -->



LogZilla NEO may also be used to reduce the amount of data sent to Splunk systems while, at the same time, generating more value in that data.

LogZilla's preduplication module provides a way to allow Splunk to avoid having to deal with data storms.

The forwarding module works the same way in terms of configuration on the LogZilla side. On the Splunk side, a transform can be used to indicate the original sending host so that Splunk doesn't think all events are coming from the same system.

### `LZ_Forwarded_For`

To help Splunk determine the correct source host, the forwarder module config (See [Downstream Syslog Receivers](/help/forwarding_to_downstream_receivers/downstream_syslog_receivers)) should add a `LZ_Forwarded_For ` key/value pair. 

## Splunk Setup

On your Splunk server, create or edit `$SPLUNK_HOME/etc/system/local/transforms.conf` and add:

**Splunk Transforms**

```
[logzilla_forwarder]
REGEX = LZ_Forwarded_For=(\S+)
FORMAT = host::$1
DEST_KEY = MetaData:Host
```

Next, create or edit the file `$SPLUNK_HOME/etc/system/local/props.conf` and associate the transform to your source. In the case of [this example](/help/forwarding_to_downstream_receivers/downstream_syslog_receivers), we're sending everything via TCP port 514, so the source used in Splunk's `props.conf` will be that.

**Splunk Props**

```
[source::tcp:514]
TRANSFORMS-lz_neo=logzilla_forwarder
```

For options on Splunk's transforms and props files, please reference [Splunk's Documentation](https://docs.splunk.com/Documentation/Splunk/7.2.5/Data/Overridedefaulthostassignments) for further help.





