<!-- @@@title:PCI Compliance@@@ -->


# PCI Logs
NEO stores its data in a binary format, making it very difficult for
logs to be altered. However, a secondary store using MD5 hashes can be
created to ensure that logs have not been tampered with. 

First, logging should be enabled in the LogZilla *Settings* page, then
*System Settings*, then *Services*.

![LogZilla PCI Compliance Settings](@@path/images/settings-pcicompliance.jpg)

 Then all data coming into LogZilla via syslog will be logged in
`/var/log/logzilla/pci-compliant/yyyy-mm/yyyy-mm-dd.log`, according to the
current date. 

Next, it is necessary to have a cron entry that will compress the logs at the end of each day
and create an MD5 Checksum file. This can be accomplished by issuing the following command (with
root privileges):


```
cat << EOF > /etc/cron.d/logzilla-pci
# Cron entry to forward syslog-ng to text logs and compress with a checksum
1 0 * * * root (find /var/log/logzilla/pci-compliant/*/*.log -daystart -mtime +0 -type f -exec echo "compressing '{}'" ';' -exec gzip '{}' ';' -exec md5sum '{}'.gz ';' >> /var/log/logzilla/pci-compliant/checksums) 2>&1
EOF

```

The compliance logs, along with their checksums will be located at
`/var/log/logzilla/pci-compliant`

It is recommended that these files be backed up to a secure location every day.
