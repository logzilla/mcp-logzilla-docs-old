<!-- @@@title:Query API@@@ -->

## Creating a New Query
A new query is created through `POST /api/query`, and always includes two parameters (usually with JSON body):

**type**  
Indicates which query you want to perform. See **Query Types** for more detail.

**params**  
A JSON object containing the parameters for the query. Every *query type* has a different list of available parameters. 

After creating a query you can get its results either immediately (if it was able to complete in 1 second) with response `200 "OK"`, or (for requests which must be completed asynchronously) a status of `202 "ACCEPTED"` with response body containing a `query_id`.

## Asynchronous Requests

> NOTE: Although you can query for results at any time with `GET /api/query/<id>` the recommended way of getting query results is to use *websockets* and *subscriptions* (see below).

If your initial query returns `202 "ACCEPTED"` run the query again to check for results using the query id value returned from the first query using `GET /api/query/<id>` to get updated results. 

### Relative Time Queries
For results that have a completed status of `200 "SUCCESS"` subsequent queries to the same id will provide refreshed results on relative time queries such as *last hour*. 

### Polling Query Results
To retrieve the current data of an existing query (whether currently processing or not) use `GET /api/query/<id>`.

`GET /api/query/<id>` can return paged results of the data by providing additional parameters of `page_size=<num of results>` and `page=<page number>`. The HTTP result message is always returned immediately but the query status (in the returned JSON) could indicate that the query is incomplete (query status `IN_PROGRESS`) or even as of yet empty (query status `PENDING`).

For example, if your query is not completed immediately the received response would be:

```
{
  "query_id": "72bc846140344b4da3cdcfb831174a3e",
  "status": "IN_PROGRESS",
  "type": "Search",
  "base_time": 1416233863,
  "results": {
    "..."
  },
  "params": {
    "sort": [
      "first_occurence"
    ],
    "filter": [],
    "page": 1,
    "page_size": 100,
    "time_range": {
      "ts_from": 1000,
      "ts_to": 10000
    }
  },
  "owner_id": 1
}
```

When a query is completed (possibly immediately) the response would be:

```
{
  "query_id": "72bc846140344b4da3cdcfb831174a3e",
  "status": "SUCCESS",
  "type": "Search",
  "base_time": 1416233863,
  "results": {
    "..."
  },
  "params": {
    "sort": [
      "first_occurence"
    ],
    "filter": [],
    "page": 1,
    "page_size": 100,
    "time_range": {
      "ts_from": 1000,
      "ts_to": 10000
    }
  },
  "owner_id": 1
}
```

### Getting query results via websocket

The recommended way of getting query results, especially for widgets, is using websockets. Using the websocket method (vs. `GET /api/query/`) provides initial calculation results, partial results for asynchronous queries, and final results of the query. 

Websockets for the API are available under `/ws/live-updates` and, after establishing the connection, allows for real-time subscription and unsubscription on events of interest. 

Websocket operations should be sent using *encoded JSON* with an array of commands and parameters, for example:

```
["subscribe", "widget", 2]
```

Subscription to a particular query or widget can be accomplished by providing the appropriate entity id, for which query id is a string and widget id is an integer, subscription to the whole dashboard can be requested in which case websocket updates will then include get updates for all widgets on that dashboard.

Unsubscribing can be accomplished either by providing the same parameters that were used for the subscription, or removal of all subscriptions with:

`["unsubscribe", "all"]`

After successful subscription/unsubscription a confirmation result will be returned, which always contains the list of currently subscribed items:
```
["subscription-update", {"query": [], "widget": [2], "dashboard": []}]
```
Once subscribed updates for the requested objects will begin. Each update is a separate message as follows:
```
["widget-update", {
    "widget_id": 2,
    "dashboard_id": null,
    "data": {
        "status": "SUCCESS",
        "query_id": "4f29934c97b1c0857c2341c3cb188371",
        "results": {
            "totals": "...",
            "details": "..."
        }
    }
}]
```
For widgets that are directly subscribed the dashboard_id as shown above will be null.  For query subscriptions, both dashboard_id and widget_id will be null. The *data* field contains exactly the same content that `GET /api/query/<id>` would return, as indicated in the documentation for each particular request type.

## Common query parameters
Although every query, type defines its own list of parameters there are some parameters used by most of them:

### time_range
For every query the start- and end-time period of the desired data must be provided. For some queries, a list of sub-periods in the given period must also be provided - i.e. when requesting event rates ordinarily a list of values will be provided, such as all minutes in the last hour, or last 30 days, etc..

the time_range parameter is an object with the following fields:

**ts_from**  
timestamp (number of seconds from epoch) defining the beginning of the period, for which 0 (zero) can be used to use the current time, or a negative number to specify time relative to the current time

**ts_to**  
timestamp defining the end of the period.  0 or a negative number can be provided to get time relative to current

**step**  
if the query needs sub-periods then a step can be provided; for example, 60 will create 1-minute periods, 900 will give 15-minutes periods, and so on. The default is set heuristically according to ts_from and ts_to - i.e. when a 1 hour time range is requested `step` will be set to 1 minute, for the range of 1 minute or less `step` will be one second, and so on.

**preset**  
alternative to ts_from and ts_to; based on the timezone determines the start of the day and uses appropriate ts_from, ts_to; available presets: ‘today’, ‘yesterday’

**timezone**  
determines the beginning of the day for preset parameter; by default, GLOBAL_TZ config value is used

Periods are always rounded to the nearest multiple of `step`. Rounding is always up so the last period is often partially in the future, such as if a step of 1 hour is requested and it is now 13:21 then the last period will be 13:00 - 14:00.  This then results in results for the current hour being received despite the hour indicated not yet being complete.
For query types that do not use subperiods (such as "LastN") only ts_from and ts_to are important, but `step` and `round_to_step` to round can still be used. (Note that in earlier versions there was an option to provide `round_to_step` and `periods` parameters, which are now unsupported).

### filter
By default, every query operates on all data (according to the given time range), but for each, a compound parameter "filter" can be provided which will filter results by selected fields (including as desired message text). This parameter is an array of filter conditions that are always "AND"-ed, meaning that each record must match all of the given conditions to be included in the final results. Filtering is always done before aggregating so if for example the event rate is queried and filtering is specified by hostname then only the number of events with this host name will be reported as the result count.

Every filter condition is an object with following fields:

name | description
- | -
`field` | name of the field to filter by, as it appears in results
`value` | actual value to filter by. for fields other than timestamp this can also be a list of possible values (only for "eq" comparison)
`op` | if type is numeric (this includes timestamps) this defines the type of comparison.  see immediately below
`ignore_case` | determines whether text comparisons are case sensitive or not. Defaults to True, meaning all comparisons are case insensitive. To force case sensitive mode set ignore_case=False

operator | description
- | -
`eq` | value is an exact value to be found. this is the default when no comparison operator is specified. you can also specify list of possible values
`lt` | match only records with field less than the given value
`le` | match only records with field less than or equal to the given value
`gt` | match only records with field greater than the given value
`ge` | match only records with field greater than or equal to the given value
`qp` | special operator for message boolean syntax

### Examples  
Return only events with counter greater than 5:
```
[ { "field": "counter", "op": "gt", "value": 5 } ]
```
Return events from host ‘fileserver23’ with severity ‘ERROR’ or higher:
```
[ { "field": "severity", "value": [0, 1, 2, 3] },
  { "field": "host", "value": "fileserver23" } ]
```
Return events from hosts "alpha" and "beta" matching "power failure" in event message text:
```
[ { "field": "message", "value": "power failure" },
  { "field": "host", "value": ["alpha", "beta"] } ]
```
### Message boolean syntax
Boolean logic expressions can be used in message filters. They work as indicated in: http://sphinxsearch.com/docs/current.html#boolean-syntax

Allowed operators between words/expressions:  
**AND**  
which is also implicitly used between two words/expressions if there is no other operator specified

**NOT**  
shortcut: use either **‘!’** or **‘-‘**

**OR**  
shortcut: **‘|’**

Operators are case-insensitive, so: ‘AND’, ‘and’, ‘AnD’ are correct

Some boolean expressions are forbidden:

`-Foobar1`  
`Foobar1 | -Foobar2`  

Examples of incorrect expressions:
Return events containing words ‘Foobar1’ or ‘Foobar2’ and not ‘Foobar3’:
```
[ { "field": "message", "op": "qp", "value": "Foobar1 | Foobar2 !Foobar3" } ]
```
Return events containing words (‘Foobar1’ or ‘Foobar2’) and (‘Foobar4 or Foobar4)’:
```
[ { "field": "message", "op": "qp", "value": "(Foobar1 | Foobar2) (Foobar3 | Foobar4)" } ]
```
### Common results format
The "results" container is always an object with one or several fields, usually containing "totals" and/or "details".  The former contains results for the whole period whereas the latter is an array of values for subperiods. Both total and subperiod usually contain "ts_from" and "ts_to" timestamps, to show exact time range for the data retrieved, and then the result "values" or just "count".

See the description of the particular *query type* for details on what the results contain and the results format, with examples.

### Generic results format for system queries
System queries return data collected by the telegraf system, for different system parameters, and are used for displaying system widgets (that can be used later on for diagnostic monitoring of system performance).

All these queries return "totals" and "details". For details the objects are similar to data for EventRateQuery but there are more keys with different values.  An example from *System_CPUQuery*:
```
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
For totals instead of an array we have a single object with keys like above, but rather than a single value there is a set of values:
```
{
  "system": {
    "count": 236,
    "sum": 1681.6008720000007,
    "min": 5.2671220000000005,
    "max": 9.599976,
    "avg": 7.125427423728817
    "last": 6.400112999999999,
    "last_ts": 1416234840,
  },
}
```
So here there are different kinds of aggregates for the selected time period:

type | description
- | -
`count` | number of known values for the given time period
`sum` | total of those values (used for calculating avg)
`min` | minimum value
`max` | maximum value
`avg` | average value (sum / count)
`last` | last known value from given period
`last_ts` | timestamp when last known value occurred

&nbsp;  
## Query types
### TopN  
Get top N values for requested field and time period, possibly with filtering. Detailed counts for subperiods of the given period can additionally be requested.

Configurable parameter | description
- | -
`time_range` | data is taken for this time range
`field` | which field to aggregate by (defaults to "host")
`with_subperiods` | boolean. if set then you’ll get not only results for the whole time range, but also for all subperiods
`top_periods` | boolean. if set then you’ll get the top N subperiods
`filter` | you can specify some extra filters. see the "common parameters" description for details
`limit` | number of values to show
`show_other` | boolean. enables one extra value called "other", with the sum of all remaining values from N+1 to the end of the list
`ignore_empty` | boolean. enables ignoring empty event field/tag values (defaults to True)
`subfields` | you can specify some extra subfields to get detailed results
`subfields_limit` | the number of subfield values to show

Data format:  
"totals" with values for the whole time period are provided first:
```
{
  "totals": {
      "ts_from": 123450000,
      "ts_to": 123453600,
      "values": [
          {"name": "host32", "count": 3245},
          {"name": "host15", "count": 2311},
          {"name": "localhost", "count": 1255},
          "..."
      ]
  }
}
```
Elements are sorted from highest to lowest count, but if "show_other" is requested then the last value is always "other" regardless of the count (which can be larger than any previous count). Number of elements in "values" can be less than "limit" parameter if not enough different values for the given field were found for the given time period.

If "with_subperiods" is enabled then besides one "totals" array a "details" array of all subperiods will also be provided:
```
{
  "details": [
      {
          "ts_from": 123450000,
          "ts_to": 123450060,
          "values": [
              {"name": "host2", "count": 1},
              {"name": "host3", "count": 10},
              {"name": "localhost", "count": 20},
              "..."
          ],
          "total_values": [
              {"name": "host32", "count": 151},
              {"name": "host15", "count": 35},
              {"name": "localhost", "count": 13},
              "..."
          ],
          "total_count": 199
      },
      {
          "ts_from": 123450060,
          "ts_to": 123450120,
          "values": [
              {"name": "host32", "count": 42},
              {"name": "host15", "count": 0},
              {"name": "localhost", "count": 51},
              "..."
          ],
          "total_count": 93
      },
      "..."
  ]
}
```
In "values" only the TopN value for the given time subperiod (which may be different from the TopN of the entire period) will be provided; in "total_values" detailed total values for the given time subperiod will be returned. Please note that for subperiods the order of "total_values" is always the same as in "totals", regardless of actual counts; also for some entries 0 (zero) can be returned for the count (but the actual name is always present).

If "top_periods" is requested then "top_periods" as an array of top (sorted by total_count) subperiods will be provided:
```
{
  "top_periods": [
      {
          "ts_from": 123450000,
          "ts_to": 123450060,
          "values": [
              {"name": "host32", "count": 151},
              {"name": "host15", "count": 35},
              {"name": "localhost", "count": 13},
              "..."
          ],
          "total_count": 199
      },
      {
          "ts_from": 123450060,
          "ts_to": 123450120,
          "values": [
              {"name": "host32", "count": 42},
              {"name": "host15", "count": 0},
              {"name": "localhost", "count": 51},
              "..."
          ],
          "total_count": 93
      },
      "..."
  ]
}
```
If "subfields" is enabled then "subfields" with a counter at each detailed subperiod will be provided:
```
{
  "totals": {
      "...""
      "values": [
          {
              "name": "host32",
              "count": 3245,
              "subfields":{
                  "program":[
                      {
                          "name": "program1",
                          "count": 3240,
                      },
                      {
                          "name": "program2",
                          "count": 5,
                      },
                  ],
                  "facility":[
                      {
                          "name": 0,
                          "count": 3000,
                      },
                      {
                          "name": 1,
                          "count": 240,
                      },
                      {
                          "name": 2,
                          "count": 5,
                      },
                  ]
              }
          },
          "..."
      ]
  },
  "details": [
      {
          "..."
          "values": [
              {
                  "name": "host32",
                  "count": 151,
                  "subfields":{
                      "program":[
                          {
                              "name": "program1",
                              "count": 150,
                          },
                          {
                              "name": "program2",
                              "count": 1,
                          },
                      ],
                      "facility":[
                          {
                              "name": 0,
                              "count": 100,
                          },
                          {
                              "name": 1,
                              "count": 50,
                          },
                          {
                              "name": 2,
                              "count": 1,
                          },
                      ]
                  }
              },
              "..."
          ],
      },
      "..."
  ],
  "top_periods": [
      {
          "..."
          "values": [
              {
                  "name": "host32",
                  "count": 151,
                  "subfields":{
                      "program":[
                          {
                              "name": "program1",
                              "count": 150,
                          },
                          {
                              "name": "program2",
                              "count": 1,
                          },
                      ],
                      "facility":[
                          {
                              "name": 0,
                              "count": 100,
                          },
                          {
                              "name": 1,
                              "count": 50,
                          },
                          {
                              "name": 2,
                              "count": 1,
                          },
                      ]
                  }
              },
              "..."
          ],
      },
      "..."
  ]
}
```

&nbsp;  
### LastN  
Get last N values for the given field and given time period, with number of occurrences per given time range

Configurable parameter | description
- | -
`time_range` | data is taken for this time range  
`field` | which field to aggregate by
`filter` | filtering; see common parameters description
`limit` | number of values to show

Data format  
Always only the "totals" part, with the following content:
```
{
  "totals": {
      "ts_from": 123450000,
      "ts_to": 123453600,
      "values": [
          {"name": "host32",    "count": 3245, "last_seen": 1401981776.890153},
          {"name": "host15",    "count": 5311, "last_seen": 1401981776.320121},
          {"name": "localhost", "count": 1255, "last_seen": 1401981920.082937},
          "..."
      ]
   }
}
```
It is similar to "TopN" but there is also a "last_seen" field, with possibly fractional part of the second. Also, elements are sorted by "last_seen" instead of "count". Both elements shown and counts are for the given time_range and filters.

&nbsp;  
### EventRate  
Get number of events per given time periods - i.e. per second for last minute, or events per day for last month, and so on.  Filters can be used to retrieve the rate for a particular host, program, severity or any combination. It is also used on the search results page to show a histogram for the search results.

Configurable parameter | description
- | -
`time_range` | data is taken for this time range, periods are generated according to the description of this parameter; see section "common parameters"
`filter` | extra filtering as desired

Data format  
Similarly to other types "totals" and "details" are returned. For details there is only "count", for "totals" there are self-explanatory aggregates (the one called "last" is the last value from "details").

"drill_up_time_range" is the time range that should be used for showing a wider time period (for example if by-minute is requested it will include the whole hour, when specifying by hour it will include the whole day, and so on). It can be null because it is always limited to one day at most - so if a whole day or wider time range is specified there will be a null value to indicate no option to drill up.

Sample data:
```
{
  "totals": {
      "ts_from": 123450000,
      "ts_to": 123453600,
      "drill_up_time_range": {
          "ts_from": 123379200,
          "ts_to": 123465600,
      },
      "sum": 5511,
      "count": 120,
      "min": 5,
      "max": 92,
      "avg": 45.925,
      "last": 51,
    },
  "details": [
    {
      "ts_from": 123450000,
      "ts_to": 123450060,
      "count": 41,
    },
    {
      "ts_from": 123450060,
      "ts_to": 123450120,
      "count": 12,
    },
    {
      "ts_from": 123450120,
      "ts_to": 123450180,
      "count": 39,
    },
    "..."
  ]
}
```

&nbsp;  
### Search  
The only query type that includes not only counts but also the list of events with details.

Configurable parameter | description
- | -
`time_range` | data is taken for this time range (periods are ignored)
`filter` | this is for search details; see common parameters for details
`sort` | list of fields to sort results by; only first_occurrence, last_occurrence and count are available. you can get descending sort order by prefixing the field name with "-" (minus) sign
`page_size` | number of events to retrieve
`page` | number of the page to retrieve, for paging; remember that the larger the page number the longer it will take to retrieve results, especially if you have a multi-host configuration

Results format  
There are two values: "totals" contains just the count of all items found, and sometimes "total_count" if there was more than could be retrieved; "events" contains the actual list of events in the form identical to all lists with paging, so information is provided about the number of items, number of pages, current page number, and then actual objects (current page only) under the "objects" key:
```
{
  "totals": {
      "ts_from": 1401995160,
      "ts_to": 1401995220,
      "count": 623,
  }
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
              "flags": ["KNOWN"],
          },
          "..."
      ]
   }
}
```

&nbsp;  
### System_CPU  
Configurable parameter | description
`time_range` | data is taken for this time range; only ts_from and ts_to are considered, step is always provided by the back-end depending on data available for the given period
`cpu` | number of CPU (from 0 to n-1, with n being the actual number of CPU cores in the system), or ‘totals’ to get the sum for all CPU's

Results format  
See "Generic results format for system queries" for the generic results format.

This query returns CPU usage broken down by different categories:

label | description
- | -
`user` | CPU used by user applications
`nice` | CPU used to allocate multiple processes demanding more cycles than the CPU can provide
`system` | CPU used by the operating system itself
`interrupt` | CPU allocated to hardware interrupts
`softirq` | CPU servicing soft interrupts
`wait` | CPU waiting for disk IO operations to complete
`steal` | Xen hypervisor allocating cycles to other tasks
`idle` | CPU not doing any work

All those are float numbers, which should sum to 100 (more or less), or with CPU param set to "totals", then to to 100*n where n is number of CPU cores.

Note The CPU plugin does not collect percentages. It collects *jiffies*, the units of scheduling. On many Linux systems, there are circa 100 jiffies in one second, but this does not mean a percentage will be returned. The number of jiffies per second will vary depending on system load, hardware, whether or not the system is virtualized, and possibly half a dozen other factors.

&nbsp;  
### System_Memory  
Configurable parameter | description
- | -
`time_range` | data are taken for this time range; only ts_from and ts_to are considered, step is always provided by the back-end, depending on data available for the given period

Results format  
See Generic results format for system queries for generic results format.

This query returns memory usage (in bytes) broken down by:

label | description
- | -
`used` | memory used by user processes
`buffered` | memory used for I/O buffers
`cached` | memory used by disk cache
`free` | free memory

&nbsp;  
### System_DF  
Configurable parameter | description
`time_range` | data is taken for this time range; only ts_from and ts_to are considered, step is always provided by the back-end depending on data available for the given period
`fs` | filesystem to show information. this always includes a "root". other possible values are system-dependent

Results format  
See "Generic results format for system queries" for generic results format.

This query returns disk usage (in bytes) broken down by:

label | description
- | -
`used` | space used by data
`reserved` | space reserved for root user
`free` | free disk space

&nbsp;  
### System_Network  
Configurable parameter | description
`time_range` | data are is for this time range; only ts_from and ts_to are considered, step is always provided by the back-end depending on data available for the given period
`interface` | network interface for which to show data; generally "lo" for loopback interface, others being system dependent

Results format  
See "Generic results format for system queries" for generic results format.

This query returns the following data for the selected network interface:

label | description
- | -
`if_packets.tx` | Number of packets transferred
`if_packets.rx` | Number of packets received
`if_octets.tx` | Number of octets (bytes) transferred
`if_octets.rx` | Number of octets (bytes) received
`if_errors.tx` | Number of transmit errors
`if_errors.rx` | Number of receive received

&nbsp;  
### ProcessingStats  
Indicates the number of events processed by the system in the given time period. Similar to the EventRates but does not allow for any filtering, or timestamps of the events (only the moment it was actually processed by the system). To use this query internal counters verbosity must be set to DEBUG (run LogZilla config INTERNAL_COUNTERS_MAX_LEVEL DEBUG)

Configurable parameter | description
- | -
`time_range` | data is taken for this time range. periods are generated according to the description of this parameter, see section "common parameters". Max time_range is last 24h

Data format  
Includes "totals" and "details". With both there is an object with time range and three keys:

label | description
- | -
`new` | number of new items processed (not duplicates)
`duplicates` | number of items that were found to be duplicates
`oot` | item ignored, because their timestamp was outside the TIME_TOLERANCE compared to the current time (this should be zero at normal circumstances)

Sample data:
```
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
          "ts_to": 1441090002,
      },
      "..."
      {
          "duplicates": 15,
          "new": 1,
          "oot": 10,
          "ts_from": 1441090060,
          "ts_to": 1441090061,
      },
  ],
}
```

&nbsp;  
### StorageStats  
Returns events counters stored by the system for the given time period. Similar to EventRates but this does not allow for any filtering and returns only total counters without subperiod details.

Time Range is rounded up to full hours -- if a 1-second time period is requested the response will be with hourly counters.

Configurable parameter | description
`time_range` | data is taken for this time range. periods are generated according to the description of this parameter, see section "common parameters". Max time_range is last 24h

Data format  
Includes  "totals" and "all_time" counters stored in the system:

label | description
- | -
`totals` | counters from given period
`all_time` | all time counters

For both there are three keys:

key | description
- | -
`new` | number of new items processed (not duplicates)
`duplicates` | number of items that were found to be duplicates
`total` | total sum

Sample data:
```
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
    "new": 18000
    "total": 20000,
  }
}
```

&nbsp;  
### Tasks
List of tasks.

Configurable parameter | description
- | -
`target` | filter list by "assigned to", which is either "assigned_to_me" and "all"
`is_overdue` | filter list by is_overdue flag (boolean)
`is_open` | filter list by is_open flag (boolean)
`assigned_to` | filter list by assigned user id list. for the empty list, it will return only unassigned
`sort` | list of fields to sort results by.  available fields are created_at and updated_at. descending sort order can be specified by prefixing the field name with "-" (minus) sign

Data format  
Sample data:
```
[
  {
      id: 1,
      title: "Task name",
      description: "Description",
      due: 1446508799,
      status: "new",
      is_overdue: false,
      is_closed: false,
      is_open: true,
      assigned_to: 1,
      updated_at: 1446371434,
      created_at: 1446371434,
      owner: {
          id: 1,
          username: "admin",
          fullname: "Admin User"
      }
  }
]
```

&nbsp;  
### Notification  
List of notifications groups, with associated events.

Configurable parameter | description
`sort` | order of notifications groups, which is "Oldest first", "Newest first", "Oldest unread first" or "Newest unread first"
`time_range` | data is taken for this time range
`time_range_field` | specify field for the time range processing, which is "updated_at", "created_at", "unread_since" or "read_at"
`is_private` | filter list by is_private flag (boolean)
`read` | filter list by read_flag flag (boolean)
`with_events` | add to data events information (boolean)

Data format  
Sample data:
```
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
