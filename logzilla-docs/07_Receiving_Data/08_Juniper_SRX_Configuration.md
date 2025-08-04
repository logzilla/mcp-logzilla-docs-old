<!-- @@@title:Juniper SRX Configuration@@@ -->

# Juniper SRX Commands

Juniper devices should be configured to send logs in [RFC5424](https://www.rfc-editor.org/rfc/rfc5424.txt) `structured-data` format, also known as key=value pairs, rather than the older [RFC3164](https://www.rfc-editor.org/rfc/rfc3164.txt) "syslog" (a.k.a. BSD) style format.

To configure `sd-format`, the following steps should be used:

1. Enter edit mode
2. Set `stream` mode for events
3. Set the format for logging to structured
4. Set the source address to use (this is one of the local interfaces on the Juniper device itself, not the destination LogZilla server)
5. Set the destination log host (LogZilla)
6. Optional: Show the changes made
7. Optional: Check the syntax of changes to be made
8. Commit the changes

```
edit
set security log mode stream
set security log format sd-syslog 
set security log source-address 1.1.1.1 
set security log stream logzilla host 10.1.1.2 
show | compare 
commit check
commit
```

There is a rule available in the *Juniper* appstore app that will format each message to make it more readable, and create some user tags to highlight important information.  This rule is available to be installed from the `Settings -> App store` in the admin menu.

![Install Juniper appstore app](@@path/images/install-juniper-app.png)

<font size="1em" color="gray">This help section is provided only as a courtesy. LogZilla Corporation does not provide support for products outside of our own software.</font>
