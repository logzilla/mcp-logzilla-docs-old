<!-- @@@title:Offline Installs and Upgrades@@@ -->

# Offline Installs and Upgrades

## Overview

This documentation provides instructions for installing or upgrading
LogZilla in an offline environment. You can perform these actions by
downloading a pre-built package from any system with internet access,
such as a local laptop, and then manually transferring it to the offline
LogZilla server.

## Prerequisites

- A system with internet access to download the LogZilla offline
  package.
- The offline LogZilla server where the installation or upgrade will
  occur.
- Root access on the logzilla server

## Downloading the LogZilla Offline Package

On any system with internet access:

1.  **Download the Offline Package**:

    Download the pre-built LogZilla package from:

        https://license.logzilla.net/download/
    
    You will be automatically redirected to the current newest version of the
    logzilla package.

2.  **Transfer the Package**:

    From the download above you'll get the newest LogZilla version package
    in the form of `logzilla-v6.x.y.tar.gz`. For all commands below please
    replace logzilla-v6.x.y.tar.gz with the actual name of the file
    you downloaded.

    Manually transfer the downladed file `logzilla-v6.x.y.tar.gz` to your
    offline LogZilla server using a USB drive, SCP, RSYNC, or any other file
    transfer method.

## Installation on the Offline LogZilla Server

All commands in the sections below must be run as the root user.

### New Installation

<font color="red">IMPORTANT</font>: This method is ONLY for new
installs, for upgrades, refer to the *Upgrade Procedure* section below.

For new installations on the offline server:

1.  **Extract the LogZilla Package**:

    ``` bash
    tar xzvf /path/to/logzilla-v6.x.y.tar.gz
    ```

    This will create a directory named `logzilla-v6.x.y` in the current
    directory.

2.  **Run the Installation Script**:

    Navigate to the directory where you extracted the files and run:

    ``` bash
    cd logzilla-v6.x.y
    bash kickstart.sh
    ```

3.  **License Retrieval and Startup**:

    After installation, follow the on-screen instructions to retrieve
    the license and start LogZilla.

### Upgrade Procedure

For upgrading an existing installation:

1.  **Extract the LogZilla Package**:

    ``` bash
    tar xzvf /path/to/logzilla-v6.x.y.tar.gz
    ```

2.  **Run the Upgrade Command**:

    From the directory where you extracted the files, execute:

    ``` bash
    cd logzilla-v6.x.y
    logzilla upgrade --offline-dir .
    ```

3.  **Verify the Upgrade**:

    After the upgrade, check the new version:

    ``` bash
    logzilla version
    ```

    This should display the upgraded version number.

## Example Walkthrough

### Performing an Offline Upgrade

1.  **Download and Transfer the Package**:

    - Go to `https://license.logzilla.net/download/` and it
      will immediately start downloading the latest version of LogZilla
    - Transfer the file to the offline LogZilla server.

2.  **Check currently installed version**:

        root@logzilla-server:/tmp$ logzilla version
        v6.28.0

3.  **Verify Internet Access Unreachable**:

    This step is not necessary, it is here to show that the system we
    ran the upgrade on does not have internet access.

        root@logzilla-server:~$ ping 8.8.8.8
        ping: connect: Network is unreachable

4.  **Extract the offline package**:

        root@logzilla-server:~$ cd /tmp
        root@logzilla-server:/tmp$ tar xzvf logzilla-v6.31.8.tar.gz
        logzilla-v6.31.8/
        logzilla-v6.31.8/kickstart.sh
        logzilla-v6.31.8/library-influxdb:1.8.10-alpine.tar.gz
        logzilla-v6.31.8/library-postgres:15.2-alpine.tar.gz
        logzilla-v6.31.8/library-redis:6.2.6-alpine.tar.gz
        logzilla-v6.31.8/library-telegraf:1.20.4-alpine.tar.gz
        logzilla-v6.31.8/logzilla-etcd:v3.5.7.tar.gz
        logzilla-v6.31.8/logzilla-front:v6.31.8.tar.gz
        logzilla-v6.31.8/logzilla-mailer:v6.31.8.tar.gz
        logzilla-v6.31.8/logzilla-runtime:v6.31.8.tar.gz
        logzilla-v6.31.8/logzilla-sec:v6.31.8.tar.gz
        logzilla-v6.31.8/logzilla-syslogng:v6.31.8.tar.gz


5.  **Begin the upgrade procedure**:

        root@logzilla-server [tmp]:# logzilla upgrade --offline-dir /tmp/logzilla-v6.31.8
         lz.manager INFO     Loading /tmp/logzilla-offline/library-influxdb:1.8.10-alpine.tar.gz ...
         lz.manager INFO     Loading /tmp/logzilla-offline/library-postgres:15.2-alpine.tar.gz ...
         lz.manager INFO     Loading /tmp/logzilla-offline/library-redis:6.2.6-alpine.tar.gz ...
         lz.manager INFO     Loading /tmp/logzilla-offline/library-telegraf:1.20.4-alpine.tar.gz ...
         lz.manager INFO     Loading /tmp/logzilla-offline/logzilla-etcd:v3.5.7.tar.gz ...
         lz.manager INFO     Loading /tmp/logzilla-offline/logzilla-front:v6.31.8.tar.gz ...
         lz.manager INFO     Loading /tmp/logzilla-offline/logzilla-mailer:v6.31.8.tar.gz ...
         lz.manager INFO     Loading /tmp/logzilla-offline/logzilla-runtime:v6.31.8.tar.gz ...
         lz.manager INFO     Assuming version v6.31.8
         lz.manager INFO     Loading /tmp/logzilla-offline/logzilla-sec:v6.31.8.tar.gz ...
         lz.manager INFO     Loading /tmp/logzilla-offline/logzilla-syslogng:v6.31.8.tar.gz ...
        Starting LogZilla upgrade to 'v6.31.8'
         lz.setup   INFO     Setup init
         lz.docker  INFO     Decommission: queryupdatemodule, front
         lz.docker  INFO     Decommission: httpreceiver, celerybeat, queryeventsmodule-1
         lz.docker  INFO     Decommission: triggersactionmodule, gunicorn, aggregatesmodule-1, dictionarymodule, parsermodule, celeryworker
         lz.docker  INFO     Decommission: storagemodule-1
         lz.docker  INFO     Decommission: logcollector, telegraf, tornado, mailer
         lz.docker  INFO     Decommission: syslog
         lz.docker  INFO     Decommission: postgres
         lz.docker  INFO     Decommission: redis, influxdb
         lz.docker  INFO     Decommission: etcd
         lz.docker  INFO     Start: etcd
         lz.docker  INFO     Start: influxdb, redis
         lz.docker  INFO     Start: postgres
         lz.containers.postgres INFO     Running postgres v15 migration ...
         lz.containers.postgres INFO     Postgres v15 migration finished successfully
        Operations to perform:
          Apply all migrations: admin, api, auth, contenttypes, django_celery_beat, sessions
        Running migrations:
          No migrations to apply.
         lz.setup   INFO     Update group permissions
         lz.setup   INFO     Update internal triggers
         lz.docker  INFO     Start: syslog
         lz.docker  INFO     Start: logcollector, tornado, telegraf, mailer
         lz.docker  INFO     Start: storagemodule-1
         lz.docker  INFO     Start: triggersactionmodule, celeryworker, dictionarymodule, aggregatesmodule-1, gunicorn, parsermodule
         lz.docker  INFO     Start: celerybeat, httpreceiver, queryeventsmodule-1
         lz.docker  INFO     Start: queryupdatemodule, front
         lz.docker  INFO     Start: watcher
        LogZilla successfully upgraded to 'v6.31.8'

6.  **Verify that the new version is running**:

        root@logzilla-server [tmp]:# logzilla version
        v6.31.8
