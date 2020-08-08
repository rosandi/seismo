from time import sleep

chn=1

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
        a=[0]*10*nchan+[-0.05]*10*nchan
        b=[0]*10*nchan+[0.05]*10*nchan
        return 1000, a+b, chn
    elif scmd.find('trig')==0:
        sleep(5)
        print("trigger simulated")
        a=[0]*10*nchan+[-0.05]*10*nchan
        b=[0]*10*nchan+[0.05]*10*nchan
        return 1000, a+b, chn
        
    elif scmd.find('chn')==0:
        chn=int(scmd.split()[1])
        return "dummy channel_mask {}".format(chn)
    else:
        return "dummy serial device"
    
def directMeasure():
    return 1000, [1]*50, chn
    
def clearQueue():
    pass

