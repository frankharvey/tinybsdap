# Introduction #

The basic TinyBSD build is quite bare-boned, containing a minimalistic 802.11 capable system.  TinyBSD\_AP incorporates some additional tools, some of them nice-to-haves and some of them necessary features.  This page documents process of building such features.

### bash ###

```
cd /usr/ports/shells/bash
make clean
make install PREFIX=/mnt/ FORCE_PKG_REGISTER=yes
```

This will install the `bash` port on the image as seen below
```
[root@fbsd70 /mnt]# find . -name bash
./bin/bash
./share/doc/bash
./share/bash
```

### dhcp Server ###

Port for `isc-dhcp3-server` is available at `/usr/ports/net/isc-dhcp3-server`
```
make clean
make install PREFIX=/mnt/ FORCE_PKG_REGISTER=yes
```

After successful compilation and installation on the target image, it looks like
```
[root@fbsd70 /mnt]# find . -name *dhcp*
./etc/rc.d/isc-dhcpd
./etc/dhcpd.conf.sample
./sbin/dhcpd
./usr/local/etc/rc.d/isc-dhcpd
./usr/local/etc/dhcpd.conf.sample
./usr/local/sbin/dhcpd
./man/man5/dhcp-eval.5.gz
./man/man5/dhcpd.conf.5.gz
./man/man5/dhcpd.leases.5.gz
./man/man5/dhcp-options.5.gz
./man/man8/dhcpd.8.gz
./share/doc/isc-dhcp3-server
```

### Perl ###