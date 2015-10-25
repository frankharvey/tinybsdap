# /etc/rc.d/mac\_filter.sh #

We use the built in MAC ACL commands in FreeBSD `ifconfig` (available from 7.0-REL onward)

```
. /etc/smartap.conf

IFCONFIG=/sbin/ifconfig
IPFW=/sbin/ipfw
SYSCTL=/sbin/sysctl
COUNT=1000

# /sbin/sysctl net.link.ether.ipfw=0
# /sbin/sysctl net.link.bridge.ipfw=0

$IPFW -q flush

while read mac_addr
do
COUNT=`expr $COUNT + 1`
echo $COUNT '->' $mac_addr
# $IPFW add $COUNT allow MAC any $mac_addr via $DEFAULT_WIRELESS_INTERFACE
$IFCONFIG $DEFAULT_WIRELESS_INTERFACE mac:add $mac_addr
done < '/etc/mac_filter.conf'

$IFCONFIG $DEFAULT_WIRELESS_INTERFACE mac:allow

#       -- Lock out everything else
# $IPFW add 9999 deny MAC any any via $DEFAULT_WIRELESS_INTERFACE

```


# /etc/mac\_filter.conf #

Just a list of MAC addresses, one per line, ex.
```
00:0f:2d:bf:51:9d
00:0e:2d:70:32:a1
00:01:2d:B9:19:d9
```