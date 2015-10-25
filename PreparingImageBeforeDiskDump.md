  1. [Install Ports](http://code.google.com/p/tinybsdap/wiki/InstallingPorts)
  1. create /etc/smartap.conf with default device configuration
  1. create /etc/wpa.conf
  1. create /etc/rc.d/init.tinybsdap.sh
  1. create /etc/rc.d/webmin.start
  1. check /etc/fstab.  It should be as below
```
/dev/ad0a / ufs rw 1 1
```
  1. create /etc/rc.d/mac\_filter.sh (for MAC based ACL)
  1. Fill in all MAC addresses to be filtered into `/etc/mac_filter.conf`, or just `touch` this file


---

Define a **service port** on one of the spare ethernet interfaces, so that if the network config is hosed, we can still access the box on this service port.  For Soekris net4511 and net4521, the service port is sis1.  Set the IP of this to 192.168.168.168 (or anything you prefer, and not used for other network interfaces on the device).

Add to `/etc/rc.conf`
```
# -- Service Port
ifconfig_sis1="inet 192.168.168.168 netmask 255.255.255.0"
```

---

Change the **default shell** to bash using `chsh`
```
[root@fbsd70 /mnt]# chroot .
[root@fbsd70 /]# chsh
#Changing user information for root.
Login: root
Password: $1$YGxyXoEh$p2f0dMeWo4brLSUfl0Ue21
Uid [#]: 0
Gid [# or name]: 0
Change [month day year]:
Expire [month day year]:
Class:
Home directory: /root
Shell: /bin/bash
Full Name: Charlie &
Office Location:
Office Phone:
Home Phone:
Other information:

~
~
/etc/pw.V7cnJJ: 15 lines, 310 characters.
chsh: warning, unknown root shell
pwd_mkdb: warning, unknown root shell
chsh: user information updated
```

### Activate the sis0 Interface ###
sis0 ethernet interface has to be activated in `/boot/default/loader.conf`
```
if_sis_load="NO"                # Silicon Integrated Systems SiS 900/7016
```

### Install WebGUI ###
Files have to be copied into 3 locations on the target for properly functioning Webmin installation
  * /etc/webmin-1.170/
  * /etc/rc.d/webmin.start
  * /usr/share/webmin-1.170

Perl on TinyBSD is located at /usr/local/bin/perl, but Webmin looks for it at /usr/bin/perl.  symlink those.

### remount scripts ###

Create `/usr/bin/remountro` and `/usr/bin/remountrw` scripts using
```
 # mount -u -o r{w,o} /
```