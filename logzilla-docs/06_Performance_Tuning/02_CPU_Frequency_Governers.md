<!-- @@@title:CPU Frequency Governors@@@ -->

Recent Intel CPUs provide both energy-saving and performance boost capabilities, respectively named `SpeedStep` and `TurboBoost`. 
These features change individual core frequency depending on system load.
However, this may not have the desired outcome on high-performance servers.

### Checking The Current Processor Speed
To check the current speed of your processor(s), type:

   cat /proc/cpuinfo  | grep MHz

For example:

    cat /proc/cpuinfo  | grep MHz
    cpu MHz   : 1400.000
    cpu MHz   : 1400.000
    cpu MHz   : 1400.000
    cpu MHz   : 1400.000
    cpu MHz   : 1400.000
    cpu MHz   : 1400.000
    cpu MHz   : 3500.000
    cpu MHz   : 3500.000

Note above that only 2 cores are running at top speed (`3500.000`).
While this may be a good use for power efficiency, it is not good for high performance servers such as LogZilla.

### Running At Top Performance
The Linux kernel provides 4 profiles, named CPU governors named `conservative`, `ondemand`,  `userspace`, and `powersave` performance 

By default, Linux distributions set the `ondemand` governor. This governor is a good compromise between energy saving and performance-boosting as it adapts to the current CPU workload. Although, there are cases in which performance is heavily degraded on moderately loaded servers. We recommend using the `performance` governor instead.

### Disabling SpeedStep/TurboBoost

Setting the CPU governor may be done using the following function. This function can either be pasted directly into an SSH session or placed in a `.bash_aliases` file. Note that this will only work like the **root user**.

```bash
function setgov ()
{
    # usage:
    # setgov ondemand
    # setgov performance
    echo "Current setting: $(cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor | sort -u)"
    echo "Current CPU Speeds:"
    cat /proc/cpuinfo | grep 'cpu MHz'
    [[ -z $1 ]] && { echo "Missing argument (ondemand|performance)"; return 1; }
    echo "$1" | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
    echo "New CPU Speeds:"
    cat /proc/cpuinfo | grep 'cpu MHz'
}
```

Once the function is in your `.bash_aliases` file, simply type `source ~/.bash_aliases` to load it, then run `setgov`. This will return something similar to:

```bash
root@myserver: # setgov
Current setting: ondemand
Current CPU Speeds:
cpu MHz		: 1400.000
cpu MHz		: 2300.000
cpu MHz		: 1400.000
cpu MHz		: 3500.000
cpu MHz		: 3500.000
cpu MHz		: 1700.000
cpu MHz		: 1400.000
cpu MHz		: 2300.000
Missing argument (ondemand|performance)
```

Running `setgov performance` will return something similar to:

```bash
root@myserver: # setgov performance
Current setting: ondemand
Current CPU Speeds:
cpu MHz		: 2900.000
cpu MHz		: 1400.000
cpu MHz		: 1700.000
cpu MHz		: 1400.000
cpu MHz		: 1400.000
cpu MHz		: 2300.000
cpu MHz		: 3500.000
cpu MHz		: 1400.000
performance
New CPU Speeds:
cpu MHz		: 3500.000
cpu MHz		: 3500.000
cpu MHz		: 3500.000
cpu MHz		: 3500.000
cpu MHz		: 3500.000
cpu MHz		: 3500.000
cpu MHz		: 3500.000
cpu MHz		: 3500.000
```

# Permanent Change

The following commands (run **as root**) will permanently set the performance governor so that it keeps the setting after a reboot:

    apt-get install cpufrequtils
    echo 'GOVERNOR="performance"' >/etc/default/cpufrequtils 
    service cpufrequtils reload

The governor may be changed at any time by altering the `GOVERNOR` variable above and reloading cpufrequtils.

>TurboBoost only runs when other CPU cores are throttled (down), due to each CPU's Thermal Design Power (TDP). This implies that enabling performance governor will have each core running exactly at nominal frequency, and never above.
>TurboBoost depends on SpeedStep, thus disabling SpeedStep in BIOS will disable CPU throttling and TurboBoost

