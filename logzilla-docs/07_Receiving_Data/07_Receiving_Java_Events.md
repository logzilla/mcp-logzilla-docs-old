<!-- @@@title:Receiving Java Events@@@ -->


Logging Java Events
---

On many systems, Java may not be configured properly to send events to a syslog server (or to send to syslog at all). log4j is the typical method used for sending events, but the format is usually quite poor. To fix this, users must edit their `log4j.properties` file on the sending host.


# Examples

The example below uses Jira, a DevOps tool created by [Atlassian](https://www.atlassian.com). The same settings used below can be used on any `log4j`-based software.

In this example, it is assumed that Jira is installed at `/opt/atlassian/jira/atlassian-jira/WEB-INF/classes/log4j.properties`.

In Ubuntu, typing `locate log4j.properties` will help find the file.

Once `log4j.properties` is located, open it and find the line similar to:

```
log4j.rootLogger=WARN, console, filelog
```
And append `, SYSLOG`, e.g.:

```
log4j.rootLogger=WARN, console, filelog, SYSLOG
```
Next, at the bottom of the file, append the following lines and replace `<IP_ADDRESS>` with the IP Address of your LogZilla server.

```
log4j.appender.SYSLOG.threshold=INFO
log4j.appender.SYSLOG=org.apache.log4j.net.SyslogAppender
log4j.appender.SYSLOG.syslogHost=<IP_ADDRESS>
log4j.appender.SYSLOG.layout=org.apache.log4j.EnhancedPatternLayout
log4j.appender.SYSLOG.Header=true
log4j.appender.SYSLOG.layout.ConversionPattern=java %m - threadName=%t className=%C{1} methodName=%M{3}%n
log4j.appender.SYSLOG.Facility=LOCAL0
```

You may need to restart your Java application before it will begin sending syslog events to LogZilla.




# Fun With Rewrites

LogZilla's rewrite capability along with user tags (metadata extraction) allows for transformation of thread names as well as setting the program name to something less generic than `Java`.

Example rewrite rule:


```yaml
rewrite_rules:
- comment: transform java thread to program name containing `localhost`
  match:
    field: message
    op: "=~"
    value: "(.+) - threadName=localhost-([a-z]+).* className=(.+) methodName=(.+)"
  rewrite:
    message: "$1 - threadName=$2 className=$3 methodName=$4"
- comment: Rewrite Java Events
  match:
  - value: java
    field: program
  - field: message
    op: "=~"
    value: "(.+) - threadName=([a-z]+).* className=(.+) methodName=(.+)"
  rewrite:
    program: Java-$2
    message: "$1"
  tag:
    Java ClassNames: "$3"
    Java MethodNames: "$4"
```

To activate the above rule, save the above contents into a file (such as `300-java-rule.json`) then do `logzilla rules add 300-java-rule.json`.  Now if you do `logzilla rules list` you should see:
```
Name                      Source           Type    Status    Errors
------------------------  ---------------  ------  --------  --------
...
300-java-rule             user             parser  enabled   -
...
```

# Result

By using the rule above, the UI will now provide widgets such as:

**Class and Method Categories**
![Class and Method Names](@@path/images/log4j-widgets.png)
![Widget Config](@@path/images/java-widget-settings.png)

**Live Search (showing transformed program names)**
![Search](@@path/images/java-events.png)









