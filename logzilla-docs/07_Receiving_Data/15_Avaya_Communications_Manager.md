<!-- @@@title:Avaya Communications Manager@@@ -->

# Avaya Communications Manager

LogZilla can receive log messages from Avaya communications systems.
This is accomplished through configuring the Avaya Communications Manager
to output logs to LogZilla. The procedure for doing so is detailed below.

## Configuration Procedure

Please refer to the screenshot below.

1. Log in to Avaya Communication Manager System Management Interface.
2. On the Administration Menu, click *Server (Maintenance)*.
3. In the left navigation pane, under *Security*, click `Server Log Files`
and do the following:
4. There is a table with columns *Log Server*, *Enabled*, *Protocol*, etc.
In this table go to the first row for which *Enabled* is `No`.  This will
likely be theh first row (*Log Server* `1`), unless Communications Manager
has already been configured to use other syslog server(s).
5. On that row, in *Enabled*, select `Yes`.
6. In *Protocol*, choose `TCP`.
7. In *Port*, type in `514`.
8. In `Server IP/FQDN`, type the name or address of the LogZilla server.
9. The following columns (*Security*, *CM IP*, *Command*, *Kernel*,
*Messages*) should be checked.  If they are not already, then check them.
10. Leave all other fields on this page alone. Click *Submit*.

![Avaya Communications Manager Screenshot](@@path/images/avaya-communications-manager-configuration.png)
