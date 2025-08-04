<!-- @@@title:Downstream Syslog Receivers@@@ -->

# Downstream Syslog Receivers

The Forwarder module allows LogZilla to forward all or specific matched events to
downstream log receivers. These destinations are not limited to `syslog` receivers;
the module also supports `file`, `splunk-hec`, and `snmp` destinations.

## Enable the Module

To enable the Forwarder Module, enter the following command in the
LogZilla server's console/ssh terminal:

```bash
logzilla config FORWARDER_ENABLED 1
```

### Forwarder Configuration Files

LogZilla uses a main forwarder configuration file, which contains configuration
options that take effect for all forwarders, and can contain definitions for one
or more specific individual forwarders. LogZilla also allows individual forwarder
configurations for multiple forwarding rules to be separated into individual
files for easier administration.

The default forwarder configuration file is `/etc/logzilla/forwarder.yaml`.
Individual forwarder configuration files can also be used (in addition to the
default file). The files can consist of JSON (`.json`) or YAML (`.yaml`).
Each file defines a particular forwarder configuration, one forwarder per file,
using the same syntax and options as specified in the `forwarders` configuration
element as explained above.

For example, a simple configuration in `/etc/logzilla/forwarder.d/non-dedup.yaml`
might contain the following:

```yaml
window_size: 0
type: file
path: /var/log/logzilla/non-dedup.log
```

## Configure Rules

### Examples of forwarder configuration files

Here are some example configurations for forwarder configuration files:

#### Forward to host A

```yaml
---
window_size: 60
forwarders:
- type: syslog
  target: 192.168.0.114:514
  transport: tcp
  unsent_buffer_limit: 250000
  protocol: rfc5424
  rules:
  - match:
      field: counter
      op: gt
      value: 1
    rewrite:
      message: $MESSAGE LZ_Forwarded_For="$HOST" LZ_dedupCount="$COUNTER"
  - match:
      field: counter
      op: le
      value: 1
    rewrite:
      message: $MESSAGE LZ_Forwarded_For="$HOST"
fast_forward_first: true
```

#### Forward to host B

```yaml
---
window_size: 60
forwarders:
- type: syslog
  target: 192.168.0.117:514
  transport: udp
  protocol: bsd
  rules:
  - match:
      field: counter
      op: gt
      value: 1
    rewrite:
      message: $MESSAGE LZ_Forwarded_For="$HOST" LZ_dedupCount="$COUNTER"
  - match:
      field: counter
      op: le
      value: 1
    rewrite:
      message: $MESSAGE LZ_Forwarded_For="$HOST"
fast_forward_first: true
```

#### Forward to file

```yaml
---
window_size: 1
fast_forward_first: true
forwarders:
- match:
    field: cisco_mnemonic
    value: BGP-5-ADJCHANGE
  type: file
  target: "/var/log/logzilla/sec/simple.log"
  format: tsv
  separator: "\t"
  fields:
  - last_occurrence
  - host
  - message
```

#### IMPORTANT: `LZ_Forwarded_For`

Downstream receivers such as Splunk (See
[Forwarding to Splunk](/help/forwarding_to_downstream_receivers/forwarding_to_splunk))
will need to know which host the event originated from. This rule adds a key/value
pair for the downstream systems to parse and use as the original sending host.
Otherwise, all events would appear to come from your local LogZilla server.

## Forwarder Configuration Options

The following configuration options can be defined in the main `forwarder.yaml` file
(JSON format is also supported with a `.json` extension):

### Global Options

`match`  
A filter that defines which events should be forwarded. The syntax is identical to
that used in [Match Conditions in Rewrite Rules](/help/data_transformation/rewrite_rules).
This serves as a global filter affecting all forwarders, but can also be configured
in individual forwarders.

`window_size`  
The default time (in seconds) to retain messages while checking for duplicates.
If not specified for a particular forwarder, this value is used. Higher values
improve deduplication efficiency but introduce longer forwarding delays, as each
message is held for the specified duration before forwarding. Setting this to `0`
disables deduplication completely.

`fast_forward_first`  
The default behavior for handling the first unique occurrence of an event. When set
to `true` (default), the first occurrence is forwarded immediately, while subsequent
duplicates are collected and forwarded at the end of the window. When set to
`false`, the first occurrence is grouped with its duplicates and all are forwarded
together at the end of the window.

`forwarders`  
This section defines forwarders. Multiple forwarders and mixing Syslog and SNMP
trap destinations may be used. Every element of the `forwarders` table has a
mandatory field `type` which defines what type of forwarder it is - currently
`snmp`, `syslog`, `file`, and `splunk-hec` are supported. Other fields depend on
the forwarder type.

For example, the following would forward to both an SNMP Trap receiver and a
Syslog receiver:

```yaml
---
forwarders:
- oid_map:
  - oid: ".1.2.0"
    src: facility
    type: s
  - oid: ".1.3.0"
    src: severity
    type: i
  - oid: ".1.4.0"
    src: cisco_mnemonic
    type: s
  - oid: ".1.5.0"
    src: message
    type: s
  - oid: ".1.99.0"
    src: counter
    type: i
  oid_prefix: 1.3.6.1.4.1.9.9.41.1.2.3
  target: snmp-server:162
  trap_oid: 1.3.6.1.4.1.2021.991
  type: snmp
- protocol: bsd
  rules:
  - match:
      field: counter
      op: gt
      value: 1
    rewrite:
      message: "$MESSAGE LZ_dedupCount=$COUNTER"
  target: central-log-collector:514
  transport: tcp
  type: syslog

```

### Forwarder Configuration

Every forwarder has two mandatory fields: `type` and `target`. Additional fields may
be required depending on the forwarder type.

#### Common Options for All Forwarder Types

The following options can be used with any forwarder type:

`match`  
Defines which events this specific forwarder will process. Works the same way as the
global `match` option but applies only to this specific forwarder.

`window_size`  
Overrides the global `window_size` setting for this specific forwarder.

`fast_forward_first`  
Overrides the global `fast_forward_first` setting for this specific forwarder.

`rules`  
Defines transformation rules to be applied to events before forwarding. You can
specify any list of rules that will be applied to the event in order before it is
forwarded. The syntax is identical to that used in
[Rewrite Rules](/help/data_transformation/rewrite_rules).

#### Forwarder Options for Particular Forwarder Types

##### Syslog

`target`  
This is host and port of the target syslog server.

`transport`  
Either `tcp` or `udp`. The `tcp` transport can operate in either blocking or
non-blocking mode depending on the configuration.

`unsent_buffer_limit`  
The maximum number of events (post predup) that will be buffered in case the
destination is down. If the destination comes back up before overflowing, events
will be forwarded in the original order. Otherwise, the buffer is emptied.
Defaults to 25000. Applies only to `tcp` transport. Note that buffering is
enabled **after** the forwarder realizes that the destination is down, which might
be significantly later depending on network communication.

`protocol`  
Either `bsd` for the classic (RFC3164) protocol or the newer `rfc5424` protocol

`octet_count`  
Use the octet counting framing method for sending messages.

#### File

This forwarder saves all forwarded events in a file, in json or TSV format, one
line per event.

`target`  
The path to the file where events are to be saved. This is a path in the container
`lz_forwarder_module`, so this file can be accessed with docker cp or via
`logzilla shell -c forwarder`. Previously known as `path`, which is still
supported for backward compatibility. Also, if desired, this file can be saved
directly on the host file system if the file is put in a path inside the
`/var/log/logzilla/` directory, because that directory (and subdirectories) is
shared between the host and the LogZilla docker container.

`format`  
Defaults to `json`, in which case it always save whole event. Another option is
`tsv` which uses tab separated values, but other separators can be specified
(defaults to TAB); with TSV format a list of fields that are written to output
file can be provided.

`separator`  
For the TSV format this is the string used to separate fields (defaults to TAB).

`fields`  
The array of fields to be written in TSV format (defaults to
`["host", "program", "message"]`).

`rotate_period`  
The time in seconds after which log file will be renamed with `.0` appended (so if
it's `fwd.log` it will become `fwd.log.0`), and then the original path will be
reopened as an empty file. As appropriate, each previous `.0` file will
overwritten so there is always no more than just two log files - the previous and
the current one. The default value of 0 disables rotation completely.

#### Splunk-HEC

This forwarder sends events in JSON format to Splunk HTTP Event Collector. The
receiving splunk instance should be configured to: have a Splunk HEC source
enabled; have a HEC token; globally enable HTTP source; and disable SSL (for now
only http is supported). Documentation for these Splunk settings is available in the
[Splunk HTTP Event Collector documentation](https://docs.splunk.com/Documentation/Splunk/latest/Data/UsetheHTTPEventCollector).

`target`  
The address in the format `HOST`, `HOST:PORT` or `http://HOST:PORT`, where `HOST`
and `PORT` are replaced with the actual values of the host name and TCP/UDP port.
If `PORT` is omitted, the default splunk value of `8088` is used. HTTPS is not
supported for now.

`token`  
The HEC token as specified in Splunk.

#### SNMP

This forwarder sends an SNMP Trap for each matching event. A list of variables
that will be added to the trap can be defined, with values copied from the
particular fields of event.

`target`  
This is the host and port of the SNMP server.

`trap_oid`  
This will be set as the type of outgoing SNMP trap.

`oid_prefix`  
Whenever `oid` in the map starts with a dot, it will be prefixed with this prefix.

`oid_map`  
This is the list of variables that will be added to the trap. For every variable
you define:

`type`  
For now only `i` (32 bit integer) and `s` (string) are supported.

`oid`  
The object id of this variable; if it starts with a dot then it is prefixed with
`oid_prefix`.

`src`  
The name of the event field variable in which the value will be set.

`value`  
If no `src` is defined, a constant can be configured here that will be copied for
this value.

## Add the Forwarder Configuration(s)

There are two methods to implement your forwarder configuration:

### Method 1: Using the LogZilla command line utility

Use the following command:

```bash
logzilla forwarder import -I NEW_CONFIG
```

Where `NEW_CONFIG` is the path to your forwarder configuration file. The file
doesn't need to be named `forwarder.yaml` or `forwarder.json` when using this
method.

### Method 2: Manual file placement

Copy the configuration file to the appropriate directory:

```bash
cp forwarder.yaml /etc/logzilla
```

### Configuration Locations

Forwarders can be configured in two locations:

1. In the main `/etc/logzilla/forwarder.yaml` or `/etc/logzilla/forwarder.json`
   file using the `forwarders` element as described above.
2. In individual configuration files placed in the forwarder configuration
   directory.

To use individual forwarder configuration files, place each file in the
`/etc/logzilla/forwarder.d` directory:

```bash
cp non-dedup.yaml /etc/logzilla/forwarder.d
```

## Restart LogZilla Modules to Enable New Configurations

After adding or modifying any forwarder configuration, restart the `forwarder`
module to apply your changes:

```bash
logzilla restart -c forwardermodule
```
