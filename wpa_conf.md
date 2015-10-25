### Sample wpa.conf ###
```
[root@SecureAP ~]# more /etc/madwifi.conf
# Thu Apr  3 17:14:53 2008

interface=ath0
driver=bsd
logger_syslog=-1
logger_syslog_level=2
logger_stdout=-1
logger_stdout_level=2
debug=1
dump_file=/tmp/hostapd.dump
ctrl_interface=/var/run/hostapd
ctrl_interface_group=0
ssid=fbsdap
macaddr_acl=0
auth_algs=1
own_ip_addr=192.168.3.150
auth_server_addr=0.0.0.0
auth_server_port=0
acct_server_addr=0.0.0.0
acct_server_port=1813
auth_server_shared_secret=dummy
acct_server_shared_secret=none
ieee8021x=1
wpa=1
wpa_passphrase=defaultnone1
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP CCMP
```