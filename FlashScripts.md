# Introduction #

A few 'primitive' scripts help create flash images fast by grouping together repetitive commands.


# flash.mount #

Used to mount the tinybsdap image (**.bin) on to the file system.  This is useful when you wish to make modifications to the flash image (for ex. store default config files/values).**

As a result of running this script, you will find the filesystem mounted at /mnt if the `mount` was successful.
```
. ./flash.conf

/sbin/mdconfig -a -t vnode -f $IMAGE_DIR/$IMAGE_FILE
/sbin/mount /dev/md0a /mnt
/bin/df -h
```

Output looks like:
```
[root@fbsd70 ~/bin]# ./flash.mount
md0
Filesystem     Size    Used   Avail Capacity  Mounted on
/dev/ad0s1a    272M    138M    112M    55%    /
devfs          1.0K    1.0K      0B   100%    /dev
/dev/ad0s1e    161M     72K    148M     0%    /tmp
/dev/ad0s1f    2.3G    1.6G    495M    77%    /usr
/dev/ad0s1d    210M    117M     77M    60%    /var
/dev/md0a      120M     62M     49M    56%    /mnt
```

# flash.burn #

This scripts burns an image mentioned in `flash.conf` file on to the compact flash device passed in as $1.
```
. ./flash.conf
DEVICE=$1
/usr/bin/time /bin/dd if=$IMAGE_DIR/$IMAGE_FILE of=$DEVICE bs=16k
```

Better run this script from console since it could take some time to write the image on to the flash and a dropped SSH connection might mean a damaged flash.

The output looks something like below, where /dev/da0 is the CF device.  You can usually find this out my running `dmesg`.
```
[root@fbsd70 ~/bin]# ./flash.burn /dev/da0
7968+0 records in
7968+0 records out
130547712 bytes transferred in 160.975639 secs (810978 bytes/sec)
      161.66 real         0.04 user         2.18 sys
```

# flash.unmount #

This simply unmounts the tinybsdap image from `/mnt` and removes the memory device (usually `md0`)

# flash.conf #

This is the config file for the above scripts, where the path and name of the source image (