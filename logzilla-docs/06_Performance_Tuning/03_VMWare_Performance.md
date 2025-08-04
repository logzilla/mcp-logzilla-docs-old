<!-- @@@title:VMWare Performance@@@ -->


If you plan to install LogZilla on a VMWare Server, then you'll want to set the resource allocation on the disk to high.

It should be noted that LogZilla does not recommend using VMWare for large-scale deployments unless you are well versed in enhancing disk I/O performance.

To set the resource allocation in VMWare, right-click on your VM and select `edit`.
Next, click the `Resources tab` and click `disk` then change the drop-down menu from `normal` to `high` as seen below:

![VMWare Resource Allocation](@@path/images/vmware-disk-priority.png)


