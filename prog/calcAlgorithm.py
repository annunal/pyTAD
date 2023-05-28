from readConfig import *
from process import solve2,addpoint,addpoint1,rootMeanSquare
import datetime
import math,random
import redis
import json, requests

class calcAlgorithm(object):
    """description of class"""
    _config={}
    initialized=False
    _x=[]
    _y=[]
    _yavg30=[]
    _yavg300=[]
    _diffe=[]
    _ratioRMS=0
    _threshold=0
    _saveURL=''
    _AddRMS=0
    _LastDateTimeAcquired=''
    _alertSignal=0
    _alertValue=0
    _n30=0
    _n300=0
    debug=False
    #_DtAverage=0.0
    def __init__(self,kk,basedir,config,buffer):
        self._config=config #readConfig(basedir)
        self._n30=int(self._config['n30'])
        self._n300=int(self._config['n300'])
        self._vmin=self._config['vmin']
        self._vmax=self._config['vmax']
    
        self._saveURL=self._config['SaveURL']
        self._ratioRMS    =float(self._config['ratioRMS'])
        self._threshold   =float(self._config['threshold'])
        self._AddRMS      =float(self._config['AddRMS'])
        #self._backFactor  =float(self._config['backFactor'])
        self._DtAverage   =float(self._config['Interval'])
        self._Tmax30=self._n30*self._DtAverage
        self._Tmax300=self._n300*self._DtAverage 
        self._index300,self._index1,self._x300,self._y300,self._yavg30,self._yavg300=buffer
        if self._index1==0:
            self._LastDateTimeAcquired = datetime.datetime.utcnow()-datetime.timedelta(seconds=7*24*3600)
        else:
            self._LastDateTimeAcquired = self._x300[self._index300-1]        
        
    def dispose(self):
        self._x = Nothing
        self._y = Nothing
        self._yavg30 = Nothing
        self._yavg300 = Nothing
        self._index300=0

    def readBuffer(self,folderOut,kk):
        max300=self._n300
        # read buffer.txt 
        self._x300=[0.0]*(max300+1)
        self._y300=[0.0]*(max300+1)
        self._yavg30=[0.0]*(max300+1)
        self._yavg300=[0.0]*(max300+1)
        self._diffe=[0.0]*(max300+1)
        t0=datetime.datetime.utcnow()
        if os.path.exists(folderOut+ os.sep +"buffer_" + format(kk) + ".txt"):
            fh=open(folderOut+ os.sep +"buffer_" + format(kk) + ".txt",'r')
            rows=fh.read().split('\n')       
            fh.close()
            try:
                self._index300,self._index1=(int(x) for x in rows[0].split(','))
                lastts=rows[-2].split(',')[0]
                delta=(t0-datetime.datetime.strptime(lastts,'%Y-%m-%d %H:%M:%S')).total_seconds()/3600
            except:
                delta=1e6
                self._index300=0
            if self.debug: print('deltaTime min buffer (h)',delta)
            print('deltaTime min buffer',delta, 'last datetime',format(datetime.strptime(lastts,'%Y-%m-%d %H:%M:%S')))
            if self._index300==max300+1 and len(rows)>=max300+1 and delta<2*24:
                try:
                    for i in range(1,self._index300):
                        self._y300[i],self._yavg30[i],self._yavg300[i]=(float(x) for x in rows[i].split(',')[1:])
                        ts=rows[i].split(',')[0]
                        self._x300[i]=datetime.datetime.strptime(ts,'%Y-%m-%d %H:%M:%S') 
                        #print(ts,x300[i],y300[i])
                    LastDateTimeAcquired = self._x300[self._index300-1]
                except Exception as e:
                    print('readBuffer error: ',e)
                    self._index300=0
                    self._x300=[0.0]*(max300+1)
                    self._y300=[0.0]*(max300+1)
                    self._index1=0
                    LastDateTimeAcquired = datetime.datetime.utcnow()-datetime.timedelta(seconds=24*3600)
            else:
               if self.debug: print(self._index300,max300,len(rows))
               self._index300=0
               self._index1=0
               LastDateTimeAcquired = datetime.datetime.utcnow()-datetime.timedelta(seconds=24*3600)
        else:
            print('file not existing ',folderOut+ os.sep+"buffer_" + format(kk) + ".txt")
            self._index300=0
            self._index1=0
            LastDateTimeAcquired = datetime.datetime.utcnow()-datetime.timedelta(seconds=24*3600)
       
        
        if self.debug: print(folderOut,LastDateTimeAcquired)
        return LastDateTimeAcquired
        
    def saveBuffer(self,folderOut,kk):
        # read buffer.txt 
        self._index300=len(self._x300)
        self._index1=self._index300
        #print(x300[0],x300[1])
        fh=open(folderOut +os.sep+ "buffer_" + format(kk) + ".txt",'w')
        fh.write(format(self._index300)+','+format(self._index1)+'\n')
        for i in range(self._index300):
            fh.write(format(self._x300[i])+','+format(self._y300[i])+','+format(self._yavg30[i])+','+format(self._yavg300[i])+'\n')
        fh.close()
        LastDateTimeAcquired1 = self._x300[self._index300-1]
        #print(LastDateTimeAcquired1)
        return
    def init(self,time0,sensorValue,folderOut,kk):
       # se esiste buffer leggo buffer e non uso i valori
        if self.debug: print(folderOut+os.sep+'buffer.txt')
        max300=self._n300
        #if os.path.exists(folderOut+ os.sep +"buffer_" + format(kk) + ".txt"):
        #    if self.debug: print('reading buffer')
        #    self.readBuffer(folderOut,kk)
        #else:
        #    self._index1=0
        #    self._index300=0
        #    self._alertValue=0
        #    self._x300=[0.0]*(max300+1)
        #    self._y300=[0.0]*(max300+1)

        #    self._yavg30=[0.0]*(max300+1)
        #    self._yavg300=[0.0]*(max300+1)
        #    self._diffe=[0.0]*(max300+1)

        if self._index1==0:
            if self.debug: print ('Initializing ',max300,' data ')
            for k in range(0,max300+1):
                self._x300[k]=( time0-datetime.timedelta(seconds=(max300-k)*self._DtAverage))
                #print(time0,x300[k],k)
                self._y300[k]=(sensorValue+random.random()*0.001)
                self._yavg30[k]=sensorValue
                self._yavg300[k]=sensorValue
                #yavg300.append(sensorValue)
            
            #diffe.append=0;
        return 

    def addMeasure(self,time0,sensorValue,folderOut,kk):
        global initialized,alertValue,index300,index1,x300,y300,yavg30,yavg300
    
        if not self.initialized:
            if self.debug: print('calling init process.py')
            self.init(time0,sensorValue,folderOut,kk)
            self.initialized=True
     
        offset30,offset300=addpoint(self._x300,self._y300,time0, sensorValue,self._n300, self._Tmax30, self._Tmax300);
        if self._DtAverage==-1:
            offset30=self._n300-self._n30
            offset300=0
        forecast30,rms30 = solve2(self._x300, self._y300, offset30,  self._n300, time0);
        forecast300 ,rms = solve2(self._x300, self._y300, offset300, self._n300, time0);
    
        nfore=addpoint1(self._yavg30, self._yavg300, self._diffe, forecast30, forecast300, self._n300)
   
        if nfore==self._n300+1:     
            rms = rootMeanSquare(self._diffe,0,self._n300)
            alertSignal = math.fabs(forecast30 - forecast300);
        else:
            alertSignal = 0.0

        if (alertSignal>self._ratioRMS*rms and alertSignal>self._threshold):
                if (self._alertValue<10):
                    self._alertValue += 1;
        else:
               if (self._alertValue>0 ):
                   self._alertValue -= 1;
    
        #print time0,',',sensorValue,',',forecast30,',',forecast300,',',rms30,',',rms,',',alertSignal,',',alertValue,',',nfore,',',ratioRMS,',',threshold
    
        #self.saveBuffer(folderOut,kk)
    
        return forecast30,forecast300,rms,alertSignal,self._alertValue
 
    def sendREDIS(self,config,dict,r=None):

        if r==None:
          passwd = config['REDISpassword']  
          redisServer=config['REDISserver'] 
          
          for key in dict.keys():
              if key !='Timestamp' and key != 'DeviceId':
                dict[key]=float(dict[key])
          r = redis.Redis(host=redisServer, port=6380, db=0,ssl=True,password=passwd)
        #resp=r.publish('Telemetry-Channel', json.dumps(dict))
        URL='https://webcritech.jrc.ec.europa.eu/tad_server/api/Data/PostAsync'
        print (json.dumps(dict))
        if not 'FeatureId' in dict:
            dict['FeatureId']=''
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        x = requests.post(URL, data=json.dumps(dict), headers=headers)
        print('resp=',x.text)
        return r,x.text

    def prepareREDIS(self,dict,k,config, tt, avg,fore30,fore300,rms,alertSignal,alertValue, log0,  press = 0,  temp = 0,  batt = 0):
          suffix = "_" +format(k+1)

          try:
              
              list=config['REDISsave']
              fields=list.split(',')
              
              for f in fields:
                  if f=='': continue
                  key,value=f.split(":")
                  #print(key,value)
                  if '$LEV'+suffix in value: value=value.replace('$LEV'+suffix,format(avg));dict[key]=value
                  if '$FORE300'+suffix in value: value=value.replace('$FORE300'+suffix,format(fore300));dict[key]=value
                  if '$FORE30'+suffix in value:value=value.replace('$FORE30'+suffix,format(fore30));dict[key]=value
                  if '$RMS'+suffix in value: value=value.replace('$RMS'+suffix,format(rms));dict[key]=value
                  if '$ALERT_LEVEL'+suffix in value: value=value.replace('$ALERT_LEVEL'+suffix,format(alertSignal));dict[key]=value
                  if '$ALERT_SIGNAL'+suffix in value: value=value.replace('$ALERT_SIGNAL'+suffix,format(alertValue));dict[key]=value
                  if '$TIMESTAMP'  in value: value=value.replace('$TIMESTAMP',format(tt,'%Y-%m-%dT%H:%M:%SZ'));dict[key]=value
                  if '$IDdevice'  in value: value=value.replace('$IDdevice',config['IDdevice']);dict[key]=value
                  if 'FeaturId' in key: dict[key]=value
                  #dict[key]=value
              return dict              
          except Exception as e:
            print('error in redis connection')
            print(e)

    def prepareString(self,k,config, ora1, avg,fore30,fore300,rms,alertSignal,alertValue, log0,  press = 0,  temp = 0,  batt = 0):
        if log0 == "":
            if self._saveURL !='':
                logData = self._saveURL.split("log=")[1]
            else:
                logData='$IDdevice,$DATE,$TIME,$TEMP,$PRESS,$LEV,$FORE30,$FORE300,$RMS,$ALERT_LEVEL,$ALERT_SIGNAL,$V1,$V2,$V3,'
            logData = logData.replace("$DATE", ora1.strftime("%d/%m/%Y"))
            logData = logData.replace("$TIME", ora1.strftime("%H:%M:%S"))
            logData = logData.replace("$PRESS", "{:.1f}".format(press))
            logData = logData.replace("$TEMP", "{:.1f}".format(temp))
            logData = logData.replace("$IDdevice", config['IDdevice'])
        else:
            logData = log0
        

        suffix = ","
        if k > 0:
            suffix = "_" +format(k+1) + ","
        
        logData = logData.replace("$LEV" + suffix, format(avg) + ",")
        logData = logData.replace("$FORE300" + suffix, "{:.3f}".format(fore300) + ",")
        logData = logData.replace("$FORE30" + suffix, "{:.3f}".format(fore30) + ",")
        logData = logData.replace("$RMS" + suffix, "{:.5f}".format(rms) + ",")
        logData = logData.replace("$ALERT_LEVEL" + suffix, "{:.3f}".format(alertSignal) + ",")
        logData = logData.replace("$ALERT_SIGNAL" + suffix, "{:.0f}".format(alertValue) + ",")
        logData = logData.replace("$V1" + suffix, "{:.2f}".format(batt) + ",")

        return logData