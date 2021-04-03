#!/usr/bin/python3

import time
import Adafruit_ADS1x15
from gpiozero import Button

chn=1 # channel mask! not number
gain=1
devchan=4
adc=None
trigpin=None

def channelnum(cmask,nchannel=None):
    maxc=devchan
    if nchannel:
        maxc=nchannel
    chlst=[]
    nch=0
    for m in range(maxc):
        pm=2**m
        if cmask & pm:
            chlst.append(pm)
            nch+=1
    return nch,chlst

def deviceInit(port='ADS1115',speed=None):
    global adc,trigpin
    
    trigpin=Button(4)
    
    if port is 'ADS1115':
        adc = Adafruit_ADS1x15.ADS1115()
    else
        adc = Adafruit_ADS1x15.ADS1015()
    

def readadc(n):
    global chn,gain
    cl=chanlist(chn)
    vals=[]
    tstart=time.time()
    for i in range(n):
        for ch in cl:
            vals.append(adc.read_adc(ch,gain))
    tend=time.time()
    
    return tend-tstart,cl

def deviceCommand(scmd):
    global chn
    
    nchan,chlist=channelnum(chn)
    
    if scmd.find('msr')==0:
        ndata=int(scmd.split()[1])
        dt,vals=readadc(nchan)
        return dt, vals, chn

    elif scmd.find('trig')==0:
        # WARNING: blocking!
        trigpin.wait_for_press()
        dt,vals=readadc(nchan)
        return dt, vals, chn
        
    elif scmd.find('chn')==0:
        chn=int(scmd.split()[1])
        nchan=channelnum(chn)
        return "channel mask: {} number {}".format(chn,chan)
    else:
        return "ADS1x15 interface"
    
def directMeasure():
    return readadc(1)
    
def clearQueue():
    pass


def deviceClose():
    pass

