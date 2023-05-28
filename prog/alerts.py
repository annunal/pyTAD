import datetime
import time
import os,sys
import readConfig as rc
from CONF import printLog

def sendSMS(config, level, alert_signal):
  idDevice=config['IDdevice']
  if '$HOSTNAME' in idDevice:
       idDevice=idDevice.replace('$HOSTNAME',os.uname()[1])

  today=datetime.datetime.utcnow()
  if config['SMSlist']=='':
    return
  template_SMS=config['SMSTemplate']
  if os.path.exists(template_SMS):
    f=open(template_SMS,'r')
    testo=f.read()
    f.close
 
    testo=testo.replace('$TITLE',config['title'])
    
    testo=testo.replace('$DATE',today.strftime("%d %b %Y"))
    testo=testo.replace('$TIME',today.strftime("%H:%M"))
    testo=testo.replace('$LEV',format(level))
    testo=testo.replace('$ALERT_SIGNAL',format(alert_signal))
    testo=testo.replace('$IDdevice',idDevice)
    
    URL=config['SMSURL'].replace('$SMSUSER',config['SMSuser']).replace('$SMSPWD',config['SMSpwd'])
    URL=URL.replace('$SMSLIST',config['SMSlist'])
    URL=URL.replace('$MSG',testo)
    URL=URL.replace('$EQ','=')
    print (URL)
    os.system('wget --output-document=outcmd.txt "'+URL+'"')
    os.system('rm outcmd.txt')
  else:
    print ('*** ERR:  Template file for periodic SMS does not exists:', template_SMS)
    
def sendEMAIL(config, level, alert_signal):
  idDevice=config['IDdevice']
  if '$HOSTNAME' in idDevice:
    idDevice=idDevice.replace('$HOSTNAME',os.uname()[1])
  
  today=datetime.datetime.utcnow()
  if config['EmailTo']=='':
    return
  body_file=config['EmailTemplate']
  subj_file=config['EmailSubject']
 
  if os.path.exists(body_file) and os.path.exists(subj_file):
    f=open(body_file,'r')
    testo=f.read()
    f.close
  
    f=open(subj_file,'r')
    subj=f.read()
    f.close
  
    subj=subj.replace('$TITLE',config['title'])
    subj=subj.replace('$IDdevice',idDevice)
    subj=subj.replace('$ALERT_SIGNAL',format(alert_signal))
    
    testo=testo.replace('$TITLE',config['title'])
    testo=testo.replace('$IDdevice',idDevice)
    testo=testo.replace('$DATE',today.strftime("%d %b %Y"))
    testo=testo.replace('$TIME',today.strftime("%H:%M"))
    testo=testo.replace('$LEV',format(level))
    testo=testo.replace('$ALERT_SIGNAL',format(alert_signal))
    
    URL=config['EmailURL']
    URL=URL.replace('$TO',config['EmailTo'])
    URL=URL.replace('$SUBJ',subj)
    URL=URL.replace('$CONTENT',testo)
    URL=URL.replace('$EQ','=')
    print (URL)
    os.system('wget --output-document=outcmd.txt "'+URL+'"')
    os.system('rm outcmd.txt')
  else:
    print ('*** ERR:  Template file (body or subject)for periodic EMAIL does not exists:', subj_file, body_file)
    

def checkAlerts(config,tt,level,alert_signal,folderOut):
    today=datetime.datetime.utcnow()
    AlertLevel=int(config['AlertLevel'])
    
    # check for SMS and Email
    #print(tt,level,alert_signal,AlertLevel)

    if (alert_signal>AlertLevel):
        newDateFile=folderOut+os.sep+'newDateAlert.txt'
        if os.path.exists(newDateFile):
          f=open(newDateFile,'r')
          newDate_s=f.read()
          f.close()
        else: 
          newDate_s='1 Jan 2000 00:00'

        newDate=datetime.datetime.strptime(newDate_s,'%d %b %Y %H:%M')
        if today>newDate:
          
          idDevice=config['IDdevice']
          if '$HOSTNAME' in idDevice:
            idDevice=idDevice.replace('$HOSTNAME',os.uname()[1])
          print ('sending sms and email')
          if alert_signal>=int(config['AlertLevel']):
            sendSMS(config,level, alert_signal)
            sendEMAIL(config,level, alert_signal)
            
            deltaMin=int(config['AlertTimeInterval'])
  
            newDate=today+datetime.timedelta(minutes=deltaMin)
            newDate_s=newDate.strftime("%d %b %Y %H:%M")
            f=open(newDateFile,'w')
            f.write(newDate_s)
            f.close()

  
        print ('New alert after '+newDate_s +' UTC')
 
    # check for photo
    photoCMD=config['PhotoCMD']
    PhotoAlertLevel=int(config['PhotoAlertLevel'])
    PhotoTimeInterval=float(config['PhotoTimeInterval'])
    LastTimePhotoFile=folderOut+'LastTimePhoto.txt'
    if os.path.exists(LastTimePhotoFile):
      f=open(LastTimePhotoFile,'r')
      LastTimePhoto_s=f.read()
      f.close()
    else: 
      LastTimePhoto_s='1 Jan 2000 00:00'
    LastTimePhoto=datetime.datetime.strptime(LastTimePhoto_s,"%d %b %Y %H:%M")
    
    if photoCMD !='' and alert_signal>PhotoAlertLevel and (today-LastTimePhoto).total_seconds()>PhotoTimeInterval*60:
        LastTimePhoto=datetime.datetime.utcnow()
        photoCMD0=photoCMD
        photoCMD0=photoCMD0.replace("$DATE",today.strftime('%d/%m/%Y'))
        photoCMD0=photoCMD0.replace("$TIME",today.strftime('%H:%M:%S'))
        photoCMD0=photoCMD0.replace("$LEV","%.3f" % level)
        photoCMD0=photoCMD0.replace("$ALERT_SIGNAL",format(alert_signal))
        printLog(photoCMD0)
        os.system(photoCMD0)
        f=open(LastTimePhotoFile,'w')
        f.write(LastTimePhoto.strftime("%d %b %Y %H:%M"))
        f.close()
      




