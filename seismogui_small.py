#!/usr/bin/python3
##################################
#  serial volt-meter-ui
#  User Interface
#  rosandi,2020
#
# -- Running command options --
# -> to run without devices (debugging purpose): comm=null
# -> run on desktop: desktop or size=WIDTHxHEIGHT
#

WSCREEN=320
HSCREEN=240
WOFFS=0
HOFFS=0
WCVS=290      # canvas width
HCVS=220      # canvas height

import sys
from tkinter import Tk, IntVar, StringVar, Canvas, ALL, Text, END, LEFT, W, INSERT,font
from tkinter.ttk import *
from time import sleep


############## PROGRESS WINDOW #############
welcome=Tk()
welcome.geometry('{}x{}+0+0'.format(WSCREEN,HSCREEN))
welcvs=Canvas(welcome,width=320,height=280)
welcvs.pack()
welcvs.create_text(160,75,text='Instrumentasi Geofisika',font=('Helvetica',20))
welcvs.create_text(160,100,text='Universitas Padjadjaran',font=('Helvetica',20))
welcvs.create_text(160,150,text='... initialization ... wait ..', font=('Helvetica',14))

welcvs.create_rectangle(20,200,300,220,outline='blue')
progress=welcvs.create_rectangle(20,200,50,220,fill='blue')
welcome.update()
###########################################

comm='/dev/ttyACM0'
speed=115200

################### COMMAND LINE ARGUMENTS ############################
for arg in sys.argv:
    if arg.find('comm=') == 0:
        comm=arg.replace('comm=','')
    if arg.find('speed=') == 0:
        speed=int(arg.replace('speed=',''))
    if arg.find('size=') == 0:
        WSCREEN=int(arg.replace('size=','').split('x')[0])
        HSCREEN=int(arg.replace('size=','').split('x')[1])
        WCVS=int(0.9*WSCREEN)
        HCVS=int(0.9*HSCREEN)
    if arg.find('offset=') == 0:
        WOFFS=int(arg.replace('offset=','').replace('+',' ').split()[0])
        HOFFS=int(arg.replace('offset=','').replace('+',' ').split()[1])
    if arg.find('desktop') == 0:
        WSCREEN=800
        HSCREEN=600
        WCVS=int(0.9*WSCREEN)
        HCVS=int(0.9*HSCREEN)
##########################################################################

import numpy as np

welcvs.delete(progress)
progress=welcvs.create_rectangle(20,200,100,220,fill='blue')
welcome.update()


if comm=='null':
    from seismoserial_dummy import deviceInit,deviceClose,deviceCommand,directMeasure,clearQueue
else:
    from seismoserial import deviceInit,deviceClose,deviceCommand,directMeasure,clearQueue
filtstrength=0.25

try:
    import scipy.signal as sg
    butta,buttb = sg.butter(4, filtstrength, btype='low', analog=False)
    filtexist=True
except:
    print('scipy signal does not exist: no foltering')
    filtexist=False

welcvs.delete(progress)
progress=welcvs.create_rectangle(20,200,150,220,fill='blue')
welcome.update()

running=False
ndata=50
minofs=-0.2
maxofs=0.2
mingain=0
maxgain=5
chandirty=True
limext=0.0

# allocate for 6 channels
chlist=[1]
choffset=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
baseoffset=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
chgain=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
chcolor=['SteelBlue3','chartreuse2','firebrick3','DarkOrchid1','dark green','maroon']
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
    # x=np.linspace(0,msrtime/1000.0,ndat)
    x=msrtime
    
    for i in chlist:
        y[i]=np.zeros(ndat)

    i=0
    for a in range(0,ndat):
        for b in chlist:
            y[b][a]=vals[i]
            i+=1


def trigdevdata(e=None):
    global running, x, y, chlist
    
    if v_buff.get():
        msrtime,vals,cmask = deviceCommand('trig '+str(ndata))
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
    # x=np.linspace(0,msrtime/1000.0,ndat)
    x=msrtime
    
    for i in chlist:
        y[i]=np.zeros(ndat)

    i=0
    for a in range(0,ndat):
        for b in chlist:
            y[b][a]=vals[i]
            i+=1

def plot(data,xlim=(0,100),ylim=(-0.55,0.55),color='black'):
    scy=HCVS/(ylim[1]-ylim[0])
    mid=scy*(ylim[1]-ylim[0])/2
    scx=WCVS/(xlim[1]-xlim[0])
    x=np.linspace(0,WCVS,len(data))
    line=[]
    for a,b in zip(x,data):
        line.append(a)
        line.append(HCVS-(b-ylim[0])*scy)
        
    cvs.create_line(line, fill=color, width=2)

def updateplot(e=None):

    yplot=[None]*6
    
    mi=1e6
    ma=-1e6
    
    if filtexist and v_filt.get():
        for i in chlist:
            yplot[i]=sg.filtfilt(butta, buttb, (baseoffset[i]+y[i])*chgain[i]+choffset[i])
            mmi=min(yplot[i])
            mma=max(yplot[i])
            mi = mmi if (mi>mmi) else mi
            ma = mma if (ma<mma) else ma
    else:
        for i in chlist:
            yplot[i]=(baseoffset[i]+y[i])*chgain[i]+choffset[i]
            mmi=np.amin(yplot[i])
            mma=np.amax(yplot[i])
            mi = mmi if (mi>mmi) else mi
            ma = mma if (ma<mma) else ma
    
    ylim=(-.1,.1)
    if mi<-0.1 or ma>0.1:
        if ma - mi < 0.2:
            ylim=(mi-0.1,ma+0.1)
        else:
            ylim=(mi,ma)
    
    ylim=(ylim[0]-limext,ylim[1]+limext)
    
    cvs.delete(ALL)
    for i in chlist:
        plot(yplot[i],xlim=(0,x),ylim=ylim,color=chcolor[i])

##### CALLBACKS #####

def zerooffset(e=None):
    global baseoffset
    for i in chlist:
        av=0
        for a in y[i]:
            av+=a
        baseoffset[i]=-av/len(y[i])
    updateplot()

def destroyme(e=None):
    print('program exit')
    mw.destroy()

def offch1(e=None):
    global choffset
    choffset[0]=minofs+float(e)*(maxofs-minofs)/100.0
    v_og1.config(text='%0.1f/%0.1f'%(choffset[0],chgain[0]))
    updateplot()

def offch2(e=None):
    global choffset
    choffset[1]=minofs+float(e)*(maxofs-minofs)/100.0
    v_og2.config(text='%0.1f/%0.1f'%(choffset[1],chgain[1]))
    updateplot()

def offch3(e=None):
    global choffset
    choffset[2]=minofs+float(e)*(maxofs-minofs)/100.0
    v_og3.config(text='%0.1f/%0.1f'%(choffset[2],chgain[2]))
    updateplot()

def offch4(e=None):
    global choffset
    choffset[3]=minofs+float(e)*(maxofs-minofs)/100.0
    v_og4.config(text='%0.1f/%0.1f'%(choffset[3],chgain[3]))
    updateplot()

def offch5(e=None):
    global choffset
    choffset[4]=minofs+float(e)*(maxofs-minofs)/100.0
    v_og5.config(text='%0.1f/%0.1f'%(choffset[4],chgain[4]))
    updateplot()

def offch6(e=None):
    global choffset
    choffset[5]=minofs+float(e)*(maxofs-minofs)/100.0
    v_og6.config(text='%0.1f/%0.1f'%(choffset[5],chgain[5]))
    updateplot()

## gain
def gainch1(e=None):
    global chgain
    chgain[0]=mingain+float(e)*(maxgain-mingain)/100.0
    v_og1.config(text='%0.1f/%0.1f'%(choffset[0],chgain[0]))
    updateplot()

def gainch2(e=None):
    global chgain
    chgain[1]=mingain+float(e)*(maxgain-mingain)/100.0
    v_og2.config(text='%0.1f/%0.1f'%(choffset[1],chgain[1]))
    updateplot()

def gainch3(e=None):
    global chgain
    chgain[2]=mingain+float(e)*(maxgain-mingain)/100.0
    v_og3.config(text='%0.1f/%0.1f'%(choffset[2],chgain[2]))
    updateplot()

def gainch4(e=None):
    global chgain
    chgain[3]=mingain+float(e)*(maxgain-mingain)/100.0
    v_og4.config(text='%0.1f/%0.1f'%(choffset[3],chgain[3]))
    updateplot()

def gainch5(e=None):
    global chgain
    chgain[4]=mingain+float(e)*(maxgain-mingain)/100.0
    v_og5.config(text='%0.1f/%0.1f'%(choffset[4],chgain[4]))
    updateplot()

def gainch6(e=None):
    global chgain
    chgain[5]=mingain+float(e)*(maxgain-mingain)/100.0
    v_og6.config(text='%0.1f/%0.1f'%(choffset[5],chgain[5]))
    updateplot()
    
def channelchg(e=None):
    global chandirty
    achan=0
    for c in v_ckch:
        achan+=c.get()
        
    chandirty=True
    print(deviceCommand("chn "+str(achan)))
        
def distplot(e=None):
    # FIXME! all the scalles must be set to 50%
    nc=len(chlist)
    if nc<=1:
        return
    
    h=0.2*nc/2
    oi=0
    for c in chlist:
        choffset[c]=oi*0.1+0.1-h
        oi+=1
        
    updateplot()


def initialize():
    deviceInit(comm,speed)
    print("initialization....")
    print(deviceCommand("dt 1"))
    print(deviceCommand("avg 10"))
    print(deviceCommand("chn 1"))


### initialization
welcvs.delete(progress)
progress=welcvs.create_rectangle(20,200,250,220,fill='blue')
welcome.update()
initialize()
welcvs.delete(progress)
progress=welcvs.create_rectangle(20,200,300,220,fill='blue')
welcome.update()
sleep(0.5)
welcome.destroy()


##### USER INTERFACE #####

mw=Tk()
mw.title('Voltage Measurement')

sty=Style()
sty.map('r.TButton',background=[('active','red'),('!disabled','red4')])
sty.map('p.TButton',background=[('active','green'),('!disabled','dark green')])
sty.map('ok.TButton',background=[('active','green'),('!disabled','dark green')])
sty.map('off.TButton',background=[('active','red'),('!disabled','red4')])
sty.configure('res.TLabel',background='white')

mainTab=Notebook(mw)

plotarea=Frame(mainTab)
cmdarea=Frame(mainTab)
setarea=Frame(mainTab)
ctrarea=Frame(mainTab)

mainTab.add(plotarea, text='plot')
mainTab.add(ctrarea, text='control')
mainTab.add(setarea, text='settings')
mainTab.add(cmdarea, text='command')
mainTab.pack(expand=1, fill="both")

##### Tk Variables
v_filt=IntVar()
v_buff=IntVar()
v_ckch=(IntVar(),IntVar(),IntVar(),IntVar(),IntVar(),IntVar())
v_ckch[0].set(1)
v_buff.set(1)

########### PLOT AREA ######

def measure(e=None):
    global chandirty
    
    getdevdata()
    updateplot()

    if chandirty:
        zerooffset()
        chandirty=False

    if running:
        mw.after(10,measure)
        
def trigger(e=None):
    global chandirty
    
    cvs.delete(ALL)
    cvs.create_text(140,100,text='Waiting: TRIGGER signal..', font=('Helvetica',16))
    mw.update()
    
    trigdevdata()
    updateplot()

    if chandirty:
        zerooffset()
        chandirty=False

    if running:
        mw.after(10,measure)

def runmeasure(e=None):
    global running
    
    if not running:
        running=True
        rpbutt.configure(style='p.TButton')
        measure()
    else:
        rpbutt.configure(style='r.TButton')
        running=False

cvs=Canvas(plotarea, width=WCVS, height=HCVS, bg='white')
cvs.grid(row=0,column=0,rowspan=3)

wbtn=WSCREEN-WCVS
rpbutt=Button(plotarea,text='R', style='r.TButton', command=runmeasure)
rpbutt.place(x=WCVS,y=0,height=50,width=wbtn)
Button(plotarea,text='M', command=measure).place(x=WCVS,y=54,height=50,width=wbtn)
Button(plotarea,text='T', command=trigger).place(x=WCVS,y=107,height=50,width=wbtn)
Button(plotarea,text='D', command=distplot).place(x=WCVS,y=160,height=50,width=wbtn)

########### CONTROL AREA ######

offgainctr=Frame(ctrarea)
chanctr=Frame(ctrarea)
axisctr=Frame(ctrarea)

offgainctr.grid(row=0,column=0,sticky='w')
chanctr.grid(row=1,column=0,sticky='w')
axisctr.grid(row=2,column=0,sticky='w')

Label(offgainctr, text='Offset').grid(column=1,row=0)
Label(offgainctr, text='Gain').grid(column=2,row=0)
Label(offgainctr, text='CH1 ').grid(column=0,row=1)
Label(offgainctr, text='CH2 ').grid(column=0,row=2)
Label(offgainctr, text='CH3 ').grid(column=0,row=3)
Label(offgainctr, text='CH4 ').grid(column=0,row=4)
Label(offgainctr, text='CH5 ').grid(column=0,row=5)
Label(offgainctr, text='CH6 ').grid(column=0,row=6)

v_og1=Label(offgainctr, text='0.0/1.0',width=8)
v_og2=Label(offgainctr, text='0.0/1.0',width=8)
v_og3=Label(offgainctr, text='0.0/1.0',width=8)
v_og4=Label(offgainctr, text='0.0/1.0',width=8)
v_og5=Label(offgainctr, text='0.0/1.0',width=8)
v_og6=Label(offgainctr, text='0.0/1.0',width=8)

Scale(offgainctr, length=100, from_=0, to=100, value=50, command=offch1).grid(column=1,row=1,padx=2)
Scale(offgainctr, length=100, from_=0, to=100, value=50, command=offch2).grid(column=1,row=2,padx=2)
Scale(offgainctr, length=100, from_=0, to=100, value=50, command=offch3).grid(column=1,row=3,padx=2)
Scale(offgainctr, length=100, from_=0, to=100, value=50, command=offch4).grid(column=1,row=4,padx=2)
Scale(offgainctr, length=100, from_=0, to=100, value=50, command=offch5).grid(column=1,row=5,padx=2)
Scale(offgainctr, length=100, from_=0, to=100, value=50, command=offch6).grid(column=1,row=6,padx=2)

Scale(offgainctr, length=100, from_=0, to=100, value=20, command=gainch1).grid(column=2,row=1,padx=2)
Scale(offgainctr, length=100, from_=0, to=100, value=20, command=gainch2).grid(column=2,row=2,padx=2)
Scale(offgainctr, length=100, from_=0, to=100, value=20, command=gainch3).grid(column=2,row=3,padx=2)
Scale(offgainctr, length=100, from_=0, to=100, value=20, command=gainch4).grid(column=2,row=4,padx=2)
Scale(offgainctr, length=100, from_=0, to=100, value=20, command=gainch5).grid(column=2,row=5,padx=2)
Scale(offgainctr, length=100, from_=0, to=100, value=20, command=gainch6).grid(column=2,row=6,padx=2)

v_og1.grid(column=3,row=1,padx=10,sticky='e')
v_og2.grid(column=3,row=2,padx=10)
v_og3.grid(column=3,row=3,padx=10)
v_og4.grid(column=3,row=4,padx=10)
v_og5.grid(column=3,row=5,padx=10)
v_og6.grid(column=3,row=6,padx=10)

## channel select
lbck=Label(chanctr,text='Channels').grid(column=0,row=0,columnspan=6)
Checkbutton(chanctr,text='CH1',variable=v_ckch[0], onvalue=1, command=channelchg).grid(column=0,row=1)
Checkbutton(chanctr,text='CH2',variable=v_ckch[1], onvalue=2, command=channelchg).grid(column=1,row=1)
Checkbutton(chanctr,text='CH3',variable=v_ckch[2], onvalue=4, command=channelchg).grid(column=2,row=1)
Checkbutton(chanctr,text='CH4',variable=v_ckch[3], onvalue=8, command=channelchg).grid(column=3,row=1)
Checkbutton(chanctr,text='CH5',variable=v_ckch[4], onvalue=16, command=channelchg).grid(column=4,row=1)
Checkbutton(chanctr,text='CH6',variable=v_ckch[5], onvalue=32, command=channelchg).grid(column=5,row=1)

### axis control

def ndatachg(e):
    global ndata
    ndata=int(float(e))
    v_ndata.config(text='#data %d'%(ndata))

def okctr(e=None):
    mainTab.select(0)
    
def plotlimit(e=None):
    global limext
    limext=float(e)
    v_limit.config(text='y_ext %0.2f'%(limext))

Checkbutton(axisctr,text='Filter',variable=v_filt,width=8).grid(row=0,column=0, padx=10,sticky='w')
Checkbutton(axisctr,text='Buffered',variable=v_buff,state='disabled').grid(row=0,column=1,sticky='e',padx=10)
v_ndata=Label(axisctr,text='#data %d'%(ndata),width=10)
v_ndata.grid(row=1,column=0,padx=10, sticky='w')
v_limit=Label(axisctr,text='y_ext 0',width=10)
v_limit.grid(row=2,column=0,padx=10, sticky='w')

Scale(axisctr, length=100, from_=10, to=200, value=ndata, command=ndatachg).grid(row=1,column=1)
Scale(axisctr, length=100, from_=0, to=0.2, value=0, command=plotlimit).grid(row=2,column=1)

Button(ctrarea,text='OK',style='ok.TButton',command=okctr).place(x=235,y=170,width=30,height=30)
Button(ctrarea,text='X',style='off.TButton',command=destroyme).place(x=270,y=170,width=30,height=30)

#### SETTINGS AREA ######

def setdt(e=None):
    v_dt.config(text='delta %4d'%(int(float(e))))
    
def setav(e=None):
    v_av.config(text='average %4d'%(int(float(e))))

def setapply(e=None):
    print(deviceCommand('dt %d'%(int(float(s_dt.get())))))
    print(deviceCommand('avg %d'%(int(float(s_av.get())))))

v_dt=Label(setarea,text='delta   0', width=12, anchor='w')
v_av=Label(setarea,text='average  10', width=12, anchor='w')
s_dt=Scale(setarea, length=100, from_=0, to=100, value=0, command=setdt)
s_av=Scale(setarea, length=100, from_=0, to=20, value=10, command=setav)

v_dt.grid(row=0,column=0)
s_dt.grid(row=0,column=1)
v_av.grid(row=1,column=0)
s_av.grid(row=1,column=1)

Button(setarea,text='Apply',command=setapply).grid(row=2,column=0,columnspan=2,pady=20)

###### COMMAND AREA #######

def dosend(e=None):
    s=deviceCommand(cmdstring.get())
    print(s)
    restext.insert(END,s+'\n')

cmdstring=StringVar(mw)
respstring=StringVar(mw)

cmdbox=Entry(cmdarea,textvariable=cmdstring)
sendbutt=Button(cmdarea,text='send',command=dosend)
restext=Text(cmdarea,width=34,height=8)

cmdbox.grid(column=0,row=0,padx=10,pady=5)
sendbutt.grid(column=1,row=0,padx=10,pady=5)
restext.grid(column=0,row=1,columnspan=2,pady=5)
cmdbox.bind('<Return>',dosend)

### Events binding ###

def tabchanges(e):
    if mainTab.tab('current')['text']=='plot':
        if chandirty:
            measure()
        else:
            updateplot()
    else:
        if running:
            # deactivate run mode
            runmeasure()

mw.bind('<<NotebookTabChanged>>', tabchanges)

###### MAIN PROGRAM ######

mw.geometry('{}x{}+{}+{}'.format(WSCREEN,HSCREEN,WOFFS,HOFFS))
#mw.resizable(False,False)
#mw.config(cursor='none')
mw.mainloop()
deviceClose()
