# Introduction #

A FreeBSD 7.0 (REL) host machine is currently being used as a host machine.  This page documents some notes pertaining to it's setup and maintenance.
```
[root@fbsd70 ~]# uname -a
FreeBSD fbsd70.kwest.wapsol.de 7.0-RELEASE FreeBSD 7.0-RELEASE #0: Sun Feb 24 19:59:52 UTC 2008     
root@logan.cse.buffalo.edu:/usr/obj/usr/src/sys/GENERIC  i386
```


# Ports Maintenance #

## Getting Ports ##

We use `cvsup` for maintenance of ports.

The `/usr/share/examples/cvsup/ports-supfile` file should be edited by hand to make sure only an optimal set of ports is downloaded to the Host machine.  This command gets the selected ports in `ports-supfile` and

```
csup -L 2 -h cvsup.de.FreeBSD.org /usr/share/examples/cvsup/ports-supfile
```

[List of CVS servers available can be found here](http://www.freebsd.org/doc/en/books/handbook/cvsup.html#CVSUP-MIRRORS).

## Installing Ports ##
For installing the required ports on a freshly made TinyBSD build, see InstallingPorts

## Updating Ports ##

`pkg_version -v` checks the installed ports against the freshest list of downloaded ports.  Output looks something like this
```
[root@fbsd70 /usr/ports/]# pkg_version -v
aircrack-ng-0.9.1                   <   needs updating (port has 1.0.r1)
bash-3.2.33                         <   needs updating (port has 3.2.39_1)
cvsup-without-gui-16.1h_3           <   needs updating (port has 16.1h_4)
gettext-0.16.1_3                    <   needs updating (port has 0.17_1)
libiconv-1.11_1                     =   up-to-date with port
libtool-1.5.24                      <   needs updating (port has 1.5.26)
lrzsz-0.12.20_1                     =   up-to-date with port
minicom-2.1                         =   up-to-date with port
openssh-portable-4.7.p1_1,1         <   needs updating (port has 5.0.p1,1)
perl-5.8.8_1                        =   up-to-date with port
```

Once the above list of ports to be updated is determined, we use `portupgrade -ai` utility to upgrade the installed ports.  This command will update each port that "needs updating" and asks for confirmation for each of them.

If `portupgrade` is not available on the host, see [4.5.4.2 Upgrading Ports using Portupgrade](http://www.freebsd.org/doc/en/books/handbook/ports-using.html).

# FAQ #

**How to activate SSH access for root on host machine.**
```
Edit the file
etc/ssh/sshd_config
#PermitRootLogin yes
```
Remove the hash on `PermitRootLogin`.