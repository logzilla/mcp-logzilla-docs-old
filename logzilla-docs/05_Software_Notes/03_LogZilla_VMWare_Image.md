<!-- @@@title:LogZilla VMWare Image@@@ -->

# LogZilla on VMWare

Users may [download](http://www.logzilla.net/download) a LogZilla
instance for use in testing or smaller scale deployments.

For larger deployments, this VM may still be used, but your System
Administrator will need to add a second disk (and likely more Ram and
CPU) to the VM to ensure that all data can be stored and processed at
scale.

The default disk size in the LogZilla VM is 50GB. Adding a second disk
to the VM is quite simple as it is pre-configured to use Linux’s Logical
Volume Manager (LVM).

### Adding More Disk Space

> Note: The VM does not need to be powered off in order to add more disk
> space.

To add more disk to the VM using VMWare, follow these steps:

1.  Add a new disk in VMWare. This disk will be formatted in the OS
    after adding it. **Do not** attempt to grow the current VM Disk; add
    a second disk instead.

2.  After adding the second disk, connect to the console or SSH to the
    running LogZilla Server as root.

3.  Identify the name of the new disk added by running:

4.  fdisk -l | grep /dev/[sv]

    Look for a disk without partitions, which is likely the new one.

5.  Format and prepare the new disk:

        disk="/dev/vdb" # replace with your disk name
        printf 'n\n\n\n\n\nt\n8e\np\nw\n' | fdisk -c -u $disk
        partprobe ${disk} # Inform the OS of partition table changes.
        part=1
        pvcreate ${disk}${part}

6.  Extend the volume group to include the new physical volume:

        vg=$(vgdisplay -c | cut -d ':' -f 2 | head -1)
        vgextend ${vg} ${disk}${part}

7.  Extend the logical volume. Identify the LV path for `/` to extend
    using the following command:

        lvpath=$(df --output=source / | tail -1)

    If the logical volume to extend is not mounted as ‘/’, replace the
    above command with criteria that accurately identify the LV.

8.  Extend the logical volume and resize the filesystem:

        lvextend -l+100%FREE ${lvpath}
        resize2fs ${lvpath}

> Note: If your disk is 100% full, the `vgextend` command will not
> complete successfully and space will need to be freed up.

8.  Verify the changes:

        partprobe

After running these commands, you should see a message stating that the
volume has been resized. No further action is needed.

If you do not have VMWare Server or Workstation, you can download the
VMWare player for free from [Downloading and installing VMware Workstation Player](https://knowledge.broadcom.com/external/article?legacyId=2053973).
