import numpy as np
import datetime
from datetime import datetime,timedelta
import time
import math,random

import numpy.polynomial.polynomial as poly

def solve2(x0, y0, i0 , i1, xForecast ): 
    # curve fit
    x=x0[i0:i1]
    dxFore = (xForecast - x0[i0]).total_seconds()
    for k in range(len(x)):
        dx = (x[k] - x0[i0]).total_seconds()
        x[k]=dx
    #print(x)
    y=y0[i0:i1]
    #print('entro in solve2 ',i0,i1)
    #popt, _ = curve_fit(objective, x, y)
    coefs = poly.polyfit(x, y, 2)
    
    # summarize the parameter values
    c,b,a = coefs
    #print('y = %.5f * x^2 + %.5f * x + %.5f' % (a, b, c))  
    #rms = rootMeanSquare(y,i0,i1)
    rms=math.sqrt(np.sum((y-np.average(y))**2)/(len(y)))

    yfore=a * dxFore*dxFore + b * dxFore + c
    #print('yfore=',yfore)
    return yfore, rms

def addpoint(xvect,yvect, time00 , sensorValue, max0, tmax30, tmax300):
#offset30,offset300=addpoint(x300,y300,time00, sensorValue,max300, Tmax30, Tmax300);

    offset30 = 0;offset300 = 0
    for k in range(1,max0+1):
        yvect[k - 1] = yvect[k]
        xvect[k - 1] = xvect[k]
        # printf("shiftVect   x[k]=%f  time0=%f   tmax300=%f  tmax30=%f  \n",x[k],time0,tmax300,tmax30);
        #print('>>>>',time00,xvect[k])
        deltaSec=(time00-xvect[k]).total_seconds()
        
        if deltaSec>tmax300 :
            offset300 = k
        if deltaSec>tmax30 :
            offset30 = k
        yvect[max0] = sensorValue
        xvect[max0] = time00
    return offset30,offset300

def addpoint1(yvect1,yvect2, dif, fore1, fore2, max0):
#offset30,offset300=addpoint(x300,y300,time00, sensorValue,max300, Tmax30, Tmax300);

    if len(dif)<max0+1:
        yvect1.append(fore1)
        yvect2.append(fore2)
        dif.append(fore2-fore1)
    else:
        #print ('max0=',max0,len(yvect1),len(yvect2),len(dif)
        yvect1.pop(0)
        yvect1.append(fore1)
        yvect2.pop(0)
        yvect2.append(fore2)
        dif.pop(0)
        dif.append(fore2-fore1)
        #for k in range(1,max0+1):
        #    yvect1[k - 1] = yvect1[k]
        #    yvect2[k - 1] = yvect2[k]
        #    dif[k - 1] = dif[k]
        
        #yvect1[max0] = fore1
        #yvect2[max0] = fore2
        #dif[max0]=fore2-fore1
        
    
    return len(dif)

    # define the true objective function
def objective(x, a, b, c):
        return a * x + b * x**2 + c

def rootMeanSquare( yvec, i0, i1, ave=None ):
    a=yvec[i0:i1]
    return math.sqrt(np.sum((a-np.average(a))**2)/(len(a)))
