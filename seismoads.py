#!/usr/bin/python3

import time
import Adafruit_ADS1x15
from gpiozero import Button

chn=15 # channel mask! not number
gain=16
devchan=4
adc=None
trigpin=None

def channelnum(cmask,nchannel=None):
    maxc=devchan
    if nchannel:
        maxc=nchannel
    chlst=[] # array index list! not mask!
    nch=0
    li=0 # list index
    for m in range(maxc):
        pm=2**m
        if cmask & pm:
            chlst.append(li)
            nch+=1
        li+=1

    return nch,chlst

def deviceInit(port='ADS1115',speed=None):
    global adc,trigpin
    
    trigpin=Button(4)
    
    if port is 'ADS1115':
        adc = Adafruit_ADS1x15.ADS1115()
    else:
        adc = Adafruit_ADS1x15.ADS1015()
    

def readadc(n):
    global chn,gain
    _,cl=channelnum(chn)
    vals=[]
    tstart=time.time()
    for i in range(n):
        for ch in cl:
            vals.append(adc.read_adc(ch,gain=gain))
            time.sleep(0.01)
            
    tend=time.time()
    
    return tend-tstart,vals

def deviceCommand(scmd):
    global chn
    
    nchan,chlist=channelnum(chn)
    
    if scmd.find('msr')==0:
        ndata=int(scmd.split()[1])
        dt,vals=readadc(ndata)
        #print('DEBUG:',vals)
        return dt, vals, chn

    elif scmd.find('trig')==0:
        # WARNING: blocking!
        trigpin.wait_for_press()
        dt,vals=readadc(ndata)
        return dt, vals, chn
        
    elif scmd.find('chn')==0:
        chn=int(scmd.split()[1])
        nchan,_=channelnum(chn)
        return "channel mask: {} number {}".format(chn,nchan)
    else:
        return "ADS1x15 interface"
    
def directMeasure(n=1):
    return readadc(n)
    
def clearQueue():
    pass


def deviceClose():
    pass

