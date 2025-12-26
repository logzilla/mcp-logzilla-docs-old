<!-- @@@title:Network Communications@@@ -->

# LogZilla Network Communications

LogZilla is able to receive communications via both TCP and UDP, over
multiple ports, and with different information formats.

The first type of communication LogZilla receives is *syslog*.  LogZilla
can receive syslog packets in both
[RFC 3164 (BSD)](https://datatracker.ietf.org/doc/html/rfc3164) and
[RFC 5424](https://datatracker.ietf.org/doc/html/rfc5424) formats.  By
default, LogZilla is configured to receive `RFC 3164` on port 514, via both
protocols `TCP` and `UDP`.  By default LogZilla is configured to receive
`RFC 5424` on port 601 via `TCP`.

In addition to *syslog*, LogZilla is able to receive raw data, not
formatted in syslog (either RFC) format.  This communication by default
is via both `TCP` and `UDP`, to port `516` (any text data), and `TCP` only, 
to port `515` (JSON data). The "raw" port is useful for devices that
send non-syslog or malformed syslog data, though in order for LogZilla
to make use of these log events, an app or rule must be used to interpret
the data.

The *raw* port can be configured using the `logzilla config` command, for 
either `SYSLOG_RAW_PORT` or `SYSLOG_RAW_UDP_PORT`, or `SYSLOG_JSON_PORT`
for the *JSON* port.  

```bash
root@demo [~]:# logzilla config SYSLOG_RAW_PORT 516
SYSLOG_RAW_PORT=516
```


The LogZilla user interface is available via HTTP(s) on ports 80 and 443 by
default. Additionally, those same ports can be used for event reception via
HTTP/HTTPS as noted in [Section
7.15](/help/receiving_data/receiving_events_using_http)

Some of the default ports can be re-configured via the following configuration 
settings:

|Configuration Option | Default | Description |
|--------------------- | ----- | ------------------------------------------------ | 
|`SYSLOG_BSD_TCP_PORT` | `514` | TCP port for incoming RFC3164/BSD syslog messages|
|`SYSLOG_BSD_UDP_PORT` | `514` | UDP port for incoming RFC3164/BSD syslog messages|
|`SYSLOG_RFC5424_PORT` | `601` | TCP port for incoming RFC5424 syslog messages    |
|`SYSLOG_JSON_PORT` | `515` | TCP port for incoming raw (non-syslog) JSON messages|
|`SYSLOG_RAW_PORT` | `516` | TCP port for incoming raw (non-syslog) messages|
|`SYSLOG_RAW_UDP_PORT` | `516` | UDP port for incoming raw (non-syslog) messages|
