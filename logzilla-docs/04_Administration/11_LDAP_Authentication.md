<!-- @@@title:LDAP Authentication@@@ -->

# Before You Begin

<font color=red>WARNING</font>: In order to avoid conflicts from adding LDAP
authentication, you must change any pre-existing local accounts that will
have the same login name or email addresses of any LDAP accounts.

# Configuration Steps

Use the options detailed below to configure LogZilla's LDAP integration.
The LDAP configuration is stored in the file `/etc/logzilla/ldap/config.yaml`.
This file will be created for you automatically as you do the
*LogZilla LDAP Initialization* described below.

If you are using certificates, LDAP certs should be placed in `/etc/logzilla/ldap`.

# LogZilla LDAP Initialization

To configure LogZilla's LDAP support, from a command line (as `root` user)
issue the `logzilla ldap init` command.

```
root@localhost:# logzilla ldap init
LDAP configuration init ...
```

Then there will be multiple configuration parameters requested.  In order,
those are:
```
* LDAP server url [ldap://localhost]: 
```

This is the host name or ip of your LDAP server, preceded by `ldap://`.
Example: `ldap://192.168.1.2`.

```
* Domain for user search [ou=users,dc=example,dc=com]: 
```

This is the LDAP object from which to start searches for users.  For example,
there may be an organizational unit named `users`, for which the response
then could be `ou=users,dc=example,dc=com`.

```
* Domain for groups search [ou=logzilla,ou=groups,dc=example,dc=com]:
```
Similar to the previous, this parameters is the LDAP object from which to
start searches for groups.  For example, there may be an organizational 
unit named `groups`, for which the response then could be
`ou=groups,dc=example,dc=com`.

```
* Class for group [posix-group]: 
```
This is the *LDAP ObjectClass Type* for groups. Unless you know that this
value should be different, accept the default value (`posix-group`).

```
* User bind dn for search []: 
```
In order to perform LDAP searches, a user account with appropriate permissions
needs to be used.  This parameters is the LDAP dn for the user account that
will be used to perform LDAP searches.  For example,
`uid=root,cn=users,dc=example,dc=com`.

```
* User bind password for search []: 
```

This is the password corresponding to the user account just entered.

```
* LDAP field used as LZ username [uid]: 
* LDAP field used as LZ first-name [givenName]: title
* LDAP field used as LZ last-name [sn]: 
* LDAP field used as LZ email [mail]: 
```
These fields are requesting the names of the LDAP attributes on the LDAP
*user* object, which will be used to correspond to the LogZilla fields
shown.  The particular values are specific to your LDAP installation.

```
Saving LDAP configuration ...
LDAP configuration initialized, run 'ldap test' or 'ldap enable'
```
This is what will be displayed once the initial configuration is
complete.

# LogZilla LDAP Configuration Options

In addition to the parameters set during the initialization process
described above, there are multiple LDAP interface properties that
can be set in the LogZilla LDAP configuration file
(`/etc/logzilla/ldap/config.yaml`).  This file is in [YAML](https://yaml.org/)
format.

## Properties

- **`ldap`** This is the section indicator for LDAP basic settings.
  - **`server_url`** : LDAP server url
  - **`user_search_dn`** : Domain for user search (as described in *Initialization*)
  - **`require_group_dn`** : The distinguished name of a group; authentication will fail for any user that does not belong to this group.
  - **`group_search_dn`** : Domain for groups search (as described in *Initialization*)
  - **`group_search_dn_filter`** : An LDAP expression providing a filter for groups search. Example: `(objectClass=posixGroup)`.  More information can be found [here](https://docs.oracle.com/cd/E19253-01/816-4556/schemas-122/index.html).
  - **`group_object_class`** : LDAP ObjectClass for group. Will usually be `posix-group`, though in special circumstances it may be `group-of-names` or `group-of-unique-names`.
  - **`group_names`** : the group LDAP dn(s) which will be imported (comma separated, ignored if group_names_exclude is set).
  - **`group_names_exclude`** : The group LDAP dn(s) which will be ignored during group search (comma separated, if set then group_names filter is ignored).
  - **`bind_dn`** : User bind dn that will be used to authenticate for permission for search.
  - **`bind_password`** : User bind password for the user account used for authentication for search.
  - **`disable_referrals`** : (`True` or `False`) Disable referrals. Setting it to `True` should help in case of problems with Active Directory.
- **`ldap_fields`** : This is the section indicator for LDAP attribute mapping.
  - **`username`** : LDAP field used as LogZilla username.
  - **`first_name`** : LDAP field used as LogZilla first-name.
  - **`last_name`** : LDAP field used as LogZilla last-name.
  - **`email`** : LDAP field used as LogZilla email.
- **`ldap_tls_options`** : The section indicator for TLS options.
  - **`start_tls`** : (`True` or `False`) Enable TLS encryption over the standard LDAP port.
  - **`tls_require_cert`** : Validation strategy for server cert. Must be one of: `NEVER`, `ALLOW`, or `DEMAND`.
  - **`tls_ca_certfile`** : Name of PEM file with CA certs.
  - **`tls_keyfile`** : Name of PEM encoded cert file for client cert authentication.
  - **`tls_certfile`** : Name of PEM encoded key file for client cert authentication.


# Testing
To test whether or not LDAP is working, do:

```
logzilla ldap test
```

When the test runs successfully, you must load and enable new settings:

```
logzilla ldap enable
```

After ensuring connectivity, log in to the UI using your LDAP credentials. 

# User Login
Users should be instructed to use only their LDAP username and not the full domain username. 

**Correct Login Name:**
`someuser`

**Incorrect:**
`someuser@domain.com`

**Incorrect:**
`DOMAIN\someuser`

