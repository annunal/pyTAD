import time
import datetime
from datetime import datetime
import serial
import io,os
import math

# http://raspi.tv/how-to-install-wir#ingpi2-for-python-on-the-raspberry-pi
#
#sudo apt-get update#
#
#sudo apt-get install python-dev python-pip
#
#sudo pip install wiringpi2
#
#
#per seriale
#sudo apt-get install python-serial

def init(config, queueData,folderOut, queueMQTT):
  print ("---------------------------------------------------")
  print ("Starting reading sensor")
  print ("opening ", config['Serial'], config['BaudRate'])
  print ("---------------------------------------------------")
  ser = serial.Serial(config['Serial'], baudrate=config['BaudRate'],
                      parity=serial.PARITY_NONE,
                      stopbits=serial.STOPBITS_ONE,
                      bytesize=serial.EIGHTBITS
                      )
  
  time.sleep(1)
  minValue=float(config['SonarMinLevel'])
  maxValue=float(config['SonarMaxLevel'])
  
  ndata=0
  try:
    print ('Data Echo Mode Enabled')
    measure=''
    while True:
        if ser.inWaiting() > 0:
            try:            
                data = ser.read().decode('utf8')
            except:
                data=''
            if (data=='\r'):
              
              try:
                 measure=measure.replace('\n','')
                 measureFloat=maxValue+1.
                 if 'R' in measure:
                    try:
                        measureFloat=float(measure.split('R')[1])/1000
                    except:
                        measureFloat=maxValue+1.
                 #sprint ('measure=',measure,measureFloat)
                 # verifica che sia tra i limiti  
                 if measureFloat>=minValue and measureFloat<=maxValue:
                   tnow=datetime.now()
                   #print(tnow,measureFloat,len(queueData))
                   queueData.append((tnow,measureFloat))
                   queueMQTT.append((tnow,measureFloat))
                   # writing on file
                   fname=folderOut+os.sep+'AllData_'+datetime.strftime(tnow,'%Y-%m-%d')+'.log'
                   fh=open(fname,'a')
                   fh.write(format(tnow)+' '+format(measureFloat)+'\n')
                   fh.close()
                   #print(format(tnow)+' '+format(measureFloat))
                   measure=''           
                 else:
                   measure=''               
              except TypeError as e:
                print ('error in data  measure=',measure, '  e=',e)
                measure=''                          
            else:
               measure+=data

  except serial.SerialException as e:
     print ("Serial error ",e)
     pass    
  except KeyboardInterrupt:
      print ("Exiting Program")
 
  except TypeError as e:
      print ("Error Occurs, Exiting Program ",e)
  
  finally:
      ser.close()
      pass

