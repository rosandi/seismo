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

WSCREEN=1016
HSCREEN=594
WOFFS=0
HOFFS=0

import sys
import os
import datetime
from tkinter import Tk, IntVar, StringVar, Canvas, Text, font
from tkinter import ALL, END, LEFT, W, INSERT
from tkinter import filedialog
from tkinter.ttk import Scale, Button, Label, Style, Notebook, Frame
from tkinter.ttk import Checkbutton, Entry
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

comm='null'  # for arduino: '/dev/ttyACM0'
speed=115200
datadir='./data'
nchannel=4

################### COMMAND LINE ARGUMENTS ############################

for arg in sys.argv:
    if arg.find('comm=') == 0:
        comm=arg.replace('comm=','')
    if arg.find('speed=') == 0:
        speed=int(arg.replace('speed=',''))
    if arg.find('size=') == 0:
        WSCREEN=int(arg.replace('size=','').split('x')[0])
        HSCREEN=int(arg.replace('size=','').split('x')[1])
    if arg.find('offset=') == 0:
        WOFFS=int(arg.replace('offset=','').replace('+',' ').split()[0])
        HOFFS=int(arg.replace('offset=','').replace('+',' ').split()[1])
    if arg.find('data=') == 0:
        datadir=arg.replace('data=','')
    if arg.find('channels=') == 0:
        nchannel=int(arg.replace('channels=',''))
		
##########################################################################

WCVS=int(0.8*WSCREEN)
HCVS=int(0.9*HSCREEN)

err=os.system('mkdir -p {}'.format(datadir))

if err:
    print('failure in creating data directory: {}'.format(datadir))
    exit(-1)

import numpy as np

welcvs.delete(progress)
progress=welcvs.create_rectangle(20,200,100,220,fill='blue')
welcome.update()

if comm=='null':
    from seismodummy import deviceInit,deviceClose,deviceCommand
    from seismodummy import directMeasure,clearQueue
    from seismodummy import channelnum
else:
    try:
        if comm.find('ADS') == 0:
            from seismoads import deviceInit,deviceClose,deviceCommand
            from seismoads import directMeasure,clearQueue
            from seismoads import channelnum
        else:
            from seismoserial import deviceInit,deviceClose,deviceCommand
            from seismoserial import directMeasure,clearQueue
            from seismoserial import channelnum
    except:
        print('Can not find seismo device. Fall back to dummy device')
        from seismodummy import deviceInit,deviceClose,deviceCommand
        from seismodummy import directMeasure,clearQueue
        from seismodummy import channelnum

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
ndata=100
minofs=-0.2
maxofs=0.2
mingain=0
maxgain=5
chandirty=True
limext=0.0
datadir="./data"
loc=(-6.914864, 107.608238)

# allocate for 6 channels
chlist=[1]
choffset=[0.0]*nchannel
baseoffset=[0.0]*nchannel
chgain=[1.0]*nchannel
cvs=[None]*nchannel
chcolor=['SteelBlue3','chartreuse2','firebrick3','DarkOrchid1','dark green','maroon']*2
y=None
x=None


def getdevdata(e=None):
    global running, x, y, chlist
    msrtime,vals=directMeasure(ndata)
    nchan,chlist=channelnum()
    ndat=int(len(vals)/nchan)
            
    x=msrtime/nchan
    y=np.array(vals).reshape((nchan,ndat),order='F')

def trigdevdata(e=None):
    global running, x, y, chlist
    msrtime,vals=directMeasure(ndata)
    nchan,chlist=channelnum()        
    ndat=int(len(vals)/nchan)

    x=msrtime
    y=np.array(vals).reshape((nchan,ndat),order='F')
            
def save():
    now=datetime.datetime.now()
    fname=datadir+'/%d%02d%02d%02d%02d%02d.dat'%(now.year,now.month,now.day,now.hour,now.minute,now.second)
    print('saving data to ',fname)
    try:
        fdat=open(fname,'w')
        ndat=len(y[0])
        xt=np.linspace(0,x,ndat)
        # header
        
        fdat.write('#$location {} {}\n'.format(loc[0],loc[1]))
        fdat.write('#$time {}\n'.format(x))
        fdat.write('#$ndata {}\n'.format(ndat))
        fdat.write('#$channels ')
        
        for ch in chlist:
            fdat.write(' %d'%(ch))
        fdat.write('\n')
        
        # content
        for a in range(ndat):
            s='%0.5f'%(xt[a])
            for b in chlist:
                s='{} {}'.format(s,y[b][a])
            fdat.write('{}\n'.format(s))
        
        fdat.close()
    except:
        print('error writting file')


####### PLOT PROCEDURE #######

def plot(cvs,data,color='black'):
    hh=int(cvs.cget('height'))
    ww=int(cvs.cget('width'))
    mid=hh/2    
    x=np.linspace(0,ww,len(data))

    line=[]

    for a,b in zip(x,data):
        line.append(a)
        line.append(mid-b)
        
    cvs.create_line(line, fill=color, width=2)

def updateplot(e=None):
    
    mi=1e6
    ma=-1e6
    
    yplot=np.array(y)
    
    if filtexist and v_filt.get():
        for i in chlist:
            yplot[i]=sg.filtfilt(butta, buttb, y[i]*chgain[i])
            mmi=min(yplot[i])
            mma=max(yplot[i])
            mi = mmi if (mi>mmi) else mi
            ma = mma if (ma<mma) else ma
    else:
        for i in chlist:
            mmi=np.amin(yplot[i])
            mma=np.amax(yplot[i])
            mi = mmi if (mi>mmi) else mi
            ma = mma if (ma<mma) else ma

    for i in chlist:
        cvs[i].delete(ALL)
        plot(cvs[i],yplot[i]*0.001,color=chcolor[i])
        cvs[i].create_text(20,10,text='ch%d'%(i+1), font=('Helvetica',10))
    
    thi['text']='%0.3f ms'%(x*1000)

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

def initialize():
    deviceInit(comm,speed)
#    deviceInit()

#    while True:
#        _,d=directMeasure(20)
#        d=np.array(d).reshape((4,20),order='F')
#        for i in range(20):
#            print('{0:>6} {1:>6} {2:>6} '.format(d[0,i],d[1,i],d[2,i]))
    
#    exit()
    
    print("initialization....")
    print(deviceCommand("dt 1"))
    print(deviceCommand("avg 10"))
    
    m=0
    for c in range(nchannel):
       m+=2**c
    
    print(deviceCommand("chn {}".format(m)))


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

### STYLES ######
sty=Style()
sty.map('r.TButton',background=[('active','red'),('!disabled','red4')])
sty.map('p.TButton',background=[('active','green'),('!disabled','dark green')])
sty.map('ok.TButton',background=[('active','green'),('!disabled','dark green')])
sty.map('off.TButton',background=[('active','red'),('!disabled','red4')])
sty.configure('res.TLabel',background='white')
sty.configure('TScale',background='blue')

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

for i,c in zip(range(6),(1,2,4,8,16,32)):
    v_ckch[i].set(c)

v_buff.set(1)

####################################################################
############# PLOT AREA ############################################
####################################################################
  
def measure(e=None):
    global chandirty
    
    getdevdata()
    updateplot()

    if chandirty:
        zerooffset()
        chandirty=False

    if running:
        mw.after(10,measure)
    elif e is None:
        save()

def trigger(e=None):
    global chandirty
    
    cvs[0].delete(ALL)
    cvs[0].create_text(WCVS/2-70,40,text='Waiting: TRIGGER signal..', font=('Helvetica',16))
    mw.update()
    
    trigdevdata()
    updateplot()

    if chandirty:
        zerooffset()
        chandirty=False

    if running:
        mw.after(10,measure)
    
    save()

def runmeasure(e=None):
    global running
    
    if not running:
        running=True
        rpbutt.configure(style='p.TButton')
        measure()
    else:
        rpbutt.configure(style='r.TButton')
        running=False

def openfile(e=None):
    global lat,lon,x,y,chlist
    global chandirty
    
    fname=filedialog.askopenfilename(initialdir = datadir, title = "Select a File",  filetypes = (("data files", "*.dat*"),("all files","*.*")))

    ndat=0
    nline=0
    
    try: 
        fdat=open(fname,'r')
        for sln in fdat:
            
            sln=sln.strip()
            
            if sln == '':
                continue
                
            if sln.find('#$location') == 0:
                s=sln.replace('#$location','').split()
                lat=float(s[0])
                lon=float(s[1])
            if sln.find('#$time') == 0:
                x=float(sln.replace('#$time',''))
            if sln.find('#$ndata') == 0:
                ndat=int(sln.replace('#$ndata',''))
            if sln.find('#$channels') == 0:
                chlist=[int(s) for s in sln.replace('#$channels','').split()]
                for ch in chlist:
                    y[ch]=np.zeros(ndat)

            if sln.find('#') == 0:
                continue        
            
            s=[float(item) for item in sln.split()]
        
            x=s[0]
            for i,ch in zip(range(len(chlist)),chlist):
                y[ch][nline]=s[i+1]
            
            nline+=1
            
        updateplot()
    except:
        if fname:
            print('file read error: ', fname)


##### PLOT CANVAS ####

def mousepos(e,c):
    global mouseln,x
    ww=int(e.widget['width'])
    hh=int(e.widget['height'])
    pointpos['text']= 'ch(%d) %0.3f ms'%(c, 1000.0*x*e.x/ww)
    e.widget.coords(mouseln,e.x,0, e.x, hh)

def mouseenter(e):
    global mouseln
    hh=int(e.widget.cget('height'))
    mouseln=e.widget.create_line(e.x,0, e.x, hh)       

def mouseleave(e):
    global mouseln
    e.widget.delete(mouseln)
    
def mousepick(e,c):
    ww=int(e.widget['width'])
    pickbox.insert(INSERT,'%d %0.3f\n'%(c, 1000.0*x*e.x/ww))

def btnpick():
    s=pointpos['text'].replace('ch(','').replace(')','').replace(' ms','\n')
    pickbox.insert(INSERT,s)

#def mousezoom(e,c):
#    print('double click on ',c)
    
for c in range(nchannel):
    cvs[c]=Canvas(plotarea, width=WCVS, height=(HCVS-20)/nchannel, bg='white')
    cvs[c].grid(row=c,column=0)

tlow=Label(plotarea, text='0 ms')
thi=Label(plotarea, text='1000 ms')

tlow.place(x=5,y=HCVS)
thi.place(x=WCVS-60,y=HCVS)

for c in range(len(cvs)):
    cvs[c].bind('<Motion>', lambda e,c=c: mousepos(e,c))
    cvs[c].bind('<Enter>', mouseenter)
    cvs[c].bind('<Leave>', mouseleave)
    cvs[c].bind('<Double-Button-1>', lambda event, chn=c: mousepick(event, chn))
#    cvs[c].bind('<Double-Button-1>', lambda event, chn=c: mousezoom(event, chn))

#### BUTTONS ####

wbtn=WSCREEN-WCVS

rpbutt=Button(plotarea,text='RUN', style='r.TButton', command=runmeasure)
rpbutt.place(x=WCVS,y=0,height=50,width=wbtn)

Button(plotarea,text='MEASURE', command=measure).place(x=WCVS,y=54,height=50,width=wbtn)
Button(plotarea,text='TRIGER', command=trigger).place(x=WCVS,y=107,height=50,width=wbtn)
Button(plotarea,text='FILE', command=openfile).place(x=WCVS,y=160,height=50,width=wbtn)

pointpos=Button(plotarea,text='ch(0) 0 ms',command=btnpick)
pointpos.place(x=WCVS,y=220,width=wbtn)

infoarea=Frame(plotarea)
infoarea.place(x=WCVS+10,y=250,width=wbtn)

Label(infoarea, text='pick times').grid(column=0,row=2,columnspan=2)
pickbox=Text(infoarea,width=22,height=12)
pickbox.grid(column=0, row=3, columnspan=2)
pickbox.insert(END,'#channel time_ms\n')

def savepicks(e=None):

    fname=filedialog.asksaveasfile(initialdir=datadir, title="File name", filetypes=(("text files", "*.txt"),))    
    try:
        print('writing file: ', fname.name)
        fl=open(fname.name, 'w')
        fl.write(pickbox.get("1.0", END))
        fl.close()
    except:
        print('error writing file')

Button(infoarea, text='CLEAR', command=lambda: pickbox.delete(1.0,END)).grid(column=0, row=4)
Button(infoarea, text='SAVE', command=savepicks).grid(column=1, row=4)

####################################################################
############### CONTROL AREA #######################################
####################################################################

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

offgainctr=Frame(ctrarea)
chanctr=Frame(ctrarea)
axisctr=Frame(ctrarea)

slen=300
pady=10

#offgainctr.grid(row=0,column=0)
#chanctr.grid(row=1,column=0)
#axisctr.grid(row=2,column=0)

offgainctr.pack(pady=20)
chanctr.pack(pady=20)
axisctr.pack(pady=20)

Label(offgainctr, text='Offset').grid(column=1,row=0, pady=pady)
Label(offgainctr, text='Gain').grid(column=2,row=0, pady=pady)
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


Scale(offgainctr, length=slen, from_=0, to=100, value=50, command=offch1).grid(column=1,row=1,padx=2, pady=pady)
Scale(offgainctr, length=slen, from_=0, to=100, value=50, command=offch2).grid(column=1,row=2,padx=2, pady=pady)
Scale(offgainctr, length=slen, from_=0, to=100, value=50, command=offch3).grid(column=1,row=3,padx=2, pady=pady)
Scale(offgainctr, length=slen, from_=0, to=100, value=50, command=offch4).grid(column=1,row=4,padx=2, pady=pady)
Scale(offgainctr, length=slen, from_=0, to=100, value=50, command=offch5).grid(column=1,row=5,padx=2, pady=pady)
Scale(offgainctr, length=slen, from_=0, to=100, value=50, command=offch6).grid(column=1,row=6,padx=2, pady=pady)

Scale(offgainctr, length=slen, from_=0, to=100, value=20, command=gainch1).grid(column=2,row=1,padx=2, pady=pady)
Scale(offgainctr, length=slen, from_=0, to=100, value=20, command=gainch2).grid(column=2,row=2,padx=2, pady=pady)
Scale(offgainctr, length=slen, from_=0, to=100, value=20, command=gainch3).grid(column=2,row=3,padx=2, pady=pady)
Scale(offgainctr, length=slen, from_=0, to=100, value=20, command=gainch4).grid(column=2,row=4,padx=2, pady=pady)
Scale(offgainctr, length=slen, from_=0, to=100, value=20, command=gainch5).grid(column=2,row=5,padx=2, pady=pady)
Scale(offgainctr, length=slen, from_=0, to=100, value=20, command=gainch6).grid(column=2,row=6,padx=2, pady=pady)

v_og1.grid(column=3,row=1,padx=10,sticky='e')
v_og2.grid(column=3,row=2,padx=10)
v_og3.grid(column=3,row=3,padx=10)
v_og4.grid(column=3,row=4,padx=10)
v_og5.grid(column=3,row=5,padx=10)
v_og6.grid(column=3,row=6,padx=10)

## channel select
lbck=Label(chanctr,text='Channels').grid(column=0,row=0,columnspan=6,sticky='w')
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

Checkbutton(axisctr,text='Filter',variable=v_filt,width=16).grid(row=0,column=0, padx=10,sticky='w')
Checkbutton(axisctr,text='Buffered',variable=v_buff,state='disabled').grid(row=0,column=1,sticky='e',padx=10)
v_ndata=Label(axisctr,text='#data %d'%(ndata),width=10)
v_ndata.grid(row=1,column=0,padx=10, sticky='w')
v_limit=Label(axisctr,text='y_ext 0',width=10)
v_limit.grid(row=2,column=0,padx=10, sticky='w')

Scale(axisctr, length=200, from_=10, to=1000, value=ndata, command=ndatachg).grid(row=1,column=1,pady=pady)
Scale(axisctr, length=200, from_=0, to=0.2, value=0, command=plotlimit).grid(row=2,column=1, pady=pady)

Button(ctrarea,text='OK',style='ok.TButton',command=okctr).place(x=WSCREEN-270,y=HSCREEN-100,width=30,height=30)
Button(ctrarea,text='X',style='off.TButton',command=destroyme).place(x=WSCREEN-200,y=HSCREEN-100,width=30,height=30)


####################################################################
########### SETTINGS AREA ##########################################
####################################################################

setframe=Frame(setarea)
setframe.pack(pady=2*pady)

def setdt(e=None):
    v_dt.config(text='delta %4d'%(int(float(e))))
    
def setav(e=None):
    v_av.config(text='average %4d'%(int(float(e))))

def setapply(e=None):
    print(deviceCommand('dt %d'%(int(float(s_dt.get())))))
    print(deviceCommand('avg %d'%(int(float(s_av.get())))))

v_dt=Label(setframe,text='delta   0', width=12, anchor='w')
v_av=Label(setframe,text='average  10', width=12, anchor='w')
s_dt=Scale(setframe, length=slen, from_=0, to=100, value=0, command=setdt)
s_av=Scale(setframe, length=slen, from_=0, to=20, value=10, command=setav)

v_dt.grid(row=0,column=0, pady=pady)
s_dt.grid(row=0,column=1, pady=pady)
v_av.grid(row=1,column=0, pady=pady)
s_av.grid(row=1,column=1, pady=pady)

Button(setframe,text='Apply',command=setapply).grid(row=2,column=0,columnspan=2,pady=20)


####################################################################
############ COMMAND AREA ##########################################
####################################################################

cmdframe=Frame(cmdarea)
cmdframe.pack(pady=2*pady)

def dosend(e=None):
    s=deviceCommand(cmdstring.get())
    print(s)
    restext.insert(END,s+'\n')

cmdstring=StringVar(mw)
respstring=StringVar(mw)

cmdbox=Entry(cmdframe,textvariable=cmdstring)
sendbutt=Button(cmdframe,text='send',command=dosend)
restext=Text(cmdframe,width=50,height=30)

cmdbox.grid(column=0,row=0,padx=10,pady=5)
sendbutt.grid(column=1,row=0,padx=10,pady=5)
restext.grid(column=0,row=1,columnspan=2,pady=5)
cmdbox.bind('<Return>',dosend)

### Events binding ###

def tabchanges(e):
    global chandirty
    
    if mainTab.tab('current')['text']=='plot':
        if chandirty:
            measure(False)
            chandirty=False
        else:
            updateplot()
    else:
        if running:
            # deactivate run mode
            runmeasure(False)

mw.bind('<<NotebookTabChanged>>', tabchanges)

####################################################################
########### MAIN PROGRAM ###########################################
####################################################################

mw.geometry('{}x{}+{}+{}'.format(WSCREEN,HSCREEN,WOFFS,HOFFS))
#mw.resizable(False,False)
#mw.config(cursor='none')
mw.mainloop()
deviceClose()
