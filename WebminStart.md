Copy the directory /usr/share/webmin-1.170 to the target and create the below startup file in `/etc/rc.d/` with `webmin.start`.

### /etc/rc.d/webmin.start ###
```
[root@SecureAP /etc/rc.d]# more webmin.start
#!/bin/sh
/sbin/mount -u -o rw /
echo Starting Webmin server in /usr/share/webmin-1.170
trap '' 1
LANG=
LD_LIBRARY_PATH=/lib:/usr/lib
export LANG LD_LIBRARY_PATH
#PERLIO=:raw
unset PERLIO
export PERLIO
PERLLIB=/usr/share/webmin-1.170
export PERLLIB

/bin/mkdir /var/webmin/

#/share/bash/exec '/usr/share/webmin-1.170/miniserv.pl' /etc/webmin-1.170/miniserv.conf
/usr/share/webmin-1.170/miniserv.pl /etc/webmin-1.170/miniserv.conf
echo $0
/sbin/mount -u -o ro /
```