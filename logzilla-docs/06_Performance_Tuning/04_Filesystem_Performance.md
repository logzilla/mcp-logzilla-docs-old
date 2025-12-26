<!-- @@@title:Filesystem Performance@@@ -->

This section covers general recommendations for server performance.

Having a well-tuned server will greatly impact system and logging performance.

Disk Format
---
OS Disks should be set up using Logical Volumes (LVM) and care should be taken to ensure that the sectors are properly aligned.

>Disk performance is possibly the single most important item for indexing and searching at scale

# Format the disk using parted

* In this example, we have set the disk to `/dev/sda`, you can view available disks using `fdisk -l | grep "/dev/[v|s|nv|mapp]"`

      disk=/dev/sda
      parted -a optimal ${disk}
      mklabel gpt
      unit s
      mkpart primary 2048s 100%
      align-check opt 1
      set 1 lvm
      p

* Next, create the physical volume in LVM

      pvcreate -M 2 --dataalignment 4k ${disk}
      
* Check alignment (the first PE should be `1.00m`)

      pvs -o +pe_start

* Create the Volume Group (this may already be on your server, so possibly optional):

      volumeName="vg0"
      partition=1 # this is the partition you created above with parted, be sure it matches!
      vgcreate ${volumeName} ${disk}${partition}
      lvcreate -l 100%FREE ${volumeName}

* Create a filesystem on the new LVM volume

      rootVol=$(lvdisplay | grep Path | grep root | awk '{print $3}')
      # THE NEXT COMMAND WILL DESTROY DATA, BE SURE IT IS WHAT YOU WANT!
      mkfs.ext4 ${rootVol}

* Create an fstab entry
>Replace ${rootVol} below with the actual volume name for your server.

      /dev/mapper/${rootVol}/               ext4    errors=remount-ro 0       1

During a new OS install, all of this is done for you when choosing the automatic option. However, be sure to select LVM as the type. LVM also allows you to add more disk and resize the root volume later without the need to reboot.

Swap
---
* Disable it...always!

>Swap was originally used to compensate for lack of Ram. Today's servers should have ample ram and, if not, will suffer severe performance degradation should the OS run low and need to swap to disk.

If you find that your server is low on memory and *must* add swap, then be sure to set the swappiness, but also be sure to consider this a temporary fix while you place an order for more RAM from your vendor.

We can see the current swappiness value by typing:

      cat /proc/sys/vm/swappiness
      60
      
For a Desktop, a swappiness setting of 60 is not a bad value. For a server, we'd want to move it closer to 0.

We can set the swappiness to a different value by using the sysctl command.

For instance, to set the swappiness to 10, type:

      sysctl vm.swappiness=10
      vm.swappiness = 10

This setting will persist until the next reboot. You can set this value automatically at restart by adding the line to `/etc/sysctl.conf`:

At the bottom, add `vm.swappiness=10`, then save and close the file when you are finished.

Next, type `sysctl -p` to have the OS re-read the new settings.

Another related value that may be useful is the `vfs_cache_pressure`. This setting configures how much the system will choose to cache inode and dentry information over other data.

This is access data about the filesystem which is generally very costly to look up and is frequently requested. So it's an excellent thing for your system to cache. You can see the current value by querying the proc filesystem again:

      cat /proc/sys/vm/vfs_cache_pressure
      100
      
As it is currently configured, our system removes inode information from the cache too quickly. We can set this to a more conservative setting such as `50` by typing:

      sysctl vm.vfs_cache_pressure=50
      vm.vfs_cache_pressure = 50
      
Again, this is only valid for our current session. We can change it by adding it to the sysctl.conf  file.

      vi /etc/sysctl.conf
      
At the bottom, add the line that specifies your new value:

      vm.vfs_cache_pressure = 50
      
Save and close the file when you are finished and type `sysctl -p` so that the changes get read.
