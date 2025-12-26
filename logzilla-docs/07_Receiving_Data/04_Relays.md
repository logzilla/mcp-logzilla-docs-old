<!-- @@@title:Relays@@@ -->

# Syslog Relays

As noted in [Syslog Basics](/help/administration/syslog_basics), relays
are used to forward events from other sources to another server that needs
to receive those logs (like LogZilla).

Relays serve several important purposes in a log management infrastructure:

- Provide a local collection point for network segments
- Reduce network traffic across WAN connections by aggregating logs
- Add an additional layer of reliability to your logging infrastructure
- Filter events before forwarding them to your main log server

## Traditional Syslog Relays

### Syslog-ng

If your relay host uses syslog-ng, the following file may be used to forward
events to LogZilla.

```text
# This is for your *relay* server (not the LogZilla server)
# filename: /etc/syslog-ng/conf.d/logzilla-relay.conf
 
#Global Options
options {
  flush_lines(100);
  threaded(yes);
  use_dns(yes);
  use_fqdn (no);
  keep_hostname (yes);
  dns-cache-size(2000);
  dns-cache-expire(87600);
};
 
source s_network {
 
# port 514 (tcp) is used for RFC3164 formatted events coming in (standard BSD-style logs)
  network(
      transport("tcp")
      port(514)
  );
 
# port 514 (udp) is used for RFC3164 formatted events coming in (standard BSD-style logs)
  network(
      transport("udp")
      so_rcvbuf(1048576)
      flags("no-multi-line")
      port(514)
  );
 
destination d_logzilla {
  network(
    "<IP OR HOSTNAME OF LZ SERVER>"
    port(514)
    transport(tcp)
  );
};
 
log {
    source(s_logzilla);
    # disable s_src if you don't want local server events
    source(s_src);
    source(s_network);
    destination(d_logzilla);
    flags(flow-control);
};
```

### Rsyslog

There are primarily two formats used for the syslog protocol. Users may
configure either RFC-3164-based forwarding or RFC-5424-based forwarding
from their rsyslog relays.

#### RFC 3164 (default)

To forward logs to LogZilla using the standard format, create a file in
`/etc/rsyslog.d/` using a `.conf` extension (i.e. `20-logzilla.conf`).
This is the *config* file. Place the following line in that file:

```text
*.*   action(type="omfwd" Target="${logzillaIP}" Port="514" Protocol="tcp")
```

Replace `${logzillaIP}` with the IP Address (or resolvable name) of your
LogZilla server.

After adding the new config file run:

```text
service rsyslog restart
```

#### RFC 5424

To send messages using the RFC 5424 method, replace content of the config
file with:

```text
*.*   action(type="omfwd" Target="${logzillaIP}" Port="514" Protocol="tcp"
             Template="RSYSLOG_SyslogProtocol23Format")
```

#### Multiline logs

If your logs contain multiple lines (the messages have embedded *newlines*),
then use RFC5424 protocol but also add `TCP_Framing="octet-counted"` to the
*action* above. The configuration would then look like this:

```text
*.*   action(type="omfwd" Target="${logzillaIP}" Port="514" Protocol="tcp"
             Template="RSYSLOG_SyslogProtocol23Format" TCP_Framing="octet-counted")
```

As an example, to read multiline events from the Tomcat log file this
configuration could be used:

```text
input(type="imfile"
    File="/var/log/tomcat.log"
    Tag="applog"
    Severity="info"
    escapeLF="off"
    startmsg.regex="^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2},"
)
```

## Secure Relay Communication with TLS/SSL

For environments requiring secure log transmission, both syslog-ng and
rsyslog support TLS/SSL encryption.

### Syslog-ng with TLS

Add the following destination to your syslog-ng relay configuration:

```text
destination d_logzilla_tls {
  network(
    "<IP OR HOSTNAME OF LZ SERVER>"
    port(443)
    transport(tls)
    tls(
      ca_dir("/etc/syslog-ng/ca.d")
      key_file("/etc/syslog-ng/key.d/relay-key.pem")
      cert_file("/etc/syslog-ng/cert.d/relay-cert.pem")
    )
  );
};
```

Update your log path to use this destination for secure forwarding.

## HTTP/HTTPS Relay Option

As an alternative to traditional syslog forwarding, you can configure
syslog-ng to forward logs to LogZilla over HTTP/HTTPS. This approach
provides several advantages:

- Web-friendly transmission allowing logs to traverse firewalls
- Authentication via tokens
- Structured data in JSON format
- Better handling of metadata via user tags

For detailed setup instructions, refer to
[Syslog-ng HTTPS setup](https://docs.logzilla.net/07_Receiving_Data/14_Syslogng_HTTP_Receiver/).

### Rsyslog with TLS

For rsyslog, create a configuration with TLS support:

```text
$DefaultNetstreamDriver gtls
$DefaultNetstreamDriverCAFile /etc/rsyslog.d/keys/ca.pem
$DefaultNetstreamDriverCertFile /etc/rsyslog.d/keys/client-cert.pem
$DefaultNetstreamDriverKeyFile /etc/rsyslog.d/keys/client-key.pem

$ActionSendStreamDriverAuthMode x509/name
$ActionSendStreamDriverPermittedPeer <SERVER_NAME>
$ActionSendStreamDriverMode 1

*.* action(type="omfwd" Target="${logzillaIP}" Port="443" Protocol="tcp")
```

## LogZilla as a Relay (Forwarding Module)

LogZilla itself can act as a relay, forwarding events to other systems such as:

- Other syslog servers
- Splunk via HTTP Event Collector
- SNMP trap receivers
- Local files

This functionality lets you use LogZilla for event processing, deduplication,
and correlation while still forwarding selected events to other systems for
additional analysis.

For configuration details, see
[Downstream Syslog Receivers](https://docs.logzilla.net/07_Receiving_Data/15_Downstream_Syslog_Receivers/).

## Relay Best Practices

For optimal relay performance and reliability, follow these guidelines:

1. **Use TCP instead of UDP** whenever possible for better reliability.

2. **Implement proper load balancing** for high-volume environments by setting
up multiple relays.

3. **Configure disk buffering** on relays to prevent message loss during
network outages:

   ```text
   # For syslog-ng
   destination d_logzilla {
     network(
       "<IP OR HOSTNAME OF LZ SERVER>"
       port(80)
       transport(tcp)
       disk-buffer(
         mem-buf-size(10000)
         disk-buf-size(2000000)
         reliable(yes)
       )
     );
   };
   ```

4. **Monitor relay performance** to ensure logs are flowing properly and the
relay is not becoming a bottleneck.

5. **Include identifying information** in forwarded messages to track which
relay processed each event:

   ```text
   # For syslog-ng
   rewrite r_add_relay_info {
     set("relay-server-1", value("relay_id"));
   };
   ```

6. **Apply initial filtering at the relay level** to reduce unnecessary traffic
to your central LogZilla server.

7. **For WAN connections**, implement both local and remote relays to ensure
reliable log delivery across unreliable networks.

> **Note:** This help section is provided only as a courtesy.
LogZilla Corporation does not provide support for products outside of our own
software.
