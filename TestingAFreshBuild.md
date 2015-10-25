## Before Adding Ports ##

Create a memory device from the image
```
mdconfig -a -t vnode -f /usr/src/tools/tools/tinybsd/tinybsd.04.bin  -u 0
```

Mount the image onto your host's file-system
```
mount /dev/md0a /mnt
cd /mnt/
```

Check if bash shell is usable
```
cd /mnt/
chroot .
```

The above may throw errors, which can be fixed by copying the missing files from the host system
```
[root@fbsd70 /mnt]# chroot .
/libexec/ld-elf.so.1: Shared object "libintl.so.8" not found, required by "bash"
```
```
[root@fbsd70 /mnt]# find / -name libintl.so.8
/usr/local/lib/libintl.so.8
^C
[root@fbsd70 /mnt]# cp /usr/local/lib/libintl.so.8 lib/
```

There are a couple of more such missing libraries that throw errors
```
[root@fbsd70 /mnt]# chroot .
/libexec/ld-elf.so.1: Shared object "libiconv.so.3" not found, required by "bash"
[root@fbsd70 /mnt]# find / -name libiconv.so.3
/usr/local/lib/libiconv.so.3
^C
[root@fbsd70 /mnt]# cp /usr/local/lib/libiconv.so.3 lib/
```

## After Adding Ports ##