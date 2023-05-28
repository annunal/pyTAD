import datetime
import time
import os,sys
import readConfig as rc
from CONF import folderOut, FTP_update_Prog, folderProg, config

 
def sendPeriodicSMS(config, level):
  today=datetime.datetime.utcnow()
  template_SMS=config['TemplatePeriodic_SMS_Msg']
  idDevice=config['IDdevice'].replace('$HOSTNAME',os.uname()[1])
  if os.path.exists(template_SMS):
    f=open(template_SMS,'r')
    testo=f.read()
    f.close
 
    testo=testo.replace('$TITLE',config['title'])
    
    testo=testo.replace('$DATE',today.strftime("%d %b %Y"))
    testo=testo.replace('$TIME',today.strftime("%H:%M"))
    testo=testo.replace('$LEV',"{0:.2f}".format(level))
    testo=testo.replace('$IDdevice',idDevice)
    
    URL=config['SMSURL'].replace('$SMSUSER',config['SMSuser']).replace('$SMSPWD',config['SMSpwd'])
    URL=URL.replace('$SMSLIST',config['SMSlistPeriodic'])
    URL=URL.replace('$MSG',testo)
    URL=URL.replace('$EQ','=')
    print (URL)
    os.system('wget --output-document=outcmd.txt "'+URL+'"')
    os.system('rm outcmd.txt')
  else:
    print ('*** ERR:  Template file for periodic SMS does not exists:', template_SMS)
    
def sendPeriodicEMAIL(config, level):
  today=datetime.datetime.utcnow()
  body_file=config['TemplatePeriodic_EMAIL_Body']
  subj_file=config['TemplatePeriodic_EMAIL_Subj']
  idDevice=config['IDdevice'].replace('$HOSTNAME',os.uname()[1])
  if os.path.exists(body_file) and os.path.exists(subj_file):
    f=open(body_file,'r')
    testo=f.read()
    f.close
  
    f=open(subj_file,'r')
    subj=f.read()
    f.close
  
    subj=subj.replace('$TITLE',config['title'])
    subj=subj.replace('$IDdevice',idDevice)
    
    testo=testo.replace('$TITLE',config['title'])
    testo=testo.replace('$IDdevice',idDevice)
    testo=testo.replace('$DATE',today.strftime("%d %b %Y"))
    testo=testo.replace('$TIME',today.strftime("%H:%M"))
    testo=testo.replace('$LEV',"{0:.2f}".format(level))
    
    URL=config['EmailURL']
    URL=URL.replace('$TO',config['EmailToPeriodic'])
    URL=URL.replace('$SUBJ',subj)
    URL=URL.replace('$CONTENT',testo)
    URL=URL.replace('$EQ','=')
    print (URL)
    os.system('wget --output-document=outcmd.txt "'+URL+'"')
    os.system('rm outcmd.txt')
  else:
    print ('*** ERR:  Template file (body or subject)for periodic EMAIL does not exists:', subj_file, body_file)
     

def checkPeriodic(config,level,folderOut):
    today=datetime.datetime.utcnow()
    if not 'Periodic_hour' in config:
            print('PeriodicChecks: exiting because no periodic hour exists in config')
            return
    try:
        newDateFile=folderOut+os.sep+'newDatePeriodic.txt'

        if os.path.exists(newDateFile):
          f=open(newDateFile,'r')
          newDate_s=f.read().replace('\n','')
          f.close()
        else: 
          delta=0
          Hour=config['Periodic_hour']
          newDate=today+datetime.timedelta(days=delta)
          newDate_s=today.strftime("%d %b %Y ")+Hour
          newDate=datetime.datetime.strptime(newDate_s,'%d %b %Y %H:%M')
          print ('newDate =',newDate )
          if newDate<today: 
            delta=1
            newDate=today+datetime.timedelta(days=delta)
            newDate_s=newDate.strftime("%d %b %Y ")+Hour
            print (newDate_s)
            datetime.datetime.strptime(newDate_s,'%d %b %Y %H:%M')

          f=open(newDateFile,'w')
          f.write(newDate_s)
          f.close()

        newDate=datetime.datetime.strptime(newDate_s,'%d %b %Y %H:%M')

        print (today,newDate, 'UTC',today>newDate)

        if today>newDate:
          idDevice=config['IDdevice'].replace('$HOSTNAME',os.uname()[1])
          print ('sending sms and email')
          sendPeriodicSMS(config,level)
          sendPeriodicEMAIL(config,level)
          f=open(newDateFile,'w')
          try:
            delta=int(config['Periodic_delta'])
          except:
            delta=1
          Hour=config['Periodic_hour']
          newDate=today+datetime.timedelta(days=delta)
          newDate_s=newDate.strftime("%d %b %Y ")+Hour
          f.write(newDate_s)
          f.close()

  
        print ('New check '+newDate_s +' UTC')
    except Exception as e:
        print('error in periodic ',e)
def killAllProgs(nleave=0):
    fnameout='/tmp/outtmp.txt'
    if not os.path.exists(folderOut):
        os.makedirs(folderOut)
    cmd="sudo ps -efd |  grep 'python3 tad.py' > "+fnameout
    os.system(cmd)
    print(cmd)
    with open(fnameout,'r') as f:
        rows=f.read().split('\n')

    nitems=len(rows)-3
    nkilled=0
    for line in rows:
        if not 'grep' in line and 'python3 tad.py' in line:
            p=line.split()
            process=p[1]
            cmd='kill -9 '+process
            print(cmd)
            os.system(cmd)
            nkilled +=1
            nkilled +=1
            if nleave>0:
                if nitems-nkilled==nleave:   #  1 per lasciarne uno solo
                    break

def updateProg():
    today=datetime.datetime.utcnow().strftime('%Y%m%d-%H%M%S')
    fprog=folderOut+os.sep+'pyTAD_'+today+'.zip'
    from ftplib import FTP
    import shutil
    with FTP(host='139.191.244.76') as ftp:
         ftp.login('TAD_user','Ecml2011')
         ftp.cwd('software')
         ftp.dir()
         filename='pyTAD.zip'
         with open( fprog, 'wb' ) as file :
            ftp.retrbinary('RETR %s' % filename, file.write)  
         file.close()
         ftp.quit()

    if os.path.exists(fprog):
        from zipfile import ZipFile

        with ZipFile(fprog, 'r') as zipObj:
           # Extract all the contents of zip file in current directory
           if not os.path.exists(folderOut+os.sep+'tmp'):
                os.makedirs(folderOut+os.sep+'tmp')
           zipObj.extractall(folderOut+os.sep+'tmp')
    
        #copio tutti i files
        for (dirpath,dirnames,filenames) in os.walk(folderOut+os.sep+'tmp'):
            fold=dirpath.replace(folderOut+os.sep+'tmp',folderProg)
            if not os.path.exists(fold):
                os.makedirs(fold)
            for f in filenames:   
                f1=f
                if f1=='config.txt':
                    f1='config_ftp.txt'
                print('copying ',f1)
                shutil.copyfile(dirpath+os.sep+f, fold+os.sep+f1)
        shutil.rmtree(folderOut+os.sep+'tmp')          
        killAllProgs()   
        os.system('python3 checkkRunningpyTAD.py')

def checkCommands(config):
    folderWWW=config['folderWWW']
    idDevice=config['IDdevice'].replace('$HOSTNAME',os.uname()[1])
    print(folderWWW+os.sep+idDevice+'_COMMANDS.TXT')
    print(os.path.exists(folderWWW+os.sep+idDevice+'_COMMANDS.TXT'))
    if os.path.exists(folderWWW+os.sep+idDevice+'_COMMANDS.TXT'):
        with open(folderWWW+os.sep+idDevice+'_COMMANDS.TXT') as f:
            rows=f.read().split('\n')
        print(rows)
        os.remove(folderWWW+os.sep+idDevice+'_COMMANDS.TXT')
        if os.path.exists(folderWWW+os.sep+idDevice+'_OUTCOMMANDS.TXT'):
            os.remove(folderWWW+os.sep+idDevice+'_OUTCOMMANDS.TXT')
        for line in rows:
            cmd=line +'>>'+folderWWW+os.sep+idDevice+'_OUTCOMMANDS.TXT'
            if cmd=='UPDATE_PYTAD':
                updateProg()
                os.kill(os.getpid(), 9)
            else:
                os.system(cmd)

if __name__ == "__main__":
    arguments = sys.argv[1:]
    count = len(arguments)
    print (count)
    
    if arguments[0]=='CHECKCOMMANDS':
        checkCommands(config)
    elif arguments[0]=='UPDATE_PYTAD':
        updateProg()
    elif arguments[0]=='PERIODIC':
        checkPeriodic(config,1.01,folderOut)
    elif arguments[0]=='testSocket':
        URL=arguments[1]
