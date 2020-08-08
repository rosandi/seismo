# SERIAL INTERFACE MEASUREMENT

This is a serial measurement project to access microcontroller 
measurement interface. bla-bla...

## Communication Specification

### Serial commands from uC

Format: '$command parameter;'
sent as byte array in python.

Accepted commands:

'$msr n;'
measure n data

'$dt n;
delay time in millisecond (may be not precise)

'$str n;'
stream the data nonstop n the block number. see $head

'$avg n;'
set the number of data to average every measurement

'$ping n;'
ping. n is arbitrary

'$head 0/1;'
set header on/off on measure and streaming
