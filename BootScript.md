# /etc/rc.d/init.tinybsdap.sh #

This script sets up the device based on system variables defined in `/etc/smartap.conf` and `/etc/wpa.conf`

```
[root@SecureAP ~]# more /etc/rc.d/init.tinybsdap.sh
. /etc/smartap.conf

MOUNT=/sbin/mount
IFCONFIG=/sbin/ifconfig
SYSCTL=/sbin/sysctl
HOSTAPD=/usr/sbin/hostapd
ROUTE=/sbin/route

echo "Initializing tinybsd_ap network netup..."

echo "  Setup sis0/ethernet interface"
$IFCONFIG $DEFAULT_ETH_INTERFACE $DEFAULT_ETH_IPADDR netmask $DEFAULT_ETH_NETMASK

echo "  Setup 802.11 interface (Layer-2)"
$IFCONFIG $DEFAULT_WIRELESS_INTERFACE ssid $DEFAULT_WIRELESS_SSID mediaopt $DEFAULT_WIRELESS_MEDIAOPT mode $DEFAULT_WIRELESS_MODE up
echo "  Setup 802.11 interface (Layer-3)"
$IFCONFIG $DEFAULT_WIRELESS_INTERFACE $DEFAULT_WIRELESS_IPADDR netmask $DEFAULT_WIRELESS_NETMASK

echo "  Bridge sis0 and "$DEFAULT_WIRELESS_INTERFACE"  (using ifconfig bridge)"
$IFCONFIG bridge create
$IFCONFIG bridge0 addm $DEFAULT_WIRELESS_INTERFACE addm $DEFAULT_ETH_INTERFACE up
$IFCONFIG $DEFAULT_WIRELESS_INTERFACE up
$IFCONFIG $DEFAULT_ETH_INTERFACE up
$IFCONFIG bridge0 inet $DEFAULT_ETH_IPADDR broadcast $DEFAULT_ETH_BROADCAST up

echo "  Setting up default route"
$ROUTE add default $DEFAULT_ETH_DEFGTWY

#       -- Setup hostapd if set in smartap.conf
if [ $WPA2_ACTIVATE -eq 1 ];
then
        echo "  Setting up WPA/WPA2"
        $HOSTAPD -B /etc/madwifi.conf

elif [ -n "$DEFAULT_WIRELESS_WEPKEY" ];
then
        echo "  Setting WEP Key"
        $IFCONFIG $DEFAULT_WIRELESS_INTERFACE wepmode on weptxkey 1 wepkey $DEFAULT_WIRELESS_WEPKEY
fi


#       -- If all goes well till here, see if it is necessary to setup
#          this AP as DHCP server for the network
if [ $START_DHCP -eq "1" ];
then
        echo "  Setting up DHCP Server on " $DEV_NAME
        touch /var/db/dhcpd.leases
        /usr/local/sbin/dhcpd;
fi
```