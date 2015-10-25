
```
Copyright (c) 1979, 1980, 1983, 1986, 1988, 1989, 1991, 1992, 1993, 1994
        The Regents of the University of California. All rights reserved.
FreeBSD is a registered trademark of The FreeBSD Foundation.nitor.
FreeBSD 7.0-RELEASE #0: Tue Mar 25 18:51:50 CET 2008
    root@fbsd70.kwest.wapsol.de:/usr/obj/usr/src/sys/TINYBSD
Timecounter "i8254" frequency 1189164 Hz quality 0
CPU: AMD Enhanced Am486DX4/Am5x86 Write-Back (486-class CPU)
  Origin = "AuthenticAMD"  Id = 0x494  Stepping = 4
  Features=0x1<FPU>
real memory  = 67108864 (64 MB)
avail memory = 56180736 (53 MB)
wlan: mac acl policy registered
ath_hal: 0.9.20.3 (AR5210, AR5211, AR5212, RF5111, RF5112, RF2413, RF5413)
cpu0 on motherboard
sysctl machdep.i8254_freq=1189161 returns 0
Timecounter "ELAN" frequency 8192000 Hz quality 1000
pcib0: <AMD Elan SC520 host to PCI bridge> pcibus 0 on motherboard
pci0: <PCI bus> on pcib0
ath0: <Atheros 5212> mem 0xa0000000-0xa000ffff irq 10 at device 16.0 on pci0
ath0: [ITHREAD]
ath0: using obsoleted if_watchdog interface
ath0: Ethernet address: 00:0b:6b:4d:73:25
ath0: mac 5.9 phy 4.3 radio 3.6
pci0: <bridge, PCI-CardBus> at device 17.0 (no driver attached)
pci0: <bridge, PCI-CardBus> at device 17.1 (no driver attached)
sis0: <NatSemi DP8381[56] 10/100BaseTX> port 0xe100-0xe1ff mem 0xa0012000-0xa0012fff irq 5 at device 18.0 on pci0
sis0: Silicon Revision: DP83815D
miibus0: <MII bus> on sis0
ukphy0: <Generic IEEE 802.3u media interface> PHY 0 on miibus0
ukphy0:  10baseT, 10baseT-FDX, 100baseTX, 100baseTX-FDX, auto
sis0: Ethernet address: 00:00:24:c2:0e:ec
sis0: [ITHREAD]
sis1: <NatSemi DP8381[56] 10/100BaseTX> port 0xe200-0xe2ff mem 0xa0013000-0xa0013fff irq 9 at device 19.0 on pci0
sis1: Silicon Revision: DP83815D
miibus1: <MII bus> on sis1
ukphy1: <Generic IEEE 802.3u media interface> PHY 0 on miibus1
ukphy1:  10baseT, 10baseT-FDX, 100baseTX, 100baseTX-FDX, auto
sis1: Ethernet address: 00:00:24:c2:0e:ed
sis1: [ITHREAD]
isa0: <ISA bus> on motherboard
pmtimer0 on isa0
orm0: <ISA Option ROM> at iomem 0xc8000-0xd1fff pnpid ORM0000 on isa0
ata0 at port 0x1f0-0x1f7,0x3f6 irq 14 on isa0
ata0: [ITHREAD]
ata1 at port 0x170-0x177,0x376 irq 15 on isa0
ata1: [ITHREAD]
sio0 at port 0x3f8-0x3ff irq 4 flags 0x10 on isa0
sio0: type 16550A, console
sio0: [FILTER]
sio1 at port 0x2f8-0x2ff irq 3 on isa0
sio1: type 16550A
sio1: [FILTER]
Timecounters tick every 1.000 msec
Elan-mmcr driver: MMCR at 0xc5ad7000. PPS support.
Elan-mmcr Soekris net45xx comBIOS ver. 1.23a 20040211 Copyright (C) 2000-2003
ipfw2 initialized, divert enabled, rule-based forwarding disabled, default to accept, logging disabled
ad0: 124MB <ZOOMCF 128MB CF040520> at ata0-master PIO4
Trying to mount root from ufs:/dev/ad0a
Loading configuration files.
No suitable dump device was found.
Entropy harvesting: interrupts ethernet point_to_point kickstart.
Starting file system checks:
/dev/ad0a: FILE SYSTEM CLEAN; SKIPPING CHECKS
/dev/ad0a: clean, 28883 free (43 frags, 3605 blocks, 0.1% fragmentation)
Setting hostuuid: c572f921-35d1-11d2-93ae-5f5a0edd7f09.
Setting hostid: 0x861ae48e.
Mounting local file systems:.
Setting hostname: SecureAP.kwest.wapsol.de.
lo0: flags=8049<UP,LOOPBACK,RUNNING,MULTICAST> metric 0 mtu 16384
        inet 127.0.0.1 netmask 0xff000000
route: writing to routing socket: Network is unreachable
add net default: gateway 192.168.3.254: Network is unreachable
Additional routing options:.
/etc/rc: WARNING: run_rc_command: cannot run /sbin/devd
Additional IP options:.
Mounting NFS file systems:.
ELF ldconfig path: /lib /usr/lib /usr/lib/compat /usr/local/lib
a.out ldconfig path: /usr/lib/aout /usr/lib/compat/aout
Creating and/or trimming log files:.
Starting syslogd.
/etc/rc: WARNING: Dump device does not exist.  Savecore not run.
Initial i386 initialization:.
Additional ABI support:.
Clearing /tmp (X related).
Starting Webmin server in /usr/share/webmin-1.170
/etc/rc.d/webmin.start: /share/bash/exec: Permission denied
/etc/rc
Starting local daemons:.
Updating motd ... /etc/motd is not writable, update failed.
Mounting late file systems:.
Starting sshd.
Starting cron.
Local package initialization:.
bridge0: Ethernet address: 9e:4d:64:6f:b6:77
bridge0
sis0: Applying short cable fix (reg=f4)
Starting background file system checks in 60 seconds.

Tue Apr  1 15:19:07 CEST 2008
Apr@ApBAACAAA
```