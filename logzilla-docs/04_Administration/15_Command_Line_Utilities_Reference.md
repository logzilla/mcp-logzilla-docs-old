<!-- @@@title:Command Line Utilities Reference@@@ -->

There are many linux shell scripts that assist with administration of LogZilla.  Where appropriate those scripts are referred to elsewhere in the documentation.  This section gives the entire list of scripts and their parameters.

These scripts are run via `logzilla scriptname [action name] [arguments]`.

## LogZilla Scripts
Note that all of these scripts accept a `-h` argument to give help on the script and any script actions.

`archives`  
manage archives of LogZilla event data

action name | description
--- | --- 
`archive` | archive selected date range of events
`remove` | remove archived data for the selected date range  
`migrate` | migrate old archives (older than v6.10) to the latest version to allow running queries without restore  

example command | example description
----------- | -------
`logzilla archives archive -E 5` | archive events for the last five days
`logzilla archives remove --ts-from 4/1/2020 --ts-to 5/1/2020` | remove archived events from 4/1/2020 up to but not including 5/1/2020
`logzilla archives migrate --ts-from 4/1/2020 --ts-to 5/1/2020` | migrate archived events from 4/1/2020 to 5/1/2020 to current format so that queries can be run without restore

`authtoken`  
Create or revoke LogZilla user token  

action name | description
--- | --- 
`create` | create an authorization token
`revoke` | revoke an authorization token
`info` | show details for the specified token
`list` | show list of all authtokens

example command | example description
----------- | -------
`logzilla authtoken create -U someuser` | create authorization token for user `someuser`
`logzilla authtoken create --ingest-only` | create authorization token for ingest
`logzilla authtoken revoke dfcf2dee6113b33f89bbfc0be3ced0c02db2b9e28bf36499` | revoke previously-created authorization token by token id
`logzilla authtoken info dfcf2dee6113b33f89bbfc0be3ced0c02db2b9e28bf36499` | show details for token with that id
`logzilla authtoken list` | show all authtokens

`config` (also `configmanager`)  
Manage LogZilla configuration settings  

action name | description
--- | --- 
(none) | list configuration settings
`setting_name` | display setting
`setting_ name` (value) | add or change value of setting

example command | example description
----------- | -------
`logzilla config TIME_ZONE` | display configuration setting for time zone
`logzilla config TIME_ZONE EST` | set configuration setting for time zone to EST

`dashboards`  
LogZilla dashboard import/export (or dashboard widgets)

action name | description
--- | --- 
`list` | list all dashboards
`export` | export dashboards
`import` | import dashboards (format must be yaml)
`performance` | run dashboard/widgets live-update benchmarks
`remove` | delete specified dashboard(s)


example command | example description
----------- | -------
`logzilla dashboards list *windows*` | list dashboards with title containing `windows`
`logzilla dashboards list -w --dashboard-id 120` | list the widgets on dashboard 120
`logzilla dashboards list --widget-id 874` | list just the widget for widget id 874
`logzilla dashboards export -O my_dashboards.json -F json --owner myname` | write (complete) dashboards for owner `myname` as JSON to file `my_dashboards.json`
`logzilla dashboards import --owner myname -I my_dashboards.yaml -p 1` | import dashboards from file `my_dashboards.yaml` as belonging to user `myname` and set to public
`logzilla dashboards performance` | list performance metrics for each dashboard by widget
`logzilla dashboards remove mydashboard` | delete specified dashboard

`download`  
Download LogZilla images

action name | description
--- | --- 
`offline_dir` | directory to save compressed images to

example command | example description
----------- | -------
`logzilla download /tmp/down` | download logzilla images to /tmp/down

`events`  
Manage LogZilla event data

action name | description
--- | --- 
`stats` | show # events, counters, deduplication
`parser-stats` | show # processed events and throughput
`cardinality` | show fields indexed and # values
`fix-cardinality` | recalculate cardinality values
`values` | show events fields and values
`fix` | fix chunks for selected data range
`tester` | test event flow

example command | example description
----------- | -------
`logzilla events stats --ts-from 4/1/2020 --ts-to 5/1/2020` | show # events, # counters, % dedup, and # dropped
`logzilla events fix --ts-from 4/1/2020 --ts-to 5/1/2020` | fix broken storage chunks (as indicated in logs)

`forwarder`  
Manage LogZilla event forwarder

action name | description
--- | --- 
`print` | display current configuration
`print-files` | display current configuration per files
`import` | display configuration from given file
`stats` | display forward statistics per target

example command | example description
----------- | -------
`logzilla forwarder stats --ts-from 4/1/2020 --ts-to 5/1/2020` | show # events, % dedup by target


`https`  
Manage Logzilla HTTPS configuration

action name | description
--- | --- 
`--on` | enable HTTPS
`--off` | disable HTTPS

example command | example description
----------- | -------
`logzilla https --on ~/certs/ssl.key ~/certs/ssl.cert` | enable HTTPS with given key & cert files for forwarding of events

`inspect-dump`  
Do not use.

`install`  
Download and install or update LogZilla image files

action name | description
--- | --- 
(n/a) | no named actions

`kinesis`  
Manage LogZilla kinesis agent

action name | description
--- | --- 
`start` | start kinesis container
`stop` | stop kinesis container
`restart` | restart kinesis container
`set-properties` | set kinesis properties
`import` | import kinesis properties
`export` | export kinesis properties
`set-aws-credentials` | set kinesis AWS credentials

example command | example description
----------- | -------
`logzilla kinesis set-properties --streamName "lz_kinesis_staging_stream"` | set the kinesis stream name for the LogZilla event stream
`logzilla kinesis set-aws-credentials --aws-access-key dfcf2dee6113b33f89bb --aws-secret-key fc0be3ced0c02db2b9e28bf36499` | set the AWS access tokens for kinesis

`ldap`  
Manage LogZilla LDAP configuration

action name | description
--- | --- 
`init` | initialize LDAP config
`enable` | validate config file and enable LDAP
`disable` | disable LDAP
`test` | test current LDAP configuration settings


`license`  
Manage LogZilla license

action name | description
--- | --- 
`load` | load license from file
`download` | download license
`info` | show license information
`key` | print host key
`verify` | verify license

example command | example description
----------- | -------
`logzilla license load ~/logzilla/license.txt` | load the LogZilla license

`logs`  
Deprecated.  Use `tail -f /var/log/logzilla/logzilla.log` .

`passwd` (also `password`)  
Set password for given user

action name | description
--- | --- 
(username) | username to set password for

example command | example description
----------- | -------
`logzilla passwd johndoe` | be prompted for new password for user johndoe

`query`  
LogZilla action-line querying tool

action name | alternate | description
--- | --- | ---
`-d` | `--debug` | debug mode
`-q` | `--quiet` | notify only on warnings and errors (be quiet)
`--timezone` | | specify the timezone for time-range parameters and exported data date formats (default: 'UTC')
`-c` | `--config` | path to config file, defaults to ~/.lz5query
`-cu` | `--config_update` | update config file with given user/password/base-url
`-u` | `--user` | username to authenticate
`-p` | `--password` | password to authenticate
`-a` | `--authtoken` | auth token to authenticate
`-bu` | `--base-url` | base url to the API
`-t` | `--type` | type of query to perform
`-st` | `--show-types` | show available query types
`-P` | `--params` | path to json file with query params
`-O` | `--output-file` | path to output file (format specified by --format)
`--format` | | output file format. If omitted, guesses from extension or defaults to JSON

example command | example description
----------- | -------
`logzilla query --show-types` | show the types of queries that can be performed
`logzilla query --config /tmp/tmpconfig.txt -t System_CPU --output-file /tmp/cpu_stats.json` | 
`logzilla query -P /tmp/params.json /tmp/params.json -t LastN` | show query results for type LastN using criteria in /tmp/params.json

Example config file (`/tmp/tmpconfig.txt`)
```
[lz5query]
user=myusername
password=mypassword
base_url=http://front/api
```

Example params file (`/tmp/params.json`)
```
{
	"field": "host",
	"limit": 5,
	"filter": [],
	"show_other": false,
	"time_range": {
		"preset": "last_3_days"
	}
}
```

`restart`  
Restart LogZilla

action name | description
--- | --- 
(n/a) | no named actions

`rules`  
Manage LogZilla rewrite rules

action name | description
--- | --- 
`list` | list rewrite rules
`reload` | reload rewrite rules
`add` | add rewrite rule (accepts .yaml, .json, .lua file)
`remove` | remove rewrite rule
`export` | export rewrite rule
`enable` | enable rewrite rule
`disable` | disable rewrite rule
`errors` | shows which rules are erroring and how many times
`performance` | benchmark rules single-thread performance
`test` | test rule(s) (against test files) for errors

example command | example description
----------- | -------
`logzilla rules add newrule.yaml --name Unity` | add new rule from file with given name
`logzilla rules test 100-existing-rule` | test existing rule for errors
`logzilla rules test --path 100-new-rule.lua` | test new/not-loaded rule for errors

Example rule file for adding (`newrule.yaml`):  
```
rewrite_rules:
- match:
    field: message
    op: =*
    value: product="UnityOne"
  rewrite:
    program: UnityOne
  tag:
    Tipping Point Actions: $act
    Tipping Point App: $app
    Tipping Point Block Category: $act
    Tipping Point DHost: $dhost
    Tipping Point Device: $dvchost
```


`script`  
Do not use.

`sender`  
Send log data to LogZilla or syslog, either read from file or generated

action name | alternate | arg example | description
--- | --- | --- | ---
`-z` | `--zmq` | (n/a) | Send data using ZeroMQ protocol
`--zmq-target` | | `=tcp://parsermodule:11411` | Where to send zmq data (defaults to `tcp://parsermodule:11411`)
`--zmq-format` | | `=json_lines` | Either `json_lines` or `eventpack` (defaults to `json_lines`)
`--zmq-timeout` | | `=0` | Send timeout  in milliseconds (for ZMQ transport only)
`-s` | `--syslog` | (n/a) | Send data using Syslog protocol (default)
`--syslog-target` | | `=localhost:32514` | Where to send syslog data (defaults to `localhost:32514`)
`--syslog-protocol` | | `=bsd` | Either `bsd` or `rfc5424` (default `bsd`)
`--syslog-transport` | | `=tcp` | Either `tcp` or `udp` (default `tcp`)
`--octet-count` | | (n/a) | Use octet counting framing method for sending syslog messages
`-S` | `--shuffle` | (n/a) | Shuffle read/generated data randomly
`-R` | `--random` | (n/a) | Generate fields in random order
`--read-messages` | | (n/a) | Read messages from given file (use `-` for stdin)
`--read-full` | | (n/a) | Read full events from given TSV file (use `-` for stdin). Overrides `--read-messages`
`--read-format` | | `=bsd` | Given TSV file format. Either `bsd` or `rfc5424` (defaults to `bsd`)
`-r` | `--rate` | `=0 0` | Rate range of sending in packets per second, default `0 0` means no limit
`-w` | `--wrap` | (n/a) | Wrap input data to get endless stream of data
`-t` | `--time` | `=0` | Finish sending after given number of seconds (usually used with `-w` and `-r`)
`-n` | `--number-of-events` | `=0` | Number of messages to generate (defaults to `10`, unless reading from file)
`--msg-priority` | | `={{0..191}}` | Fixed priority or list of priorities (numbers 0 to 191, possibly separated by `..` or `,`)
`--msg-host` | | `={{hosta,hostb,hostc}}` | Fixed host or list of hosts
`--msg-program` | | `={{programa,programb,programc}}` | Fixed program or list of programs
`--msg-body`| | `=Message nr {{1..32}}` | Fixed message body or list of such
`--msg-user-tags` | | (n/a) | Fixed user tag or list of user tags (for ZMQ transport only).format: `tag1_name=value1,tag2_name=value2`
`--pack-size` | | `=0` | Pack messages (for ZMQ transport only) in packets of that size
`--dedup-level` | | `=-1` | Generate extra messages to reach given deduplication level (value in percent, allowed range: 0 - 100
`--dedup-window` | | `=60` | Value of dedup window on server, needed only with dedup-level
`-l` | `--log` | (n/a) | Enable usage and counter logging using zmqlog
`-v` | `--verbose` | (n/a) | Verbose mode (show progress while sending)
`-d` | `--debug` | (n/a) | Debug mode (show every message sent)
`--zero-ts` | | (n/a) | Set timestamps to zero so they will be set by parser (zmq only)

example command | example description
----------- | -------
`logzilla sender --zero-ts --read-full mylog.tsv -w --syslog-target=192.168.10.191:514 --syslog-transport=udp --syslog-protocol=bsd -r 5 10 -v 5` | send events from given file to given target at specified rate, marking events with current timestamp

Example events file for sending (`mylog.tsv`)
```
7 206.190.60.138 10.0.0.1 62443 80 offset 8 S 832026162 win 8192 blocked sites (Internal Policy)
0	nyc-m500	142	firewall	msg_id="3000-0173" Deny 0-External Firebox 52 tcp 20 127 206.190.60.138 10.0.0.1 62443 80 offset 8 S 832026162 win 8192 blocked sites (Internal Policy)
0	nyc-m500	142	firewall	msg_id="3000-0173" Deny 0-External Firebox 52 tcp 20 127 206.190.60.138 10.0.0.1 62443 80 offset 8 S 832026162 win 8192 blocked sites (Internal Policy)
```

`shell`  
Execute given command (default `bash`) in the specified LogZilla container.

action name | alternate| description
--- | --- | --- 
`-c` | `--container` | container to attach to


`snapshot`  
LogZilla configuration backup/restore tool

action name | description
--- | --- 
create | create snapshot
restore | restore LogZilla from snapshot
list | list existing LogZilla snapshots
autoremove | remove old snapshots

example command | example description
----------- | -------
`logzilla snapshot create` | backup current LogZilla configuration
`logzilla snapshot restore --id v6.11.0-dev5_20200601T095908.462993Z` | restore given LogZilla configuration

`speedtest`  
LogZilla maximum EPS estimator

action name | description
--- | --- 
(n/a) | no named actions

example command | example description
----------- | -------
`logzilla speedtest` | show LogZilla current performance metrics

`start`  
Start LogZilla

action name | description
--- | --- 
(n/a) | no named actions

`stop`  
Stop LogZilla

action name | description
--- | --- 
(n/a) | no named actions


`triggers`  
LogZilla triggers import/export tool

action name | description
--- | --- 
list | list all non-default triggers
export | export triggers
import | import triggers
delete | delete triggers
update | update given trigger
performance | run trigger benchmarks

example trigger import file:  
```
 filter:
  - field: message
    op: qp
    value:
    - entered forwarding state
  mark_known: true
  name: entered forwarding state
  send_webhook_method: GET
  send_webhook_ssl_verify: true
```

example command | example description
----------- | -------
`logzilla triggers list *cisco*` | list triggers containing the word `cisco`
`logzilla triggers import -I new_trigger.yaml --owner johndoe` | import new trigger with owner johndoe

`uninstall`  
Uninstall LogZilla

action name | description
--- | --- 
(n/a) | no named actions

`upgrade`  
Upgrade LogZilla to latest version

action name | description
--- | --- 
(n/a) | no named actions

example command | example description
----------- | -------
`logzilla upgrade` | upgrade LogZilla to latest version
`logzilla upgrade --version v6.1.0-rc7` | upgrade LogZilla to a specific version

`version`  
Show LogZilla version

action name | description
--- | --- 
(n/a) | no named actions

