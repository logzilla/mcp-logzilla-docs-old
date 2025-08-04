<!-- @@@title:Cisco IOS Configuration@@@ -->

# Cisco IOS Commands
Configuring a Cisco IOS device for Syslog involves more than just defining the actual Syslog destination receiver. Each device must be configured to include the proper `timestamp` information, `time zone`, a `logging source`, the `console buffer size`, the `logging level`, and `NTP`.

## Sample IOS Configuration

>LogZilla uses UTC0 time on the server itself. However, the user's browser will display in their local time. All incoming events will be marked with the time **of the LogZilla server** and not the timestamp from the originating device. This eliminates the chance of a misconfigured device sending the wrong time in the syslog packet causing the event to be stored incorrectly.

    service timestamps debug datetime localtime show-timezone
    service timestamps log datetime localtime show-timezone
    clock timezone GMT 0
    !
    logging source-interface loopback0
    logging buffered 65536
    logging host <ip address 1>
    logging host <ip address 2>
    logging trap informational
    !
    ntp server <ip address 4>
    ntp server <ip address 5>
    ntp peer <ip address 6>
    ntp peer <ip address 7>
    ntp update-calendar

## Configuration Command Detail

### Timestamps

    service timestamps debug datetime localtime show-timezone
    service timestamps log datetime localtime show-timezone
    clock timezone GMT 0

Timestamps may be added to either `debugging` or `logging` messages independently.

BAD: The `uptime` form of the command adds timestamps in the format `HHHH:MM:SS`, indicating the time since the system was rebooted.

GOOD: The `datetime` form of the command adds timestamps in the format `MMM DD HH:MM:SS`, indicating the date and time according to the system clock.
Adding a timestamp to messages allows you to tell what time the message was generated rather than a message indicating how long the device has been powered up.

The `show-timezone` form of the command adds a TZ to the incoming message.

**<font color="red">IMPORTANT:</font>**

On some Cisco IOS versions, it is **imperative** that this portion of the command is included. Without it, the syslog daemon may detect your device's hostname as a `:` instead of the actual hostname.


For example:


**Hostname Missing**


```
0    :    189    UTC    %SYS-5-CONFIG_I: Configured from console by user1 on vty3 (192.168.2.207)
```

**Correct Hostname**


```
0    192.168.2.252    189    UTC    %SYS-5-CONFIG_I: Configured from console by user1 on vty3 (192.168.2.207)
```



### Logging

    logging source-interface loopback0
    logging buffered 65536
    logging host <ip address 1>
    logging host <ip address 2>
    logging trap informational

The `logging source-interface` command instructs the system to generate messages to the remote system from the defined source interface. This ensures that all messages appear to come from the same IP across reboots and makes it easier to track in the destination syslog receiver. This also allows you to create a DNS entry for that source interface.
> If the `logging source-interface` command is **not** used and the system reloads, the first IP that comes up will be used, this will result in LogZilla assuming it is an entirely different device.

The `logging buffered` command is used to reserve a memory buffer for logging to the console of the device.  The typical recommendation is to have `256K` buffers on core devices and `64K` elsewhere.
> `console buffer` refers to the output of the screen when attached to the device either by serial or via telnet/ssh using the "Terminal Monitor" command. The `console buffer` command has no effect on sending syslogs to remote destinations.

The `logging host` command specifies the remote LogZilla server to send messages to.
>Network devices should be configured with a maximum of four syslog destinations. The remote syslog server can then be configured to forward messages to other network management systems if more than four IP addresses are required. This reduces the changes needed on network devices.
>Devices should be set to log severities `0-6` for normal operation and `0-7` while connected directly to the device's console.

The `logging trap informational` command tells the device to log all messages of severity 0-6 to the LogZilla server.
> The `trap` portion of this command should not be confused with SNMP traps, it is simply the command used to indicate which severity levels to send and has nothing to do with SNMP.


<font size="1em" color="gray">This help section is provided only as a courtesy. LogZilla Corporation does not provide support for products outside of our own software.</font>
