<!-- @@@title:UDP Buffer Tuning@@@ -->

In larger deployments (greater than 5-10k EPS), you may find that the server is dropping UDP packets.
Drops may be seen by using the command `netstat -su`, for example:

    Udp:
    107425170 packets received
    2287 packets to unknown port received.
    0 packet receive errors
    62601926 packets sent
    IgnoredMulti: 576830

`packets received` indicates the total amount of packets received to the system since the last reboot.
`packets to unknown port` indicates that there was no application available when a UDP packet was sent to the server. For example, if you were to shut down the LogZilla service, but devices were still trying to send, this number would increase.
`packet receive errors` indicate that there were errors while trying to receive and process the incoming packets.  Note that a single packet may generate multiple errors.

## Testing UDP Performance

First, make sure that no other applications are listening on the UDP port used during testing. If using port 514, be sure to shut down syslog-ng (`service syslog-ng stop`) prior to running the following commands.

Run `netcat` in listening mode

    netcat -u -p 514 -l > /tmp/logs

In a separate ssh terminal, use `loggen` (provided with the syslog-ng application) to generate messages:

    ./loggen -r 10000 -D -I 10 127.0.0.1 514

Once loggen completes, it will provide the rate information:

    average rate = 10877.62 msg/sec, count=108783, time=10.006, msg size=256, bandwidth=2719.40 kB/sec

use `wc -l` to verify the line count reported by the `loggen` command.
This number should match, or come very close to, the number from `loggen`.

    wc -l /tmp/logs

Sample output:

    #wc -l /tmp/logs
    108783 /tmp/logs

Next, check for any UDP errors using `netstat -su` as noted above.
 If `netstat` shows errors, try increasing the UDP buffers using:
 
    sysctl -w net.core.rmem_max=33554432

>This will set the buffer to 32M (the default in linux is 122k: `net.core.rmem_default = 124928`)

Continue with testing until you are comfortable with the buffer size assigned.

Once you have a good buffer size, you may set it permanently by adding the setting to `/etc/sysctl.conf` and applying it using `sysctl -p`, for example:

    echo "net.core.rmem_max=33554432" >> /etc/sysctl.conf
    sysctl -p

You may want to also add a few other tuning options, such as

    net.ipv4.udp_mem = 192576 256768 385152 
    net.ipv4.udp_rmem_min = 4096
    sysctl -w net.ipv4.udp_mem='262144 327680 393216'

> net.ipv4.udp_mem works in pages, so multiply values by `PAGE_SIZE`, where `PAGE_SIZE = 4096` (4K). Thus, the maximum udp_mem is set to `385152 * 4096` = `1,577,582,592`

You may also increase the queue size for incoming packets using:

    sysctl -w net.core.netdev_max_backlog=2000

> Remember that using `sysctl -w` only changes these values until the server is rebooted. To make the changes permanent, be sure to add them to the `/etc/sysctl.conf` file.
