<!-- @@@title:Syslog-ng HTTPS setup @@@ -->

# Syslog-ng to LZ over HTTP/HTTPS

This section details how to set up LogZilla and Syslog-ng so that syslog-ng
log messages are sent to LogZilla (over HTTP/HTTPS) for processing.

## LogZilla Setup

### Authorization Token
An authorization token must be used to direct LogZilla to
allow incoming events from the syslog-ng source.  If an
auth token currently exists 
(viewable via `logzilla authtoken list`) it can be used, 
or if one is not available then a new one should be generated,
as detailed in the section titled **Authentication (Auth Tokens)**
on page
[9.1 Using The LogZilla API](/help/logzilla_api/using_the_logzilla_api).

## Syslog-ng configuration

To relay logs directly to LogZilla, an `http` destination must be configured.

### Standard Configuration (Recommended for Most Environments)

The following configuration is suitable for most standard deployments:

- Replace `YOUR_LOGZILLA_SERVER` and, optionally, a port `YOUR_HTTP_PORT`.
- Replace `YOUR_GENERATED_TOKEN` with the generated token from LogZilla.
- Custom tags can be added using the `--pair` option as shown in the example.
- In the source section, replace `s_src` with the source you want to use.
  For example, in Ubuntu, the source is `s_src` as defined in the
  main `/etc/syslog-ng/syslog-ng.conf` file.

```text
destination d_logzilla {
    http(
        url("https://YOUR_LOGZILLA_SERVER:YOUR_HTTP_PORT/incoming")
        method("POST")
        user-agent("syslog-ng User Agent")
        headers(
            "Content-Type: application/json",
            "Authorization: token YOUR_GENERATED_TOKEN"
        )
        body-prefix("{\"events\": [\n")
        delimiter(",\n")
        body('$(format-json
            --pair priority=int($PRI)
            --pair host="$HOST"
            --pair program="$PROGRAM"
            --pair message="$MESSAGE"
            --pair user_tags.custom_tag="custom_value"
            --pair user_tags.custom_tag2="custom_value2"
        )')
        body-suffix("\n]}")
        batch-lines(10000)
        batch-bytes(10485760)
        batch-timeout(500)
    );
};

log {
    source(s_src);
    destination(d_logzilla);
    flags(flow-control);
};
```

### Advanced Configuration (For Special Requirements)

For environments that need more advanced processing capabilities, such as
handling structured data (SDATA) elements, RFC5424 format details, or
specialized fields, a more detailed configuration is provided below:

#### Key Advanced Parameters Explained

- **`ts=double(${R_UNIXTIME}.${R_USEC})`**: Combines Unix timestamp with microsecond
  precision using syslog-ng's built-in macros. The `double` type specification
  ensures proper numeric formatting in JSON.

- **`--key extra_fields.*`**: Creates a string-to-string map for metadata that
  comes from syslog itself (not from the log message content). Unlike `user_tags`
  (which are indexed automatically), `extra_fields` are removed after parsing and
  are primarily used for fast matching in LogZilla rules. Think of them as
  temporary user tags for efficient processing of incoming events. Common uses
  include capturing metadata like `SOURCE_IP` or `HOST_FROM`.

- **`--scope sdata`**: Processes RFC5424 structured data elements, which contain
  standardized metadata about the log message.

- **`--rekey .SDATA.* --add-prefix json`**: Renames structured data fields to have a
  `json` prefix, making them more identifiable and preventing field name
  collisions. While you can put any data in these json fields, be aware that
  unpacking JSON in LogZilla rules is computationally expensive, so this approach
  should be used sparingly for complex data.

- **Batch parameters**: Controls how many events are collected before sending:
  - `batch-lines`: Maximum number of events in a single batch
  - `batch-bytes`: Maximum size of a batch
  - `batch-timeout`: Maximum time to wait before sending a batch (milliseconds)

```text
destination d_logzilla_advanced {
    http(
        url("https://YOUR_LOGZILLA_SERVER:YOUR_HTTP_PORT/incoming")
        method("POST")
        user-agent("syslog-ng User Agent")
        headers(
            "Content-Type: application/json",
            "Authorization: token YOUR_GENERATED_TOKEN"
        )
        body-prefix("{\"events\": [\n")
        delimiter(",\n")
        body('$(format-json
            ts=double(${R_UNIXTIME}.${R_USEC})
            priority=int($PRI)
            host=$HOST
            program=$PROGRAM
            message=$MESSAGE

            --key extra_fields.*
            extra_fields.HOST_FROM=$HOST_FROM
            extra_fields.SOURCEIP=$SOURCEIP
            extra_fields.SOURCE=$SOURCE

            --scope sdata
            --key PID --rekey PID --add-prefix json.
            --key MSGID --rekey MSGID --add-prefix json.
            --rekey .SDATA.* --add-prefix json

            --key .JSON.* --rekey .JSON.* --replace-prefix .JSON.=json.
        )')
        body-suffix("\n]}")
        batch-lines(5000)
        batch-bytes(512Kb)
        batch-timeout(100)
    );
};

log {
    source(s_src);
    destination(d_logzilla_advanced);
    flags(flow-control);
};
```

- **JSON Body Format:** Matches LogZilla's structured JSON event array format,
  as detailed in
  [Receiving Events using HTTP](https://docs.logzilla.net/07_Receiving_Data/15_HTTP_Event_Receiver/).
  Each event includes essential fields like `host`, `program`, `message`, `priority`,
  and optional `user_tags`.

## Verifying Successful Transmission

On successful receipt of logs, LogZilla responds with an **HTTP 200** `OK`
status
(or possibly `HTTP 202 Accepted`) and the message:

```json
{"status": "ok"}
```

## Using User Tags

User tags are additional pieces of data composed of key-value pairs.
Each log entry ingested may have one or more user tags.
More information about user tags can be found in the [User
Tags](https://docs.logzilla.net/10_Data_Transformation/04_User_Tags/) section.

### Example

```bash
curl \
  -H 'Content-Type: application/json' \
  -H 'Authorization: token YOUR_GENERATED_TOKEN' \
  -X POST -d '{
    "events": [{ 
      "message": "Test Message",
      "host": "curl.test",
      "program": "myapp",
      "user_tags": { "city": "Atlanta", "state": "Georgia" }
    }]
  }' \
  'http://YOUR_LOGZILLA_SERVER:YOUR_HTTP_PORT/incoming'
```

This configuration is useful in two primary scenarios:

1. **Constant tags:** Tags that remain constant for each log sent from a
particular syslog originator (e.g., `"relay_server": "server1"`).
2. **Dynamic tags:** Tags populated dynamically from syslog data elements
(e.g., `"relay_server": "$LOGHOST"`).
