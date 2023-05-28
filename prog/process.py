from CONF import folderOut,config
import io
import datetime
from datetime import datetime,timedelta
import time
import math,random
import readConfig as rc
import os,socket
import numpy as np

import numpy.polynomial.polynomial as poly
from alerts import checkAlerts
 
debug=False



max300      =int(config['n300'])
max30       =int(config['n30'])
ratioRMS    =float(config['ratioRMS'])
threshold   =float(config['threshold'])
#AddRMS      =float(config['AddRMS'])
#backFactor  =float(config['backFactor'])
DtAverage   =float(config['Interval'])
folderWWW   =config['folderWWW']
print('folderWWW: '+folderWWW)
if folderWWW !='':
    print('folderWWW: '+folderWWW)
    if not os.path.exists(folderWWW):
        try:
            os.makedirs(folderWWW)
        except:
            print('unable to create folderWWW: '+folderWWW)
Tmax30=max30*DtAverage
Tmax300=max300*DtAverage  #to avoid to include too old data
alertValue=0
x300=[0.0]*(max300+1)
y300=[0.0]*(max300+1)

yavg30=[0.0]*(max300+1)
yavg300=[0.0]*(max300+1)
diffe=[0.0]*(max300+1)
config={}

initialized=False
#print ('initialized=',initialized)



def init(time0,sensorValue,folderOut):
   # se esiste buffer leggo buffer e non uso i valori
    print(folderOut+os.sep+'buffer.txt')
    if os.path.exists(folderOut+os.sep+'buffer.txt'):
        print('reading buffer')
        index300,index1,x300,y300,yavg30,yavg300=readBuffer(folderOut,max300)
    else:
        index1=0
        index300=0
        alertValue=0
        x300=[0.0]*(max300+1)
        y300=[0.0]*(max300+1)

        yavg30=[0.0]*(max300+1)
        yavg300=[0.0]*(max300+1)
        diffe=[0.0]*(max300+1)

    if index1==0:
        print ('Initializing ',max300,' data ')
        for k in range(0,max300+1):
            x300[k]=( time0-timedelta(seconds=(max300-k)*DtAverage))
            #print(time0,x300[k],k)
            y300[k]=(sensorValue+random.random()*0.001)
            #yavg30.append (sensorValue)
            #yavg300.append(sensorValue)
            
        #diffe.append=0;
    return index300,index1,x300,y300,yavg30,yavg300
    
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
    
def solve20(x, y, i0 , i1, xForecast ):
    #int k
    #double a, b, c
    #double a11, a12, a13, a21, a22, a23, a31, a32, a33, c1, c2, c3
    #double sumx2, sumx1, sumy1,dx
    #double sumx3, sumx4, sumx2y, sumxy
    #int np
    #float yavg,rm

    sumx2 = 0  
    sumx1 = 0  
    sumy1 = 0  
    np = 0  
    sumx3 = 0 
    sumx4 = 0  
    sumx2y = 0  
    sumxy = 0 
    for k in range(i0,i1+1):
        dx = (x[k] - x[i0]).total_seconds()
        sumx4 += dx*dx*dx*dx
        sumx2 += dx*dx
        sumx3 += dx*dx*dx
        sumx1 += dx
        sumy1 += y[k]
        sumxy += dx * y[k]
        sumx2y += dx*dx * y[k]
        np += 1
    

    c1 = sumx2y
    c2 = sumxy
    c3 = sumy1

    a11 = sumx4
    a12 = sumx3
    a13 = sumx2

    a21 = sumx3
    a22 = sumx2
    a23 = sumx1

    a31 = sumx2
    a32 = sumx1
    a33 = np

    #double denom;

    denom = multi2(a11, a21, a31, a12, a22, a32, a13, a23, a33)
    if (denom != 0):
        a = multi2(c1, c2, c3, a12, a22, a32, a13, a23, a33) / denom
        b = multi2(a11, a21, a31, c1, c2, c3, a13, a23, a33) / denom
        c = multi2(a11, a21, a31, a12, a22, a32, c1, c2, c3) / denom
        yavg = average(y,i0,i1)
        rms = rootMeanSquare(y,i0,i1,yavg)
        dx = (xForecast - x[i0]).total_seconds()
        yfore=a * dx*dx + b * dx + c
        return yfore, rms
    
    else:
        return sumy1 / np,0


def multi2( a11,  a21,  a31,  a12,  a22,  a32,  a13,  a23,  a33):
    #double multi0
    multi0 = a11 * a22 * a33 + a12 * a23 * a31 + a13 * a21 * a32
    multi0 -= (a13 * a22 * a31 + a11 * a23 * a32 + a33 * a12 * a21)
    return multi0


def rootMeanSquare( yvec, i0, i1, ave=None ):
    a=yvec[i0:i1]
    return math.sqrt(np.sum((a-np.average(a))**2)/(len(a)))
def average(yvec,i0,i1):
    a=yvec[i0:i1]
    return np.average(a)
    
def rootMeanSquare0( yvec, i0, i1, ave=None ):
    if ave is None:
        ave=average(yvec,i0,i1)
    rm = float(0)
    for k in range(i0,i1+1):
        rm += (yvec[k]-ave)*(yvec[k]-ave)/(i1-i0+1)
    
    rm = math.sqrt(rm)
    return rm

def average0(y,i1,i2):
    av=0.0
    for i in range(i1,i2+1):
        av +=y[i]
    av /=(i2-i1+1)
    return av

def readBuffer(folderOut,max300,kk='',Force=False):
    # read buffer.txt 
    x300=[0.0]*(max300+1)
    y300=[0.0]*(max300+1)
    index300=0
    t0=datetime.utcnow()
    if kk=='':
        suffix=''
    else:
        suffix='_'+format(kk)
    if os.path.exists(folderOut+ os.sep +"buffer" + suffix + ".txt"):
    
        fh=open(folderOut+'/buffer'+suffix+'.txt','r')
        rows=fh.read().split('\n')       
        fh.close()
        try:
            index300,index1=(int(x) for x in rows[0].split(','))
            lastts=rows[-2].split(',')[0]
            delta=(t0-datetime.strptime(lastts,'%Y-%m-%d %H:%M:%S')).total_seconds()/60.
            print('deltaTime min buffer',delta, 'last datetime',format(datetime.strptime(lastts,'%Y-%m-%d %H:%M:%S')))
        except:
            delta=1e6       
        
        if index300==max300+1 and len(rows)>=max300+1 and (delta<60 or Force):
            try:
                for i in range(1,index300):
                    y300[i],yavg30[i],yavg300[i]=(float(x) for x in rows[i].split(',')[1:])
                    ts=rows[i].split(',')[0]
                    x300[i]=datetime.strptime(ts,'%Y-%m-%d %H:%M:%S') 
                    #print(ts,x300[i],y300[i])
            except Exception as e:
                print('readBuffer error: ',e)
                index300=0
                x300=[0.0]*(max300+1)
                y300=[0.0]*(max300+1)
                index1=0
        else:
           print(index300,max300,len(rows))
           index300=0
           index1=0
    else:
        print('file not existing ',folderOut+ os.sep +"buffer" + suffix + ".txt")
        index300=0
        index1=0
    return index300,index1,x300,y300,yavg30,yavg300

def saveBuffer(x300,y300,yavg30,yavg300,folderOut,kk=''):
    # read buffer.txt 
    index300=len(x300)
    index1=index300
    #print(x300[0],x300[1])
    if kk=='':
        suffix=''
    else:
        suffix='_'+format(kk)
    
    fh=open(folderOut+'/buffer'+suffix+'.txt','w')
    fh.write(format(index300)+','+format(index1)+'\n')
    for i in range(index300):
        fh.write(format(x300[i])+','+format(y300[i])+','+format(yavg30[i])+','+format(yavg300[i])+'\n')
    fh.close()

    return

def addMeasure(config,time0,sensorValue,folderOut):
    global initialized,alertValue,index300,index1,x300,y300,yavg30,yavg300
    
    if not initialized:
        print('calling init process.py')
        index300,index1,x300,y300,yavg30,yavg300=init(time0,sensorValue,folderOut)
        initialized=True
     
    offset30,offset300=addpoint(x300,y300,time0, sensorValue,max300, Tmax30, Tmax300);
    if config['Interval']=='-1':
        offset30=max300-int(config['n30'])
        offset300=0
    forecast30,rms30 = solve2(x300, y300, offset30,  max300, time0);
    forecast300 ,rms = solve2(x300, y300, offset300, max300, time0);
    
    nfore=addpoint1(yavg30, yavg300, diffe, forecast30, forecast300, max300)
   
    if nfore==max300+1:     
        rms = rootMeanSquare(diffe,0,max300)
        
    alertSignal = math.fabs(forecast30 - forecast300);

    if (alertSignal>ratioRMS*rms and alertSignal>threshold):
            if (alertValue<10):
                alertValue += 1;
    else:
           if (alertValue>0 ):
               alertValue -= 1;

    #print time0,',',sensorValue,',',forecast30,',',forecast300,',',rms30,',',rms,',',alertSignal,',',alertValue,',',nfore,',',ratioRMS,',',threshold
    
    saveBuffer(x300,y300,yavg30,yavg300,folderOut)
    
    return forecast30,forecast300,rms,alertSignal,alertValue

def procSaveURL(SaveURL,wgetData,config,adcData,tt,mavg,forecast30,forecast300,rms,alertSignal,alertValue,nd1):
            SaveURL=SaveURL.replace('$EQ','=')
            SaveURL=SaveURL.replace('\$','$')
            #print SaveURL
            idDevice=config['IDdevice']
            if '$HOSTNAME' in idDevice:
                idDevice=idDevice.replace('$HOSTNAME',os.uname()[1])
            #idDevice=idDevice.replace('$HOSTNAME',socket.gethostname())
            #idDevice=idDevice.replace('$HOSTNAME','IDSL-50x')
            #print idDevice
            SaveURL=SaveURL.replace('$IDdevice',idDevice)
            #print SaveURL 
            SaveURL=SaveURL.replace('$DATE',format(tt,'%d/%m/%Y'))
            SaveURL=SaveURL.replace('$TIME',format(tt,'%H:%M:%S'))
            SaveURL=SaveURL.replace('$TEMP','%.1f' % float(adcData['tempCPU']))
            SaveURL=SaveURL.replace('$PRESS','%.2f' % float(adcData['pressure']))
            SaveURL=SaveURL.replace('$LEV',"%.3f" % mavg)
            SaveURL=SaveURL.replace('$FORE300',"%.3f" % forecast300)
            SaveURL=SaveURL.replace('$FORE30',"%.3f" % forecast30)
            
            SaveURL=SaveURL.replace('$RMS',"%.4f" % rms)
            SaveURL=SaveURL.replace('$ALERT_SIGNAL',"%.3f" % alertValue)
            SaveURL=SaveURL.replace('$ALERT_LEVEL',"%.3f" % alertSignal)
            SaveURL=SaveURL.replace('$V1','%.2f' % float(adcData['batteryValue']))
            SaveURL=SaveURL.replace('$V2','%.1f' % float(adcData['panelValue']))
            SaveURL=SaveURL.replace('$V3','%.3f' % float(adcData['tempValue']))
            SaveURL=SaveURL.replace('$V4','%.3f' % float(adcData['temperature380']))
            SaveURL=SaveURL.replace('$V5',format(nd1))
            
            #cmd='wget "'+SaveURL+'" -T 2 -r 1 -nv -o outlogwget.txt'
            #cmd='wget "'+SaveURL+'" -nv -o '+folderOut+'/outlogwget.txt -O '+folderOut+'/outwget.txt'
            #print (SaveURL)
            if debug: print(7)
            wgetData.append(SaveURL)
            return SaveURL

def process5Sec(config,queueData,adcData,wgetData,folderOut,queueMQTT):

  print ("---------------------------------------------------")
  print ("Starting process5Sec")
  print ("opening ", config['Interval'], config['sensorMultFac'], config['sensorAddFac'])
  print ("---------------------------------------------------")
  
  folderWWW   =config['folderWWW']
  print('folderWWW: '+folderWWW)
  if folderWWW !='':
        print('folderWWW: '+folderWWW)
        if not os.path.exists(folderWWW):
            try:
                os.makedirs(folderWWW)
            except:
                print('unable to create folderWWW: '+folderWWW)
  INTERVAL=float(config['Interval'])
  sensorMultFac=float(config['sensorMultFac'])
  sensorAddFac=float(config['sensorAddFac'])
  
  t0=datetime.utcnow()
  t00=t0 #datetime(t0.year,t0.month,t0.day,t0.,0)
  mavg=0.0
  nd=0
  secs0=0
  nd1=1
  first=True
  #queueData=[]
  time.sleep(.1)
  print('starting loop ',len(queueData))
  while True: 
     
    todayS=datetime.utcnow().strftime('%Y-%m-%d')
    #print(nd,ndata)
    while len(queueData)>0: # or (nd>=len(queueData)-1 and nd>ndata):
        
        if debug: print(1)
        nd=0
        if first:
            if debug: print(2)
            first=False
            t00,value=queueData[0]
        if debug: print(3)
        skip=True
        nd=0
        for j in range(len(queueData)):
            tt,value=queueData[j]
            secs=(tt-t00).seconds
            #print(secs,secs0,secs0+INTERVAL,tt,t00)
            nd+=1
            if (secs>INTERVAL and nd>2) or INTERVAL==-1:
                #print(secs,secs0+INTERVAL,tt,t00)
                skip=False
                break                
            
        #print(secs,secs0+INTERVAL,skip,nd)
        if debug: print(4)
        if not skip:
            #print('****************************')
            nd1=0
            mavg=0.0  
            if debug: print(5) 
            QDL0=len(queueData)
            for tt,value in queueData[:nd]:
                secs=(tt-t00).seconds
                
                queueData.pop(0)
                if config['MQTT_server']+config['MQTT_listener']=='' and len(queueMQTT)>0:
                    queueMQTT.pop(0)
                nd1+=1
                mavg +=value
            mavg /=(nd1)
            if debug: print(6)
            #print('nd1,mavg',nd1,mavg)
            mavg=mavg*sensorMultFac+sensorAddFac
            if INTERVAL != -1:
                tsec=int(int(tt.second/INTERVAL)*INTERVAL)
                tt1=datetime(tt.year,tt.month,tt.day,tt.hour,tt.minute,tsec)
            else:
                tt1=tt

            
            #print(tt1,mavg,secs,INTERVAL) 
            tt=tt1
            
            t00=tt  #datetime(tt.year,tt.month,tt.day,tt.hour,tt.minute,int(tsec+INTERVAL))
            if debug: print(6.1)
            forecast30,forecast300,rms,alertSignal,alertValue= addMeasure(config,tt,mavg,folderOut)
            if debug: print(6.2)
            fh=open(folderOut+'/'+todayS+'_out5s.txt','a')
            fh.write(format(tt,'%d/%m/%y %H:%M:%S')+','+"%.3f" % mavg+','+"%.3f" % forecast30+','+"%.3f" % forecast300+','+format("%.1f" % float(adcData['batteryValue']))+','+format("%.1f" % float(adcData['tempValue']))+','+'%.1f' % float(adcData['tempCPU'])+'\n')
            fh.close()

            SaveURL=config['SaveURL']
            SaveURL=procSaveURL(SaveURL,wgetData,config,adcData,tt,mavg,forecast30,forecast300,rms,alertSignal,alertValue,nd1)
            
            if 'SaveURL1' in config:
                SaveURL1=config['SaveURL1']
                print(SaveURL1)
                procSaveURL(SaveURL1,wgetData,config,adcData,tt,mavg,forecast30,forecast300,rms,alertSignal,alertValue,nd1)
            if 'SaveURL2' in config:
                SaveURL2=config['SaveURL2']
                procSaveURL(SaveURL2,wgetData,config,adcData,tt,mavg,forecast30,forecast300,rms,alertSignal,alertValue,nd1)

            #print(tt,mavg)
            try:
                riga='time='+format(tt,'%d/%m/%y %H:%M:%S')+'\n'
                riga+='Level (m)='+"%.3f" % mavg+'\n'
                riga+='Short Term forecast='+"%.3f" % forecast30+'\n'
                riga+='Long Term forecast='+"%.3f" % forecast300+'\n'
                riga+='RMS='+"%.4f" % rms+'\n'
                riga+='Alert Value='+"%.3f" % alertValue+'\n'
                riga+='Alert Signal='+"%.3f" % alertSignal+'\n'
                riga+='Battery value='+"%.1f" % float(adcData['batteryValue'])+'\n'
                riga+='Air Temprtature='+"%.1f" % float(adcData['tempValue'])+'\n'
                riga+='CPU temperature='+"%.1f" % float(adcData['tempCPU'])+'\n'
                riga+='Pressure='+'%.2f' % float(adcData['pressure'])+'\n'
                riga+='Temperature380='+'%.1f' % float(adcData['temperature380'])+'\n'
                if folderWWW !='':
                    f=open(folderWWW+os.sep+'CurrentData.txt','w')
                    f.write(riga)
                    f.close()
                #riga+=format(nd1)
                if 'log=' in SaveURL:                
                    riga=SaveURL.split('log=')[1].replace('$S','').replace('$E','')
                if 'log$EQ' in SaveURL:
                    riga=SaveURL.split('log$EQ')[1].replace('$S','').replace('$E','')
                checkAlerts(config,tt,mavg,alertValue, folderOut)

                QDL1=len(queueData)
                riga +=' ('+format(QDL0)+' '+format(QDL1)+' '+format(QDL1-QDL0)+' wget:'+format(len(wgetData))+')'
                print(riga)
                
                fname=folderOut+os.sep+'execLog_'+datetime.strftime(tt,'%Y-%m-%d')+'.txt'
                f=open(fname,'a')
                f.write(riga+'\n')
                f.close()
            except Exception as e:
                print(e)
            nd1=nd
            if debug: print(format(datetime.utcnow()))

if __name__ == "__main__":
    adcData={}
    wgData=[]
    adcData['batteryValue']=12
    adcData['panelValue']=-1
    adcData['tempValue']=22.4
    adcData['tempCPU']=39.
    
    queueData=[[1,-1]]*200000
    
    #fh=open('AllData_2018-02-18.log','r')
    #fh=open('AllData_IDSL-01_2018-02-16.log','r')
    #fh=open('AllData_IDSL-101_2018-02-14.log','r')
    #fh=open('AllData_IDSL-01_20022018.txt','r')
    fh=open('./IDSL-26/AllData_IDSL-26_2018-02-24.log','r')
    i=0
    while True:
        r=fh.readline()
        if r=='': break
        da=r.split(' ')[0]+' '+r.split(' ')[1]
        datTime=datetime.strptime(da, '%d/%m/%Y %H:%M:%S.%f')
        #datTime=datetime.strptime(da, '%Y-%m-%d %H:%M:%S.%f')
        value=float(r.split(' ')[2].split('\n')[0])
        #print datTime,value
        i +=1
        if int(i/25000)*25000==i:
            print( datTime,value)
        if i>=len(queueData)-1: break
        queueData[i]=(datTime,value)
    
    fh.close()
    queueData[0][0]=i
    process5Sec(config,queueData,adcData,wgData)
    
    
    # for i in range(1,10):
        # ti=datetime.now()
        # va=10*math.sin(i)
        # addMeasure(ti,va)
        # time.sleep(5)