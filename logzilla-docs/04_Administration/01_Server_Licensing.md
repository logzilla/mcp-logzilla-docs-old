<!-- @@@title:Server Licensing@@@ -->

# Server License Information

Your license key can be obtained via the UI or command line.

## Viewing Your Host Key

To locate your server license information in the LogZilla interface,
navigate to the following path:

    Settings -> System Settings -> License Information

By accessing this section, you can view details about your current
server license, such as the host key, expiration date, and allowed
features.

## Checking Host Key via Shell

To view your LogZilla server’s host key, access the server’s shell using
the console or SSH. Once logged in, execute the following command:

    logzilla license key

The command returns your unique server key, which you can provide to
your LogZilla account manager. For example:

    73cde9bfce9a15a0ae3a97f0c501231712813fc6

## Updating License

After your LogZilla account manager informs you that your license has
been updated on the licensing server, you can update your server’s
license by running the following command:

    logzilla license download

LogZilla does not need to be restarted for the key to take effect.

# Manually Installing Your License

If your server is offline, you can download the license from a different
system and manually transfer it to your server. In the example below,
we’ll use a host key of `73cde9bfce9a15a0ae3a97f0c501231712813fc6`, but
be sure to replace it with your actual key obtained from one of the
methods noted above.

## Browser

If using a browser, visit
`https://license.logzilla.net/keys/73cde9bfce9a15a0ae3a97f0c501231712813fc6`

## SSH/Terminal

If using a terminal from another Linux system, use:

    wget https://license.logzilla.net/keys/73cde9bfce9a15a0ae3a97f0c501231712813fc6 -O lic.json

Remember to replace `73cde9bfce9a15a0ae3a97f0c501231712813fc6` with your
actual host key.

## Copy/Update your license

After obtaining the `JSON` file from our license server:

1.  Copy the contents of the JSON file and save it to a file with any
    name, such as `lic.json`.
2.  Load the license on the offline server using the following command:

``` bash
logzilla license load lic.json
```

This action will place the license file in the appropriate directory,
allowing your LogZilla server to recognize and use the updated license
information.
