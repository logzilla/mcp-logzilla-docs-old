<!-- @@@title:Rewrite Rules@@@ -->

# LogZilla Rules

LogZilla *Rules* are how LogZilla can parse and rewrite log messages to extract
the specific bits of useful information, as well as to rewrite the log message
so that when you review the log messages the information shown is more useful
to you. There are two types of LogZilla rules: rewrite rules, which are defined
through simple `JSON` or `YAML` files; and *lua* rules, which are very powerful
but are defined in lua programming language files. Both types of rules can be
used at the same time, but be aware that lua rules are executed before rewrite
rules, so that any data modifications or other actions taken by the lua rules
will precede the execution of the rewrite rules.

# Rewrite Rule Files

Rewrite rules may be written in either `JSON` or `YAML`

# Best Practice

When creating rewrite rules it is suggested to use the following syntax in the **comment** section of the rule. This makes testing easier in the future for other members of your team should they require it.

The comments should contain the following:

* Name
* Sample Log
* Description
* Category (generally one of the categories from [FCAPS](https://en.wikipedia.org/wiki/FCAPS))

For example:

```yaml
first_match_only: true
pre_match:
- field: host
  value: foo
- field: program
  value: bar*
rewrite_rules:
- comment:
  - 'Severity: INFO'
  - 'Area: Firewall / Packet Filter'
  - 'Name: IPv4 source route attack'
  - 'Sample: msg_id="3000-0152" IPv4 source route attack from 10.0.1.34 detected.'
  - 'Description: IPv4 source route attack was detected.'
  - 'Format: IPv4 source route attack from %s detected.'
  - 'Variables: IPv4 source route from ${src} detected.'
  match:
    value: msg_id="3000-0152"
    op: "=~"
    field: message
  tag:
    WatchGuard Firewall IPv4 Src: "${src}"
    WatchGuard Firewall Msg Ids: 3000-0152
  rewrite:
    message: '$MESSAGE NEOMeta: area="Firewall / Packet Filter" name="IPv4 source
      route attack" description="IPv4 source route attack was detected."'
    program: WatchGuard_Firewall
<truncated for brevity>
```

# Rule Overview

Each rule must define a `match` condition and at least one of the following:

- `rewrite`: a key-value map of fields and their eventual values
- `replace`: replace one or all occurrences of one substring with another
- `tokenize`: handle messages in tsv, csv, or similar formats
- `drop`: a boolean flag indicating the matched event should be ignored/dropped (not inserted into LogZilla).

All types of rules only modify events that match their filter,

Drop rules are the simplest - except for `match`, they are just `drop: true`

Replace rules must define what field it should run regex replace on (`replace`).

Tokenize rules must have a `tokenize` section, defining the fields used and
optionally `separator`.  Tokenize rules must define what fields to rewrite (`rewrite`),
and/or what tags to set (`tag`).

In all other cases, if a rule does not define `tokenize`, `replace` or `drop`,
it is a rewrite rule.  Rewrite rules must define what fields to rewrite (`rewrite`),
and/or what tags to set (`tag`).

## Basic Rule Example


```yaml
match:
  field: host
  value:
  - host_a
  - host_b
rewrite:
  program: new_program_name
  host: new_host_name
```
In this example, the rule above changes the incoming event in the following manner:

1. Match on either `host_a` or `host_b`
2. Set the `program` field to `new_program_name`
3. Set the `host` field to `new_host_name`


# Rule Syntax

## Match Conditions

* `match` may be a single condition or an array of conditions.
* If `match` is an array, it will only match if **ALL** conditions are met (implied `AND`).
* Each condition must define a `field` and `value` along with an optional `op` (match operator).
* `value` may be a string or an array of strings.
* If `value` is an array, the condition will be met if **ANY** element of the array matches (implied `OR`).

### Valid `match` examples:

```yaml
rewrite_rules:
- match:
  - field: program
    value:
    - program_a
    - program_b
  - field: host
    op: ne
    value: 127.0.0.1
  - field: message
    op: "=~"
    value: "\\d+foo\\s?(bar)"
  rewrite:
    program: "$1"
```


## Operators
Operators control the way the `match` condition is applied. If no `op` is supplied, the default operator `eq` is assumed.

| Operator | Match Type        | Description                                                                                   |
|----------|-------------------|-----------------------------------------------------------------------------------------------|
| eq       | String or Integer | Matches the entire incoming message against the string/integer specified in the `match` condition |
| ne       | String or Integer | Does *not* match anything in the incoming message `match` field.                              |
| gt       | Integer Only      | Incoming integer value is greater than this number                                            |
| lt       | Integer Only      | Incoming integer value is less than this number                                               |
| ge       | Integer Only      | Incoming integer value is greater than or equal to this number                                |
| le       | Integer Only      | Incoming integer value is less than or equal to this number                                   |
| =~       | RegEx             | Match based on RegEx pattern                                                                  |
| !~       | RegEx             | Does *not* match based on RegEx pattern                                                       |
| =*       | String            | Given substring appears anywhere in the incoming message                                      |
| !*       | String            | Given substring does *not* appear anywhere in the incoming message                            |

When searching for strings with operators `eq` or `ne`, special characters
`?` and `*` can be used as a wildcard to match any character or characters.
It can be placed at the start of a string, at the end of a string,
or in the middle of a string. Note that you cannot search for the literal
characters `*` or `?` using this method.

# Rewriting Fields
To transform an incoming event into a new string, use the `rewrite` keyword.

When replacing incoming event parts, the rules can reuse events from the original field's values in three ways:

1. Capturing RegEx sub-matches
2. key/value parsing of the incoming MESSAGE field
3. Full string values of incoming MESSAGE, HOST and/or PROGRAM fields
4. Combinations of the above (i.e. these features may be used together in a single rule)

To replace parts from `field` RegEx operators in a `rewrite`, one or more of its values must contain capture references.

These RegEx capture references **must not** be escaped.
**Example**: `$1`, `$2`, `$3`, etc.

- `$1` is the correct way to replace the value with the captured RegEx.
- `\$1` would match `$1` *literally* (and would not reference the RegEx captured).
- One (and exactly one) `match` condition must capture these sub-matches.
- The value must be a RegEx string with at least as many captures used by the `rewrite` fields.
- The condition must have the `op` (operator) set as a RegEx operator, e.g.: `"=~"`.
- If the operator type (`op`) is excluded, `eq` will be assumed.


### RegEx Rewrite Example

The following rule rewrites a `program` field on events `not` originating from the host named `127.0.0.1`.

1. Match on the `message` field
2. Use the RegEx operator of `=~`
3. Match on any message containing either of the strings set in the `value`
4. Do not consider this a match if the `host` is `127.0.0.1`
5. If the above criteria are met, set the `program` name to `$1` (the RegEx capture obtained from the `value` in the `match` statement).


```yaml
match:
- field: message
  op: "=~"
  value:
  - output of program (\w+)
  - error while running (\w+)
- field: host
  value: 127.0.0.1
  op: ne
rewrite:
  program: "$1"

```

# Automatic key-value detection

LogZilla automatically detects events containing `key="value"` pairs. This feature allows users to avoid having to write Regular Expression patterns to extract/use the values provided in KV pairs and simply use the `value` portion using the variable of `${key}`.

To use these values, one or more of the `rewrite` fields must reference an unescaped key variable (`${key}`) from the incoming event. The key will automatically be replaced only if the text of the `message` contains that key.

At least one explicit `match` condition must still be applied in order to tell LogZilla to process that event using this rule.

For example, the following rule will rewrite the entire message of an incoming Juniper event (which uses `key="value"` pairs).

Sample Original Incoming Message (before rewrite):

> Note: the sample message below is *only* the message itself and doesn't include the host, pri, or program.

```
2017-07-03T12:23:33.146 SRX5800 RT_FLOW - RT_FLOW_SESSION_CREATE [junos@2636.1.1.1.2.26 source-address="1.2.7.19" source-port="46157" destination-address="2.4.21.21" destination-port="443" service-name="junos-https" nat-source-address="6.12.7.29" nat-source-port="46157" nat-destination-address="1.3.21.22" nat-destination-port="443" src-nat-rule-name="None" dst-nat-rule-name="SSL-vpn" protocol-id="6" policy-name="SSL" source-zone-name="intn" destination-zone-name="dmz" session-id-2="3341217" username="N/A" roles="N/A" packet-incoming-interface="eth0.1"]
```

**Desired Outcome:**

1. Match on the incoming `message` field using a RegEx operator.
2. Rewrite the entire message using the `values` contained in each of the original event's `keys` as well as the extra captured RegEx from this rule.
3. Set the `program` name to `Juniper`.
4. Create a second `match` condition and match on the `Juniper` program set in the first `match`.
5. Use RegEx to find out if the `message` contains the word *reason*
6. If it does contain a *reason* value, then add that *reason* to the message.


```yaml
rewrite_rules:
- match:
    field: message
    op: "=~"
    value: "(\\S+) (\\S+) \\S+ - RT_FLOW_(SESSION_\\w+)"
  rewrite:
    message: "$3 reason=${reason} src=${source-address} dst=${destination-address}
      src-port=${source-port} dst-port=${destination-port} service=${service-name}
      policy=${policy-name} nat-src=${nat-source-address} nat-src-port=${nat-source-port}
      nat-dst=${nat-destination-address} nat-dst-port=${nat-destination-port} src-nat-rule=${src-nat-rule-name}
      dst-nat-rule=${dst-nat-rule-name} protocol=${protocol-id} src-zone=${source-zone-name}
      dst-zone=${destination-zone-name} session-id=${session-id-32} ingress-interface=${packet-incoming-interface}
      $2 $1"
    program: Juniper
- match:
  - value: Juniper
    field: program
  - value: "(.+?) reason= (.+)"
    field: message
  rewrite:
    message: "$1 $2"
```

## Key-Value Custom Delimiters and Separators

In LogZilla, KV pairs are detected using a default separator (the character separating each key from the value) as `=` and the default delimiter (the character on either end of the value) as `"`. For example: `key="value"`

For custom environments where KV pairs may use something else, LogZilla rules may also be customized to accommodate by including a `kv` name in the rule definition itself, for example:

```yaml
rewrite_rules:
- match:
    field: message
    op: "=~"
    value: RT_FLOW_SESSION_\w+
  rewrite:
    message: "${reason}"
  kv:
    separator: ":"
    delimiter: ''
```

The example above changes the kv separator to `:` and defines an empty delimiter, allowing the key-value parser to correctly recognize a `foo:bar` format instead of the default `key="value"` format.
There are two rules that aren't customizable at the moment:
1. Keys cannot contain non-alphanumeric characters except for `_` and `-`.
2. `separator` cannot be an empty string.

### Pair separator

For more complex events you may want to split the message into pairs before looking for a specific key and value inside every part.
To do so you can define a `pair_separator` inside the `kv` field.
For values that can contain spaces and do not have any delimiter, this is the only way to correctly parse the message.
For example, with the following message:

```
field1=some value,field2=other value
```

to get "some value" under `${field1}`, define a `kv` as follows:

```yaml
kv:
  delimiter: ''
  separator: "="
  pair_separator: ","
```

> Note: you cannot define both an empty delimiter and empty pair_separator.


## The `rewrite` keyword

The `rewrite` keyword may also be used to "recall" any of:

1. Message (the message itself)
2. Host - The host name
3. Program - The program name

### `rewrite` Example

```yaml
rewrite:
  message: "$PROGRAM run on $HOST: $MESSAGE"
```

## Dropping events - `drop` keyword

To completely ignore events coming into LogZilla, use `"drop": true`.

This can be used to remove noise and only focus on important events.

> Note that `drop` cannot be used with any keyword except `match`.

### Drop example

The following example shows how to completely ignore diagnostic messages from a program called `thermald`.

```yaml
rewrite_rules:
- match:
  - field: program
    value: thermald
  - field: severity
    op: ge
    value: 6
  drop: true
```

Operator `"ge"` means `greater or equal`, so it only drops events of severity 6 (informational) and 7 (debug).


## Skipping after first match - `first_match_only` flag

The `first_match_only` flag tells the Parser to stop trying to match events on each subsequent rule in that rule file after the first time it matches. This is useful when there is a need to rewrite a field based on an array of rules which are mutually exclusive. Additionally, using `first_match_only` can save a lot of processing time on larger files.

> Note that this flag only affects the scope of *this* current rule file (not all JSON files in `/etc/logzilla/rules.d/`). Regardless of whether or not any of these rules match, other rule files which do make a match will still be applied.


### Example

* Because this is a large ruleset and there's no need to continue parsing after the first match, we use `first_match_only` to save processing time as we know the others won't match anyway.
* The last rule is a catch-all. If no matches are made on the well-known ports defined above it, we tell the rule to set the tag to `dynamic`.
* Note: the rule below has been truncated for brevity.

```yaml
first_match_only: true
rewrite_rules:
- match:
    field: ut_dst_port
    value: '1'
  tag:
    ut_dst_port: rtmp
- match:
    field: ut_dst_port
    value: '60179'
  tag:
    ut_dst_port: fido
- match:
    field: ut_dst_port
    op: "=~"
    value: "^\\d+$"
  tag:
    ut_dst_port: dynamic
```

# Comma Separated Values, Tab Separated Values, Other Delimited

When dealing with messages in a format of fields of defined order,
separated with a single character, use a tokenize rule to easily rewrite them.  

`separator` defaults to ',' so it can be skipped for csv messages.

### Example

  match:
    field: message
    value: palo alto
  tokenize:
    separator: ','
    fields:
      - incident
      - device
      - program
      - source_port
      - destination_port
      - unused_field
  rewrite:
    message: ${incident},
    program: PaloAlto-${program},
  tag:
    dst: ${destination_port}
    src: ${source_port}

Note: as indicated, the syntax for field reference is identical to key/value parser.
Thus  `kv` with `tokenize` cannot be used together in one rule.  If both features are
needed two consecutive rules should be used.

# Extra Fields
LogZilla event handling is based on syslog-ng basic fields (TS, PRI, MESSAGE, HOST, PROGRAM)
plus additional (cisco_mnemonic, status, user_tags). To pass other fields and
use them in rewrite rules extra fields can be used.
Extra fields properties:

    * read-only (cannot be added, modified, deleted)
    * schema less/nested
    * limited life (available only in parser and forwarder)
    * does not affect cardinality and size of the events in storage

Read-only `extra fields` can be used to provide other fields to parser rules.
Extra fields can be nested::

```yaml
message: Test message
host: testhost
extra_fields:
  foo:
    content: 'Extra Content: Foo bar'
    name: custom_program_name
  baz:
    id: '123'
  some_list:
  - host1
  - host2
  - host3
```

To extract nested values from extra fields, the dot-separated path to field
value should be provided (``${extra:x.y.0``) :

    {
        "match": [
            {
                "field": "host",
                "value": "testhost"
            },
            {
                "field": "${extra:foo.bar}",
                "value": "Extra Content:(\w+)"
            }
       ],
        "rewrite": {
            "message": "$MESSAGE $1", # "Test message Extra Content: Foo bar"
            "program": "${extra:foo.name}", # "custom_program_name"
            "host": "${extra:some_list.2}", # "host3"
        },
        "tag": {"sample_id": ${extra:baz.id} # "123"
    }
```yaml
match:
- field: host
  value: testhost
- field: "${extra:foo.bar}"
  value: "Extra Content:(\w+)"
rewrite:
  # "Test message Extra Content: Foo bar"
  message: "$MESSAGE $1"
  # "custom_program_name"
  program: "${extra:foo.name}"
  # "host3"
  host: "${extra:some_list.2}"
tag:
  sample_id:
    # "123"
    extra: baz.id
```

*Note that extra field values are always converted to "string"*


# Syslog Structured Data

Extra field are used as a placeholder for additional syslog-ng fields:

    - SDATA - rfc5424 structured data (key/value)
    - MGSID - message id (string)
    - PID - pid (string)

To use SDATA/MGSID/PID in the parser rule extra field accessors are used.
Example raw line::

"... host1 prog1 - ID47[exampleSDID@0 iut="3" eventSource="Application" eventID="1011"][examplePriority@0 class="high"] Message1"

Parsed event::

```yaml
HOST: host1
PROGRAM: prog1
MESSAGE: Message1
extra_fields:
  PID: "-"
  MSGID: ID47
  SDATA:
    exampleSDID@0:
      iut: "3"
      eventSource: Application
      eventID: '1011'
    examplePriority@0:
      class: high
```

Usage in the parser rules::

```yaml
rewrite:
  # "Message1 PriorityClass=high"
  message: "$MESSAGE PriorityClass=${extra:SDATA.examplePriority@0.class}"
  # "Application"
  program: "${extra:SDATA.exampleSDID@0.eventSource}"
tag:
  # "1011"
  eventID: ${extra:SDATA.eventID}
```

# Text Substitution

To substitute a field text `replace` rules should be used.
Replace rule configuration :

    - `field` : field field (required)
    - `expr` : substring regex (required)
    - `fmt` : output text formatter (required)
    - `ignore_case` : ignore case in expre (optional, default:true)
    - `first_only` : replace only first expr occurrences (optional, default:false)

Example `replace` section::

```yaml
replace:
- field: message
  expr: foo
  fmt: bar
- field: message
  expr: Foo
  fmt: bar
  ignore_case: false
- field: message
  expr: Foo
  fmt: bar
  ignore_case: false
  first_only: true
- field: message
  expr: \"
  fmt: "\""
- field: message
  expr: "(\\w+)=(\\w+)"
  fmt: "$2=$1"
- field: message
  expr: date=\d{2}:\d{2}:\d{2}(\s+)
  fmt: ''
- field: message
  expr: "\\s+$"
  fmt: ''
```

# Built-in Parser Rules

LogZilla provides a small number of default, built-in rules that among other things handle:
- rewriting the "program" field to the base (`/usr/sbin/cron` becomes `cron`)
- setting "cisco_mnemonic" field for Cisco events
- setting ip source and destination port in the event as tags
- ignoring unnecessary programs (to increase the signal-to-noise ratio)

# Rule Order

* All JSON rules files contained in `lz_syslog:/etc/logzilla/rules.d/` are processed in alphabetical order.
* The Rules contained in each file are processed sequentially.
* If there are multiple rules with the same matching criteria, the last rule wins.

## Rule Order Example

**file1.yaml**

```yaml
rewrite_rules:
- comment: rule1
  match:
    field: host
    value: host_a
  rewrite:
    program: new_program_name
```

**file2.yaml**

```yaml
rewrite_rules:
- comment: rule2
  match:
    field: host
    value: host_a
  rewrite:
    program: new_program_name2
```

### Result

Events matching the filters above will have the following properties.

```yaml
#### rule2
program: "new_program_name2"#### rule2
```


### Testing
A command line tool `logzilla rules` may be used to perform various functions including:

* list   -             List rewrite rules
* reload  -            Reload rewrite rules
* add    -             Add rewrite rule
* remove   -           Remove rewrite rule
* enable   -           Enable rewrite rule
* disable   -          Disable rewrite rule
* performance   -      Test rules single thread performance

To add your rule, simply type `logzilla rules add myfile.json`.

When a new `json` or `yaml` file is added it will be read in, there is no need to restart LogZilla.


