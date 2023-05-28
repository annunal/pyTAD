import ftplib
from CONF import config, folderOut
import json,os,sys,ssl
import urllib
from datetime import datetime, timedelta
import time
from urllib.request import urlopen
import urllib
import uuid

from alerts import checkAlerts

from readConfig import readConfig
import requests

import xml.etree.ElementTree as ET
import urllib.parse, urllib.request, urllib.error



def saveData(config,wgetData,folderOut,tt,press,temp,measure_Float,forecast30,forecast300,rms,alertValue,alertSignal,batt,tempCPU,temp380):
        SaveURL=config['SaveURL']
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
        SaveURL=SaveURL.replace('$TEMP','22')
        SaveURL=SaveURL.replace('$PRESS','908')
        SaveURL=SaveURL.replace('$LEV',"%.3f" % measure_Float)
        SaveURL=SaveURL.replace('$FORE300',"%.3f" % forecast300)
        SaveURL=SaveURL.replace('$FORE30',"%.3f" % forecast30)
                
        SaveURL=SaveURL.replace('$RMS',"%.4f" % rms)
        SaveURL=SaveURL.replace('$ALERT_SIGNAL',"%.3f" % alertValue)
        SaveURL=SaveURL.replace('$ALERT_LEVEL',"%.3f" % alertSignal)
        SaveURL=SaveURL.replace('$V1','%.2f' % batt)
        SaveURL=SaveURL.replace('$V2','%.1f' % 0.0)
        SaveURL=SaveURL.replace('$V3','%.3f' % tempCPU)
        SaveURL=SaveURL.replace('$V4','%.3f' % temp380)

        SaveURL=SaveURL.replace('$V1','0')
        SaveURL=SaveURL.replace('$V2','0')
        SaveURL=SaveURL.replace('$V3','0')
        SaveURL=SaveURL.replace('$V4','0')
        SaveURL=SaveURL.replace('$V5','0')
                
        #cmd='wget "'+SaveURL+'" -T 2 -r 1 -nv -o outlogwget.txt'
        #cmd='wget "'+SaveURL+'" -nv -o '+folderOut+'/outlogwget.txt -O '+folderOut+'/outwget.txt'
        #print (SaveURL)

        wgetData.append(SaveURL)
        #print(tt,mavg)
        try:
            riga='time='+format(tt,'%d/%m/%y %H:%M:%S')+'\n'
            riga+='Level (m)='+"%.3f" % measure_Float +'\n'
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
                    
            riga=SaveURL.split('log=')[1].replace('$S','').replace('$E','')
            riga +=' ( wget:'+format(len(wgetData))+')'
            checkAlerts(config,tt,measure_Float,alertValue, folderOut)

            print(riga)
                    
            fname=folderOut+os.sep+'execLog_'+datetime.strftime(tt,'%Y-%m-%d')+'.txt'
            f1=open(fname,'a')
            f1.write(riga+'\n')
            f1.close()
            with open(folderOut+os.sep+'lastRead.txt','w') as f1:
                f1.write(datetime.strftime(tt,'%Y-%m-%d %H:%M:%S'))

        except Exception as e:
            print(e)

def scrape_init(config,wgetData,folderOut):
    from  process import addMeasure
    from calcAlgorithm import calcAlgorithm as ca
    session_requests = requests.session()
    tt='';measure_Float=''
    sl=config['scrapeLogin'] #"http://202.90.199.202/tntmon/loginauth.php"
    if '@http' in sl:
        login_url=sl.split('@')[1]
        uname=sl.split('@')[0].split(':')[0]
        pwd=sl.split('@')[0].split(':')[1]
        payload={ "username":uname,"password":pwd, "submit":"Login"}
    else:
        login_url=sl
    while True:
        login_ref=login_url 
        result = session_requests.get(login_url)

        result = session_requests.post(
            login_url,
            data = payload,
            headers = dict(referer=login_ref)
        )
        res=result.content
        fnameOut=folderOut+os.sep+config['IDdevice']+'.txt'
        if os.path.exists(folderOut+os.sep+'lastRead.txt'):
            try:
                with open(folderOut+os.sep+'lastRead.txt') as f1:
                    lr=f1.read()
                lastread=datetime.strptime(lr,'%Y-%m-%d %H:%M:%S')
            except:
                lastread=datetime(2022,1,1)  
        else:
            lastread=datetime(2022,1,1)  
        
        while True:
            t0=datetime.utcnow() -timedelta(seconds=3600)
            t1=datetime.utcnow()
            tstart=t0.strftime('%Y-%m-%d %H:%M:%S')
            tend=t1.strftime('%Y-%m-%d %H:%M:%S')

            url=config['scrapePage'] 
            url=url.replace('$DATESTART',tstart)
            url=url.replace('$DATEEND',tend)
            url=url.replace('$EQ','=')
            print(url)
            try:
                result = session_requests.get(
                     url,
                     headers = dict(referer = url)
                )
            except:
                break
            res=result.content
            if res.decode() !='':
                js=json.loads(res)

                radData=js['DATA']['RAD']
                #preData=js['DATA']['BAR']
        
                f=open(fnameOut,'a')
                for j in range(len(radData)):
                
                    rd=radData[len(radData)-j-1]
                    t,v=rd
            
                    try:
                        tt = datetime.fromtimestamp(t/1000) #- timedelta(seconds=2*3600)  # on azure there is no need for this
                        measure_Float=float(v)
                        #print(format(tt)+', '+format(measure_Float))
                    except:
                        print('errore',t,measure_Float)
                    
                    if tt>lastread:
                        f.write(format(tt)+' '+format(measure_Float)+'\n')
                        lastread=tt
                        forecast30,forecast300,rms,alertSignal,alertValue= addMeasure(config,tt,measure_Float,folderOut)
                        saveData(config,wgetData,folderOut,tt,908,22,measure_Float,forecast30,forecast300,rms,alertValue,alertSignal,0,0,0)

                        time.sleep(0.05)
                    
                f.close()
    
            print('Sleeping 1 min , last values ', format(tt)+' '+format(measure_Float))
            time.sleep(60)
        time.sleep(60)   

def scrape_TCP(config,queueData,folderOut):
    import socket,time

    #HOST = '62.48.216.99'  # Standard loopback interface address (localhost)
    #PORT = 4001  # Port to listen on (non-privileged ports are > 1023)
    HOST=config['TCP_host']
    PORT=int(config['TCP_port'])
    while True:
        t0=datetime.utcnow()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            stream=''
            while True:
                try: 
                    data = s.recv(1024).decode()
                    connected=True
                except socket.error as msg:
                    print("disconnected")
                    s.close()
                    connected=False
                if connected:            
                    if config['TCP_type']=='SECIL':
                        levs=data.split('\n\r')

                        for lev in levs:
                            if lev !='':
                                tt=datetime.utcnow()
                                queueData.append((tt,float(lev)))
                                fname=folderOut+os.sep+'AllData_'+datetime.strftime(tt,'%Y-%m-%d')+'.log'
                                fh=open(fname,'a')
                                fh.write(format(tt)+' '+format(lev)+'\n')
                                fh.close()
                                #print(tt,lev)
                                #forecast30,forecast300,rms,alertSignal,alertValue= addMeasure(tt,lev,folderOut)
                                #saveData(config,wgetData,folderOut,tt,908,22,lev,forecast30,forecast300,rms,alertValue,alertSignal,0,0,0)     
                    elif config['TCP_type']=='MIROS-IS':
                        levs=data.split('\r\n')
                        #print (levs)
                        for lev in levs:

                            if lev !='' and lev.startswith('$YXXDR'):
                                tt=datetime.utcnow()
                                floatLev=lev.split(',')[2]
                                queueData.append((tt,float(floatLev)))
                                fname=folderOut+os.sep+'AllData_'+datetime.strftime(tt,'%Y-%m-%d')+'.log'
                                fh=open(fname,'a')
                                fh.write(format(tt)+' '+format(lev)+'\n')
                                fh.close()
                                #print(tt,lev)
                                #forecast30,forecast300,rms,alertSignal,alertValue= addMeasure(tt,lev,folderOut)
                                #saveData(config,wgetData,folderOut,tt,908,22,lev,forecast30,forecast300,rms,alertValue,alertSignal,0,0,0)     
                    time.sleep(0.1)
                    t1=datetime.utcnow()
                    #print('time from opening: ',(t1-t0).seconds)
                    if (t1-t0).seconds>3600:
                        print('close connection and restart')
                        break
                    else:
                        t0=t1
                else:
                    break
        time.sleep(1)       

def saveSamples(config,calg,data,ncols,folderConfig, folderOut):
    from  process import addMeasure,readBuffer,saveBuffer
    logData=''
    kj=-1
    redisObj=None
    for tim,samp in data:
        logDataAdd=''
        overallDict={}
        for k in range(ncols):
            if ncols>1:
                measure_Float=samp[k]
            else:
                if type(samp)==list:
                    measure_Float=samp[0]
                else:
                    measure_Float=samp
            if measure_Float==None:
                continue
            try:
                forecast30,forecast300,rms,alertSignal,alertValue= calg[k].addMeasure(tim,measure_Float,folderConfig,k)
                checkAlerts(config ,tim, measure_Float, alertSignal,folderConfig)
                logDataAdd = calg[k].prepareString(k,config, tim, measure_Float,forecast30,forecast300,rms,alertSignal,alertValue, logDataAdd)
                if 'REDISserver' in config:
                    overallDict=calg[k].prepareREDIS(overallDict,k,config, tim, measure_Float,forecast30,forecast300,rms,alertSignal,alertValue, logDataAdd)                    
                saveBuffer(calg[k]._x300,calg[k]._y300,calg[k]._yavg30,calg[k]._yavg300,folderConfig,k)
            except Exception as e:
                print(e)
        if 'REDISserver' in config:
            resp,redisObj=calg[k].sendREDIS(config,overallDict,redisObj)
        logDataAdd=logDataAdd.replace('$V1','0')
        logDataAdd=logDataAdd.replace('$V2','0')
        logDataAdd=logDataAdd.replace('$V3','0')
        if 'inp1' in logDataAdd or '$LEV' in logDataAdd or '$LEV_2' in logDataAdd or '$LEV' in logDataAdd:
            logDataAdd=logDataAdd
        else:
            logData += logDataAdd +'\n'
        print('.......'+logDataAdd[:80])
        fname=folderOut+os.sep+'execLog_'+datetime.strftime(tim,'%Y-%m-%d')+'.txt'
        with open(fname,'a') as f1:
            f1.write(logDataAdd+'\n')

        with open(folderConfig+os.sep+'lastRead.txt','w') as f1:
            f1.write(datetime.strftime(tim,'%Y-%m-%d %H:%M:%S'))
        oldDat = tim
        oldvalue = measure_Float
        newData = True

        #File.WriteAllText("lastValue.txt", Format(tim, "dd MMM yyyy HH:mm") & ", " & Format(value, "#0.00"))
        kj+=1
       
        if (int(kj / 20) * 20 == kj or kj==len(data)-1) and config['SaveURL'] !='':
            uploadToURL(config['SaveURL'],logData,config['IDdevice'])
            if 'SaveURL1' in config:
                uploadToURL(config['SaveURL1'],logData,config['IDdevice'])
            if 'SaveURL2' in config:
                uploadToURL(config['SaveURL2'],logData,config['IDdevice'])

            kj=0
            logData=''
            newData=False

def uploadToURL(SaveURL,logData,idDevice):
        URL = SaveURL.split( "log=")[0]+"log=" + logData
        URL = URL.replace("$IDdevice", idDevice)
        try:
            x=requests.get(URL)
            print(x.text)
        except Exception as e:
            x=''
        return x

def scrape_BIG_ID_SRG(config,wgetData,folderOut,killProcess=True):
    from CONF import folderConfig
    from  process import readBuffer
    from calcAlgorithm import calcAlgorithm as ca
    settings=readConfig('',folderConfig+os.sep+config['settingsFile'])
    calg={}
    ncols=1
    for j in range(ncols):
        buffer=readBuffer(folderConfig, int(config['n300']),j)
        calg[j]=ca(j,folderConfig,config,buffer)
    if os.path.exists(folderConfig+os.sep+'lastRead.txt') :
        with open (folderConfig+os.sep+'lastRead.txt') as f:
            ts=f.read()
            LastDateTimeAcquired=datetime.strptime(ts,'%Y-%m-%d %H:%M:%S')
    else:
        LastDateTimeAcquired=calg[0]._LastDateTimeAcquired

    URL=config['serverAddress']    
    URL=URL.replace("$DAY",datetime.utcnow().strftime('%Y-%m-%d'))
    context = ssl._create_unverified_context()
    resp=urllib.request.urlopen(URL,context=context)
    #URL='https://srgi.big.go.id/api/pasut/stations'
    #resp=requests.get(URL)
    respText=resp.read().decode("utf-8")
    respText=respText.split('{"results":')[1]
    respText='{"results":'+respText
    measures=json.loads(respText)
    kj=0
    logData = ""
    data=[]
    for meas in measures['results']:
        ts=meas['ts']
        found=False
        if 'RAD1' in meas:
            value=meas['RAD1'];found=True
        elif 'PRS1' in meas:
            value=meas['PRS1'];found=True
        elif 'ENC1' in meas:
            value=meas['ENC1'];found=True
        if found:
            tim=datetime.strptime(ts,'%Y-%m-%d %H:%M:%S')
            tim0=tim
            if tim > LastDateTimeAcquired:
                samp=[]
                for k in range(ncols):
                    try:
                        measure_Float = float(value)
                    except Exception as e:
                            print(e)
                    samp.append(measure_Float)
                data.append((tim,samp))

    saveSamples(config,calg,data,ncols,folderConfig, folderOut)  
    if killProcess:
        os.kill(os.getpid(), 9)

def scrape_BIG_INA(config,wgetData,folderOut):
    from CONF import folderConfig
    from  process import readBuffer
    from calcAlgorithm import calcAlgorithm as ca
    settings=readConfig('',folderConfig+os.sep+config['settingsFile'])
    
    URL=config['serverAddress']    
    URL=URL.replace("$DAY",datetime.utcnow().strftime('%Y-%m-%d'))
    with open(folderConfig+os.sep+'html.htm') as f:
        testo=f.read()
    #response=urlopen(URL)
    #testo=response.read().decode("utf-8")
    tabe = testo.split("<table class='table table-striped'>")[1].split("</table>")[0]
    lines = tabe.split("<tr>")
    ncols=int(config['ncols'])
    
    
    calg={}
    for j in range(ncols):
        buffer=readBuffer(folderConfig, int(config['n300']),j)
        calg[j]=ca(j,folderConfig,config,buffer)

    kj=0
    logData = ""
    data=[]
    for line0 in lines[3:]:
        line = line0.replace( "<td>", "")
        if line.strip() != "":
            p = line.split( "</td>")
            tim = datetime.strptime(p[1],'%Y-%m-%d %H:%M:%S')
            print(tim,calg[1]._LastDateTimeAcquired)

            if tim > calg[1]._LastDateTimeAcquired:
                samp=[]
                for k in range(ncols):
                    try:
                        measure_Float = float(p[k +2])
                    except Exception as e:
                            print(e)
                    samp.append(measureFloat)
                data.append((tim,samp))

    saveSamples(config,calg,data,ncols,folderConfig)    
    os.kill(os.getpid(), 9)

def scrape_TAD_server(config,wgetData,folderOut,killProcess=True):
    from CONF import folderConfig
    from  process import readBuffer
    from calcAlgorithm import calcAlgorithm as ca
    calg={}
    ncols=1
    data=[]
    for j in range(ncols):
        buffer=readBuffer(folderConfig, int(config['n300']),j)
        calg[j]=ca(j,folderConfig,config,buffer)
    if os.path.exists(folderConfig+os.sep+'lastRead.txt') :
        with open (folderConfig+os.sep+'lastRead.txt') as f:
            ts=f.read()
            LastDateTimeAcquired=datetime.strptime(ts,'%Y-%m-%d %H:%M:%S')
    else:
        LastDateTimeAcquired=calg[0]._LastDateTimeAcquired
    #https://webcritech.jrc.ec.europa.eu/TAD_server/api/Data/Get/$IDdevice?tMin=$TMIN&tMax=$TMAX&nRec=5000&mode=json
    URL=config['serverAddress'] 
    #mappingVars={"inp1":"inp5","Temperature":"inp13","anag3":"inp11"}
    #levID=inp1
    levID=config['levID']
    URL=URL.replace('$EQ','=')
    URL=URL.replace('$IDdevice',config['IDdevice'])
    print('opening URL=',URL)
    period=0.25
    tmax=datetime.utcnow()
    tmin=tmax-timedelta(days=period)
    tminS=tmin.strftime('%Y-%m-%dT%H:%M:%S')
    tmaxS=tmax.strftime('%Y-%m-%dT%H:%M:%S')    
    URL=URL.replace('$TMIN',tminS )
    URL=URL.replace('$TMAX',tmaxS )
    print(URL)
    jsonS=urllib.request.urlopen(URL).read()
    if jsonS =='':
        return
    dataweb=json.loads(jsonS)
    for k in range(len(dataweb)):
        rec=dataweb[k]
        tim=datetime.strptime(rec['Timestamp'],'%Y-%m-%dT%H:%M:%SZ')
        if tim>LastDateTimeAcquired:
           samp=[rec['Values'][levID]]
           data.append((tim,samp))  
    saveSamples(config,calg,data,ncols,folderConfig, folderOut)  
    os.kill(os.getpid(), 9)


def combineDict(a,b):
    for key in b.keys():
        if not key in a:
            a[key]=b[key]
    return a


def scrape_NOAA(config,folderConfig,killProcess=True):
    #from CONF import folderConfig
    from  process import readBuffer
    from calcAlgorithm import calcAlgorithm as ca
    folderOut=folderConfig+os.sep+'outTemp'
    if not os.path.exists(folderOut):
        os.makedirs(folderOut)
    if 'settingsFile' in config:
        setFile=config['settingsFile'].replace('\\',os.sep)
        settings=readConfig('',folderConfig+os.sep+setFile)
    else:
        settings={}
    today=datetime.utcnow().strftime('%Y%m%d')
    yesterday=(datetime.utcnow()-timedelta(days=1)).strftime('%Y%m%d')
    URL=config['serverAddress']    
    URL=URL.replace("$BEGINDATE",yesterday)
    URL=URL.replace("$ENDDATE",today)
    URL=URL.replace('$EQ', '=')
    resp=requests.get(URL)
    json=resp.json()
    if not 'data'in json:
        print(json)
        return
    samples=json['data']
    ncols=1
    
    calg={}
    for j in range(ncols):
        buffer=readBuffer(folderConfig, int(config['n300']),j)
        calg[j]=ca(j,folderConfig,config,buffer)
    print('scrape: last time acquired:', config['IDdevice'],calg[0]._LastDateTimeAcquired)
    kj=0
    logData = ""
    newData=False
    data=[]
    combConfig=combineDict(config, settings)
    for dat in samples:
        tim = datetime.strptime(dat['t'],'%Y-%m-%d %H:%M')
        try:
            if dat['v'] !='':
                measure_Float = float(dat['v'])
        except:
            print('*** error',dat)
            #print(tim,calg[0]._LastDateTimeAcquired)
        if tim > calg[0]._LastDateTimeAcquired and dat['v']!='':
            data.append((tim,(measure_Float)))

    
    saveSamples(config,calg,data,ncols,folderConfig, folderOut)  
    if killProcess:
        os.kill(os.getpid(), 9)



def scrape_GLOSS(config,folderConfig,killProcess=True):
    #from CONF import folderConfig
    from  process import readBuffer
    from calcAlgorithm import calcAlgorithm as ca
    if config['sensors']=='':
        return
    folderOut=folderConfig +os.sep+'outTemp'
    if not os.path.exists(folderOut):
        os.makedirs(folderOut)

#  1)  collect the data into the "samples" collection
    URL=config['serverAddress'] 
    URL=URL.replace('$EQ','=')
    URL=URL.replace('$IDdevice',config['IDdevice'])
    print('opening URL=',URL)
    if URL=='https://www.ioc-sealevelmonitoring.org/service.php?query=data&format=xml&code=acaj&period=7':
         URL=URL
    period=2
    URL=URL.replace('period=7','period='+format(period))
    URL+='&timestart=$TMIN&timestop=$TMAX'
    tmax=datetime.utcnow()
    tmin=tmax-timedelta(days=period)
    tminS=tmin.strftime('%Y-%m-%dT%H:%M:%S')
    tmaxS=tmax.strftime('%Y-%m-%dT%H:%M:%S')    
    URL=URL.replace('$TMIN',tminS )
    URL=URL.replace('$TMAX',tmaxS )
    print(URL)
    xmlbin=urllib.request.urlopen(URL).read()
    xmlstr=xmlbin.decode()
    print('len(xmlstr)',len(xmlstr))
    fname='temp_'+format(uuid.uuid1().int)+'.xml'
    with open(fname,'w') as f:
        f.write(xmlstr)
    #    
    time.sleep(.1)    
    print('opening ',fname)
    tree = ET.parse(fname)
    os.remove(fname)    
    root=tree.getroot()
    samples=root.findall('sample')
    print('len(samples)',len(samples))
    if len(samples)==0:
        return
    #
    sensors=config['sensors'].split(',')
    
    indexSens={}
    if type(sensors)==list:
        ncols=len(sensors)
        for k in range(len(sensors)):
            indexSens[sensors[k]]=k
    else:
        ncols=1
        indexSens[sensors]=0

#  2)  initialize the calculation algorithms
    calg={}
    for j in range(ncols):
        print(j,folderConfig)
        buffer=readBuffer(folderConfig, int(config['n300']),j)
        calg[j]=ca(j,folderConfig,config,buffer)
    
    if os.path.exists(folderConfig+os.sep+'lastRead.txt'):
        try:
            with open(folderConfig+os.sep+'lastRead.txt') as f:
                LastDateTimeAcquired=datetime.strptime(f.read(),'%Y-%m-%d %H:%M:%S')
                #if LastDateTimeAcquired<datetime.strptime('2022-08-09','%Y-%m-%d'):
                #    os.kill()
        except:
            LastDateTimeAcquired=calg[0]._LastDateTimeAcquired
    else:
        LastDateTimeAcquired=calg[0]._LastDateTimeAcquired

    print('scrape:', config['IDdevice'],format(LastDateTimeAcquired))
    kj=0
    logData = ""
    newData=False

#  3)  add the sampled data beyond the last acquired data into "data"
    data= []
    data0={}
    
    for samp in samples:
        try:
            tiSt=samp.findall('stime')[0].text
            sens=samp.findall('sensor')[0].text
            if sens in indexSens:
                inds=indexSens[sens]
                if not inds in data0:
                    data0[inds]=[]
                tim=datetime.strptime(tiSt,'%Y-%m-%d %H:%M:%S')
                try:
                    measure_Float = float(samp.findall('slevel')[0].text)
                except:
                    print('*** error',samp)
                if tim > LastDateTimeAcquired:
                    data0[inds].append((tim,measure_Float))
        except:
            samp=samp
     # ora devo ricreare data in modo che tutti abbiano gli stessi punti
    maxPt=-1
    setTime=-1
    if len(data0)>0:
        try:
            if ncols>1:
                for kk in range(ncols):
                     if len(data0[kk])>maxPt:
                         maxPt=len(data0[kk])
                         setTime=kk
                #  il ref time e' setTime
                for hh in range(len(data0[setTime])):
                    tim=data0[setTime][hh][0]
                    measure_Float=[]                    
                    for kk in range(ncols):
                        vmeasure=-1
                        for jj in range(len(data0[kk])):
                            t1=data0[kk][jj][0]
                            v=data0[kk][jj][1]
                            if t1>=tim:
                                vmeasure=v
                                break
                        measure_Float.append(vmeasure)


                    data.append((tim,(measure_Float)))
            else:
                data=data0[0]
        except:
            data=data
        
#  4)  save the data or print them
    saveSamples(config,calg,data,ncols,folderConfig, folderOut)    
    if killProcess:
        os.kill(os.getpid(), 9)

def getDATA_DART(URL,LastTimeRecorded):
    resp=requests.get(URL).text
    dataOut=[]
    if '#yr  mo dy hr mn  s -      m'  in resp:
        data=resp.split('#yr  mo dy hr mn  s -      m')[1].split('</textarea')[0].split('\n')
    else:
        return []
    try:
        for j in range(len(data)-1,0,-1):
            d=data[j]
            if d=='' or d=='\n': continue
            #2022 08 07 11 45 00 1 4737.192
            #01234567890123456789012
            datTime=datetime.strptime(d[:18],'%Y %m %d %H %M %S')
            lev    =float(d[21:])
            if datTime>LastTimeRecorded:
                dataOut.append((datTime,lev))
    except Exception as e:
        print(e)
    return dataOut

def scrape_DART(config,folderConfig,killProcess=True):
    #from CONF import folderConfig
    from  process import readBuffer
    from calcAlgorithm import calcAlgorithm as ca

    folderOut=folderConfig +os.sep+'outTemp'
    if not os.path.exists(folderOut):
        os.makedirs(folderOut)

#  1)  collect the data into the "samples" collection
    URL=config['serverAddress'] 
    URL=URL.replace('$EQ','=')
    URL=URL.replace('$IDdevice',config['IDdevice'])
    print('opening URL=',URL)
    if os.path.exists(folderConfig+os.sep+'lastRead.txt'):
        try:
            with open(folderConfig+os.sep+'lastRead.txt') as f:
                LastDateTimeAcquired=datetime.strptime(f.read(),'%Y-%m-%d %H:%M:%S')
                #if LastDateTimeAcquired<datetime.strptime('2022-08-09','%Y-%m-%d'):
                #    os.kill()
        except:
            LastDateTimeAcquired=datetime.strptime('2000-01-01','%Y-%m-%d')
    else:
        LastDateTimeAcquired=datetime.strptime('2000-01-01','%Y-%m-%d')

    samples=getDATA_DART(URL,LastDateTimeAcquired)
    print('len(samples)',len(samples))
    if len(samples)==0:
        return
    #
    ncols=1
#  2)  initialize the calculation algorithms
    calg={}
    for j in range(ncols):
        print(j,folderConfig)
        buffer=readBuffer(folderConfig, int(config['n300']),j)
        calg[j]=ca(j,folderConfig,config,buffer)
    

    print('scrape:', config['IDdevice'],format(LastDateTimeAcquired))
    
    logData = ""
   
        
#  4)  save the data or print them
    saveSamples(config,calg,samples,ncols,folderConfig, folderOut)    
    if killProcess:
        os.kill(os.getpid(), 9)

def scrape_TR(config,folderConfig,killProcess=True):
    #from CONF import folderConfig

    from  process import readBuffer
    from calcAlgorithm import calcAlgorithm as ca
    folderOut=folderConfig +os.sep+'outTemp'
    if not os.path.exists(folderOut):
        os.makedirs(folderOut)

#  1)  collect the data into the "samples" collection
    # KAN:K2020@ftp://193.140.203.10/sea_level/Antalya_Sec30.dat
    URL=config['serverAddress'] 
    #USERNAME=URL.split('@')[0].split(':')[0]
    #PASSWORD=ÚSERNAME=URL.split('@')[0].split(':')[1]
    #HOSTNAME=URL.split('//')[1].split('/')[0]
    #remoteDir=URL.split(HOSTNAME+'/')[1].split('/')[0]
    #filename=URL.split(remoteDir+'/')[1]
    print('opening URL=',URL)
    #ftp_server = ftplib.FTP(HOSTNAME, USERNAME, PASSWORD)
    #ftp_server.cwd(remoteDir) 
    #with open(folderOut+os.sep+filename, "wb") as file:
    ## Command for Downloading the file "RETR filename"
    #    ftp_server.retrbinary(f"RETR {filename}", file.write)
    rows=requests.get(URL).text.split('\r\n')
    #with open(folderOut+os.sep+filename, "r") as file:
    #    testo=file.read()
 

    #rows=testo.split('\n')
    print('file opened ',len(rows))
    if len(rows)<4:
        return
    #
    
    ncols=1

#  2)  initialize the calculation algorithms
    calg={}
    for j in range(ncols):
        buffer=readBuffer(folderConfig, int(config['n300']),j)
        calg[j]=ca(j,folderConfig,config,buffer)
        #calg[0]._LastDateTimeAcquired=datetime(2022,1,1)
    kj=0
    logData = ""
    newData=False

#  3)  add the sampled data beyond the last acquired data into "data"
    data= []
    for row in rows[4:]:
        if not row.startswith('#') and row !='':
            tiSt=row.split(',')[0]
            tim=datetime.strptime(tiSt,'%Y/%m/%d %H:%M:%S')
            try:
                measure_Float = float(row.split(',')[1])
            except:
                print('*** error',samp)
            if tim > calg[0]._LastDateTimeAcquired:
                print(tim,measure_Float)
                data.append((tim,(measure_Float)))

#  4)  save the data or print them
    if data !=[]:
        saveSamples(config,calg,data,ncols,folderConfig, folderOut)    
    if killProcess:
        os.kill(os.getpid(), 9)

def read_execLog_IDSL0(config,wgetData):
    readExec=config['READ_EXECLOG']
    SaveURL=config['SaveURL']
    SaveURL=SaveURL.replace('$EQ','=')
    SaveURL=SaveURL.replace('\$','$')

    with open(readExec) as f:
        lines=f.read().split('\n')
    for line in lines:
        idDevice=line.split(',')[0]
        data=line.split('(')[0].strip()
        SaveURL1=SaveURL.replace('$IDdevice',idDevice)
        SaveURL1=SaveURL1.split('log=')[0]+'log=$S'+data+'$E'
        print (SaveURL1,len(wgetData))
        wgetData.append(SaveURL1)
        time.sleep(0.2)
    while True:
        print(len(wgetData))
        time.sleep(1)

def saveAllLog(URL,logData,config):
        URL = config['SaveURL']
        URL = URL.replace("$EQ", '=')
        URL=URL.replace('\$','$')
        URL = URL.replace("$IDdevice", config['IDdevice'])

        URL = URL.split( "log=")[0]+"log=" + logData
        

        param = URL.split("?")[1]
        params={}
        for keyvalue in param.split('&'):
            try:
                key,value=keyvalue.split('=')
                params[key]=value
            except:
                params=params
        URL = URL.split("?")[0]

        x=requests.post(URL,data=params)
        print(x.text)
        time.sleep(2)

def read_execLog_IDSL(config,wgetData):
    readExec=config['READ_EXECLOG']
    SaveURL=config['SaveURL']
    SaveURL=SaveURL.replace('$EQ','=')
    SaveURL=SaveURL.replace('\$','$')

    with open(readExec) as f:
        lines=f.read().split('\n')
    n=0
    allLog=''
    for line in lines:
        if line=='':continue
        idDevice=line.split(',')[0]
        data=line.split('(')[0].strip()
        #data=','.join(data.split(',')[:8])+','+data.split(',')[9]+','+data.split(',')[8]+','+','.join(data.split(',')[10:])
        print(data)
        allLog += '$S'+data+'$E\n'
        n+=1
        if n==100:
            try:
                saveAllLog(SaveURL,allLog,config)
            except:
                n=n
            n=0
            allLog=''
    if n>0:
        saveAllLog(SaveURL,allLog,config)

def scrape_ISPRA_NF(config,folderConfig,killProcess=True):
    #from CONF import folderConfig

    from  process import readBuffer
    from calcAlgorithm import calcAlgorithm as ca
    folderOut=folderConfig +os.sep+'outTemp'
    if not os.path.exists(folderOut):
        os.makedirs(folderOut)

#  1)  collect the data into the "samples" collection
    URL=config['serverAddress'].split('|')[0]
    location=config['serverAddress'].split('|')[1]
    print('opening URL=',URL, location)
    rows=requests.get(URL).text.split('\r\n')
    row0=rows[0].split(';')
    index={}
    for j in range(len(row0)):
        index[row0[j]]=j
    print('file opened ',len(rows))
    if len(rows)<4:
        return
    #
    
    ncols=1

#  2)  initialize the calculation algorithms
    calg={}
    for j in range(ncols):
        buffer=readBuffer(folderConfig, int(config['n300']),j,True)
        calg[j]=ca(j,folderConfig,config,buffer)
        #calg[0]._LastDateTimeAcquired=datetime(2022,1,1)
    kj=0
    logData = ""
    newData=False

#  3)  add the sampled data beyond the last acquired data into "data"
    data= []
    for row in rows[1:]:
        if row=='':  continue
        try:
            skip=False
            value=row.split(';')[index[location]]
        except Exception as e:
            print(row)
            value='NA'
        if  value !='NA':
            tiSt=row.split(';')[0]
            tim=datetime.strptime(tiSt,'%Y-%m-%d %H:%M:%S')
            try:
                measure_Float = round(float(value)/100.,3)
            except Exception as e:
                print('*** error',e, row)
            if tim > calg[0]._LastDateTimeAcquired:
                #print(tim,measure_Float)
                data.append((tim,(measure_Float)))

#  4)  save the data or print them
    if data !=[]:
        saveSamples(config,calg,data,ncols,folderConfig, folderOut)    
    if killProcess:
        os.kill(os.getpid(), 9)

def scrape_OTT(config,folderConfig,killProcess=True):
    from  process import readBuffer
    from calcAlgorithm import calcAlgorithm as ca
    folderOut=folderConfig
    if not os.path.exists(folderOut):
        os.makedirs(folderOut)
    calg={};ncols=1
    for j in range(ncols):
        buffer=readBuffer(folderConfig, int(config['n300']),j,True)
        calg[j]=ca(j,folderConfig,config,buffer)
        #22/06/2022,17:51
        #calg[0]._LastDateTimeAcquired=datetime(2022,6,22,17,51)
        #calg[0]._LastDateTimeAcquired=datetime(2022,1,1)
    kj=0
    logData = ""
    newData=False

#  3)  add the sampled data beyond the last acquired data into "data"
    data= []
    folderData=config['OutFolder']
    levcode=config['sensorCodeOTT']
    battcode=config['batteryCodeOTT']
    sensmult=float(config['sensorMultFac'])
    sensorAddFac=float(config['sensorAddFac'])
    n=-1
    dir_list = os.listdir(folderData)
    for f in dir_list:
        #0000325686_20220706061925.MIS
        #0123456789012345678901234
        ts=f[11:25]
        tim=datetime.strptime(ts,'%Y%m%d%H%M%S')
        if tim>calg[0]._LastDateTimeAcquired:
            with open(folderData+os.sep+f) as f:
                testo=f.read()
            for line in testo.split('\n'):
                if line=='':continue
                if '<STATION>' in line:
                    n=-1
                    code=line.split('<SENSOR>')[1].split('</SENSOR>')[0]
                    if code==levcode:
                        lev=True
                    else:
                        lev=False
                else:
                    n+=1
                    p=line.split(';')
                    ts=datetime.strptime(p[0]+p[1],'%Y%m%d%H%M%S')
                    if lev: 
                        measured_level=round(float(p[2]) *sensmult+sensorAddFac,3)
                        #data[n]['ts']=ts
                        #data[n]['level']=measured_level
                        data.append((ts,(measured_level)))
                        print(ts,measured_level)
                    else: 
                        battValue=float(p[2]) 
                        #data[n]['batt']=battValue
    if data !=[]:
        saveSamples(config,calg,data,ncols,folderConfig, folderOut)    
    if killProcess:
        os.kill(os.getpid(), 9)
            
                

def tsINC(timestamp):
    import datetime
    d=datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=timestamp)
    return datetime.datetime(d.year+1900,d.month,d.day,d.hour,d.minute,d.second)

def scrape_INCOIS(config,folderConfig,killProcess=True):
    from  process import readBuffer
    from calcAlgorithm import calcAlgorithm as ca
    folderOut=folderConfig +os.sep+'outTemp'
    

    if not os.path.exists(folderOut):
        os.makedirs(folderOut)

#  1)  collect the data into the "samples" collection
    URL=config['serverAddress']    
    print('opening URL=',URL)
    with requests.get(URL, verify=False) as resp:
        json=resp.json()
    
    if json==[]:
        return
    indexCol=[]
    values0={}
    for n in range(len(json)):
        d=json[n]
        if d['name']=='PRS' or d['name']=='ENC' or d['name']=='RAD':
            indexCol.append(n)
            values0[n]=0
    ncols=len(indexCol)

#  2)  initialize the calculation algorithms
    calg={}
    for j in range(ncols):
        buffer=readBuffer(folderConfig, int(config['n300']),j,True)
        calg[j]=ca(j,folderConfig,config,buffer)
        #22/06/2022,17:51
        #calg[0]._LastDateTimeAcquired=datetime(2022,6,22,17,51)
        #calg[0]._LastDateTimeAcquired=datetime(2022,1,1)
    kj=0
    logData = ""
    newData=False

#  3)  add the sampled data beyond the last acquired data into "data"
    data= []
    
    for j in range(len(json[0]['data'])):
        try: 
            tim=tsINC(json[0]['data'][j][0])
            if tim > calg[0]._LastDateTimeAcquired:
                samp=[]
                for i in indexCol:
                    try:
                        value=json[i]['data'][j][1]
                        values0[i]=value
                    except:
                        value=values0[i]
                    samp.append(value)
                #print(tim,measure_Float)
                data.append((tim,samp))
        except Exception as e:
            print(e)
#  4)  save the data or print them
    if data !=[]:
        saveSamples(config,calg,data,ncols,folderConfig, folderOut)    
    if killProcess:
        os.kill(os.getpid(), 9)

def multi_scrape(idThread,config,wgetData,listConfig):
    from  process import addMeasure
    from calcAlgorithm import calcAlgorithm as ca
    t0=datetime.utcnow()
    print('****************************************************')
    print(t0.strftime('%Y-%m-%d %H:%M')+': initiating '+idThread+' for ',len(listConfig),' stations')
    print('****************************************************')
    
    for j in range(len(listConfig)):
        dir=listConfig[j]
        print('\n\n****************************************')
        print(' Station: '+dir+ ' thread: '+format(idThread)+'  id:'+format(j)+'/'+format(len(listConfig)))
        print(' -c '+dir)
        print('****************************************\n\n')
        config=readConfig(dir)
        if 'folderOut' in config:
            folderOut=config['folderOut']
        else:
            folderOut=dir+os.sep+'temp'
        if not os.path.exists(folderOut):
            os.makedirs(folderOut)
        #try:  
        if True:
            if config['scrapePage']=='BIG_INA':
                scrape_BIG_INA(config,wgetData,folderOut)

            if config['scrapePage']=='BIG_ID_SRG':
                scrape_BIG_ID_SRG(config,wgetData,folderOut,False)

            elif config['scrapePage']=='NOAA':
                scrape_NOAA(config,dir,False)

            elif config['scrapePage']=='GLOSS':
                scrape_GLOSS(config,dir, False)     

            elif config['scrapePage']=='DART':
                scrape_DART(config,dir, False)     
            
            elif config['scrapePage']=='TR':
                scrape_TR(config,dir,False)  
            
            elif config['scrapePage']=='ISPRA_NF':
                scrape_ISPRA_NF(config,dir,False)  
            
            elif config['scrapePage']=='INCOIS':
                scrape_INCOIS(config,dir,False)     
       # except Exception as e:
       #     print(e)
       # time.sleep(1)    
    t1=datetime.utcnow()
    delta=int(((t1-t0).seconds)/60)
    print('****************************************************')
    print(t1.strftime('%Y-%m-%d %H:%M')+': end '+idThread+' for ',len(listConfig),' stations,  delta=',delta,'min')
    print('****************************************************')



if __name__ == "__main__":

    arguments = sys.argv[1:]
    count = len(arguments)
    print (count)
    if count<2:
        print('example of call: scrape.py -code  adak  -n300 100  -n30 15  -mult 4  -add 0.1  -th 0.08 -mode GLOSS  -out /temp/adak')
        print('example of call: scrape.py -IDdevice NOAA_Clearance_Water -code  9432780  -n300 100  -n30 15  -mult 4  -add 0.1  -th 0.08 -mode NOAA  -out /temp/Clearance_Water')
    else:
        for j in range(len(arguments[1:])):
            arg,argv=arguments[j:j+2]
            if arg=='-sensors':
                config['sensors']=argv
            if arg=='-mode':
                mode=argv

        if mode=='GLOSS':
            fold=config['outFolder']
            scrape_GLOSS(config,fold)
        elif mode=='NOAA':
            fold=config['outFolder']
            scrape_NOAA(config,fold)
       