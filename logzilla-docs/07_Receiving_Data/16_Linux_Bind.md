<!-- @@@title:Receiving Events from Linux Bind@@@ -->

# Linux Bind DNS Event Query Logging

This documentation provides a comprehensive guide on how to send Linux
BIND logs to LogZilla. LogZilla enables you to unlock the full potential
of your network data, turning what would be a deluge of logs into
actionable insights. Linux BIND, being a crucial part of your networking
infrastructure, should be seamlessly integrated into your log management
solution.

BIND is the most widely used Domain Name System (DNS) software on the
internet, developed and maintained by the Internet Systems Consortium.
It is an open-source software that allows users to publish their Domain
Name System (DNS) information on the Internet, and to resolve DNS
queries for their users.

In the sections that follow, you will learn how to configure your named
server, set up Syslog-ng and Rsyslog, and how to ensure that your named
server has the correct configuration for sending logs via Syslog. We
also explain how to forward these events to LogZilla through Syslog-ng
or Rsyslog, as BIND does not directly support sending Syslog to a remote
server.

# Prerequisites

Before proceeding with the steps detailed in this documentation, it’s
necessary to ensure that you have a few components set up and running.
Below is a list of prerequisites needed to successfully send Linux BIND
logs to LogZilla:

- **A functioning BIND setup:** This documentation assumes you have a
  Linux server running BIND. This server should be configured and
  functioning correctly to serve DNS requests. If you’re not yet set up
  with BIND, consult the official BIND documentation to get started.

- **A LogZilla instance:** You need an operational LogZilla instance to
  send your BIND logs to. LogZilla can be deployed on many platforms,
  from on-premise servers to cloud environments. If you don’t have a
  LogZilla instance running, please refer to the LogZilla installation
  guide.

- **Syslog-ng or Rsyslog:** You will need one of these logging systems
  installed and correctly configured on your BIND server. These systems
  will facilitate forwarding logs from your local server to the remote
  LogZilla server.

- **Root or sudo privileges:** In order to edit configuration files and
  restart services, you’ll need root or sudo privileges on the server
  where BIND is installed.

- **Network access:** The BIND server must have network access to the
  LogZilla server. Ensure any firewalls or security groups allow traffic
  between these servers on the necessary ports.

Once these prerequisites are met, you can move forward to configure the
named server.

# Sending Linux BIND Logs to LogZilla

## Configuring Named Server

Configuring the Named server is the first crucial step in forwarding
BIND logs to LogZilla. The configuration of the named server involves
modifying the existing BIND configuration to send logs to the local
syslog server.

### Updating Named Config

To set up your named server for log sending, you need to modify the
`/etc/bind/named.conf.options` file. Please replace or update the
logging section with the configuration below. This configuration directs
BIND to send logs to the local syslog server.

``` yaml
logging {
        channel syslog {
                syslog local0;
                severity info;
                print-severity yes;
                print-category yes;
        };
        category lame-servers { null; };
        category default { syslog; };
        category queries { syslog; };
        # if there are no other 'category' statements,
        # it will include everything except query logging.
};
```

This configuration sets up a syslog channel with severity info and
enables the printing of both severity and category information. It sets
the default and queries categories to send logs via the syslog channel.
It also sends the lame-servers category to null, discarding any logs of
this type.

Save and exit the file after adding this configuration.

## Configuring Syslog-ng

The next step is configuring Syslog-ng or rsyslog. While BIND can’t directly send
logs to a remote server, it can send them to a local syslog server.
Syslog-ng or Rsyslog can then forward those logs to your LogZilla
server.

### Setting up Syslog-ng Config

Here is the process to configure Syslog-ng:

1.  Check the main Syslog-ng configuration file located at
    `/etc/syslog-ng/syslog-ng.conf` and ensure that `s_src` is defined
    in this file. It should look similar to the following:

        source s_src {
               system();
               internal();
        };

2.  Create a new file named `/etc/syslog-ng/conf.d/named.conf` and add
    the destination for your LogZilla server. Replace `1.2.3.4` with the
    IP address or hostname of your LogZilla server. The configuration
    should look something like this:

    ``` yaml
    destination d_logzilla {
        udp("1.2.3.4" port(514));
    };

    log {
      source(s_src);
      destination(d_logzilla);
    };
    ```

In the configuration above, `destination d_logzilla` defines the
destination that represents your LogZilla server. In the log block, the
logs from the source `s_src` are being sent to this destination.

3.  Save and exit the file after adding the configuration.

## Configuring Rsyslog

For those using Rsyslog instead of Syslog-ng, you can also set it up to
forward BIND logs to your LogZilla server.

To configure Rsyslog, follow these steps:

1.  Open the Rsyslog configuration file, which is typically located at
    `/etc/rsyslog.conf`.

2.  Add the following lines to the end of the file, replacing `1.2.3.4`
    with the IP address or hostname of your LogZilla server and `514`
    with the port number where your LogZilla server is listening for
    incoming logs.

    ``` yaml
    *.* @@1.2.3.4:514
    ```

    In this configuration, `*.*` means that logs of all facilities and
    of all priorities will be forwarded. The `@@` symbol means that logs
    will be sent via TCP. If you want to send logs via UDP, use a single
    `@`.

3.  Save and close the Rsyslog configuration file.

## Restarting Syslog-ng, Rsyslog and Named Services

Now that you have configured BIND, Syslog-ng, and Rsyslog, it’s time to
restart these services for the changes to take effect.

To restart these services, use the systemctl command as shown below:

``` bash
systemctl restart syslog-ng
systemctl restart rsyslog
systemctl restart named
```

Note: Only restart the service you are using to forward logs, i.e., if
you’re using Syslog-ng, you don’t need to restart Rsyslog, and vice
versa.

Once you restart the services, they should begin forwarding the logs to
your LogZilla server.

# Troubleshooting

Even with careful configuration, there’s always a chance that something
may not work as expected. This section provides some basic
troubleshooting tips if you’re having trouble sending Linux BIND logs to
LogZilla.

- **Check BIND configuration:** Make sure the `named.conf.options` file
  has the correct settings for logging. Errors in the configuration may
  prevent logs from being sent.

- **Verify Syslog-ng or Rsyslog configuration:** Confirm that the
  configuration file for Syslog-ng or Rsyslog has the correct
  destination for your LogZilla server.

- **Check service statuses:** Use the `systemctl status` command to
  check if BIND, Syslog-ng, or Rsyslog services are running properly.
  For example, `systemctl status named` would show the status of the
  BIND service.

- **Check firewall rules:** If your logs are not appearing in LogZilla,
  there may be a firewall rule preventing your BIND server from
  communicating with your LogZilla server. Ensure that traffic on the
  relevant ports is allowed.

- **Inspect log files:** Checking the Syslog-ng or Rsyslog and BIND logs
  can provide clues about any issues. These logs typically contain error
  messages or other information about what the service is doing.

- **Use diagnostic tools:** Tools like `tcpdump` or `wireshark` can be
  useful to see if log data is leaving your BIND server and arriving at
  your LogZilla server.

Remember, troubleshooting is often a process of elimination. By working
through potential issues one by one, you should be able to identify and
resolve any issues.
