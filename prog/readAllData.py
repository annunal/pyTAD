#  pip install sh    * per tail

from CONF import folderData, folderOut,queueData,lastTime
import os
import time
import readConfig as rc
import process as pr
from datetime import datetime
import threading
import shutil as sh
#import readADC as adc
#import readCPUTemp as rcpu
import wgetProc as wg
#from sh import tail
wgetData=[]
adcData={}
adcData['batteryValue']=12
adcData['panelValue']=-1
adcData['tempValue']=22.4
adcData['tempCPU']=39.


def init_simple(config, queueData,folderOut):
  print ("---------------------------------------------------")
  print ("Starting read AllData on the fly")
  print ("opening ", config['Tail'])
  print ("----------------------------")
  lastread=datetime(2022,1,1)  
  if 'SonarMinLevel' in config:
    minValue=float(config['SonarMinLevel'])
    maxValue=float(config['SonarMaxLevel'])  
  else:
    minValue=-1e6
    maxValue=1e6
  while True:
      tnow=datetime.utcnow()
      fname=config['TailSimple']
      fname=fname.replace('$DATE',datetime.strftime(tnow,'%Y-%m-%d'))
      print('reading '+fname)

      if os.path.exists(fname):
         try:
            f=open(fname,'r')
            rows=f.read().split('\n')
            f.close()
         except:
            rows=[]
         for line in rows:
            if line !='':
                
                p=line.split(' ')
                ts=p[0]+' '+p[1]
                measureFloat=float(p[2])
                
                if '.' in ts:
                    tnow=datetime.strptime(ts,'%d/%m/%Y %H:%M:%S.%f')
                else:
                    try:
                        tnow=datetime.strptime(ts,'%d/%m/%Y %H:%M:%S')
                    except:
                        tnow=datetime.strptime(ts,'%Y-%m-%d %H:%M:%S')
                #print(tnow,lastread,tnow>lastread,len(queueData))
                if tnow>lastread:
                    #print(tnow)
                    lastread=tnow
                    if measureFloat>=minValue and measureFloat<=maxValue:
                        queueData.append((tnow,measureFloat))
                    fname=folderOut+os.sep+'AllData_'+datetime.strftime(tnow,'%Y-%m-%d')+'.log'
                    fh=open(fname,'a')
                    fh.write(format(tnow)+' '+format(measureFloat)+'\n')
                    fh.close()
      time.sleep(5)        
                     
        
        
        
def init(config, queueData,folderOut):
  print ("---------------------------------------------------")
  print ("Starting read AllData on the fly")
  print ("opening ", config['Tail'])
  print ("----------------------------")

  minValue=float(config['SonarMinLevel'])
  maxValue=float(config['SonarMaxLevel'])
  
  while True:
      tnow=datetime.utcnow()
      fname=config['Tail']
      fname=fname.replace('$DATE',datetime.strftime(tnow,'%Y-%m-%d'))
      print('reading '+fname)


      for line in tail("-f", fname, _iter=True):
        if not os.path.exists(fname):
            break
        p=line.split(' ')
        #print(line)
        #print(line.replace('\n',''),len(line))
        ts=p[0]+' '+p[1]
        measureFloat=float(p[2])
        if '.' in ts:
            tnow=datetime.strptime(ts,'%d/%m/%Y %H:%M:%S.%f')
        else:
            tnow=datetime.strptime(ts,'%d/%m/%Y %H:%M:%S')
        if measureFloat>=minValue and measureFloat<=maxValue:            
            queueData.append((tnow,measureFloat))
        fname=folderOut+os.sep+'AllData_'+datetime.strftime(tnow,'%Y-%m-%d')+'.log'
        fh=open(fname,'a')
        fh.write(format(tnow)+' '+format(measureFloat)+'\n')
        fh.close()
        
      print('resetting Tail')
      time.sleep(1)

def init_file(config, queueData,folderOut):
  print ("---------------------------------------------------")
  print ("Starting read AllData from a file")
  print ("opening ", config['ReadFile'])
  print ("----------------------------")

  minValue=float(config['SonarMinLevel'])
  maxValue=float(config['SonarMaxLevel'])
  
  while True:
      tnow=datetime.utcnow()
      fname=config['ReadFile']
      fname=fname.replace('$DATE',datetime.strftime(tnow,'%Y-%m-%d'))
      print('reading '+fname)
      if os.path.exists(fname):
          f=open(fname,'r')
          rows=f.read().split('\n')
          f.close()

      for line in rows:
        p=line.split(' ')
        #print(line)
        #print(line.replace('\n',''),len(line))
        ts=p[0]+' '+p[1]
        measureFloat=float(p[2])
        if '-' in ts:
            if '.' in ts:
                tnow=datetime.strptime(ts,'%Y-%m-%d %H:%M:%S.%f')
            else:
                tnow=datetime.strptime(ts,'%Y-%m-%d %H:%M:%S')
        else:
            if '.' in ts:
                tnow=datetime.strptime(ts,'%d/%m/%Y %H:%M:%S.%f')
            else:
                tnow=datetime.strptime(ts,'%d/%m/%Y %H:%M:%S')

        if measureFloat>=minValue and measureFloat<=maxValue:            
            queueData.append((tnow,measureFloat))
        fname=folderOut+os.sep+'AllData_'+datetime.strftime(tnow,'%Y-%m-%d')+'.log'
        fh=open(fname,'a')
        fh.write(format(tnow)+' '+format(measureFloat)+'\n')
        fh.close()
        #print('Reading: '+format(tnow)+' '+format(measureFloat))
        #time.sleep(.1)
