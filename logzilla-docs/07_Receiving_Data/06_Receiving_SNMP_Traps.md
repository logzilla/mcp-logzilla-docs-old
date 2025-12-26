<!-- @@@title:Receiving SNMP Traps@@@ -->

# Enabling SNMP Trap Reception

LogZilla includes the ability to receive SNMP Traps. To enable it, simply do so from the Admin menu in the UI under `Settings->System Settings->SNMPTraps`

![SNMP Traps](@@path/images/snmptrap-enable.jpg)

Once enabled, the default port of `32162` will receive SNMP Traps. Users may change this port to the standard SNMP Trap port by using the following command from a terminal:

```
logzilla config SNMPTRAPD_PORT 162
```

After changing the port setting, send a restart signal to LogZilla to re-configure that port:

```
logzilla restart
```







    

