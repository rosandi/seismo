#!/usr/bin/python3
##################################
#  serial volt-meter-ui
#  User Interface
#  rosandi,2020
#

from tkinter import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
from seismoserial import deviceInit,deviceClose,deviceCommand,directMeasure,clearQueue

filtstrength=0.25

try:
    import scipy.signal as sg
    butta,buttb = sg.butter(4, filtstrength, btype='low', analog=False)
    filtexist=True
except:
    print('scipy signal does not exist: no foltering')
    filtexist=False

comm='/dev/ttyACM0'
speed=115200
running=False
ndata=200

# allocate for 6 channels

choffset=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
baseoffset=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
chgain=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
y=[None, None, None, None, None, None]

for arg in sys.argv:
    if arg.find('com=') == 0:
        comm=arg.replace('com=','')
    if arg.find('speed=') == 0:
        speed=int(arg.replace('speed=',''))
    if arg.find('verbose') == 0:
        verbose=True

def getdevdata(e=None):
    global running, x, y, chlist
    
    if v_buff.get():
        msrtime,vals,cmask = deviceCommand('msr '+str(ndata))
    else:
        msrtime,vals,cmask=directMeasure(ndata)
    
    # channel!
    chlist=[]
    nchan=0
    i=0
    for m in (1,2,4,8,16,32):
        if cmask & m:
            chlist.append(i)
            nchan+=1
        i+=1
    
    ndat=int(len(vals)/nchan)

    # time in uSec -> convert to mSec
    x=np.linspace(0,msrtime/1000.0,ndat)
    
    for i in chlist:
        y[i]=np.zeros(ndat)

    i=0
    for a in range(0,ndat):
        for b in chlist:
            y[b][a]=vals[i]
            i+=1

def updateplot(e=None):

    yplot=[None]*6
    
    mi=1e6
    ma=-1e6
    if filtexist and v_filt.get():
        for i in chlist:
            yplot[i]=sg.filtfilt(butta, buttb, (baseoffset[i]+y[i])*chgain[i]+choffset[i])
            mmi=np.amin(yplot[i])
            mma=np.amax(yplot[i])
            mi = mmi if (mi>mmi) else mi
            ma = mma if (ma<mma) else ma
    else:
        for i in chlist:
            yplot[i]=(baseoffset[i]+y[i])*chgain[i]+choffset[i]
            mmi=np.amin(yplot[i])
            mma=np.amax(yplot[i])
            mi = mmi if (mi>mmi) else mi
            ma = mma if (ma<mma) else ma
    
    ax.set_xlim([0,np.amax(x)])

    ax.cla()
    for i in chlist:
        ax.plot(x,yplot[i],'C'+str(i))
        
    
    if mi<-0.1 or ma>0.1:
        if ma - mi < 0.2:
            ax.set_ylim([mi-0.1,ma+0.1])
        else:
            ax.set_ylim([mi,ma])
    else:
        ax.set_ylim([-.1,.1])
    
    fig.canvas.draw()

def measure(e=None):
    getdevdata()
    updateplot()
    if running:
        mw.after(10,measure)
    

##### CALLBACKS #####
def runmeasure(e=None):
    global running
    
    if not running:
        running=True
        rpbutt.configure(bg='green')
        measure()
    else:
        rpbutt.configure(bg='red')
        running=False

def destroyme(e=None):
    print('program exit')
    mw.destroy()

def dosend(e=None):
    s=deviceCommand(cmdstring.get())
    print(s)
    respstring.set(s)

def offch1(e=None):
    global choffset
    choffset[0]=float(e)
    updateplot()

def offch2(e=None):
    global choffset
    choffset[1]=float(e)
    updateplot()

def offch3(e=None):
    global choffset
    choffset[2]=float(e)
    updateplot()

def offch4(e=None):
    global choffset
    choffset[3]=float(e)
    updateplot()

def offch5(e=None):
    global choffset
    choffset[4]=float(e)
    updateplot()

def offch6(e=None):
    global choffset
    choffset[5]=float(e)
    updateplot()

## gain
def gainch1(e=None):
    global chgain
    chgain[0]=float(e)
    updateplot()

def gainch2(e=None):
    global chgain
    chgain[1]=float(e)
    updateplot()

def gainch3(e=None):
    global chgain
    chgain[2]=float(e)
    updateplot()

def gainch4(e=None):
    global chgain
    chgain[3]=float(e)
    updateplot()

def gainch5(e=None):
    global chgain
    chgain[4]=float(e)
    updateplot()

def gainch6(e=None):
    global chgain
    chgain[5]=float(e)
    updateplot()

def zerooffset(e=None):
    global baseoffset
    for i in chlist:
        av=0
        for a in y[i]:
            av+=a
        baseoffset[i]=-av/len(y[i])
    updateplot()
    
def channelchg(e=None):
    achan=0
    for c in v_ckch:
        achan+=c.get()
    print(deviceCommand("chn "+str(achan)))

def ndatachg(e):
    global ndata
    ndata=int(e)

# to make sense
deviceInit(comm,speed)
print(clearQueue())
print(deviceCommand("dt 1"))
print(deviceCommand("avg 10"))
clearQueue()

##### USER INTERFACE #####

mw=Tk()
mw.title('Voltage Measurement')
plotarea=Frame(mw,padx=10,pady=10)
cmdarea=Frame(mw,padx=10,pady=10)
ctrarea=Frame(mw,padx=10,pady=10)

plotarea.grid(row=0)
cmdarea.grid(row=1)
ctrarea.grid(row=0,column=1,rowspan=2,sticky=(N,S))

##### Tk Variables
v_filt=IntVar()
v_buff=IntVar()
v_ckch=(IntVar(),IntVar(),IntVar(),IntVar(),IntVar(),IntVar())
v_ckch[0].set(1)
v_buff.set(1)

###### PLOT AREA ######

fig = Figure(figsize=(8, 6), dpi=100)
ax = fig.add_subplot(111)
measure()

canvas = FigureCanvasTkAgg(fig, master=plotarea)
canvas.draw()
canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

rpbutt=Button(cmdarea,text='Run/Pause', bg='red', command=runmeasure)
rpbutt.grid(column=0,row=0,sticky=W)

Button(cmdarea,text='Measure', command=measure).grid(column=1,row=0,sticky=W)
Button(cmdarea,text='Quit', command=destroyme).grid(column=2,row=0,sticky=W)

###### COMMAND AREA #######

cmdstring=StringVar(mw)
respstring=StringVar(mw)

cmdbox=Entry(cmdarea,textvariable=cmdstring)
sendbutt=Button(cmdarea,text='send',command=dosend);
cmdbox.grid(column=3,row=0,sticky=E)
sendbutt.grid(column=4,row=0,sticky=E)
reslabel=Label(cmdarea,textvariable=respstring,bg='yellow')
reslabel.grid(column=0,row=1,columnspan=5,pady=5,sticky='ew')
cmdbox.bind('<Return>',dosend)

###### CONTROL AREA ######
offgainctr=Frame(ctrarea)
chanctr=Frame(ctrarea, pady=20)
axisctr=Frame(ctrarea, pady=20)

offgainctr.grid(row=0,column=0)
chanctr.grid(row=1,column=0)
axisctr.grid(row=2,column=0)

Label(offgainctr, text='Offset').grid(column=1,row=0)
Label(offgainctr, text='Gain').grid(column=2,row=0)
Label(offgainctr, text='CH1').grid(column=0,row=1)
Label(offgainctr, text='CH2').grid(column=0,row=2)
Label(offgainctr, text='CH3').grid(column=0,row=3)
Label(offgainctr, text='CH4').grid(column=0,row=4)
Label(offgainctr, text='CH5').grid(column=0,row=5)
Label(offgainctr, text='CH6').grid(column=0,row=6)

Scale(offgainctr, length=150, from_=-0.225, to=0.225, resolution=0.0005, orient=HORIZONTAL, command=offch1).grid(column=1,row=1)
Scale(offgainctr, length=150, from_=-0.225, to=0.225, resolution=0.0005, orient=HORIZONTAL, command=offch2).grid(column=1,row=2)
Scale(offgainctr, length=150, from_=-0.225, to=0.225, resolution=0.0005, orient=HORIZONTAL, command=offch3).grid(column=1,row=3)
Scale(offgainctr, length=150, from_=-0.225, to=0.225, resolution=0.0005, orient=HORIZONTAL, command=offch4).grid(column=1,row=4)
Scale(offgainctr, length=150, from_=-0.225, to=0.225, resolution=0.0005, orient=HORIZONTAL, command=offch5).grid(column=1,row=5)
Scale(offgainctr, length=150, from_=-0.225, to=0.225, resolution=0.0005, orient=HORIZONTAL, command=offch6).grid(column=1,row=6)


Scale(offgainctr, length=150, from_=1.0, to=10, resolution=0.1, orient=HORIZONTAL, command=gainch1).grid(column=2,row=1)
Scale(offgainctr, length=150, from_=1.0, to=10, resolution=0.1, orient=HORIZONTAL, command=gainch2).grid(column=2,row=2)
Scale(offgainctr, length=150, from_=1.0, to=10, resolution=0.1, orient=HORIZONTAL, command=gainch3).grid(column=2,row=3)
Scale(offgainctr, length=150, from_=1.0, to=10, resolution=0.1, orient=HORIZONTAL, command=gainch4).grid(column=2,row=4)
Scale(offgainctr, length=150, from_=1.0, to=10, resolution=0.1, orient=HORIZONTAL, command=gainch5).grid(column=2,row=5)
Scale(offgainctr, length=150, from_=1.0, to=10, resolution=0.1, orient=HORIZONTAL, command=gainch6).grid(column=2,row=6)

## channel select
lbck=Label(chanctr,text='Channels').grid(column=0,row=0,columnspan=6)
Checkbutton(chanctr,text='CH1',variable=v_ckch[0], onvalue=1, command=channelchg).grid(column=0,row=1)
Checkbutton(chanctr,text='CH2',variable=v_ckch[1], onvalue=2, command=channelchg).grid(column=1,row=1)
Checkbutton(chanctr,text='CH3',variable=v_ckch[2], onvalue=4, command=channelchg).grid(column=2,row=1)
Checkbutton(chanctr,text='CH4',variable=v_ckch[3], onvalue=8, command=channelchg).grid(column=3,row=1)
Checkbutton(chanctr,text='CH5',variable=v_ckch[4], onvalue=16, command=channelchg).grid(column=4,row=1)
Checkbutton(chanctr,text='CH6',variable=v_ckch[5], onvalue=32, command=channelchg).grid(column=5,row=1)

### axis control
Checkbutton(axisctr,text='Signal filter',variable=v_filt).pack(side=LEFT)
Checkbutton(axisctr,text='Buffered',variable=v_buff).pack(side=LEFT)
sc=Scale(axisctr, label='DATA LENGTH', length=100, from_=10, to=200, resolution=10, orient=HORIZONTAL, command=ndatachg)
sc.pack(side=LEFT)
sc.set(ndata)
Button(axisctr,text='Zero Axis', command=zerooffset).pack(side=RIGHT)

###### MAIN PROGRAM ######

mw.resizable(False,False)
mw.mainloop()
deviceClose()
