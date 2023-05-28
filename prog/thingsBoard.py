import time,os
import datetime
import json
from  process import addMeasure
from alerts import checkAlerts

def getToken(username, pwd, folderOut):
    cmd='curl -X POST --header "Content-Type: application/json" --header "Accept: application/json" -d "{\\"username\\":\\"'+username+'\\", \\"password\\":\\"'+pwd+'\\"}" "http://pumma.kkp.go.id:8080/api/auth/login"'
    
    os.system(cmd+ ' -o '+ folderOut+os.sep+'out.txt')
    if os.path.exists(folderOut+os.sep+'out.txt'):
        with open(folderOut+os.sep+'out.txt') as f:
            testo = f.read()
        
        os.remove(folderOut+os.sep+'out.txt')
        token = testo.split('"')[3]
        return token
    else:
        return ''

def getTokenRead(dev,deviceID,ts1,et1,username,pwd,keys,folderOut,forceToken=False):
    #print(' checking ', folderOut+os.sep+"token" + dev + ".txt  ts1,et1",ts1,et1)
    if os.path.exists(folderOut+os.sep+"token" + dev + ".txt") and not forceToken:
            with open(folderOut+os.sep+"token" + dev + ".txt") as f:
                token=f.read()
    else: 
        token = getToken(username, pwd, folderOut)
        with open(folderOut+os.sep+"token" + dev + ".txt", 'w') as f:
            f.write(token)
    if os.path.exists(folderOut+os.sep+"out.txt"):
        os.remove(folderOut+os.sep+"out.txt")        
    if ts1==-1 and et1==-1:
        cmd= 'curl -X GET  --header "Content-Type: application/json" --header "Accept: application/json" --header "X-Authorization: Bearer ' + token + '" -d "{\\"username\\":\\"' + username + '\\", \\"password\\":\\"' + pwd + '\\"}" "http://pumma.kkp.go.id:8080/api/plugins/telemetry/DEVICE/' + deviceID + '/values/timeseries?keys=' + keys + '&agg=AVG"'
    else:
        cmd= 'curl -X GET  --header "Content-Type: application/json" --header "Accept: application/json" --header "X-Authorization: Bearer ' + token + '" -d "{\\"username\\":\\"' + username + '\\", \\"password\\":\\"' + pwd + '\\"}" "http://pumma.kkp.go.id:8080/api/plugins/telemetry/DEVICE/' + deviceID + '/values/timeseries?keys=' + keys + '&startTs=' + ts1 + '&endTs=' + et1 + '&interval=6000&limit=10000&agg=AVG"'
    #print(cmd)
    os.system(cmd+ ' -o '+ folderOut+os.sep+'out.txt')
    if os.path.exists(folderOut+os.sep+'out.txt'):
        with open(folderOut+os.sep+'out.txt') as f:
            testo = f.read()
        #print(testo)
        os.remove(folderOut+os.sep+'out.txt')
        if "has expired" in testo:
            if os.path.exists(folderOut+os.sep+"token" + dev + ".txt"):
                os.remove(folderOut+os.sep+"token"+ dev + ".txt")
                testo=''
    else:
       testo=''
    return testo

def getfromVector(vect, ts):
    batt = 0
    if not 'ts'in vect:
        for k  in range(len(vect)-1):
            ts3 = datetime.datetime.fromtimestamp(vect[k]['ts']/1000)
            if ts3 >= ts:
                batt = vect[k]['value']
                break
    else:
        batt=vect['value']
    return batt

def procSaveURL(SaveURL,wgetData,config,tt,temp,press,lev,forecast30,forecast300,rms,alertSignal,alertValue,batt,cpuTemp):
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
            SaveURL=SaveURL.replace('$TEMP',format(temp))
            SaveURL=SaveURL.replace('$PRESS',format(press))
            SaveURL=SaveURL.replace('$LEV',"%.3f" % lev)
            SaveURL=SaveURL.replace('$FORE300',"%.3f" % forecast300)
            SaveURL=SaveURL.replace('$FORE30',"%.3f" % forecast30)
            
            SaveURL=SaveURL.replace('$RMS',"%.4f" % rms)
            SaveURL=SaveURL.replace('$ALERT_SIGNAL',"%.3f" % alertValue)
            SaveURL=SaveURL.replace('$ALERT_LEVEL',"%.3f" % alertSignal)
            SaveURL=SaveURL.replace('$V1',format(batt))
            SaveURL=SaveURL.replace('$V2','0')
            SaveURL=SaveURL.replace('$V3',format(cpuTemp))
            SaveURL=SaveURL.replace('$V4','0')
            SaveURL=SaveURL.replace('$V5','0')
            
            #cmd='wget "'+SaveURL+'" -T 2 -r 1 -nv -o outlogwget.txt'
            #cmd='wget "'+SaveURL+'" -nv -o '+folderOut+'/outlogwget.txt -O '+folderOut+'/outwget.txt'
            #print (SaveURL)

            wgetData.append(SaveURL)
            return SaveURL

def scrapeTB(config,wgetData,folderOut):
    print('*************************************')
    print('start scraping:', config['TB_scrapeLogin'])
    print('*************************************')
    #if dev == "IDSL-PUMMA-003":
    #    deviceID = "01b04ed0-24be-11eb-ab95-f53f234a2a89"
    #    username = "kkp@pumma.kkp.go.id"
    #    pwd = "K4K4P3@Th1ngs"
    #    keys = "ch00,ch01,ch02"
    #    model = "PUMMA003"
    #    #  TB_scrapeLogin=01b04ed0-24be-11eb-ab95-f53f234a2a89|kkp@pumma.kkp.go.id|K4K4P3@Th1ngs
    #    #  TB_model=PUMMA003
    #    #  TB_keys = ch00,ch01,ch02

    #elif dev == "IDSL-PUMMA-Lampung-001":
    #    deviceID = "b958de10-dbb3-11eb-80fc-c57ef20eb460"
    #    username = "lampung@pumma.kkp.go.id"
    #    pwd = "L4mpung#pumma"
    #    keys = "tinggi,temperature,tegangan,pressure,suhu"
    #    model = "LAMPUNG"
    #    #  TB_scrapeLogin=b958de10-dbb3-11eb-80fc-c57ef20eb460|lampung@pumma.kkp.go.id|L4mpung#pumma
    #    #  TB_model=LAMPUNG
    #    #  TB_keys = tinggi,temperature,tegangan,pressure,suhu

    
    sl=config['TB_scrapeLogin'] #"http://202.90.199.202/tntmon/loginauth.php"
    deviceID=sl.split('|')[0]
    username=sl.split('|')[1]
    pwd=sl.split('|')[2]
    keys=config['TB_keys']
    model=config['TB_model']
    dev=config['IDdevice']
    bias= (datetime.datetime.now()-datetime.datetime.utcnow()).total_seconds()
    print('bias=', bias)
    tt='';lev=''
    while True:
        endTime=datetime.datetime.utcnow()
        startTime=endTime-datetime.timedelta(seconds=3600)

        if os.path.exists(folderOut+os.sep+'lastRead.txt'):
            try:
                with open(folderOut+os.sep+'lastRead.txt') as f1:
                    lr=f1.read()
                lastread=datetime.datetime.strptime(lr,'%Y-%m-%d %H:%M:%S')
                
                if (endTime-lastread).seconds<3600:
                    startTime=lastread
                    #endTime=startTime+datetime.timedelta(seconds=3600)
            except:
                lastread=datetime.datetime(2022,1,1)  
        else:
            lastread=datetime.datetime(2022,1,1) 
        
        ts1=format(int(bias*1000+time.mktime(startTime.timetuple())*1000))
        et10=format(int(time.mktime(endTime.timetuple())*1000))
        et1=format(int(bias*1000+time.mktime(endTime.timetuple())*1000))
        #print(startTime,endTime,ts1,et1,et10)
          
        testo=getTokenRead(dev,deviceID,ts1,et1,username,pwd,keys,folderOut)
        #print(' -aa-',testo)
        if (testo=='' or testo==None):
            testo1=getTokenRead(dev,deviceID,-1,-1,username,pwd,keys,folderOut)
            testo=testo1
        if not (testo=='' or testo==None):
            err=False
            try:
                
                js=json.loads(testo)
            except  Exception as e:
                print(e)
                err=True
            if not err:
                fnameOut=folderOut+os.sep+config['IDdevice']+'.txt'
                f=open(fnameOut,'a')
                if not keys.split(',')[0] in js:
                    break
                for j in range(len(js[keys.split(',')[0]])):
                    if model=='PUMMA003':
                            if (not 'ch00' in js) :
                                testo1=getTokenRead(dev,deviceID,-1,-1,username,pwd,keys,folderOut,True)
                                break
                            ts=int(js['ch00'][j]['ts'])-bias*1000
                            tt=datetime.datetime.fromtimestamp(ts/1000)
                            lev=float(js['ch00'][j]['value'])
                            if 'ch01' in js:
                                temp=js['ch01'][j]['value']
                            if 'ch02' in js:
                                batt=js['ch02'][j]['value']
                            press=999.
                            cpuTemp=50.
                    elif model=='LAMPUNG':
                            ts=int(js['tinggi'][j]['ts'])-bias*1000
                            tt=datetime.datetime.fromtimestamp(ts/1000)
                            lev=float(js['tinggi'][j]['value'])/100.0
                            cpuTemp=getfromVector(js['temperature'],tt)
                            press=getfromVector(js['pressure'],tt)
                            if 'tenangan' in js:
                              batt=getfromVector(js['tegangan'],tt)
                            else:
                              batt=0
                            temp=getfromVector(js['suhu'],tt)
                    #print(tt,lev)            
                    if tt>lastread:
                        f.write(format(tt)+' '+format(lev)+' '+format(temp)+' '+format(press)+' '+format(batt)+' '+format(cpuTemp)+'\n')
                        lastread=tt
                        forecast30,forecast300,rms,alertSignal,alertValue= addMeasure(config,tt,lev,folderOut)

                        SaveURL=config['SaveURL']
                        SaveURL=procSaveURL(SaveURL,wgetData,config,tt,temp,press,lev,forecast30,forecast300,rms,alertSignal,alertValue,batt,cpuTemp)
                        if 'SaveURL1' in config:
                            SaveURL1=config['SaveURL1']
                            procSaveURL(SaveURL1,wgetData,config,tt,temp,press,lev,forecast30,forecast300,rms,alertSignal,alertValue,batt,cpuTemp)
                        if 'SaveURL2' in config:
                            SaveURL2=config['SaveURL2']
                            procSaveURL(SaveURL2,wgetData,config,tt,temp,press,lev,forecast30,forecast300,rms,alertSignal,alertValue,batt,cpuTemp)
                        #print(tt,mavg)
                        try:
                            riga='time='+format(tt,'%d/%m/%y %H:%M:%S')+'\n'
                            riga+='Level (m)='+"%.3f" % lev +'\n'
                            riga+='Short Term forecast='+"%.3f" % forecast30+'\n'
                            riga+='Long Term forecast='+"%.3f" % forecast300+'\n'
                            riga+='RMS='+"%.4f" % rms+'\n'
                            riga+='Alert Value='+"%.3f" % alertValue+'\n'
                            riga+='Alert Signal='+"%.3f" % alertSignal+'\n'
    
                            if 'folderWWW' in config:
                                folderWWW=config['folderWWW']
                                f1=open(folderWWW+os.sep+'CurrentData.txt','w')
                                f1.write(riga)
                                f1.close()
                            #riga+=format(nd1)
                
                            
                            if 'log=' in SaveURL:                
                                riga=SaveURL.split('log=')[1].replace('$S','').replace('$E','')
                            if 'log$EQ' in SaveURL:
                                riga=SaveURL.split('log$EQ')[1].replace('$S','').replace('$E','')
                            checkAlerts(config,tt,lev,alertValue, folderOut)

                            print(riga)
                
                            fname=folderOut+os.sep+'execLog_'+datetime.datetime.strftime(tt,'%Y-%m-%d')+'.txt'
                            f1=open(fname,'a')
                            f1.write(riga+'\n')
                            f1.close()
                            with open(folderOut+os.sep+'lastRead.txt','w') as f1:
                                f1.write(datetime.datetime.strftime(tt,'%Y-%m-%d %H:%M:%S'))
                        except Exception as e:
                            print(e)
                        time.sleep(0.05)
                
                f.close()
        else:
            print(testo)
    
        print('Sleeping 20sec , last values ', format(tt)+' '+format(lev))
        time.sleep(20)
   

