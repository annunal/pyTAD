#!/usr/bin/python3
#  python TAD programme for IDSL
#  
#  required packages:
#     - python3, pip3
#     sudo apt-get update
#     if python3 is not instaled:
#          sudo apt-get install python3
#     sudo apt-get install python3-pip
#     sudo pip3 install wiringpi2
#     sudo pip3 install pyserial
#     NO xxxsudo pip3 install sh
#     sudo pip3 install smbus
#     if pressure sensor:
#         sudo pip3 install adafruit-circuitpython-bmp3xx
# sudo apt-get install libatlas-base-dev
# sudo pip3 install pybind11
# sudo pip3 install numpy  --upgrade
# sudo pip3 install psutil
# sudo pip install pycountry-convert

#  TODO:
#  
#     DONE restart 
#     DONE check if long time passed since last datum  online
#     DONE webcam alert
#     DONE alerts, SMS etc
from CONF import folderData, folderOut,machine,config,is_raspberrypi,listConfigs,debugSession
import os
import time
import threading
import multiprocessing
import io
import readConfig as rc
from periodicChecks import  checkPeriodic,checkCommands
import process as pr
import wgetProc as wg
import sys

queueData=[]
queueMQTT=[]
wgetData=[]
adcData={}
adcData['batteryValue']=-1
adcData['panelValue']=-1
adcData['tempValue']=-1
adcData['tempCPU']=-1
adcData['pressure']= 0.0
adcData['temperature380']= 0.0
adcData['SensorLevel']=-1000


print(machine)
print(machine=='raspberry')

if 'Serial' in config:
    import readLevelSensor as lev
if machine=='raspberry':
    import readADC as adc
    import readCPUTemp as rcpu
if config['MQTT_listener'] !='' or config['MQTT_server']!='':   
    import mqtt_client as mq
    
processes=[]
procScrapMulti=[]
is_raspberry=is_raspberrypi()
t1a=None

print ('---------------- start of config-----------------\n\n')
for i in config:
       print (i,'=',config[i])
print ('---------------- end of config-----------------\n\n')

if config['MQTT_server'] !='':
    t0 =threading.Thread(target=mq.init_push, args=(config,queueMQTT,adcData,folderOut))
    #t0 = threading.Thread(target=rcpu.init, args=(config,adcData,10))
    t0.start()
    processes.append((t0,'mqtt push'))

print (config['Tail']+'-'+config['TailSimple']+'-'+config['ReadFile']+'-'+config['MQTT_listener'])    
if 'Serial' in config: 
    t1 = threading.Thread(target=lev.init, args=(config,queueData,folderOut,queueMQTT))
    processes.append((t1,'Serial level read'))
if config['Tail'] !='':
    import readAllData as rall
    t1a = threading.Thread(target=rall.init, args=(config,queueData,folderOut))
    processes.append((t1a, 'ReadAll Init'))
    
elif config['TailSimple'] !='':
    import readAllData as rall
    print('starting TailSimple=',config['TailSimple'])
    t1a = threading.Thread(target=rall.init_simple, args=(config,queueData,folderOut))
    processes.append((t1a, 'ReadAll Simple'))
    
elif config['ReadFile'] !='':
    import readAllData as rall
    t1a = threading.Thread(target=rall.init_file, args=(config,queueData,folderOut))
    processes.append((t1a, 'ReadAll Init_file'))

elif config['scrapePage'] !='' and len(listConfigs)==0:
    if config['scrapePage']=='ThingBoard':
        import thingsBoard as tb
        t1a = threading.Thread(target=tb.scrapeTB, args=(config,wgetData,folderOut))
        processes.append((t1a, 'scrapeTB'))
        t1a.start()
    elif config['scrapePage']=='BIG_ID_SRG':
        import scrape as sc
        t1a = threading.Thread(target=sc.scrape_BIG_ID_SRG, args=(config,wgetData,folderOut))
        processes.append((t1a, 'scrape BIG_ID_SRG'))
    elif config['scrapePage']=='TAD_SERVER':
        import scrape as sc
        t1a = threading.Thread(target=sc.scrape_TAD_server, args=(config,wgetData,folderOut))
        processes.append((t1a, 'scrape TAD_SERVER'))

    elif config['scrapePage']=='BIG_ID_INA':
        import scrape as sc
        t1a = threading.Thread(target=sc.scrape_BIG_INA, args=(config,wgetData,folderOut))
        processes.append((t1a, 'scrape BIG_INA'))
    elif config['scrapePage']=='GLOSS':
        import scrape as sc
        t1a = threading.Thread(target=sc.scrape_GLOSS, args=(config,folderOut))
        processes.append((t1a, 'scrape GLOSS'))
        t1a.start()
    elif config['scrapePage']=='DART':
        import scrape as sc
        t1a = threading.Thread(target=sc.scrape_DART, args=(config,folderOut))
        processes.append((t1a, 'scrape DART'))
        t1a.start()

    elif config['scrapePage']=='TR':
        import scrape as sc
        t1a = threading.Thread(target=sc.scrape_TR, args=(config,folderOut))
        processes.append((t1a, 'scrape TR'))
        print('t1a isalive',t1a.is_alive())
        t1a.start()
    elif config['scrapePage']=='INCOIS':
        import scrape as sc
        t1a = threading.Thread(target=sc.scrape_INCOIS, args=(config,folderOut))
        processes.append((t1a, 'scrape INCOIS'))
        print('t1a isalive',t1a.is_alive())
        t1a.start()
    elif config['scrapePage']=='OTT_plane':
        import scrape as sc
        t1a = threading.Thread(target=sc.scrape_OTT, args=(config,folderOut))
        processes.append((t1a, 'scrape OTT'))
        print('t1a isalive',t1a.is_alive())
        t1a.start()    
    elif config['scrapePage']=='EXECLOG':
        import scrape as sc
        t1a = threading.Thread(target=sc.read_execLog_IDSL, args=(config,wgetData))
        processes.append((t1a, 'scrape EXECLOG'))
        print('t1a isalive',t1a.is_alive())
        t1a.start()

    else:
        import scrape as sc
        t1a = threading.Thread(target=sc.scrape_init, args=(config,wgetData,folderOut))
        processes.append((t1a, 'scrape'))
        t1a.start()
elif config['scrapePage'] !='' and len(listConfigs)!=0:
        import scrape as sc
        for j in range(len(listConfigs)):
            lc=listConfigs[j]
            desc='multi scrape  '+format(j)
            t1a = threading.Thread(target=sc.multi_scrape, args=(desc,config,wgetData,lc))
            t1a.start()
            procScrapMulti.append((t1a, desc))


elif config['MQTT_listener'] !='':
    print('definisco t1a')
    t1a =threading.Thread(target=mq.init_listen, args=(config,queueData,adcData,queueMQTT,folderOut))
    #t1a.start()
    processes.append((t1a, 'ReadAll mqtt listen'))

elif config['TCP_host'] !='':
    import scrape as sc
    print('definisco t1a')
    t1aM =threading.Thread(target=sc.scrape_TCP, args=(config,queueData,folderOut))
    #t1a.start()
    processes.append((t1aM, 'Listen TCP port'))
    t1aM.start()

if 'MQTT_AzureIOTHub_PUSH_conn_str' in config:
    import mqtt_azure as ma
    
    taz =threading.Thread(target=ma.init_push, args=(config,queueMQTT,adcData,folderOut))
  
    processes.append((taz, 'MQTT Azure push'))
    taz.start()
if 'MQTT_AzureIOTHub_LISTEN_conn_str' in config:
    import mqtt_azure as ma
    
    taL =threading.Thread(target=ma.Azure_Listen, args=(config,queueData,adcData,queueMQTT,folderOut))
  
    processes.append((taL, 'MQTT Azure listen'))
    taL.start()   

if config['scrapePage']=='':
    t2 = threading.Thread(target=pr.process5Sec, args=(config,queueData,adcData,wgetData,folderOut,queueMQTT))
    processes.append((t2,'process5s'))

if machine=='raspberry' and config['MQTT_listener'] =='':
    t3 = threading.Thread(target=adc.init, args=(config,adcData,10,))
    t4 = threading.Thread(target=rcpu.init, args=(config,adcData,10))
    processes.append((t4,'readCPU temp'))
    processes.append((t3,'read ADC'))

t5 = threading.Thread(target=wg.wgetProc, args=(config,wgetData,0.25,folderOut,debugSession))
processes.append((t5,'wget process'))

if config['pressureSensor'] !=''  and machine=='raspberry' and config['MQTT_listener'] =='':
    import bmp380_ada as bmp
    t6 = threading.Thread(target=bmp.init, args=(config,adcData,10,folderOut))
    processes.append((t6,'BMP Process'))
    
    
for t,desc in processes:
        print(desc)
        t.deamon=True

 
if 'Serial' in config: 
    t1.start()

if not t1a==None : #.is_alive():    
    if not t1a.is_alive():    
        if len(listConfigs)==0 and config['scrapePage']+config['Tail']+config['TailSimple']+config['ReadFile']+ config['MQTT_listener'] !='':
            print('starting t1a ',t1a.is_alive())
            t1a.start()

if config['scrapePage']=='':    
    t2.start()   #Process5s

if machine=='raspberry'  and config['MQTT_listener'] =='':
    t3.start()
    t4.start()

t5.start()  #  wget

    
if config['pressureSensor'] !='' and machine=='raspberry'  and config['MQTT_listener'] =='':
    t6.start()
    

        
def checkProcesses(procs, procsMulti):
    while True:
        n=0
        for t,desc in procs:
          n +=1
          if not t.is_alive():
              print('one of the threads is not alive, exiting:',n,desc)
              os.kill(os.getpid(), 9)
              sys.exit()
        if len(procsMulti)>0:
            OneAlive=False
            for t,desc in procsMulti:
              n +=1
              if t.is_alive():
                  print('proc multi',n,t.is_alive())
                  OneAlive=True
            if not OneAlive:
                  print('all processes multi scraping finished,  ending')
                  os.kill(os.getpid(), 9)
                  sys.exit()

        time.sleep(10)
        #print('all processes running ',len(procs))

tcontrol=threading.Thread(target=checkProcesses, args=(processes, procScrapMulti,))  
time.sleep(30) 
tcontrol.start()
    
while True:
  #print('adcData=',adcData)  
  #if adcData['SensorLevel'] !=-1000:
  print('checking periodic tasks')
  checkPeriodic(config,adcData['SensorLevel'],folderOut)
  if config['folderWWW'] !='':
      try:
          if is_raspberry:
            checkCommands(config) 
      except:
          print(' error un runCommands')
  time.sleep(30)

  #  -s "D:\mnt\DISKD\BIG_SRG" 