<!-- @@@title:Using The LogZilla API@@@ -->

# The LogZilla API

<iframe style="display: block; margin-left: auto; margin-right: auto;" width="560" height="315" src="https://www.youtube.com/embed/mXVZg16z0DM" title="LogZilla API | LogZilla University" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

The LogZilla API is available to standard HTTP/HTTPS requests.  This 
can be accomplished via `wget`/`curl` or any tool capable of sending
GET/POST, etc. commands.  LogZilla API access is restricted so that
only specified users are allowed access.  This is accomplished via
*auth tokens* as described below.

## Authentication (Auth Tokens)

All API functions (and receipt of events via HTTP) require authentication
via an *authorization token*.  An *auth token* is a long sequence
of alphanumeric digits, which represents a "key" that is associated
with a particular user. When this *auth token* is provided to LogZilla,
LogZilla can verify that the particular token has been configured
to allow API or "back-end" access. Each auth token should be kept private,
because it can be used to authorize access to the data stored in LogZilla.
Each auth token will persist indefinitely, until specifically revoked as
described below.

There are two types of auth tokens: full-function "user" tokens,
and ingest-only tokens.  Ingest-only tokens are used for receiving data
via the HTTP Event Receiver and are not useful for any other purpose.

*Administrator* or "root" access should be used in dealing with auth
tokens (this can be accomplished via privileged login or via `sudo`).

To manage tokens, administrators may use the `logzilla authtoken` CLI tool:

```
# logzilla authtoken -h
usage: authtoken [-h] [-d] [-q] {create,revoke,info,list} ...

LogZilla AuthToken manipulation

positional arguments:
  {create,revoke,info,list}
    create              create new token
    revoke              revoke new token
    info                show token info
    list                list all active tokens

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           debug mode
  -q, --quiet           notify only on warnings and errors (be quiet).
```

## Auth Token Management

### Auth Token Generation

Use `logzilla authtoken create` to create a new "user" full-function auth
token, as shown here:

Sample output:

```
root[~]: # logzilla authtoken create
Creating USER token
user-317526c44e0e04348f3dd084e997cc15950107700ddd7be0
```

The last line shows the auth token.  

You can create auth tokens for other users, as well.  For example, to create
an auth token for the user "john":

```
root[~]: # logzilla authtoken create -U john
Creating USER token
user-317526c44e0e04348f3dd084e997cc15950107700ddd7be0
```

Ingest-only tokens are created using the `--ingest-only` option:

```
root[~]: # logzilla authtoken create --ingest-only
Creating INGEST token
ingest-317526c44e0e04348f3dd084e997cc15950107700ddd7be0
```

### Auth Token Review

Currently usable auth tokens can be listed using 
`logzilla authtoken list`:
```
# logzilla authtoken list
Active tokens:
8210276eca565481f66677438ec454025a621e05d7df2a80 created: 2022-05-12 14:37:51.769886+00:00; user: admin
```

Details for an auth token can be examined via
`logzilla authtoken info`:
```
# logzilla authtoken info 8210276eca565481f66677438ec454025a621e05d7df2a80
Token: 8210276eca565481f66677438ec454025a621e05d7df2a80
User: admin
Created: 2022/05/12 14:37:51
```

### Auth Token Revocation

Auth tokens can be "revoked", which will effectively delete
them and prevent any access or usage of LogZilla from that
point on.  This is done via `logzilla authtoken revoke`:
```
# logzilla authtoken revoke 8210276eca565481f66677438ec454025a621e05d7df2a80
Token 8210276eca565481f66677438ec454025a621e05d7df2a80 revoked.
```

### Using the Auth Token

The authorization token may be provided to the API in two ways:

- `Authorization` header
- Via the `AUTHTOKEN` parameter used in a request URI

#### Header based

Using an authtoken in Authorization HTTP header:

```
Authorization: token 701a75372a019fc3b1572454a582a5705bc4e929d305694c
```

#### URI based

Using an authtoken in request URL:

```
POST /incoming?AUTHTOKEN=701a75372a019fc3b1572454a582a5705bc4e929d305694c
```

#### Example

After creating the token, users can connect to the API using any POST/GET/PATCH/PUT, etc. command.

As outlined in [HTTP Event
Receiver](/help/receiving_data/receiving_events_using_http),
an example of this would be to send a log message into LogZilla using CURL:

```
curl \
  -H 'Content-Type: application/json' \
  -H 'Authorization: token 91289817dec1abefd728fab4f43aa58b5e6fa814f' \
  -X POST -d '{"message": "Test Message"}' \
  'http://logzilla.mycompany.com/incoming/raw'
```

## Try it out
Users may try the API and get more documentation by visiting the address
`/api/docs` on the LogZilla server.
