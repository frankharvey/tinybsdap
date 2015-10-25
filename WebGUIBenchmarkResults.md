## Introduction ##

This page documents benchmark testing results for the Webmin based web-GUI included in TinyBSD\_AP.  The web server is Perl based MiniServ.  Goal of performing this benchmarking is:

  * See if MiniServ crashes under high load, or behaves abnormally in any other way
  * Compare with standard response times, as Webmin is resource hungry and there's plenty of room to speed up the webGUI.




## TinyBSD\_AP 0.9 ##

### Sample Test: 1 request, no concurrency ###
```
ashant@feather:~$ ab http://192.168.3.150:900/
This is ApacheBench, Version 2.0.41-dev <$Revision: 1.141 $> apache-2.0
Copyright (c) 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Copyright (c) 1998-2002 The Apache Software Foundation, http://www.apache.org/

Benchmarking 192.168.3.150 (be patient).....done


Server Software:        MiniServ/0.01
Server Hostname:        192.168.3.150
Server Port:            900

Document Path:          /
Document Length:        2196 bytes

Concurrency Level:      1
Time taken for tests:   6.272732 seconds
Complete requests:      1
Failed requests:        0
Write errors:           0
Total transferred:      2514 bytes
HTML transferred:       2196 bytes
Requests per second:    0.16 [#/sec] (mean)
Time per request:       6272.732 [ms] (mean)
Time per request:       6272.732 [ms] (mean, across all concurrent requests)
Transfer rate:          0.32 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        3    3   0.0      3       3
Processing:  6269 6269   0.0   6269    6269
Waiting:     5399 5399   0.0   5399    5399
Total:       6272 6272   0.0   6272    6272

```