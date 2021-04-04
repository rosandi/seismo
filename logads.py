#!/usr/bin/python3

from time import sleep
import sys
import signal as sg
import seismoads as sa
import numpy as np


blocklen=1024
run=True
nkill=0
bcnt=0
nb=None

for arg in sys.argv:
    if arg.find('block=') == 0:
        blocklen=int(arg.replace('block=',''))
        print('block length: %d'%(blocklen), file=sys.stderr)
    if arg.fing('N=') == 0:
        nb=int(arg.replace('N=',''))

sa.deviceInit()

def termhandle(num,frm):
    global run,nkill
    if nkill > 0:
        print('Brutally killed.', file=sys.stderr)
        exit()
    else:
        print('Signal recieved..', file=sys.stderr)
        nkill+=1
    run=False

sg.signal(sg.SIGINT, termhandle)

while run:

    bcnt+=1
    print('reading block %d'%(bcnt),file=sys.stderr)

    t,d=sa.directMeasure(blocklen)
    d=np.array(d).reshape((4,blocklen),order='F')
    print('# %0.10f'%(t))
    for i in range(blocklen):
        print('{0} {1:>6} {2:>6} {3:>6} '.format(i,d[0,i],d[1,i],d[2,i]))
    
    if nb is None:
        continue
    
    if bcnt >= nb:
        break
