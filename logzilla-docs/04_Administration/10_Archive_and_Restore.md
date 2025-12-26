<!-- @@@title:Archive and Restore@@@ -->


LogZilla provides the ability to archive old data and later re-import that data should users need to access and search it later on. This helps users with smaller systems or low disk space to keep historical logs without the need to index all of them at all times.

Archival is particularly useful in environments where users need to be able to search and run reports on events within the last week or month, but may only periodically need to access events from a year ago.

## Live Data Retention
By default, LogZilla will keep 1 week of data "online" and up to 1 year of historical data. To make changes to your desired archive preferences, browse to your server's settings page at `/settings/system/generic`

## Archive Logs
A full list of all archives activity is available via the web API web interface located on your server at `/api/archive-restore-logs`

## Archive Management
Logzilla archives are where "warm" event data is stored.  This data is still searchable, albeit much more slowly than the "hot" event data.  The `logzilla` command line utility is used for management of archive data.

### Archiving Event Data
`logzilla archives archive --ts-from 2020-05-01 --ts-to 2020-06-01` would move events from "hot" storage to "warm" archival storage for the period 2020-05-01 up to 2020-06-01.  Alternatively `logzilla archives archives --expire-days 30` would archive events older than 30 days.

### Removing Archived Event Data
`logzilla archives remove --ts-from 2020-03-01 --ts-to 2020-04-01` would eliminate from the archives event data between 2020-03-01 and 2020-04-01.  Warning:  this data is then gone and unavailable for searching or querying!

### Migrating Previous-Version Archive Data
In order for archived data to be accessible and used as "warm" data for searches and queries, the archived data must be formatted for LogZilla version 6.10 or later.  If your archived data is a prior version it must be migrated.  Migration is done through `logzilla archives migrate --ts-from 2020-04-01 --ts-to 2020-05-01` (to migrate data between 2020-04-01 and 2020-05-01).  This process is a one-time action to be performed on the older version archived data, after which that data is always available to searches and queries.

### Using Archived Data for Searches and Queries
Archived data is usable for searches and queries by selecting the "WithArchive" check box for queries and searches.  This option causes searches and queries to search not only the "hot" event data but also go back into the "warm" archived data.  Be aware that choosing this option will slow down the search or query, possibly greatly.

(Note that in previous LogZilla versions, archived data needed to be "restored" to be available for searches and queries.  This is no longer the case, and archived data is available to searches and queries as "warm" data, until that event data is removed from the archives.)
