<!-- @@@title:Moving LogZilla Archive Files@@@ -->

# Relocating LogZilla Archive Files

LogZilla keeps a record of past events in an archive. The archive’s size
is managed by the `logzilla config ARCHIVE_FLUSH_DAYS` and
`logzilla config ARCHIVE_EXPIRE_DAYS` commands, as explained in the
[backend configuration
options](/help/administration/backend_configuration_options).

The LogZilla archive’s size depends on the settings mentioned above and
the number of events LogZilla processes. To check the space occupied by
the LogZilla archive, use the following command:

    du -csh /var/lib/docker/volumes/lz_archive/

If necessary, you can move the LogZilla archive to a different drive or
directory to save disk space. To do this, execute the following commands
as the `root` user:

    logzilla stop
    docker run --rm -v /new_archive_dir:/new_archive_dir -v lz_archive:/temp_archive  logzilla/runtime sh -c "mv  /temp_archive/* /new_archive_dir/"
    docker rm lz_watcher
    docker volume rm lz_archive
    docker volume create --opt type=none --opt o=bind --opt device=/new_archive_dir  lz_archive
    logzilla start

In these commands, replace `old_archive_dir` with the current location
of the LogZilla archive. For a default LogZilla installation, this is
`/var/lib/docker/volumes/lz_archive`. Substitute `new_archive_dir` with
the desired new location (directory) for the LogZilla archive. The
`new_archive_dir` represents the destination where you want to move the
archive. Make sure that this directory already exists before proceeding
with the relocation process.
