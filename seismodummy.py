from time import sleep
from random import random
from math import pi,sin,exp

chn=1
devchan=6

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

def deviceInit(port,speed):
    pass

def deviceClose():
    pass
    
def deviceCommand(scmd):
    global chn
    
    nchan,chlist=channelnum(chn)
    
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

