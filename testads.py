from time import sleep
import seismoads as sa
import numpy as np
import matplotlib.pyplot as plt 
sa.deviceInit()

while True:
    _,d=sa.directMeasure(20)
    d=np.array(d).reshape((4,20),order='F')
    for i in range(20):
        print('{0:>6} {1:>6} {2:>6} '.format(d[0,i],d[1,i],d[2,i]))
        
#    break
    #d=np.reshape(d,(4,10),order='F')
    #print('{0:>6} : {1:>6} : {2:>6} : {3:>6}'.format(*d))
    #x=np.linspace(0,10,10)
    #plt.plot(x,d[0])
    #plt.plot(x,d[1])
    #plt.plot(x,d[2])
    #plt.show()

