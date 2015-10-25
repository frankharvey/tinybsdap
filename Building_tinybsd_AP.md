# Building #
Change this kernel configuration in wireless/TINYBSD, so that if\_sis.ko module gets compiled, assuming `wireless` is the configuration being used.
```
device          miibus          # MII bus support
device          sis             # Silicon Integrated Systems SiS 900/SiS 7016
```

By default, all the fun is going on in `/usr/src/tools/tools/tinybsd/`
```
cd /usr/src/tools/tools/tinybsd/
time ./tinybsd sectors=254960 heads=64 spt=32 conf=wireless image=tinybsd.bin batch new
```

The sectors, heads and sectors per track information is available from `diskinfo -v`.