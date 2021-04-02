#!/usr/bin/python3

import time
import Adafruit_ADS1x15

chn=1 # channel mask! not number
gain=1
devchan=4
adc=None

def channelnum(cmask=None):
    # returns device maximum channel
    if cmask is None:
        return devchan
    
    # or translate cmask to number of channels
    nchan=0
    for m in (1,2,4,8,16,32):
        if cmask & m:
            nchan+=1

    return nchan

def chanlist(cmask):
     for m in (1,2,4,8,16,32,64,128):
        if cmask & m:
            nchan
   

def deviceInit(port='ADS1115',speed=None):
    global adc
    if port is 'ADS1115':
        adc = Adafruit_ADS1x15.ADS1115()
    else
        adc = Adafruit_ADS1x15.ADS1015()
    

def deviceClose():
    pass

def readadc(n):
    nchan=channelnum(chn)
    vals=[]
    for i in range(n):
        for ch in range(nchan):
            vals.append(adc.read_adc(ch,gain))
    return 
        

def deviceCommand(scmd):
    global chn, gain
    
    nchan=channelnum(chn)
    
    if scmd.find('msr')==0:
        ndata=int(scmd.split()[1])
        
        for i in range(nchan):
            x=adc.read_adc(gain)
        return 1000, createsignal(nchan), chn
    elif scmd.find('trig')==0:
        sleep(5)
        print("trigger simulated")
        return 1000, createsignal(nchan), chn
        
    elif scmd.find('chn')==0:
        chn=int(scmd.split()[1])
        return "dummy channel_mask {}".format(chn)
    else:
        return "dummy serial device"
    
def directMeasure():
    return 1000, [1]*50, chn
    
def clearQueue():
    pass

