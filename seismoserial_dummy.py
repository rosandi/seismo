from time import sleep
from random import random
from math import pi,sin,exp

chn=1

def createsignal(nch):
    nd=500
    f=20.0
    v=[]
    theta=[nd*random() for xx in range(nch)]
    
    for i in range(nd):
        for th in theta:
            a=2.0*pi*f*i/nd
            v.append(sin(a)*exp(-(0.001*(i-th)**2)))
    return v

def channelnum(cmask):
    nchan=0
    for m in (1,2,4,8,16,32):
        if cmask & m:
            nchan+=1
    return nchan

def deviceInit(port,speed):
    pass

def deviceClose():
    pass
    
def deviceCommand(scmd):
    global chn
    
    nchan=channelnum(chn)
    
    if scmd.find('msr')==0:
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

