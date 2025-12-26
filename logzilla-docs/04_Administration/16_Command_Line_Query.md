<!-- @@@title:Command Line Query Tool@@@ -->

# Command Line Query Tool

The `logzilla query` command is an "unofficial" command provided to allow direct
queries to LogZilla using the command line. This tool may be useful for
generating reports such as TopN hosts, etc., along with the ability to export to
Excel.

## Prerequisites

- When running `logzilla query`, you will need to be the `root` user (or a user
  who has access to the `logzilla` command).
- The `logzilla query` command requires either `-u USER -p PASSWORD` OR an API
  key using the `-a` command.

## Command Options

| Parameter             | Alternate              | Description                                                                            |
|-----------------------|------------------------|----------------------------------------------------------------------------------------|
| `-h`                  | `--help`               | Show help text                                                                         |
| `-d`                  | `--debug`              | Debug mode                                                                             |
| `-q`                  | `--quiet`              | Notify only on warnings and errors (be quiet)                                          |
| `--timezone TIMEZONE` |                        | Specify the timezone for time-range parameters and exported data date formats          |
|                       |                        | (default: 'UTC')                                                                       |
| `-c CONFIG`           | `--config CONFIG`      | Specify path to config file, defaults to ~/.lz5query                                   |
| `-cu`                 | `--config_update`      | Update config file with given user/password/base-url                                   |
| `-u USER`             | `--user USER`          | Username to authenticate                                                               |
| `-p PASSWORD`         | `--password PASSWORD`  | Password to authenticate                                                               |
| `-a AUTHTOKEN`        | `--authtoken AUTHTOKEN`| Auth token to authenticate                                                             |
| `-bu BASE_URL`        | `--base-url BASE_URL`  | Base URL to the API                                                                    |
| `-t QTYPE`            | `--type QTYPE`         | Type of query to perform                                                               |
| `-st`                 | `--show-types`         | Show available query types                                                             |
| `-P PARAMS`           | `--params PARAMS`      | Path to JSON file with query parameters                                                |
| `-O OUTPUT_FILE`      | `--output-file OUTPUT_FILE` | Path to output file (format specified by --format)                                   |
| `--format {xlsx,json}`|                        | Output file format. If omitted, guesses from extension or defaults to JSON             |

## Query Types

The query types available can be listed using `logzilla query -st`. Those query
types are listed below:

| Query Type           | Description                                                  |
|----------------------|--------------------------------------------------------------|
| Search               | List events including detail                                 |
| EventRate            | Number of events per given time period                       |
| TopN                 | Top N values for a given field and time period               |
| LastN                | Last N values for a given field and time period              |
| StorageStats         | LogZilla storage counters for given time period              |
| ProcessingStats      | Number of events processed by LogZilla in a period           |
| Notifications        | List notification groups with detail                         |
| Tasks                | LogZilla tasks with detail                                   |
| System_CPU           | LogZilla host CPU usage                                      |
| System_Memory        | LogZilla host memory usage                                   |
| System_DF            | LogZilla host disk space free                                |
| System_IOPS          | LogZilla host IO operations per second                       |
| System_Network       | LogZilla host network usage                                  |
| System_NetworkErrors | LogZilla host network errors                                 |

The general way this command is used is to specify primarily the query type and
any of the parameters for the query itself, some of which, depending on the query
type, are necessary, and some optional. Use the remaining options as
appropriate. The query type is specified using the `-t` or `--type` options.
After specifying that option flag, put the query type name as listed in the query
type column above. Then query parameters must be specified in a JSON file. The
specific query types and their parameters are listed below.

## Specifying Query Parameters

Query parameters must be specified as a JSON file, which must be indicated on
the `logzilla query` command line. The query parameters are specified as a simple
JSON object in the file. Examples:

Return only events with a counter greater than 5:

```json
[ { "field": "counter", "op": "gt", "value": 5 } ]
```

Return events from host 'fileserver23' with severity 'ERROR' or higher:

```json
[ { "field": "severity", "value": [0, 1, 2, 3] },
  { "field": "host", "value": "fileserver23" } ]
```

Return events from hosts "alpha" and "beta" matching "power failure" in event
message text:

```json
[ { "field": "message", "value": "power failure" },
  { "field": "host", "value": ["alpha", "beta"] } ]
```

## Common Query Parameters

Although every query type has a particular list of parameters, there are some
parameters used by most or all queries:

### Time Range

Every query needs to have specified the start and end time of the period for
which to retrieve data. For some queries, the list of sub-periods in a given
period must also be specified - i.e., when getting events, some options would
be all minutes in the last hour, or last 30 days, etc.

The `time_range` parameter is an object with the following fields:

- `ts_from`: Timestamp (number of seconds from epoch) defining the beginning
  of the period. Use 0 (zero) to use the current time, or a negative number to
  specify time relative to the current time.

- `ts_to`: Timestamp defining the end of the period. 0 or negative numbers can
  be used to get time relative to the current time.

- `step`: If the query needs sub-periods, a step can be specified - such as 60
  will create 1-minute periods, 900 will give you 15-minute periods, etc.; the
  default is set heuristically according to `ts_from` and `ts_to` - i.e., when
  you specify a 1-hour time range, the step will be set to 1 minute, for the
  range of 1 minute or less, the step will be one second, etc.

- `preset`: Alternative to `ts_from` and `ts_to`; based on the timezone,
  determines the start of the day and uses corresponding `ts_from`, `ts_to`;
  available presets: 'today', 'yesterday'.

- `timezone`: Determines the beginning of the day for the `preset` parameter; by
  default, the `GLOBAL_TZ` config value is used.

For query types which do not use sub-periods (such as "LastN"), only `ts_from`
and `ts_to` are important (but still `step` and `round_to_step` can be used to
round those values).

### Filter

By default, every query operates on all data (according to the given time
range), but for each, a compound parameter "filter" can be specified, which
filters the returned results by selected fields (including optionally message
text). This parameter is an array of filter conditions which are always ANDed,
meaning each record must match all of them to be included in the final results.
Filtering is always done before aggregating, so for example, in a query for
event rate and with specified filtering by hostname, then only the events with
this hostname will be reported in query results.

Every filter condition is an object with the following fields:

- `field`: Name of the field to filter by, as it appears in the results.

- `value`: Actual value to filter by. For fields other than timestamp, this can
  also be a list of possible values (only for "eq" comparison).

- `op`: If the type is numeric (this includes timestamps), this can be used to
  define the type of comparison. It can be one of:

  | Operation | Meaning                                      |
  |-----------|----------------------------------------------|
  | eq        | Value is an exact value to be found, this is the default when no op is specified. Also accepts a list of possible values |
  | lt        | Match only records with field less than the given value |
  | le        | Match only records with field less than or equal to the given value |
  | gt        | Match only records with field greater than the given value |
  | ge        | Match only records with field greater than or equal to the given value |
  | qp        | Special operator for "message boolean syntax" |

- `ignore_case`: Determines whether text comparisons are case-sensitive or not.
  Default is `True`, so all text comparisons are case-insensitive. To force
  case-sensitive mode, set `ignore_case` to `False`.

## Query Results

"Results" is always an object with one or a few fields. Usually, this is
"totals" and/or "details", the first containing results for the whole period,
the second an array of values for sub-periods. Both total and sub-period usually
contain "ts_from" and "ts_to" timestamps, to show the exact time range that data
were retrieved for, and then some "values

" or just "count".

See the description of the particular query type for details on what results
contain and the results format, with some examples.

### Generic Results Format for System Queries

System queries return data collected by the system regarding different system
parameters and are used for displaying system widgets (that can be used later
on for diagnosing system performance).

All these queries return "totals" and "details". For details, the result objects
are similar to data for `EventRateQuery`, only there are more keys with different
values (this one is from `System_CPUQuery`):

```json
{
  "details": [
    {
      "ts_from": 1416231300,
      "ts_to": 1416231315,
      "softirq": 0,
      "system": 8.400342,
      "idle": 374.946619,
      "user": 16.067144,
      "interrupt": 0.20001199999999997,
      "nice": 0,
      "steal": 0,
      "wait": 0.20001199999999997
    },
    "..."
  ]
}
```

For totals, instead of an array, there is a single object with keys like above,
but rather than a single result value, it is a set of values:

```json
{
  "system": {
    "count": 236,
    "sum": 1681.6008720000007,
    "min": 5.2671220000000005,
    "max": 9.599976,
    "avg": 7.125427423728817,
    "last": 6.400112999999999,
    "last_ts": 1416234840
  }
}
```

Here are different kinds of aggregates for a selected time period:

| Aggregate Name | Meaning                                           |
|----------------|---------------------------------------------------|
| count          | Number of known values for the given time period  |
| sum            | Total of those values (used for calculating avg)  |
| min            | Minimum value                                     |
| max            | Maximum value                                     |
| avg            | Average value (sum / count)                       |
| last           | Last known value from the given period            |
| last_ts        | Timestamp when last known value occurred          |

## Query Details

### Search

Show a list of event detail matching the specified search filter parameters.

**Parameters:**

- `time_range`: Data are taken for this time range (periods are ignored).

- `filter`: Desired filters for the search to limit the results returned.

- `sort`: List of fields to sort results by; only `first_occurrence`,
  `last_occurrence`, and `count` are available. Descending sort order is
  indicated by prefixing the field name with a "-" (minus) sign.

- `page_size`: Number of events to retrieve.

- `page`: Number of pages to retrieve, used with `page_size`. The bigger the
  page number, the longer it will take to retrieve results, especially in
  multi-host configurations.

In the results, there are two values: `totals` contains the count of all items
found, including sometimes "total_count" if there were more than could be
retrieved; "events" contains the actual list of events in the form identical to
all lists with paging - so information is provided about the number of items,
number of pages, current page number, and then actual objects (current page only)
under the "objects" key:

```json
{
  "totals": {
    "ts_from": 1401995160,
    "ts_to": 1401995220,
    "count": 623
  },
  "events": {
    "page_count": 7,
    "item_count": 623,
    "page_number": 1,
    "page_size": 100,
    "objects": [
      {
        "id": 2392934923,
        "first_occurence": 1401995162.982510,
        "last_occurence": 1401995162.982510,
        "count": 1,
        "host": "router-32",
        "program": "kernel",
        "severity": 5,
        "facility": 3,
        "message": "This is some message from kernel",
        "flags": []
      },
      {
        "id": 2392939813,
        "first_occurence": 1401995162.990218,
        "last_occurence": 1401995164.523620,
        "count": 5,
        "host": "router-32",
        "program": "kernel",
        "severity": 5,
        "facility": 3,
        "message": "This is another message from kernel",
        "flags": ["KNOWN"]
      },
      "..."
    ]
  }
}
```

### EventRate

Get the number of events per given time period - i.e., per second for the last
minute, or events per day for the last month, etc. Filters can be used to get
rates for a particular host, program, severity, or any combination of them. It
is also used on the search results page to show a histogram for the search
results.

**Parameters:**

- `time_range`: Data are taken for this time range, periods are generated
  according to the description of this parameter. See section "Common Query
  Parameters".

- `filter`: Extra filtering.

**Results Format:**

Similar to other types, there are "totals" and "details". For details, there is
only "count", for "totals" there are self-explanatory aggregates (the one called
"last" is just the last value from "details").

`drill_up_time_range` is the time range that should be used for showing a wider
time period (such as if *minute* is selected, the whole hour will be shown, when
*hour* is selected, it will show the whole day, etc.). It can be `null` as it is
always limited to one day at most - so if a whole day or wider time range is
chosen, the `null` value will be used to indicate there is no option to drill up.

```json
{
  "totals": {
    "ts_from": 123450000,
    "ts_to": 123453600,
    "drill_up_time_range": {
      "ts_from": 123379200,
      "ts_to": 123465600
    },
    "sum": 5511,
    "count": 120,
    "min": 5,
    "max": 92,
    "avg": 45.925,
    "last": 51
  },
  "details": [
    {
      "ts_from": 123450000,
      "ts_to": 123450060,
      "count": 41
    },
    {
      "ts_from": 123450060,
      "ts_to": 123450120,
      "count": 12
    },
    {
      "ts_from": 123450120,
      "ts_to": 123450180,
      "count": 39
    },
    "..."
  ]
}
```

### TopN

Get the top N values for the specified field and period, optionally with
filtering. Also optional are detailed counts for sub-periods of the specified
period.

**Parameters:**

- `time_range`: Data are taken for this time range.

- `field`: Which field to aggregate by (defaults to "host").

- `with_subperiods`: Boolean; if set, then the results will include not only
  data for the whole time range but also for all sub-periods.

- `top_periods`: Boolean; if set, then the results will include the top N
  sub-periods.

- `filter`: Extra filters can be specified; see "Common Query Parameters"
  description for details.

- `limit`: This is the actual "N", that is, the number of values to retrieve.

- `show_other`: This boolean enables one extra value called "other", with the
  sum of all remaining values from N+1 to the end of the list.

- `ignore_empty`: This boolean enables ignoring empty event field/tag values
  (default: `True`).

- `subfields`: Extra subfields can be specified to get detailed results.

- `subfields_limit`: This is the actual "N" for subfields, that is, the number
  of subfield values to show.

**Results Format:**

First, "totals" are always included with values for the whole time period:

```json
{
  "totals": {
    "ts_from": 123450000,
    "ts_to": 123453600,
    "values": [
      { "name": "host32", "count": 3245 },
      { "name": "host15", "count": 2311 },
      { "name": "localhost", "count": 1255 },
      "..."
    ]
  }
}
```

Elements are sorted from highest to lowest count, but if "show_other" is chosen
then the last value is always "other" regardless of the count, which can be
larger than any previous. The number of elements in "values" can be less than
the "limit" parameter if not enough different values for the specified field
were found in the specified time period.

If "with_subperiods" is enabled, then besides "totals" there will be "details",
an array of all sub-periods:

```json
{
  "details": [
    {
      "

ts_from": 123450000,
      "ts_to": 123450060,
      "values": [
        { "name": "host2", "count": 1 },
        { "name": "host3", "count": 10 },
        { "name": "localhost", "count": 20 },
        "..."
      ],
      "total_values": [
        { "name": "host32", "count": 151 },
        { "name": "host15", "count": 35 },
        { "name": "localhost", "count": 13 },
        "..."
      ],
      "total_count": 199
    },
    {
      "ts_from": 123450060,
      "ts_to": 123450120,
      "values": [
        { "name": "host32", "count": 42 },
        { "name": "host15", "count": 0 },
        { "name": "localhost", "count": 51 },
        "..."
      ],
      "total_count": 93
    },
    "..."
  ]
}
```

In "values", the TopN value only for the specified time sub-period will be given
(which may be different from the TopN of the entire period). In "total_values",
there will be detailed total values for the specified time sub-period. Please
note that for sub-periods, the order of "total_values" is always the same as in
"totals", regardless of actual counts; also, for some entries, there can be 0
(zero) as a count (but the actual name is always present).

If "top_periods" is enabled, there will be a "top_periods" array of top (sorted
by total_count) sub-periods:

```json
{
  "top_periods": [
    {
      "ts_from": 123450000,
      "ts_to": 123450060,
      "values": [
        { "name": "host32", "count": 151 },
        { "name": "host15", "count": 35 },
        { "name": "localhost", "count": 13 },
        "..."
      ],
      "total_count": 199
    },
    {
      "ts_from": 123450060,
      "ts_to": 123450120,
      "values": [
        { "name": "host32", "count": 42 },
        { "name": "host15", "count": 0 },
        { "name": "localhost", "count": 51 },
        "..."
      ],
      "total_count": 93
    },
    "..."
  ]
}
```

If "subfields" is enabled, there will be "subfields" with a counter at each
detail sub-period:

```json
{
  "totals": {
    "values": [
      {
        "name": "host32",
        "count": 3245,
        "subfields": {
          "program": [
            { "name": "program1", "count": 3240 },
            { "name": "program2", "count": 5 }
          ],
          "facility": [
            { "name": 0, "count": 3000 },
            { "name": 1, "count": 240 },
            { "name": 2, "count": 5 }
          ]
        }
      },
      "..."
    ]
  },
  "details": [
    {
      "values": [
        {
          "name": "host32",
          "count": 151,
          "subfields": {
            "program": [
              { "name": "program1", "count": 150 },
              { "name": "program2", "count": 1 }
            ],
            "facility": [
              { "name": 0, "count": 100 },
              { "name": 1, "count": 50 },
              { "name": 2, "count": 1 }
            ]
          }
        },
        "..."
      ]
    },
    "..."
  ],
  "top_periods": [
    {
      "values": [
        {
          "name": "host32",
          "count": 151,
          "subfields": {
            "program": [
              { "name": "program1", "count": 150 },
              { "name": "program2", "count": 1 }
            ],
            "facility": [
              { "name": 0, "count": 100 },
              { "name": 1, "count": 50 },
              { "name": 2, "count": 1 }
            ]
          }
        },
        "..."
      ]
    },
    "..."
  ]
}
```

### LastN

Get the last N values for the specified field and time period, with the number
of occurrences per given time range.

**Parameters:**

- `time_range`: Data are retrieved for this time range.

- `field`: Which field to aggregate by.

- `filter`: Filtering; see "Common Query Parameters" description.

- `limit`: This is the actual "N" -- number of values to show.

**Results Format:**

There is always only a "totals" section, with the following content:

```json
{
  "totals": {
    "ts_from": 123450000,
    "ts_to": 123453600,
    "values": [
      { "name": "host32", "count": 3245, "last_seen": 1401981776.890153 },
      { "name": "host15", "count": 5311, "last_seen": 1401981776.320121 },
      { "name": "localhost", "count": 1255, "last_seen": 1401981920.082937 },
      "..."
    ]
  }
}
```

As indicated, it is similar to "TopN", but there is also a "last_seen" field,
with possibly a fractional part of a second. Also, elements are sorted by
"last_seen" instead of "count". Both elements shown and counts take into account
time_range and filters.

### StorageStats

Get LogZilla event counters for the specified time period. This is similar to
"EventRate", but does not allow for any filtering and returns only total
counters without sub-period details.

Time Range is rounded up to full hours, so if a 1s time period is specified the
result will be hourly counters.

**Parameters:**

- `time_range`: Data are retrieved for this time range. Periods are generated
  according to the description of this parameter, see section "Common Query
  Parameters". Max time_range is the last 24 hours.

**Results Format:**

The result will be "totals" and "all_time" counters:

- `totals`: Counters from the given period.

- `all_time`: All-time counters.

For both, there are three keys:

- `new`: Number of new items processed (not duplicates).

- `duplicates`: Number of items that were found to be duplicates.

- `total`: Total sum.

Sample data:

```json
{
  "totals": {
    "duplicates": 25,
    "new": 75,
    "total": 100,
    "ts_to": 1441090061,
    "ts_from": 1441090001
  },
  "all_time": {
    "duplicates": 20000,
    "new": 18000,
    "total": 20000
  }
}
```

### ProcessingStats

Get the number of events processed by LogZilla in the specified time period.
Similar to the EventRates but does not allow for any filtering. Also, event
timestamps are irrelevant; only the moment it was actually processed by LogZilla
is used. To use this query, internal counters verbosity must be set to DEBUG
(run `logzilla config INTERNAL_COUNTERS_MAX_LEVEL DEBUG`).

**Parameters:**

- `time_range`: Data are retrieved for this time range. Periods are generated
  according to the description of this parameter, see section "Common Query
  Parameters". Max time_range is the last 24 hours.

**Results Format:**

Similar to other query types, there are "totals" and "details". For both, there
will be an object with the time range and three keys:

- `new`: Number of new items processed (not duplicates).

- `duplicates`: Number of items that were found to be duplicates.

- `oot`: Item ignored, because their timestamp was outside the `TIME_TOLERANCE`
  compared to the current time (this should be zero under normal circumstances).

Sample data:

```json
{
  "totals": {
    "duplicates": 20,
    "oot": 5,
    "new": 75,
    "total": 100,
    "ts_to": 1441090061,
    "ts_from": 1441090001
  },
  "details": [
    {
      "duplicates": 10,
      "new": 5,
      "oot": 15,
      "ts_from": 1441090001,
      "ts_to": 1441090002
    },
    "..."
    {
      "duplicates": 15,
      "new": 1,
      "oot": 10,
      "ts_from": 1441090060,
      "ts_to": 1441090061
    }
  ]
}
```

### Notifications

Get the list of notification groups, with associated events.

**Parameters:**

- `sort`: Order of notification groups, which can be one of "Oldest first",  "Newest first", "Oldest unread first", and "Newest unread first".

- `time_range`: Data are taken for this time range.

- `time_range_field`: Specify the field for the time range processing. Available
  fields: "updated_at", "created_at", "unread_since", and "read_at".

- `is_private`: Filter list by `is_private` flag; true or false.

- `read`: Filter list by `read_flag` flag; true or false.

- `with_events`: Add to data events information; true or false.

Sample data:

```json
[
  {
    "id": 1,
    "name": "test",
    "trigger_id": 1,
    "is_private": false,
    "read_flag": false,
    "all_count": 765481,
    "unread_count": 765481,
    "hits_count": 911282,
    "read_at": null,
    "updated_at": 1446287520,
    "created_at": 1446287520,
    "owner": {
      "id": 1,
      "username": "admin",
      "fullname": "Admin User"
    },
    "trigger": {
      "id": 1,
      "snapshot_id": 1,
      "name": "test",
      "is_private": false,
      "send_email": false,
      "exec_script": false,
      "snmp_trap": false,
      "mark_known": false,
      "mark_actionable": false,
      "issue_notification": true,
      "add_note": false,
      "send_email_template": "",
      "script_path": "",
      "note_text": "",
      "filter": [
        {
          "field": "message",
          "value": "NetScreen"
        }
      ],
      "is_active": false,
      "active_since": 1446287518,
      "active_until": 1446317276,
      "updated_at": 1446317276,
      "created_at": 1446287518,
      "owner": {
        "id": 1,
        "username": "admin",
        "fullname": "Admin User"
      },
      "hits_count": 911282,
      "last_matched": 1446317275,
      "notifications_count": 911282,
      "unread_count": 911282,
      "last_issued": 1446317275,
      "order": null
    }
  }
]
```

### Tasks

Get the list of tasks.

**Parameters:**

- `target`: Filter list by assigned to, which can be `assigned_to_me` or `all`.

- `is_overdue`: Filter list by `is_overdue` flag; true or false.

- `is_open`: Filter list by `is_open` flag; true or false.

- `assigned_to`: Filter list by assigned user id list; for an empty list, it
  will return only unassigned.

- `sort`: List of fields to sort results by; available fields are "created_at"
  and "updated_at". Descending sort order is indicated by prefixing the field
  name with a `-` (minus) sign.

Sample data:

```json
[
  {
    "id": 1,
    "title": "Task name",
    "description": "Description",
    "due": 1446508799,
    "status": "new",
    "is_overdue": false,
    "is_closed": false,
    "is_open": true,
    "assigned_to": 1,
    "updated_at": 1446371434,
    "created_at": 1446371434,
    "owner": {
      "id": 1,
      "username": "admin",
      "fullname": "Admin User"
    }
  }
]
```

### System_CPU

Get the LogZilla system CPU utilization statistics.

**Parameters:**

- `time_range`: Data are taken for this time range; only `ts_from` and `ts_to`
  are used; the step is always determined by the system, depending on data
  available for the given period.

- `cpu`: Number of CPUs (from 0 to n-1, with n being the actual number of CPU
  cores in the system), or 'totals' to get the sum for all CPUs.

**Results Format:**

This query returns CPU usage broken down by different categories:

- `user`: CPU used by user applications.

- `nice`: CPU used to allocate multiple processes demanding more cycles than
  the CPU can provide.

- `system`: CPU used by the operating system itself.

- `interrupt`: CPU allocated to hardware interrupts.

- `softirq`: CPU servicing soft interrupts.

- `wait`: CPU waiting for disk IO operations to complete.

- `steal`: Xen hypervisor allocating cycles to other tasks.

- `idle`: CPU not doing any work.

All of those are float numbers, which should sum to approximately 100, or with
`cpu` param set to "totals" then to `100*n` where n is the number of CPU cores.

**Note:**

The CPU plugin does not collect percentages. It collects "jiffies", the units
of scheduling. On many Linux systems, there are circa 100 jiffies in one
second, but this does not mean you will end up with a percentage. Depending on
system load, hardware, whether or not the system is virtualized, and possibly
half a dozen other factors, there may be more or less than 100 jiffies in one
second. There is absolutely no guarantee that all states add up to 100, an
absolute must for percentages.

Sample data:

The following query types follow a similar pattern for returned data:

```json
{
  "details": [
    {
      "ts_from": 1611867480,
      "ts_to": 1611867540,
      "usage_softirq": 0,
      "usage_system": 0,
      "usage_idle": 0,
      "usage_user": 0,
      "usage_irq": 0,
      "usage_nice": 0,
      "usage_steal": 0,
      "usage_iowait": 0
    },
    {
      "ts_from": 1611867540,
      "ts_to": 1611867600,
      "usage_softirq": 0,
      "usage_system": 0,
      "usage_idle": 0,
      "usage_user": 0,
      "usage_irq": 0,
      "usage_nice": 0,
      "usage_steal": 0,
      "usage_iowait": 0
    },
    "..."
    {
      "ts_from": 1611870960,
      "ts_to": 1611871020,
      "usage_softirq": 1.3373717712305375,
      "usage_system": 2.1130358200960164,
      "usage_idle": 88.01073838110112,
      "usage_user": 8.521107515994341,
      "usage_irq": 0,
      "usage_nice": 0.0053355008139296,
      "usage_steal": 0,
      "usage_iowait": 0.012411010763977177
    },
    {
      "ts_from": 1611871020,
      "ts_to": 1611871080,
      "usage_softirq": 1.3263522984202727,
      "usage_system": 1.9636949977972675,
      "usage_idle": 88.57548790373977,
      "usage_user": 8.114988886402712,
      "usage_irq": 0,
      "usage_nice": 0.0030062024636270655,
      "usage_steal": 0,
      "usage_iowait": 0.01646971117643204
    }
  ],
  "totals": {
    "usage_softirq": {
      "sum": 5.14695979124877,
      "last": 0,
      "count": 60,
      "min": 0,
      "max": 1.3373717712305375,
      "avg": 0.0857826631874795
    },
    "usage_system": {
      "sum": 9.440674464879018,
      "last": 0,
      "count": 60,
      "min": 0,
      "max": 2.889874887810517,
      "avg": 0.1573445744146503
    },
    "usage_idle": {
      "sum": 346.47517999267575,
      "last": 0,
      "count": 60,
      "min": 0,
      "max": 88.57548790373977,
      "avg": 5.774586333211262
    },
    "usage_user": {
      "sum": 37.39057249683675,
      "last": 0,
      "count": 60,
      "min": 0,
      "max": 12.814818659484397,
      "avg": 0.6231762082806125
    },
    "usage_irq": {
      "sum": 0,
      "last": 0,
      "count": 60,
      "min": 0,
      "max": 0,
      "avg": 0
    },
    "usage_nice": {
      "sum": 0.05683650311556292,
      "last": 0,
      "count":

 60,
      "min": 0,
      "max": 0.03198513688698273,
      "avg": 0.0009472750519260487
    },
    "usage_steal": {
      "sum": 0,
      "last": 0,
      "count": 60,
      "min": 0,
      "max": 0,
      "avg": 0
    },
    "usage_iowait": {
      "sum": 1.4897767512445244,
      "last": 0,
      "count": 60,
      "min": 0,
      "max": 1.3717653475044271,
      "avg": 0.024829612520742072
    }
  }
}
```

### System_Memory

Get the system memory utilization statistics for the LogZilla host.

**Parameters:**

- `time_range`: Data are taken for this time range; only `ts_from` and `ts_to`
  are used; the step is always determined by the system, depending on data
  available for the given period.

**Results Format:**

This query returns memory usage (in bytes) broken down by:

- `used`: Memory used by user processes.

- `buffered`: Memory used for I/O buffers.

- `cached`: Memory used by disk cache.

- `free`: Free memory.

Data returned is similar to System_CPU.

### System_DF

Get the system disk space free amounts for the LogZilla host.

**Parameters:**

- `time_range`: Data are taken for this time range; only `ts_from` and `ts_to`
  are used; the step is always determined by the system, depending on data
  available for the given period.

- `fs`: Filesystem to show information - "root" is always included, other
  possible values are system-dependent.

**Results Format:**

This query returns disk usage (in bytes) broken down by:

- `used`: Space used by data.

- `reserved`: Space reserved for root user.

- `free`: Free disk space.

Data returned is similar to System_CPU.

### System_IOPS

Get the system IO operations per second for the LogZilla host.

**Parameters:**

- `time_range`: Data are taken for this time range; only `ts_from` and `ts_to`
  are used; the step is always determined by the system, depending on data
  available for the given period.

**Results Format:**

This query returns the read/write counts for each sub-period and then the totals
for sum/last/count/min/max/average.

- `writes`: Write IO operations per second.

- `reads`: Read IO operations per second.

Data returned is similar to System_CPU.

### System_Network

Get system network utilization statistics for the LogZilla host.

**Parameters:**

- `time_range`: Data are taken for this time range; only `ts_from` and `ts_to`
  are used; the step is always determined by the system, depending on data
  available for the given period.

- `interface`: Network interface to show data from; usually, there's "lo" for
  loopback interface, others are system-dependent.

**Results Format:**

This query returns the following data for the selected network interface:

- `if_packets.tx`: Number of packets transferred.

- `if_packets.rx`: Number of packets received.

- `if_octets.tx`: Number of octets (bytes) transferred.

- `if_octets.rx`: Number of octets (bytes) received.

- `if_errors.tx`: Number of transmit errors.

- `if_errors.rx`: Number of receive errors.

Data returned is similar to System_CPU.

### System_NetworkErrors

Get system network error counts for the LogZilla host.

**Parameters:**

- `time_range`: Data are taken for this time range; only `ts_from` and `ts_to`
  are used; the step is always determined by the system, depending on data
  available for the given period.

- `interface`: Network interface to show data from; usually, there's "lo" for
  loopback interface, others are system-dependent.

**Results Format:**

This query returns the following data for the selected network interface:

- `drop_in`: Number of incoming packets dropped.

- `drop_out`: Number of outgoing packets dropped.

- `err_in`: Number of incoming errored packets.

- `err_out`: Number of outgoing errored packets.

Data returned is similar to System_CPU.

## Use Cases

This section provides practical examples of how to use the LogZilla Command Line Query Tool.

### Generate Weekly Excel Reports for Top Devices by Severity

The following example demonstrates how to generate a weekly Excel report showing the
top 20 devices by total message count, filtered on high severity, along with each
host's top severities.

The implementation process consists of the following steps:

1. Make sure you are root:

   ```sh
   sudo su -
   ```

2. Create a file (e.g., `myfile.sh`) on your LogZilla server with the following
   content:

   ```sh
   #!/bin/bash

   # Ensure the script is run as root
   if [ "$(id -u)" -ne 0 ]; then
       echo "This script must be run as root. Please switch to root using 'sudo su -' and try again."
       exit 1
   fi

   # Check if LOGZILLA_API_KEY is set in root's .bashrc
   if ! grep -q "LOGZILLA_API_KEY" /root/.bashrc; then
       echo "LOGZILLA_API_KEY is not set in /root/.bashrc."
       echo "Please run 'logzilla authtoken list' to retrieve your API key."
       echo "Add 'LOGZILLA_API_KEY=your_api_key' to /root/.bashrc, replace 'your_api_key' with the actual key."
       echo "Then run 'source /root/.bashrc' to apply the changes and re-run this script."
       exit 1
   fi

   # Create the cron job
   echo "Adding the following to '/etc/cron.d/logzilla-daily-report':"
   echo "0 6 * * * root logzilla query -t TopN -P \${HOME}/.logzilla-topn-report.json --output-file /tmp/top20_devices_with_severities-$(date +%Y%m%d).xlsx --format xlsx -a \${LOGZILLA_API_KEY}" | tee /etc/cron.d/logzilla-daily-report

   # Create the .logzilla-topn-report.json configuration file
   cat <<EOL > /root/.logzilla-topn-report.json
   {
       "field": "host",
       "limit": 20,
       "time_range": {
           "preset": "last_24_hours"
       },
       "filter": [
           { "field": "severity", "value": [0, 1, 2, 3] }
       ],
       "subfields": ["severity"],
       "subfields_limit": 20
   }
   EOL
   ```

3. Run the script:

   ```sh
   bash ./myfile.sh
   ```

The script creates an `/etc/cron.d/logzilla-daily-report` file that automatically
generates the Excel report with the current date to
`/tmp/top20_devices_with_severities-$(date +%Y%m%d).xlsx` on a daily basis at 6 AM.

> Note: The example stores the report in `/tmp` for simplicity, but should be
> modified to a more permanent location if desired.

### Extract Events Per Week from Last Year

This procedure generates a report of event counts per week for the past year, converting the results into an easy-to-use CSV file.

> **Important:** Set the `LOGZILLA_API_KEY` in your environment before proceeding.

1. **Create a parameter file** (`eventrate-params.json`):

   ```json
   {
     "time_range": {
       "preset": "last_365_days",
       "step": 604800
     },
     "with_archive": true
   }
   ```

> **Note:** The `step` value `604800` equals one week (60 seconds × 60 minutes
> × 24 hours × 7 days).

1. **Run the LogZilla query:**

   ```sh
   sudo logzilla query -t EventRate -P eventrate-params.json \
       --output-file eventrate.json -a ${LOGZILLA_API_KEY}
   ```

   This generates a JSON file named `eventrate.json` containing event data.

2. **Convert the JSON to CSV using `jq`:**

   ```sh
   jq -r '
   .results.details |
   (["ts_from","ts_to","count"]),
   (.[] | [
     (.ts_from | todate),
     (.ts_to | todate),
     .count
   ]) | @csv' eventrate.json > eventrate.csv
   ```

Your results are now saved in `eventrate.csv`.

1. **Example CSV output:**

   ```csv
   "ts_from","ts_to","count"
   "2025-03-18T12:17:00Z","2025-03-18T12:18:00Z",7019
   "2025-03-18T12:18:00Z","2025-03-18T12:19:00Z",7036
   "2025-03-18T12:19:00Z","2025-03-18T12:20:00Z",6870
   ```

### EventRate Sample Shell Script

Here's a complete shell script example to automate the above steps:

```bash
#!/bin/bash

LOGZILLA_API_KEY="your_logzilla_api_key_here"

PARAM_FILE="eventrate-params.json"
JSON_OUTPUT="eventrate.json"
CSV_OUTPUT="eventrate.csv"

cat > "$PARAM_FILE" <<EOF
{
    "time_range": {
      "preset": "last_365_days",
      "step": 604800
    },
    "with_archive": true
}
EOF

sudo logzilla query -t EventRate -P "$PARAM_FILE" \
    --output-file "$JSON_OUTPUT" -a "$LOGZILLA_API_KEY"

if [ ! -f "$JSON_OUTPUT" ]; then
  echo "Error: JSON output file not created."
  exit 1
fi

jq -r '
.results.details |
(["ts_from","ts_to","count"]),
(.[] | [
  (.ts_from | todate),
  (.ts_to | todate),
  .count
]) | @csv' "$JSON_OUTPUT" > "$CSV_OUTPUT"

echo "CSV output successfully generated at: $CSV_OUTPUT"
```

### Find the Oldest Event in the System

This procedure identifies the oldest event stored in LogZilla, including archived data:

1. **Create a parameter file** (`oldest-event.json`):

   ```json
   {
     "time_range": {
       "preset": "last_9999_days"
     },
     "sort": [
       "first_occurrence"
     ],
     "limit": 1,
     "with_archive": true
   }
   ```

   > **Note:** A large time range (`last_9999_days`) ensures the search includes
   > all available data, including archives.

2. **Run the query:**

   ```sh
   sudo logzilla query -t Search -P oldest-event.json -a ${LOGZILLA_API_KEY}
   ```

3. **View the oldest event:** The result will display details of the earliest
   recorded event in LogZilla.

   Sample output:

   ```json
   {"page_number":1,"page_size":1,"offset":0,"page_count":1,"item_count":1,"objects":[{"id":6330125066960896,"severity":6,"facility":23,"trigger_ids":[],"message":"%ASA-6-302023: Teardown forwarder TCP connection for outside:69.133.216.93/443 to unknown:123.191.222.48/38496 duration 0:00:00 forwarded bytes 0 Forwarding or redirect flow removed to create director or backup flow","host":"EDGEFW-ASACL01","program":"Cisco ASA","cisco_mnemonic":"ASA-6-302023","user_tags":{},"extra_fields":{},"status":0,"counter":1,"first_occurrence":1741910400.000908,"last_occurrence":1741910400.000908,"_id":"6330125066960896","severity_name":"INFO","facility_name":"LOCAL7","status_name":"UNKNOWN","triggers_fired_count":0,"triggers_fired_data":[],"notes_count":0,"notes":[],"first_occurrence_date":"2025/03/14 00:00:00","last_occurrence_date":"2025/03/14 00:00:00"}]}
   ```

### Oldest Event Sample Shell Script

Here's a complete shell script example to automate the above steps:

```bash
#!/bin/bash

LOGZILLA_API_KEY="your_logzilla_api_key_here"

# Define parameter and output file paths
PARAM_FILE="oldest-event.json"
JSON_OUTPUT="oldest.json"
CSV_OUTPUT="oldest.csv"

# Create parameter file
cat > "$PARAM_FILE" <<EOF
{
  "time_range": {
    "preset": "last_9999_days"
  },
  "sort": [
    "first_occurrence"
  ],
  "limit": 1,
  "with_archive": true
}
EOF

# Run LogZilla query command
sudo logzilla query -t Search -P "$PARAM_FILE" \
    --output-file "$JSON_OUTPUT" -a "$LOGZILLA_API_KEY"

# Check if JSON file was created successfully
if [ ! -f "$JSON_OUTPUT" ]; then
  echo "Error: JSON output file not created."
  exit 1
fi

# Convert JSON to CSV using jq
jq -r '
.objects |
(["id","severity","facility","message","host","program","severity_name","facility_name","status_name","first_occurrence_date","last_occurrence_date"]),
(.[] | [
  .id,
  .severity,
  .facility,
  .message,
  .host,
  .program,
  .severity_name,
  .facility_name,
  .status_name,
  .first_occurrence_date,
  .last_occurrence_date
]) | @csv' "$JSON_OUTPUT" > "$CSV_OUTPUT"

# Final message
echo "CSV output successfully generated at: $CSV_OUTPUT"
```
