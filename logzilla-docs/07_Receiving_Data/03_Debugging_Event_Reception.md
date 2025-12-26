<!-- @@@title:Debugging Event Reception@@@ -->

# No Events In LogZilla
If LogZilla is showing no events from other systems there are several ways to 
determine the cause.

## Check the log

Check LogZilla's internal log file using:

```sh
sudo tail -f /var/log/logzilla/logzilla.log
```

## Verify that the source is sending

`tcpdump` can be used on the LogZilla server to determine if the remote host's 
events are reaching the LogZilla server.

If your source device/app is not sending to `udp port 514`, then change the 
line below to accommodate:

```sh
sudo tcpdump -vvv -i $(awk '$2 == 00000000 { print $1 }' /proc/net/route) udp port 514.
```

This will listen on the ethernet interface assigned to the default gateway for 
incoming events on `udp port 514` (the default for UDP syslog events).

Note that if the LogZilla server's appropriate ethernet interface or the 
configured listening port is different than shown, those parameters for `tcpdump` 
above should be changed accordingly.

For example:

- `-i` (used below) manually specifies the interface to use instead of the 
default gateway in the example above.

```sh
sudo tcpdump -vvv -i p1p1 udp port 514
```

After running the command, you will see data similar to:

```sh
tcpdump: listening on eth0, link-type EN10MB (ethernet), capture size 65535 bytes 17:01:01.955523 IP (tos 0x0, ttl 64, id 44193, offset 0, flags [DF], proto UDP  (17), length 272) 25.92.104.22.57053 > logzilla.myserver.com.syslog: [udp sum ok] SYSLOG, length: 244 Facility kernel (0), Severity warning (4) Msg: Sep  3 13:01:02 www kernel: [UFW BLOCK] IN=eth0 OUT= MAC=01:22:33:02:e5:01:44:c5:9c:f9:18:30:08:00 SRC=191.168.1.2 DST=10.2.1.6 LEN=60 TOS=0x00 PREC=0x00 TTL=44 ID=65267 DF PROTO=TCP SPT=41410 DPT=22 WINDOW=14600 RES=0x00 SYN URGP=0 \0x0a0x0000:  3c34 3e53 6570 2
```

## Set LogZilla's syslog container to Debug Mode

Once you have verified that events are being received as noted above, try 
enabling debug mode on the **lz_syslog** container by issuing the following 
command at the shell prompt:

```sh
sudo docker exec -it lz_syslog bash -c 'syslog-ng-ctl debug --set=on'
sudo docker logs lz_syslog --tail 100 -f
```

<font color="red">WARNING:</font> Debug mode should be disabled once you are 
finished checking the output:

```sh
sudo docker exec -it lz_syslog bash -c 'syslog-ng-ctl debug --set=off'
```

If this indicates that events are being received but are still not appearing in 
LogZilla, the next step is to verify that the syslog container is processing 
them properly.

# Log to a debug file

Enable syslog debug to file using:

```sh
sudo logzilla config syslog_debug 1
```

> Once troubleshooting is complete, debug logging should be disabled, since it
generates extra load on the syslog process and can quickly fill up disk: 
`logzilla config syslog_debug 0`.

All raw log events will be logged to `/var/log/logzilla/syslog/debug.log`

<font color="red">WARNING:</font> Leaving raw debug log enabled can fill your 
disk. Be sure to disable it once you are finished troubleshooting.

View the logs using:

```
sudo tail -F /var/log/logzilla/syslog/debug.log
```

This should indicate entries coming in. If not, a sample log can be generated 
locally by:

```
sudo logger -T -P 514 --rfc3164 -n localhost -p local0.emerg -t "test" "rfc3164 
event test on TCP Port 514 from $(hostname)"
sudo logger -u -P 514 --rfc3164 -n localhost -p local0.emerg -t "test" "rfc3164 
event test on UDP Port 514 from $(hostname)"
```

Any errors displayed will help narrow down any communication issues.

For more diagnostics, there is also another log file generated when syslog 
debugging is on. This file is located in `/var/log/logzilla/syslog/debug-json.log`.
It contains a JSON document for each line with details of the events received 
and initially processed by syslog.

The JSON-based log can be enabled using:

```sh
sudo logzilla config syslog_debug_json 1
```

> Once troubleshooting is complete, debug logging should be disabled, since it 
generates extra load on the syslog process and can quickly fill up disk: 
`logzilla config syslog_debug_json 0`.

# Raw Tcpdump Capture

If LogZilla is still showing no received events, support is available at 
https://support.logzilla.net. Please include the output from the following 
command:

1. Ensure that the host sending events is sending to LogZilla on `udp port 514`. 
Otherwise, our support team has no way to replay your network environment in the lab.
2. Run the command below to capture a sample of your incoming event stream.

Note: Change `-G 10800` below to a larger number if your LogZilla server doesn't 
normally receive a large amount of events. Ideally, you want to capture a large 
enough window to ensure that the event(s) in question can be captured.

```
# "10800" below equates to 3 hours
# "86400" would be 24 hours
# In some cases, support may ask that you capture an entire day's worth in 
order to have a proper sample of event data

tcpdump -i $(awk '$2 == 00000000 { print $1 }' /proc/net/route) \
 "udp port 514 or (ip[6:2] & 0x1fff) != 0" \
 -nnvvXSs 0 -G 10800 -W 1 -z gzip -w /tmp/$(hostname).pcap
```

3. After 3 hours (or the time specified above in the `-G 10800` portion), the 
capture will automatically stop and place a `.gz` file in `/tmp/` with the 
hostname as the filename. For example `/tmp/myhost.pcap.gz`.

In your support ticket please include the installed LogZilla version, which is 
found at the bottom right corner of the LogZilla Web Interface, or by typing 
`sudo logzilla version` from the console.
