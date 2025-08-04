 <!-- @@@title:Correlating Windows Events@@@ -->

## Sample Windows Event Correlation

LogZilla can be used with Simple Event Correlator 
[SEC](https://simple-evcorr.github.io/)
to supplement Windows event log messages for use in reporting and alerting.

**Example Problem**

The event log service is critical to maintaining awareness of operations
performed on or by the system of interest.  It would be desirable to track
event log startup after event log shutdown in order to verify that any time
window in which event logging is turned off is minimal.  This example will
verify that the event log service is restarted after no more than 10
seconds since shutdown.

LogZilla will receive the following events from the Windows Syslog Agent:
![LogZilla Windows Event Log events](@@path/images/windows_eventlog_shutdownstartup.png)

Event message #1:
```
DESKTOP-K2HQUHV EventLog The Event log service was stopped.
```

Event message #2:
```
DESKTOP-K2HQUHV EventLog The Event log service was started.
```

**Example Solution**

#### Prepare SEC rule

`/etc/logzilla/sec/windows-shutdown-startup/rule.sec`:

``` text
#
# SEC rule for Windows event log shutdown / startup
#

type=PairWithWindow
ptype=RegExp
pattern=(\S+) \S+ The Event log service was stopped"
desc=Event log service on $1 has been down for over 10 seconds.
action=shellcmd (logger -n $SYSLOG_HOSTNAME -P $SYSLOG_BSD_TCP_PORT \
                --rfc3164 -s -t SEC-ALERT %s)
ptype2=RegExp
pattern2=(\S+) \S+ The Event log service was started"
desc2=Event log service on $1 successfully restarted within 10 seconds.
action2=logonly
window=10 
```

SEC instance will be watching incoming events for `pattern` to occur.
If the pattern is matched an SEC operation will be created for that hostname 
and the rule will start watching for `pattern2` to occur within 
the specified 10 second window.

If `pattern2` is seen then the SEC operation performs `action2`, which
specifies to merely log the paired operation, and removes that SEC
operation. However if it is *not* seen then `action` (the first) will fire
which will create new event using `desc` as message body and send it to
LogZilla via syslogng protocol. 
`$SYSLOG_HOSTNAME` and `$SYSLOG_BSD_TCP_PORT` are environment variables 
injected by LogZilla during SEC server start.


#### Forwarder configuration

``` json
{
  "forwarders": [
    {
      "pre_match": {
        "field": "message",
        "op": "=~",
        "value": "The Event log service was (stopped|started)"
      },
      "type": "sec",
      "name": "windows-shutdown-startup",
    }
  ]
}
```

#### Reload SEC and Forwarder

Apply configuration and reload modules:

``` bash
logzilla settings reload sec forwardermodule
```
