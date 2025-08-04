<!-- @@@title:Backend Configuration Options@@@ -->


`logzilla config` command
---

In order to protect users from damaging the system, some of the settings for LogZilla are not configurable in the UI. These settings are documented below.
>Note: Changing any of these settings may cause irreparable damage to your server. Please use extreme caution.

`logzilla config` lists all config items  
`logzilla config ITEM` shows item value  
`logzilla config ITEM VALUE` sets a new value  

All of the following settings require a restart of LogZilla before they will
take effect:
```bash
sudo logzilla restart
```


### Configuration Option Descriptions
category | setting | description | default / min / max
-------- | ------- | ----------- | ---------------
Miscellaneous | `TIME_ZONE` | Sets timezone for LogZilla usage and reporting | `GMT`
Miscellaneous | `REPORTS_BASE_URL` | Base URL for reports. This should point to the LogZilla instance, to be visible to all reporting users | `http://localhost`
Miscellaneous | `DEDUP_WINDOW` | Length of time window (in seconds) during identical messages will be aggregated into one, with number of occurrences | `60` / `0` / `3600`
Miscellaneous | `FUTURE_TIME_TOLERANCE` | Maximum difference in seconds between server time and timestamp of incoming message - if difference is greater, incoming message timestamp will be reset to current server time | `2` / `1` / *
Miscellaneous | `INTERNAL_EVENTS_MAX_LEVEL` | Control which logzilla.log message levels are sent to system as 'internal' events - as opposed to' external' events coming from syslog or other external sources") | `WARNING` / `CRITICAL`, `ERROR` , `WARNING` , `WARN` , `INFO` , `NONE`
Miscellaneous | `INTERNAL_COUNTERS_MAX_LEVEL` | Controls which internal counters should be collected | `INFO` / `CRITICAL` , `INFO` , `DEBUG`	
Miscellaneous | `LOG_MAX_LEVEL` | Controls which message levels are sent to the log file | `INFO`
Miscellaneous | `RBAC_ENABLED` | Enable role based access control, in every query the user will get results from only those hosts to which he has access | `True`
Miscellaneous | `EULA_ACCEPTED` | Has the EULA been accepted | `False`
Miscellaneous | `AUTOLOGIN_ENABLED` | Allow auto-login as user without password | `False`
Miscellaneous | `AUTOLOGIN_USER` | Auto-login username | `admin`
Miscellaneous | `ARCHIVE_EXPIRE_DAYS` | Number of days after which events will be archived | `7` / `3` / *
Miscellaneous | `ARCHIVE_FLUSH_DAYS` | Number of days after which archived data will be removed | `365` / `0` / *
Miscellaneous | `AUTOARCHIVE_CRON_HOUR` | hour (in 24-hour format) which defines the starting time for daily archives. Coincides with LogZilla's TZ setting | `5` / `0` / `23`
Miscellaneous | `SEARCH_DEFAULT_LIMIT` | Default limit number of search results | `100` / `1` / `10000`
Miscellaneous | `PARSER_WORKERS` | Number of worker threads used to parse messages | minimum of (`10`, CPU_COUNT / 2)
Miscellaneous | `OFFLINE` | Disable outside communications | `False`
Miscellaneous | `FORWARDER_ENABLED` | Enable the forwarder module | `False`
Miscellaneous | `SEC_ENABLED` | Enable the SEC module | `False`
Miscellaneous | `SEC_EXTRA_PARAMS` | Extra params for the SEC daemon | (blank)
Miscellaneous | `PRUNE_DOCKER_IMAGES` | Periodically remove unused docker images left after upgrade | `True`
Search | `SPHINX_MAX_MATCHES` | Maximum number of results when exporting search results. Please note that setting too large value can result is excessive RAM usage and query failures | `1000000` / `1` / *
Search | `SPHINX_MIN_WORD_LENGTH` | Minimum indexed word length | `4` / `1` / *
Search | `SPHINX_MIN_PREFIX_LENGTH` | Minimum word prefix length to index | `4` / `1` / *
Search | `SPHINX_MIN_INFIX_LENGTH` | Minimum infix prefix length to index (default: 4 - infix disabled). Enabling the option will override SPHINX_MIN_PREFIX_LENGTH setting | `4` / `0` / *
Triggers | `SEND_MAIL_PERIOD` | The minimum period in sec between successive trigger emails | `60` / `1` / *
Triggers | `SEND_WEBHOOK_PERIOD` | The minimum period in sec between successive webhooks | `10` / `1` / *
Triggers | `EXEC_SCRIPT_PERIOD` | The minimum period in sec between successive script executions | `1` / `1` / *
Triggers | `TRIGGER_ENGINE_WORKERS` | Number of worker threads used processing triggers | Minimum of (`6`, Maximum of (`2`, CPU Count / 4)) / `1` / *
SMTP | `MAIL_SENDER` | Outgoing e-mail sender | (blank)
SMTP | `SMTP_SERVER` | SMTP server address (see _SMTP Note_ below) | `mailer`
SMTP | `SMTP_PORT` | SMTP server port (see _SMTP Note_ below) | `25` / `1` / *
SMTP | `SMTP_AUTH_REQUIRED` | Controls whether SMTP AUTH should be required (see _SMTP Note_ below) | `False`
SMTP | `SMTP_USER` | SMTP server login username (see _SMTP Note_ below) | (blank)
SMTP | `SMTP_PASS` | SMTP server login password (see _SMTP Note_ below) | (blank)
SMTP | `SMTP_CRYPT` | SMTP secure connection type (see _SMTP Note_ below) | `NONE` / `NONE` , `TLS` , `SSL`
Services | `SYSLOG_BSD_TCP_PORT` | TCP port on which LogZilla will receive BSD/RFC3164 syslog traffic | `514`
Services | `SYSLOG_BSD_UDP_PORT` | UDP port on which LogZilla will receive BSD/RFC3164 syslog traffic | `514`
Services | `SYSLOG_RFC5424_PORT` | TCP port on which LogZilla will receive RFC5424 syslog traffic | `601`
Services | `SYSLOG_JSON_PORT` | TCP port on which LogZilla will receive raw JSON data traffic | `515`
Services | `SYSLOG_MAX_CONNECTIONS` | Specifies the maximum number of simultaneous syslog-ng connections | `50` / `1` / *
Services | `HTTP_PORT` | TCP port on which LogZilla will accept HTTP requests (and respond) | `80`
Services | `HTTP_PORTS` | TCP port on which LogZilla will accept HTTPS requests (and respond) | `443`
Services | `FORCE_HTTPS` | Use HTTPS instead of HTTP | `False`
Services | `STORAGE_NODE_COUNT` | Number of parallel Event Processing Nodes (see warning below) | `1` / `1` / *
SNMPTraps | `SNMPTRAPD_ENABLED` | Enabling snmptrapd module | `False`
SNMPTraps | `SNMPTRAPD_FORMAT` | Format of message field, see man snmptrapd(8) for details | See below
SNMPTraps | `SNMPTRAPD_PROGRAM` | Value of "program" field for events generated from snmp traps | `SNMPTrap`
SNMPTraps | `SNMPTRAPD_FACILITY` | Value of "facility" field for events generated from snmp traps | `LOCAL0`
SNMPTraps | `SNMPTRAPD_SEVERITY` | Value of "severity" field for events generated from snmp traps | `INFO`
SNMPTraps | `SNMPTRAPD_PORT` | Port number from snmptrapd container to host | `162`
System/Parsers | `UNPARSED_LINES_FILE` | File where all unparsed lines will be written | `unparsed_lines`
System/Dirs | `REPORTS_DIR` | Directory to store all generated reports | `reports`
System/Dirs | `SCRIPTS_DIR` | Directory to store scripts allowed to run by triggers | `scripts`


#### SMTP Note
SMTP is the interface protocol used to send outgoing emails from the
LogZilla server. These settings control what email server LogZilla uses
for sending as well as the protocol specifics for that interaction.

#### `STORAGE_NODE_COUNT` Warning
WARNING: Any change to this value (incrementing OR decrementing) can lead
to data loss and invalid query results for already stored data. If there
is any question or doubt about this value and changes to it, contact LogZilla
support.

#### `SNMPTRAPD_FORMAT` Default Setting
Enterprise OID: %N, Trap Type: %W, Trap Sub-Type: %q, 
Uptime: %T, Description: %W, 
PDU Attribute/Value Pair Array: %v


