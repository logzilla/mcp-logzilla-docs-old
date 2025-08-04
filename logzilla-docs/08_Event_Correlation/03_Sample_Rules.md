<!-- @@@title:Sample Rules@@@ -->


# Enabling SEC rules

To enable SEC you need:

* to prepare appropriate SEC-rules 
* add the appropriate configuration to the forwarder
* activate SEC and FORWARDER services:

``` bash
logzilla settings update SEC_ENABED=1 FORWARDER_ENABLED=1
```

## Sample SEC Rules

LogZilla comes pre-installed with a few sample rules to help users get started. 
Others may be found on
our [GitHub](https://github.com/logzilla/extras/tree/master/sec) repository.
The included sample rules are located on `/etc/logzilla/sec/example`
to help get you started.

An `.sec` file is a set of rules which tell the correlator how to match and
process incoming events, as noted in 
the [Rule Types](/help/event_correlation/event_correlation_rule_types) 
section of this guide.

For example:

```
# ----- Process reload and restart events -----

# Looks for a reload
#
type=single
continue=takeNext
ptype=regexp
pattern=(\S+) .?SYS-5-RELOAD: (.*)
desc=(WARNING) reload requested for $1
action=write - '%s details:$2'
action=shellcmd (logger -n $SYSLOG_HOSTNAME -P $SYSLOG_BSD_TCP_PORT \
                --rfc3164 -s -t SEC-ALERT '%s details:$2')


# Looks for a reload followed by a restart event
#
type=pairWithWindow
ptype=regexp
pattern=(\S+) .?SYS-5-RELOAD:
desc=(CRITICAL) $1 RELOAD_PROBLEM
action=shellcmd (logger -n $SYSLOG_HOSTNAME -P $SYSLOG_BSD_TCP_PORT \
                --rfc3164 -s -t SEC-ALERT %s)
ptype2=regexp
pattern2=($1) .?%SYS-5-RESTART:
desc2=(NOTICE) $1 RELOAD_OK
action2=shellcmd (logger -n $SYSLOG_HOSTNAME -P $SYSLOG_BSD_TCP_PORT \
                --rfc3164 -s -t SEC-INFO %s)
window=300

# Looks for a restart without reload command
#
type=single
ptype=regexp
pattern=(\S+) .?%SYS-5-RESTART:
desc=(CRITICAL) $1 restart without reload command
action=shellcmd (logger -n $SYSLOG_HOSTNAME -P $SYSLOG_BSD_TCP_PORT \
                --rfc3164 -s -t SEC-ALERT %s)
```

These three rules all share the same "flow", meaning that they work together 
to form a full Correlation.

Referencing the 
[Rule Types](/help/event_correlation/event_correlation_rule_types) help page,
we see that the rules used here are `Single` and `pairWithWindow`.

The first rule waits for a reload event sent by your devices. The pattern used
here is easy because we only need to send the Host and Message from the 
LogZilla forwarder in order to get the rule to trigger.

The next rule, `pairWithWindow`, tells the event correlator to wait 
for 5 minutes (300 seconds), to receive a `RELOAD` event followed by 
a `RESTART` event. If it does not arrive within 5 minutes, write a information
to stdout.

The last rule tells the EC to check for a `RESTART` event in case no 
prior `RELOAD` event has been seen.


# Editing/Adding SEC rules

A sample rule is included in LogZilla. You can edit this file in the
following directory.

```
/etc/logzilla/sec/example/sample.sec
```

or create new sec instance by creating a new subdirectory
in the `/etc/logzilla/sec/` and adding your rules there.


```
/etc/logzilla/sec/cisco-reload/rule1.sec
/etc/logzilla/sec/cisco-reload/rule2.sec
```

Putting the .sec config files in a separate directory will create
a separate SEC instance for those configuration files and use 
the directory name as the SEC instance name.

# Configuring forwarder for SEC

``` json
{
  "forwarders": [
    {
      "pre_match": {
        "field": "cisco_mnemonic",
        "value": "SYS-5-RELOAD"
      },
      "type": "sec",
      "name": "cisco-reload",
    }
  ]
}
```

To reload SEC instances you need to do:
```
logzilla settings reload sec forwardermodule
```

