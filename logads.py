from time import sleep
import signal as sg
import seismoads as sa
import numpy as np

sa.deviceInit()
blockln=1024
run=True

def termhandle():
    global run
    run=False

while run:
    t,d=sa.directMeasure(blocklen)
    d=np.array(d).reshape((4,blocklen),order='F')

    print('# %0.10f'%(t))
    for i in range(blocklen):
        print('{0} {1:>6} {2:>6} {3:>6} '.format(i,d[0,i],d[1,i],d[2,i]))
