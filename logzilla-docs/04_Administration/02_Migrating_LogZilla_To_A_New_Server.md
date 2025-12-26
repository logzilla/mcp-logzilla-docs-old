<!-- @@@title:Migrating LogZilla To A New Server@@@ -->

# Process
The process for migrating to a new server requires the following steps:

> Step 1 *must* be done first. If not, you must restore to the exact same version of LogZilla on the new server.

1. Updating to the latest release of LogZilla.
2. Stopping LogZilla and all associated processes.
3. Compressing relevant data.
4. Restoring to the new server.
5. Creating a license for the new server.


## Old Server

Upgrade LogZilla to the most recent version with `logzilla upgrade`.

Once the old server is updated, run `logzilla stop` to stop it.

> *WARNING*: Be sure there is enough disk space available for the backup files.


Compress data of the old server and copy it to the new server:

    for v in lz_archive lz_etcd lz_influxdb lz_postgres lz_redis; do
        cd /var/lib/docker/volumes/$v/_data
        tar -czf /tmp/$v.tgz *
    done

Copy resulting archives to the new server.

## New Server

Install or update LogZilla on the new server using `logzilla install`

Once the new server is installed, run `logzilla stop` to stop it.

Remove the contents of all the volumes mentioned above and unpack the migrated data:

    for v in lz_archive lz_etcd lz_influxdb lz_postgres lz_redis; do
        cd /var/lib/docker/volumes/$v/_data
        rm -rf *
        tar -xzf /tmp/$v.tgz
    done

You're almost done! All you need to refresh the license:

    logzilla license download

This will overwrite the now invalid license you copied from the old server,
and replace it with a demo license. Remember to contact support later and ask
them to extend it.

This concludes the migration process. You can now start LogZilla:

    logzilla start

Depending on the amount of data you have, it will take some time for LogZilla to fully start and begin showing data in the user interface. You can check the status of the initialization by browsing to your server's `/api/monitor`. For example: `http://logzilla.mycompany.com/api/monitor`

You can also check LogZilla logs for any errors:

    tail -f /var/log/logzilla/logzilla.log -n 40
