<!-- @@@title:Using TLS Tunnels@@@ -->

### LogZilla Server Configuration

#### Creating LogZilla Server SSL Keys

During this process, you’ll be prompted for a passphrase to create the
keys. Once created, the passphrase will be removed. You’ll also be asked
for the server’s name, location, and contact information. Make sure the
server name matches the entry in your `/etc/hostname` file.

To generate a new key, run the following command:

    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout tls.key -out tls.crt

Provide the requested identification information:

    Country Name (2 letter code) [AU]:US
    State or Province Name (full name) [Some-State]:New York
    Locality Name (eg, city) []:New York City
    Organization Name (eg, company) [Internet Widgits Pty Ltd]:Bouncy Castles, Inc.
    Organizational Unit Name (eg, section) []:Ministry of Water Slides
    Common Name (e.g. server FQDN or YOUR name) []:server_IP_address
    Email Address []:admin@your_domain.com

After creating the keys, copy them to the `syslog-ng` directory:

    cp tls.key tls.crt /etc/logzilla/syslog-ng

The correct paths for the key and certificate files are:

| Purpose     | Path                              |
|-------------|-----------------------------------|
| Key         | `/etc/logzilla/syslog-ng/tls.key` |
| Certificate | `/etc/logzilla/syslog-ng/tls.crt` |

#### Configuring *syslog-ng*

By default, LogZilla uses port `6514` for incoming TLS connections. You
can change this (for example, to `12345`) with the following command:

    logzilla config SYSLOG_TLS_PORT 12345

Enable TLS support:

    logzilla config SYSLOG_TLS_ENABLED 1

LogZilla’s *syslog* server will restart automatically. To check if TLS
support is working, use the `openssl` command as shown below. Replace
`11.22.33.44:12345` with your LogZilla server address and TLS port.

    $ openssl s_client -connect 11.22.33.44:12345 < /dev/null

If the output shows your identification information (`C`, `ST`, `L`,
`O`, etc.), certificate details from your `tls.crt` file, and TLS cipher
and key specifications in use, then TLS support is operational.

If you see an error like the following, verify your steps from the start
of this document and restart if necessary:

    $ openssl s_client -connect 192.168.10.12:1234 < /dev/null

### Adding Key Files to Client Systems

On the syslog-sending system, create a new directory:

    mkdir -p /etc/syslog-ng/ssl

Transfer the key and certificate files created earlier on the **LogZilla
Server** to the **Client** system, placing them in the
`/etc/syslog-ng/ssl` directory. You can use `scp` or a similar method.

### Configuring *syslog-ng* on the Client

There are two scenarios:

1.  You have a local LogZilla instance and want to forward events to
    another LogZilla instance.
2.  You have a standalone syslog-ng on your client server and want to
    forward events to a LogZilla instance.

#### Forwarding Events from One LogZilla Instance to Another

Replace `LZ_SERVER` below with the DNS Name or IP Address of your
LogZilla Server. Change port number accordingly if you configured a
different port number at the receiving site. Also, in the `log{}`
section, you may need to update the `source` according to the sources
configured in your `/etc/syslog-ng/syslog-ng.conf` file.

Create a new file named `/etc/syslog-ng/conf.d/tls_to_LogZilla.conf` and
put the following content into it:

``` yaml
destination d_tls {
    syslog-ng(
        server("LZ_SERVER")
        port(6514)
        transport(tls)
        tls(ca-file("/etc/syslog-ng/ssl/tls.crt"))
    );
};

log {
  source(s_src);
  destination(d_tls);
};
```

Restart syslog-ng on the Client system by typing:

    service syslog-ng restart

#### Checking configuration

Check your LogZilla server to verify that events are now being received
from this Client.

If you encounter any issues, refer to the [Debugging Event
Reception](/help/receiving_data/debugging_event_reception) section of
this guide.

### Advanced server configuration

If you need more than just a single source port with TLS transport, TLS
can be added to any syslog source by directly editing the
`/etc/logzilla/syslog-ng/config.yaml` file. Find the `sources` array
element and for any source, you can add `transport: tls` and then
`tls_key_file` and `tls_cert_file` options. For example, to enable TLS
transport for JSON input, add this:

``` yaml
  - name: json-tls
    enabled: True
    type: network
    transport: tls
    port: 6515
    tls_cert_file: "/etc/logzilla/syslog-ng/tls.crt"
    tls_key_file: "/etc/logzilla/syslog-ng/key.crt"
    flags:
      - no-parse
    program_override: _JSON
```

After any change to this configuration file, the LogZilla *syslog*
module must be restarted by:

    logzilla restart -c syslog
