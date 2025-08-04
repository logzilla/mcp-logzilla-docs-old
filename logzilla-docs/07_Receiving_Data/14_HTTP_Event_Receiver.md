<!-- @@@title:Receiving Events using HTTP@@@ -->

# HTTP Event Receiver

LogZilla has a "universal" facility to receive events via HTTP.
This is called "universal" because it is not specific to any
particular scenario -- it is intended to be used with custom
integrations.

LogZilla listens for incoming events via HTTP to its standard HTTP port
(configured by `logzilla config HTTP_PORT`, see section [4.8 Backend
Configuration Options](/help/administration/backend_configuration_options)),
at path `/incoming`. 

Full http receiver api documentation is available at path `/incoming/docs`


## Structured JSON Data Format

Recommended format of incoming data allows for best performance, as multiple
events can be sent in single request. The events sent to LogZilla should to be
formatted as JSON, with structure:

```
{
  "events": [
    // event1,
    // event2,
    // etc.
  ]
}
```

As the JSON array notation indicates, more than one event message
can be sent per transmission, if desired. Then each event should
have structure:

```
{
  "ts": 1704063600.1234,
  "host": "testhost.org",
  "program": "testprogram",
  "message": "this is the message",
  "user_tags": {
      "": "Atlanta",
      "state": "Georgia"
  },
  "extra_fields": {
      "city": "Atlanta",
      "state": "Georgia"
  },
  "json": {
      "int_value": 1,
      "float_value": 1.1,
      "string_value": "foo",
      "object_value": {
        "foo" : "bar",
      },
      "array_value": ["bar", "baz"],
  }
}
```

### Data Contents

The event fields that can be sent to LogZilla via HTTP are:

| Field | Description |
| --- | --- |
| `ts` | epoch timestamp |
| `host` | the originating host of the log message |
| `program` | the program that generated the log message |
| `message` | log message |
| `priority` | number represents both the RFC-3164 Facility and Severity of the event in the message |
| `user_tags` | additional string fields that will be available as event attributes in both LogZilla rules and queries |
| `extra_fields` | additional string fields that will be available as event attributes in LogZilla rules |
| `json` | a special field that contains any json that will be available as event attribute in LogZilla rules |

## Unstructured JSON Data Format

If it's not possible to use the structured JSON format, then the raw JSON can be
sent, by using `/incoming/raw` path. In this case, the JSON can contain any
values, and it will be in the `extra_fields` of the message, and also in the
serialized form in the `message` field. The `host` will be set to the IP address
of the sender, and the `program` will be set to `http_receiver`.

This case is usually used with cooperation with some rules (usually from an app)
that will extract interested fields from `extra_fields` and create appropriate
event, depending on the actual content.

You can also use any subpath of `/incoming/raw`, like for example
`/incoming/raw/app1`. The subpath will be available in the
 `extra_fields._url_path` field - in this example it will be `/app1`. This can
be used in the rules to recognize events from different sources. 


## Authentication

When sending events to LogZilla (either as structured or non-structured JSON),
the API key (with the appropriate header) must be used. This is documented in
[Obtaining an Auth Token](/help/logzilla_api/using_the_logzilla_api).

NOTE: after generating an authorization token the LogZilla HTTP receiver module
must be restarted This can be accomplished either via standard `logzilla
restart` or by restarting just the HTTP receiver module:
```
logzilla restart -c httpreceiver
```

Upon successful receipt of a JSON `events` data element, the
HTTP receiver will respond with HTTP status code `200` and message:

```
{"status": "ok"}
```

## Examples

An example curl command using structured JSON:

```
curl \
  -H 'Content-Type: application/json' \
  -H 'Authorization: token 7ce02b52bfb225a2b4a0ef992b4c2afe9dc10853aecf97f6' \
  -X POST -d  '{
      "events": [ { 
        "message": "Test Message", 
        "host": "curl.test", 
        "program": "myapp", 
        "extra_fields": { "city": "Atlanta", "state": "Georgia" },
        "json": { "int_value": 1, ""string_value": "foo", "array_value": ["foo"] }
      } ] }' \
  'http://lzserver.company.com/incoming'
```

An example of using unstructured JSON:

```
curl \
  -H 'Content-Type: application/json' \
  -H 'Authorization: token 7ce02b52bfb225a2b4a0ef992b4c2afe9dc10853aecf97f6' \
  -X POST -d  '{"foo": "bar"}'
  'http://lzserver.company.com/incoming/raw/testapp'
```

In the latter case, the event will be created with `host` set to the IP address
of the sender, `program` set to `http_receiver`, and `message` set to the
`{"foo": "bar"}` string. Also the `extra_fields.foo` will contain `bar` and `extra_fields._url_path` will contain `/testapp`.