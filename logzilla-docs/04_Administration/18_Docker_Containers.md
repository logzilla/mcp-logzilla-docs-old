<!-- @@@title:Docker Containers@@@ -->

# Docker Containers Used by LogZilla
LogZilla operates by means of multiple docker containers handling various facets of its operation.  The following are the containers used:

Container Name | Purpose
--- | ---
lz_aggregatesmodule-1 | provides aggregates for events
lz_celerybeat | advances the internal task queue
lz_celeryworker | controls the execution of LogZilla modules
lz_dictionarymodule | handles user tags
lz_etcd | configuration data for use by all containers
lz_feeder | sends batch data from file to LogZilla
lz_forwardermodule | forwards events (for ex. after deduping)
lz_front | LogZilla web UI
lz_gunicorn | hosting of the API
lz_influxdb | processed log/event data storage
lz_logcollector | collects and combines logs from the various LogZilla containers
lz_mailer | mail send service
lz_parsermodule | parses log events against rules
lz_postgres | permanent data storage (dashboards, triggers, rules, etc.)
lz_queryeventsmodule-1 | handles query Lifecycle
lz_queryupdatemodule | updates redis with query results
lz_redis | in-memory data storage of temp data like query results
lz_sec | simple event correlator
lz_storagemodule-1 | read/write activities on event data
lz_syslog | handling of incoming syslog events
lz_telegraf | maintains metrics of LogZilla performance
lz_tornado | API websocket support
lz_triggerexec-1234567890 | example of a dynamic container used to run custom scripts
lz_triggersactionmodule | triggers handling
lz_watcher | monitors and maintains the LogZilla docker containers
