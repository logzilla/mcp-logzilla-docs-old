<!-- @@@title:Lua Rules Reference@@@ -->

## Lua Resources
There are resources for Lua available that will be helpful in understanding the following descriptions of LogZilla Lua rule usage.  An in-depth examination of this information is not necessary at this point but the detailed breakdown will make more sense after at least a cursory review. For creating these Lua rules Lua version 5.1 is supported.

* [the official Lua site](https://www.lua.org/manual/5.1/manual.html)
* [Programming in Lua (first edition)](https://www.lua.org/pil/contents.html)
* [LEARN LUA](https://www.tutorialspoint.com/lua/index.htm)
* [Lua Tutorial](http://lua-users.org/wiki/LuaTutorial)
* [LPeg - Parsing Expression Grammars for Lua](http://www.inf.puc-rio.br/~roberto/lpeg/)
* [An introduction to Parsing Expression Grammars with LPeg](https://leafo.net/guides/parsing-expression-grammars.html)

## Detailed Example
The reference material below uses the following detailed example rule file and tests file for illustrative purposes.

### Detailed Lua Rule File
```
HC_TAGS={
    "SrcIP",
    "Query",
    "Response",
}

local lpeg = require "lpeg"
local core = require "lpeg_patterns.core"
local IPV4_EXP = require "lpeg_common".IPv4_simple

local SEP_EXP = lpeg.S(", \t")
local ALPHANUM_EXP = core.ALPHA + core.DIGIT
local ELEMENT_EXP = (lpeg.P(1) - SEP_EXP)^1

local INFOBLOX_DNSQUERY_EXP = lpeg.Ct(
        lpeg.P("infoblox-responses: ")
        -- 18-Jun-2018 
        * core.DIGIT^2 * "-" * ALPHANUM_EXP^3 * "-" * core.DIGIT^4 * SEP_EXP^1
        -- 17:07:34.171 
        * core.DIGIT^2 * ":" * core.DIGIT^2 * ":" * core.DIGIT^2 *"." * core.DIGIT^3 * SEP_EXP^1
        -- client 
        * ALPHANUM_EXP^1 * SEP_EXP^1
        -- 10.17.159.198#65129: 
        * lpeg.Cg(IPV4_EXP, "ip") * "#" * core.DIGIT^1 * ":" * SEP_EXP^1
        -- UDP: 
        * ALPHANUM_EXP^1 * ":" * SEP_EXP^1
        -- query: 
        * ALPHANUM_EXP^1 * ":" * SEP_EXP^1
        -- 23-courier.push.apple.com
        * lpeg.Cg(ELEMENT_EXP, "query") * SEP_EXP^1
        -- IN 
        * ALPHANUM_EXP^1 * SEP_EXP^1
        -- A 
        * lpeg.Cg(ALPHANUM_EXP^1, "qtype") * SEP_EXP^1
        -- response: 
        * "response:" * SEP_EXP^1
        -- NOERROR
        * lpeg.Cg(ALPHANUM_EXP^1, "msg")
    )

function process(event)
    if event.program == "named" then
        local match = INFOBLOX_DNSQUERY_EXP:match(event.message)
        if match then
            event.program = "Infoblox"
            event.user_tags["SrcIP"] = match.ip
            event.user_tags["Query"] = match.query
            event.user_tags["Query Type"] = match.qtype
            event.user_tags["Response"] = match.msg
        end
    end
end
```

### Detailed Tests File

```
TEST_CASES:
- event:
    program: named
    message: 'infoblox-responses: 05-Nov-2018 13:42:54.339 client 10.17.192.71#63094: UDP: query: canvas-iad-prod-c8-1212199460.us-east-1.elb.amazonaws.com IN AAAA response: NOERROR +'
  expect:
    program: Infoblox
    user_tags:
      SrcIP: 10.17.192.71
      Query: canvas-iad-prod-c8-1212199460.us-east-1.elb.amazonaws.com
      Query Type: AAAA
      Response: NOERROR
```


## Reference

### Lua Rule File

The Lua rule file is a plain text file that consists only of valid Lua code.  The naming convention is `123-sourceortype.lua`, where `123` provides a numeric ordering for the sequence in which LogZilla processes rules on incoming log events;  `sourceortype` corresponds to some indication of the source or type of log message handled by the rule (this could be `cisco_ise` or `mswindows` for example), and then the `.lua` extension.

First of note is that Lua rule files benefit from including comments, which are lines that are prefixed with `--`.  The example includes many such for explanatory purposes.

Second, there are many utility functions provided by the LogZilla Lua interpreter that assist with logic within the Lua rule function.  These utility functions are described in the *Lua Utility Functions* section below.

Somewhere in the Lua rule file (in this case, at the top) should be the declaration of any *high-cardinality* user tags that are going to be assigned.  "High cardinality" indicates that there will be a great many individual values for those user tags, for which maintaining indexes of that data will require special handling.  Examples of such data include source and destination IP addresses, which could possibly include thousands of "random" internet IP addresses.

LogZilla needs to be alerted to user tags that meet this condition.  This is done by setting the `HC_TAGS` table to include the user tag names for such user tags.  (This is the section of the example that starts with `HC_TAGS={`).

Similary, if your app is using computationaly expensive functions, you can
allow source filtering by defining `SOURCE_FILTER="foo"` in your rule file.
Then user can create a dedicated syslog source for events that should be
processed by this rule - then only events from this source will be processed by
this rule. See [Source Filtering](/help/receiving_data/receiving_syslog_events)
for more information.

Near the top of the Lua file should ordinarily be statements "importing" any of the utility libraries or functions just mentioned (in this case `local core = require "lpeg_patterns.core`, also `local IPV4_EXP = require "lpeg_common".IPv4_simple`).  There is a list of some of the libraries and functions provided by LogZilla listed in the *Utility Functions* reference below.

After any utility libraries or functions are imported should be the definitions of any LPEG expressions that are to be used in the rule function.  As described in the LPEG reference links above these expressions are composed of multiple LPEG clauses that together match the incoming log messages and break those log messages down into their constituent parts, for further handling. (This is the section of the example that starts with `local SEP_EXP = lpeg.S(", \t")` and continues on through `local INFOBLOX_DNSQUERY_EXP = lpeg.Ct(`).

The main portion of the Lua rule file is the Lua function that does the handling of each incoming log message.  This function is executed once per every incoming log message.  This function must be named `process` and takes a single argument, which argument corresponds to a Lua object that holds all the relevant information regarding that incoming log message. (This section of the example starts with `function process(event)`).

This function's purpose is to inspect the log message *event* data that is coming in from the incoming log message and to rewrite that event data for storage or display by LogZilla.  As such, the `event` object that is the argument to the `process` function should be modified as desired for that purpose -- rather than the function returning any value, the function "result" is the modification of that `event` object.

There are multiple constituent fields of the `event` argument (please note that most of these fields correspond to the data that would come in on a standard syslog-protocol log message - (RFC3164 format)[https://datatracker.ietf.org/doc/html/rfc3164] (RFC5424 format)[https://datatracker.ietf.org/doc/html/rfc5424]) .  These fields are read-write (for the same `event` argument the function should read in the incoming log event data then write out the desired data to be stored/displayed).

| Field | Explanation |
| --- | --- |
| `message` | the text log message portion of the incoming log event data |
| `program` | the `program` field of the incoming log data (such as per `syslog` log format) |
| `host` | the source host of the log data (such as per `syslog` log format) |
| `timestamp` | the date and time of the log event, in (unix epoch)[https://en.wikipedia.org/wiki/Unix_time] microseconds |
| `severity` | as per syslog, the numeric severity value of the log event |
| `facility` | as per syslog, the numeric facility value of the log event |
| `cisco_mnemonic` | event Cisco mnemonic, if available |
| `extra_fields` | JSON fields from incoming JSON log messages (see below) |
| `user_tags` | the Lua table (or dictionary) of the user tag key/values to be set (see below) |


Two of the log message formats LogZilla can accept are *syslog* formatted messages (as referenced above) and *JSON* formatted messages (using standard JSON format). 

For syslog messages, the incoming data is broken down into the fields listed above (
`event.program`, `event.host`, `event.timestamp`, etc.)

For JSON messages all the incoming JSON fields are put into `extra_fields` in the `event` object.  For example, this JSON would result in the event fields that follow:
```
{
  "host": "source.company.com",
  "program": "myprogram",
  "message": "this is the text of the log message",
  "timestamp": TODO timestamp value,
  "somekey": "somevalue"
}
```

Event fields:

```
event.extra_fields["host"]
event.extra_fields["program"]
event.extra_fields["message"]
event.extra_fields["timestamp"]
event.extra_fields["somekey"]
```

Please note that for syslog messages the log data is placed directly into the LogZilla event fields, from which it can be used (displayed and stored) without requiring any handling or modification.

However for JSON data only the `host` and `timestamp` fields are directly set, without modification -- the `host` field corresponding to the sending host from which the log message was received, and the timestamp corresponding to LogZilla's receipt of that message.  **Any** of the other LogZilla event fields must be set in the Lua rule by reading the JSON `extra_fields` and accordingly setting the `event` fields from that data.  In the JSON example given above the likely desired behavior would be that `event.program = event.extra_fields["program"]`.

Each rule must specify a `process()` function; however `preprocess(event)` and `postprocess(event)` functions can also be provided.  These functions are used as follows: first for every rule the preprocess function is called (if it exists), then for every rule there’s call to process and finally for every rule there’s call to the postprocess. If any of the functions are not defined they are skipped without any error or warning.

Although the main purpose of each rule is to modify the contents of the `event` argument to reflect the desired results, the `process` (and `preprocess` and `postprocess`) functions can return special values indicating desired handling:
* `Result.CONTINUE` : (this is default) - continue processing with other rules
* `Result.STOP` : stop processing this stage, so if for example this is returned by the process function, then no other process will be called, but all postprocess (if any defined) will be called normally.
* `Result.DROP` : event will be deleted and any further processing will be stopped (as pointless)

Debugging of Lua rule files can be assisted by the use of the `print` command.  The `print()` command allows the display of specified values during the execution of the rule, to provide for inspection of those values at various stages of event processing. An example:

```
function process(event)
     print("Starting processing, program=" .. event.program)
     if event.program == '-' then
         print("Inside the if block")
         event.program = 'Unknown'
     end
     print("Finishing processing, program=" .. event.program)
 end
```

`print()` takes one argument which is the string to be printed; furthermore the `..` operator can be used to concatenate multiple strings and variables (such as demonstrated in the second `print()` statement above).

Now when running the tests each `print()` will be displayed:

```
$ logzilla rules test --path err.lua
================================= test session starts ==================================
platform linux -- Python 3.8.5, pytest-6.2.2, py-1.10.0, pluggy-0.13.1 -- /usr/bin/python3
cachedir: .pytest_cache
rootdir: /tmp
collected 3 items

err.tests.yaml::test_case_1 PASSED                                               [ 33%]
err.tests.yaml::test_case_2 PASSED                                               [ 66%]
err.tests.yaml::test_case_3 PASSED                                               [100%]

================================== 3 passed in 0.02s ===================================
Starting processing, program=-
Inside the if block
Finishing processing, program=Unknown
Starting processing, program=xyz
Finishing processing, program=xyz
Starting processing, program=fail
Finishing processing, program=fail
```

Note `print()` should only be used during *testing* of the rule; every `print()` statement should be removed before adding the rule to LogZilla.


### Utility Functions
There are many utility expressions and functions provided by LogZilla for use in Lua rules.  Here is a list of some of the expressions provided:

For the following note that if you `local core = require "lpeg_patterns.core"` at the top of the rule then you would use for example `ALPHA` as `core.ALPHA`.  The LPEG expressions below are described in terms of their equivalent regular expressions.

LPEG expressions in `lpeg_patterns.core`:

| LPEG | Regular Expression |
| --- | --- |
| `ALPHA` | `[a-zA-Z]` |
| `BIT` | `[01]` |
| `CHAR` | `[\x01-\x7F]` |
| `CR` | `\r` |
| `CRLF` | `(\r\n)` |
| `CTL` | `[\x00-\x1F\x7F]` |
| `DIGIT` | `[0-9]` |
| `DQUOTE` | `\"` |
| `HEXDIG` | `[0-9a-fA-F]` |
| `HTAB` | `\t` |
| `LF` | `\n` |
| `OCTET` | `.` |
| `SP` | ` ` |
| `VCHAR` | `[\x21-\x7E]`
| `WSP` | `[ \t]` |
| `LWSP` | `( \r\n )*`


In `lpeg_common`:

| LPEG | Explanation | Examples |
| --- | --- | --- |
| `IPv4_WITH_PORT` | numeric IP v4 address followed by either `:` or `/` followed by numeric port number | `87.65.43.210:443`, `87.65.43.210/443` |
| `IPv6_WITH_PORT` | hexadecimal IP v6 address followed by either `:` or `/` followed by numeric port number | `12:34:56:78:9A:BC:DE:F0:443`, `12:34:56:78:9A:BC:DE:F0/443` |
| `IP_WITH_PORT` | either of `IPv4_WITH_PORT` or `IPv6_WITH_PORT` | `87.65.43.210:443`, `12:34:56:78:9A:BC:DE:F0/443` |
| `MAC_ADDR` | hexadecimal MAC address | `11:22:33:44:55:66` |
| `IPv4_simple` | standard 4-part-separated-by-periods numeric IP address | `87.65.43.210` |
| `PROTOCOL` | network protocol | `TCP`, `tcp`, `UDP`, `udp` |

In `helpers`:

* `get_port_name(port)`: returns the port service name for the given numeric port, such as `get_port_name(22)` returns `ssh` and `get_port_name(443)` returns `https`
* `get_kv_parser(sep_sign, delimiter_sign, quote_sign, key_pattern)` : returns an LPEG expression that parses key-value pairs (such as `firstkey="firstvalue", secondkey="secondvalue"`) into a Lua key-value table.  The function arguments are: `sep_exp` is the separator expression, such as `lpeg.P(" ")` for space or `lpeg.P(",")` for comma; `delimiter_sign` is the key-to-value indicator, such as `lpeg.P("=")` for `=`; `quote_sign` is the quote character surrounding values, such as `lpeg.P("'")` or `lpeg.P("\"")` for `'` or `"`; and key_pattern expresses the valid values for the key name, such as `lpeg.R("az", "AZ", "09") + lpeg.P("_")` or in regex terms `[azAz09_]`
* `get_csv_parser()`: returns an LPEG expression that parses comma-separated values (CSV), such as `firstvalue, secondvalue, thirdvalue`, into a Lua table
* `get_ip_with_port(o)`: uses the above `IP_WITH_PORT` LPEG expression to parse `o` into a two-value Lua table consisting of `ip` and `port` parts
* `get_GeoIP()`: returns a geo-ip converter that allows to:
    * `geoip:get_values(ip_address)` - extract data such as city / state / country from the given IP address:
        * returns the map containing City, Country and State
        * returns the empty map if given ip is not valid IP address or geoip data can't be
        found
    * `geoip:add_geo_tags(event, user_tag)` - add extra GeoIP user tags based on the selected user tag:
        * adds a set of geoip user tags to the event
        * new geoip user tags consist of the original tag name and City/Country/State postfix
        * no tags are added if given user tag value is not valid IP address or
        geoip data can't be found

```
    geoip = get_GeoIP()

    function process(event)
        -- add "ScrIP City", "ScrIP Country", "ScrIP State" user tags to the event
        geoip:add_geo_tags(event, "ScrIP")

        -- extract geo-ip City/Contry/State from the host
        local geoip_data = geoip:get_values(event.host)
        if geoip_data["City"] ~= nil then
            event.program = geoip_data["City"]
        end
    end
```

Note that there is a help video available for geoip use
[here](https://youtu.be/3EKapGYf46w).
