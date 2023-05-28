import io,os,sys
import datetime
import xml.etree.ElementTree as ET
import urllib,time,uuid
from big_utils import getListBIG
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

def readConfig(fold='.',fname=''):
        # read the configuration file
        config={}
        if fname=='':
            if os.path.exists(fold+os.sep+'config.txt'):
                fh=open(fold+os.sep+'config.txt','r')
            else:
                print('configuration file does not exists. for test purposes it can continue')
                return config
        else:
            fh=open(fname,'r')
        righe=fh.readlines()
        config['pressureSensor']=''
        config['Tail']=''       
        config['TailSimple']=''
        config['folderWWW']='' #fold+os.sep+'/html'
        config['folderOut']='' #fold+os.sep+'/tmp'
        config['ReadFile']=''
        config['PhotoCMD']=''
        config['PhotoAlertLevel']=10
        config['PhotoTimeInterval']=2
        config['MQTT_server']=''
        config['MQTT_listener']=''        
        config['MQTT_username']='' 
        config['MQTT_password']='' 
        config['MQTT_msg']=''
        config['ADC_1']=106
        config['ADC_2']=105
        config['scrapePage'] =''
        config['TCP_host']=''
        config['AlertLevel']=2

        for  riga in righe:
                #print(riga)
                if not riga.startswith('*'):
                        if '=' in riga:
                                tag=riga.split('=')[0].strip()
                                value=riga[riga.find('=')+1:].strip().replace('\n','')
                                #value=riga.split('=')[1].split('*')[0].strip()
                                #print (tag,value)
                                config[tag]=value

        fh.close()


        return config

def prepareFolders(fname):
        import requests
        multY = 1.0
        vminDev = -10
        vmaxDev = 10
        ncols = -1
        multicols = False
        multicolsBIG = False
        provider = ""
        typePlot = ""
        region0=''
        with open (fname) as f:
            testo = f.read().split('\n')
#        if InStr(testo0, "jsonurl") <> 0 :
#            jsonurl = Split(Split(testo0, "jsonurl=")(1), vbCrLf)(0)
#            testo0 += getListNOAA(jsonurl)


#        End if
#        File.WriteAllText(startupPath() & "listLocations0.txt", testo0)
        
        ntotDev = len(testo) - 2
        nbat = int(ntotDev / 50) + 1
        if nbat < 1: nbat = 1
        for f in ("sqlText.txt","sqlDeviceFieldsMap.txt","sqlDeviceFieldsMap.txt"):
            if os.path.exists(f):
                os.remove(f)
        n = 0
        ngr = 1
        ndev = 0
        prefixURL=''
        region=''
        for line in testo:
            if line == "":continue
            if line[0] == "*":continue
            if line[0]== "$":
                p = line.split("$")[1].strip().split('\t')
                for  d in p:
                    if d == "": continue
                    print(d)
                    key=d.split('=')[0]
                    value=d[d.find('=')+1:].strip()
                    
                    if key == "mode":
                        mode = value
                    elif key == "type":
                        type = value
                    elif key == "outSRV":
                        outSrv = value
                    elif key == "provider" :
                        provider = value
                    elif key == "typePlot":
                        typePlot = value
                    elif key == "ng":
                        ng = value
                    elif key == "vmin":
                        vminDev = value
                    elif key == "vmax":
                        vmaxDev = value
                    elif key == "multY" :
                        multY = value
                    elif key == "prefixURL" :
                        prefixURL = value

                    elif key == "jsonurl" :
                        url = value
                    elif key == "multicols" :
                        multicols = (value == "True")
                    elif key == "multicolsBIG" :
                        multicolsBIG = (value == "True")
                    
                for nn in range(nbat):
                    with open("run_" + type + "_" + format(nn ) +".sh",'w') as f:
                        f.write("echo %DATE% %TIME% START BATCH >> logCalls.txt  \n")
                if provider == "" :
                    provider = type
            
                if typePlot == "" :
                    typePlot = type

                continue
            
            pars = line.split('\t')
            
            lat = pars[0].strip()
            lon = pars[1].strip()
            country = pars[2].strip()
            name = pars[3].strip()
            if '"' in country :
                country = country.replace('"','')
            if '"' in name :
                name = name.replace('"','')

            link = pars[4].strip()
            code = pars[5].strip()
            typecode=code
            ncols=1
            #if type !=''  and not type in code:
            #    typecode=type+'-'+code
            if len(pars) > 6 :
                region = pars[6].strip()

            if multicols:
                if type=='INCOIS':
                    with requests.get(link, verify=False) as resp:
                        json=resp.json()
                    indexCol=[]
                    for n in range(len(json)):
                        d=json[n]
                        if d['name']=='PRS' or d['name']=='ENC' or d['name']=='RAD':
                            indexCol.append(n)
                    ncols=len(indexCol)
                if type=='GLOSS' :
                    URL = prefixURL + link
                    URL=URL.replace('$EQ','=')
                    sensors=checkSensorGLOSS(URL)
                    ncols = len(sensors)
                    if ncols==0:
                        ncols=ncols

            #if multicolsBIG :
            #    ncols = 3
#            if multicols:
#                ncols=3
            conf = ""
            conf += "title         = " + name +'\n'
            conf += "location      = " + lat + "," + lon +'\n'
            conf += "IDdevice      = " + typecode +'\n'
            conf += "serverAddress = " + prefixURL +link.replace('=',"$EQ") +'\n' #'&period$EQ30&starttime$EQ$START"
            conf += "ServerPort    = 0" +'\n'
            conf += 'OutFolder     = .\\logs\\\n'
            if (multicols or multicolsBIG) and ncols>1 :
                conf += "ncols         = " +format( ncols) +'\n'
                if ncols == 2 :
                    conf += "SaveURL       = " + outSrv + "/SensorGrid/EnterData.aspx?idDevice=$IDdevice&log=$S$IDdevice,$DATE,$TIME,$TEMP,$PRESS,$LEV,$FORE30,$FORE300,$RMS,$ALERT_LEVEL,$ALERT_SIGNAL,$LEV_2,$FORE30_2,$FORE300_2,$RMS_2,$ALERT_LEVEL_2,$ALERT_SIGNAL_2,0,0,0,0,0,0,$V1,$E" +'\n'
                elif ncols == 3 :
                    conf += "SaveURL       = " + outSrv + "/SensorGrid/EnterData.aspx?idDevice=$IDdevice&log=$S$IDdevice,$DATE,$TIME,$TEMP,$PRESS,$LEV,$FORE30,$FORE300,$RMS,$ALERT_LEVEL,$ALERT_SIGNAL,$LEV_2,$FORE30_2,$FORE300_2,$RMS_2,$ALERT_LEVEL_2,$ALERT_SIGNAL_2,$LEV_3,$FORE30_3,$FORE300_3,$RMS_3,$ALERT_LEVEL_3,$ALERT_SIGNAL_3,$V1,$E" +'\n'
                elif ncols == 1 :
                    conf += "SaveURL       = " + outSrv + "/SensorGrid/EnterData.aspx?idDevice=$IDdevice&log=$S$IDdevice,$DATE,$TIME,$TEMP,$PRESS,$LEV,$FORE30,$FORE300,$RMS,$ALERT_LEVEL,$ALERT_SIGNAL,$V1,$V2$E" +'\n'
                else:
                    print('errore')
                    quit()
                
            else:
                conf += "SaveURL       = " + outSrv + "/SensorGrid/EnterData.aspx?idDevice=$IDdevice&log=$S$IDdevice,$DATE,$TIME,$TEMP,$PRESS,$LEV,$FORE30,$FORE300,$RMS,$ALERT_LEVEL,$ALERT_SIGNAL,$V1,$V2,$E" +'\n'
            
            if type=='GLOSS':
                conf += 'sensors       ='+','.join(sensors)+'\n'
            conf += "AlertURL      = " + outSrv + "/SensorGrid/EnterAlert.aspx?idDevice=$IDdevice&AlertLevel=$ALERT_SIGNAL&DateTime=$DATE $TIME&SignalType=TAD&AlertType=AUTO" +'\n'
            conf += "DataFile      = Data_yyyyMMdd.txt" +'\n'
            conf += "Datalog       = dataLog_yyyyMMdd.txt" +'\n'
            conf += "Interval      = -1" +'\n'
            if multY != 1 :
                conf += "MultY      = " & multY +'\n'

            conf += "n300          =  100" +'\n'
            conf += "n30           =  10" +'\n'
            conf += "threshold     = 0.1" +'\n'
            conf += "ratioRMS      = 3" +'\n'
            conf += "AddRMS        = 0.1" +'\n'
            conf += "backFactor    = 0" +'\n'
            conf += "vmin          = " + format(vminDev) +'\n'
            conf += "vmax          = " + format(vmaxDev) +'\n'
            conf += "remAndInvert  = 0." +'\n'
            conf += "mode          = " + mode +'\n'
            conf += "scrapePage          = " + type +'\n'
            conf += "settingsFile  = .."+os.sep+"settings.txt" +'\n'
            if not os.path.exists(code) :
                os.makedirs(code )
            with open ('.'+os.sep + code + os.sep+"config.txt",'w') as f:
                f.write(conf)

            linetoadd = "INSERT INTO [dbo].[devices] ([DeviceName],[Location] ,[lat],[lon],[Type],[status],[CountryM],[RegionM],[groupId],[Provider],[ConsistencyCheck],[Notes],[TypePlots])"
            linetoadd += " VALUES ('" + code + "' "

            linetoadd += ",'" +name.replace("'" ,"''")+ "'"
            linetoadd += "," + format(lat)
            linetoadd += "," + format(lon)
            linetoadd += ",2"
            linetoadd += ",'active'"
            linetoadd += ",'" + country + "'"
            linetoadd += ",'" + region + "'"
            linetoadd += "," + format(ng)
            linetoadd += ",'" + provider + "','N'," + "'" + type + "',"
            if multicols or multicolsBIG :
                linetoadd += "'" + typePlot + "_" + format(ncols) + "' )"
            else:
                linetoadd += "'" + typePlot + "' )"

            with open ("sqlText.txt",'a') as f:
                f.write(linetoadd +'\n')

            n += 1
            ndev += 1
            print(format(ndev) + " " + country + " " + name + " ncols=" + format(ncols))
            nb = int(ndev / ntotDev * nbat)
            batTxt = "cd " + code +'\n'
            #batTxt += "copy /y ..\gaugeListener.exe ." +'\n'
            #batTxt += "gaugeListener.exe" +'\n'
            #batTxt += "set / p lastValue=<lastValue.txt" +'\n'
            #batTxt += "echo %DATE% %TIME% %lastValue% >> logCalls.txt" +'\n'
            #batTxt += "cd .." +'\n' +'\n'

            #File.AppendAllText("run_" + type + "_" & nb & ".sh", batTxt)
            linetoadd = "insert into [TAD_server].[dbo].[deviceFieldsMap] ( [DeviceID] , [Label], [name], [Main], [MeasureUnit] ) select ID, 'Level', 'inp1', 1, 'm' from devices where DeviceName = '" + code + "'" +'\n'
            linetoadd += "insert into [TAD_server].[dbo].[deviceFieldsMap] ( [DeviceID] , [Label], [name], [Main], [MeasureUnit] ) select ID, 'Forecast30', 'inp2', 0, 'm' from devices where DeviceName = '" + code + "'" +'\n'
            linetoadd += "insert into [TAD_server].[dbo].[deviceFieldsMap] ( [DeviceID] , [Label], [name], [Main], [MeasureUnit] ) select ID, 'Forecast300', 'inp3', 0, 'm' from devices where DeviceName = '" + code + "'" +'\n'
            linetoadd += "insert into [TAD_server].[dbo].[deviceFieldsMap] ( [DeviceID] , [Label], [name], [Main], [MeasureUnit] ) select ID, 'RMS', 'inp4', 0, 'm' from devices where DeviceName = '" + code + "'" +'\n'
            linetoadd += "insert into [TAD_server].[dbo].[deviceFieldsMap] ( [DeviceID] , [Label], [name], [Main], [MeasureUnit] ) select ID, 'Alert Level', 'anag1', 0, 'm' from devices where DeviceName = '" + code + "'" +'\n'
            linetoadd += "insert into [TAD_server].[dbo].[deviceFieldsMap] ( [DeviceID] , [Label], [name], [Main], [MeasureUnit] ) select ID, 'Alert Value', 'anag2', 0, '' from devices where DeviceName = '" + code + "'" +'\n'
      #..,[inp1],[inp2],[inp3],[inp4],[anag1],[anag2]
      #,[anag3] ,[anag4],[inp5],[inp6],[inp7],[inp8]
      #,[inp9],[inp10] ,[inp11],[inp12],[inp13] ,[inp14]
      #,[inp15],[inp16]

            if ncols>1:
                linetoadd += "insert into [TAD_server].[dbo].[deviceFieldsMap] ( [DeviceID] , [Label], [name], [Main], [MeasureUnit] ) select ID, 'Level_2', 'anag3', 1, 'm' from devices where DeviceName = '" + code + "'" +'\n'
                linetoadd += "insert into [TAD_server].[dbo].[deviceFieldsMap] ( [DeviceID] , [Label], [name], [Main], [MeasureUnit] ) select ID, 'Forecast30_2', 'anag4', 0, 'm' from devices where DeviceName = '" + code + "'" +'\n'
                linetoadd += "insert into [TAD_server].[dbo].[deviceFieldsMap] ( [DeviceID] , [Label], [name], [Main], [MeasureUnit] ) select ID, 'Forecast300_2', 'inp5', 0, 'm' from devices where DeviceName = '" + code + "'" +'\n'
                linetoadd += "insert into [TAD_server].[dbo].[deviceFieldsMap] ( [DeviceID] , [Label], [name], [Main], [MeasureUnit] ) select ID, 'RMS_2', 'inp6', 0, 'm' from devices where DeviceName = '" + code + "'" +'\n'
                linetoadd += "insert into [TAD_server].[dbo].[deviceFieldsMap] ( [DeviceID] , [Label], [name], [Main], [MeasureUnit] ) select ID, 'Alert Level_2', 'inp7', 0, 'm' from devices where DeviceName = '" + code + "'" +'\n'
                linetoadd += "insert into [TAD_server].[dbo].[deviceFieldsMap] ( [DeviceID] , [Label], [name], [Main], [MeasureUnit] ) select ID, 'Alert Value_2', 'inp8', 0, '' from devices where DeviceName = '" + code + "'" +'\n'
            if ncols>2:
                linetoadd += "insert into [TAD_server].[dbo].[deviceFieldsMap] ( [DeviceID] , [Label], [name], [Main], [MeasureUnit] ) select ID, 'Level_3', 'inp9', 1, 'm' from devices where DeviceName = '" + code + "'" +'\n'
                linetoadd += "insert into [TAD_server].[dbo].[deviceFieldsMap] ( [DeviceID] , [Label], [name], [Main], [MeasureUnit] ) select ID, 'Forecast30_3', 'inp10', 0, 'm' from devices where DeviceName = '" + code + "'" +'\n'
                linetoadd += "insert into [TAD_server].[dbo].[deviceFieldsMap] ( [DeviceID] , [Label], [name], [Main], [MeasureUnit] ) select ID, 'Forecast300_3', 'inp11', 0, 'm' from devices where DeviceName = '" + code + "'" +'\n'
                linetoadd += "insert into [TAD_server].[dbo].[deviceFieldsMap] ( [DeviceID] , [Label], [name], [Main], [MeasureUnit] ) select ID, 'RMS_3', 'inp12', 0, 'm' from devices where DeviceName = '" + code + "'" +'\n'
                linetoadd += "insert into [TAD_server].[dbo].[deviceFieldsMap] ( [DeviceID] , [Label], [name], [Main], [MeasureUnit] ) select ID, 'Alert Level_3', 'inp13', 0, 'm' from devices where DeviceName = '" + code + "'" +'\n'
                linetoadd += "insert into [TAD_server].[dbo].[deviceFieldsMap] ( [DeviceID] , [Label], [name], [Main], [MeasureUnit] ) select ID, 'Alert Value_3', 'inp14', 0, '' from devices where DeviceName = '" + code + "'" +'\n'            
            with open ("sqlDeviceFieldsMap.txt",'a') as f:
                f.write(linetoadd +'\n')

            if region != region0 or region0 == "" :
                ngr += 1
                linetoadd = "INSERT INTO [dbo].[groups] ([ID], [GroupName], [Note], [Color]) VALUES (" +format( ngr )+ ", '" + region + "' ,'Indonesia Region " + region + "' ,'" + format(ngr * 5) + ",0,255')" +'\n'
                region0 = region
                
                with open ("sqlGroups.txt",'a') as f:
                    f.write(linetoadd +'\n')

            tp = type
            if ncols > 1 :
                tp += "_" + format(ncols)

            linetoadd = "update devices set typePlots='" + tp + "',countryM='" + country + "',regionM='" + region + "', groupID=" +format( ngr  )+ " where deviceName='" + code + "'" +'\n'
            
            with open ("sqlupdateDevices.txt",'w') as f:
                f.write(linetoadd +'\n')

        
        linetoadd = "INSERT INTO [dbo].[Plots] ([TypePlots],[NrPlot],[Description],[Title],[fieldTitle1],[fieldDBName1],[fieldTitle2],[fieldDBName2],[plotWidth],[WebCams],[fieldTitle3],[fieldDBName3],[axisLimits],[fieldColor1],[fieldColor2],[fieldColor3]) VALUES ('" + typePlot + "',1,'Water Level','Measured Water Level','Water Level (m)','inp1',NULL,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL)" +'\n'
        linetoadd += "INSERT INTO [dbo].[Plots] ([TypePlots],[NrPlot],[Description],[Title],[fieldTitle1],[fieldDBName1],[fieldTitle2],[fieldDBName2],[plotWidth],[WebCams],[fieldTitle3],[fieldDBName3],[axisLimits],[fieldColor1],[fieldColor2],[fieldColor3]) VALUES ('" + typePlot + "',2,'Forecast','Forecast 30 (red) - Forecast 300 (blue)','Forecast 30','inp2','Forecast300','inp3',0,NULL,NULL,NULL,NULL,NULL,NULL,NULL)" +'\n'
        linetoadd += "INSERT INTO [dbo].[Plots] ([TypePlots],[NrPlot],[Description],[Title],[fieldTitle1],[fieldDBName1],[fieldTitle2],[fieldDBName2],[plotWidth],[WebCams],[fieldTitle3],[fieldDBName3],[axisLimits],[fieldColor1],[fieldColor2],[fieldColor3]) VALUES ('" + typePlot + "',3,'Rms Alert Signal','Rms (blue) - Alert Signal (red) - Rms Limit (green)','Alert Level (m)','anag1','RMS','inp4',0,NULL,'Calc','inp4*4+0.1',NULL,NULL,NULL,NULL)" +'\n'
        linetoadd += "INSERT INTO [dbo].[Plots] ([TypePlots],[NrPlot],[Description],[Title],[fieldTitle1],[fieldDBName1],[fieldTitle2],[fieldDBName2],[plotWidth],[WebCams],[fieldTitle3],[fieldDBName3],[axisLimits],[fieldColor1],[fieldColor2],[fieldColor3]) VALUES ('" + typePlot + "',4,'Alert Level','Alert Level (0-10)','Alert Level (-)','anag2',NULL,NULL,0,NULL,NULL,NULL,'0;11;1',NULL,NULL,NULL)" +'\n'
        linetoadd += "INSERT INTO [dbo].[Plots] ([TypePlots],[NrPlot],[Description],[Title],[fieldTitle1],[fieldDBName1],[fieldTitle2],[fieldDBName2],[plotWidth],[WebCams],[fieldTitle3],[fieldDBName3],[axisLimits],[fieldColor1],[fieldColor2],[fieldColor3]) VALUES ('" + typePlot + "',7,'Latency','Data Latency','Latency (s)','datediff(second,[Date],[UpdateTime])',NULL,NULL,0,NULL,NULL,NULL,NULL,'0;600;50',NULL,NULL)" +'\n'
        linetoadd += "INSERT INTO [dbo].[Plots] ([TypePlots],[NrPlot],[Description],[Title],[fieldTitle1],[fieldDBName1],[fieldTitle2],[fieldDBName2],[plotWidth],[WebCams],[fieldTitle3],[fieldDBName3],[axisLimits],[fieldColor1],[fieldColor2],[fieldColor3]) VALUES ('" + typePlot + "',1,'Water Level','Measured Water Level','Water Level (m)','inp1',NULL,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL)" +'\n'

        #linetoadd += "INSERT INTO [dbo].[groups] ([ID], [GroupName], [Note], [Color]) VALUES (" + format(ng) + ", '" + type + "' ,'" + type + "' ,'255,0,255')"

        
        with open ("sqlPlots.txt",'a') as f:
            f.write(linetoadd +'\n')

def getListNOAA(URL):
        import requests
        resp=requests.get(URL)
        stations = resp.json()['stations']
        testo = ""
        vbTab='\t'
        for station in stations:
            print(format(station['lat']) + "," + format(station['lng']) + "," + station['name'] + " " + station['id'])
            #'*lat	lon	Country	name	filename	code
            testo += format(station['lat']) + vbTab + format(station['lng']) + vbTab +"United States" + vbTab + station['name'] +vbTab
            testo += "https://tidesandcurrents.noaa.gov/api/datagetter?product=water_level&application=NOS.COOPS.TAC.WL&begin_date=$BEGINDATE&end_date=$ENDDATE&datum=MSL&station=" + station['id'] + "&time_zone=GMT&units=metric&format=json" + vbTab
            newID = station['name'].split(",")[0].replace(" ", "_").replace(".", "")
            if newID == "Charleston" and ',' in station['name'] :
                newID += "_" + station['name'].split(",")[1].replace(" ", "_").replace(".", "")
            
            testo +='NOAA-'+newID
            testo += vbTab + station['id'] +'\n'
        return testo

def getListBIGSRG(URL):
        import requests
        resp=requests.get(URL)
        stations = resp.json()['stations']
        testo = ""
        vbTab='\t'
        for station in stations:
            print(format(station['lat']) + "," + format(station['lng']) + "," + station['name'] + " " + station['id'])
            #'*lat	lon	Country	name	filename	code
            testo += format(station['lat']) + vbTab + format(station['lng']) + vbTab +"United States" + vbTab + station['name'] +vbTab
            testo += "https://tidesandcurrents.noaa.gov/api/datagetter?product=water_level&application=NOS.COOPS.TAC.WL&begin_date=$BEGINDATE&end_date=$ENDDATE&datum=MSL&station=" + station['id'] + "&time_zone=GMT&units=metric&format=json" + vbTab
            newID = station['name'].split(",")[0].replace(" ", "_").replace(".", "")
            if newID == "Charleston" and ',' in station['name'] :
                newID += "_" + station['name'].split(",")[1].replace(" ", "_").replace(".", "")
            
            testo +='NOAA-'+newID
            testo += vbTab + station['id'] +'\n'
        return testo
def checkSensorGLOSS(URL):
    print('opening URL=',URL)
    URL=URL.replace('period=7', 'period=0.5')
    xmlbin=urllib.request.urlopen(URL).read()
    xmlstr=xmlbin.decode()
    #print('len(xmlstr)',len(xmlstr))
    fname=format(uuid.uuid1().int)+'.xml'
    with open(fname,'w') as f:
        f.write(xmlstr)
    #    
    time.sleep(1)    
    print('opening ',fname)
    tree = ET.parse(fname)
    os.remove(fname)
    root=tree.getroot()
    samples=root.findall('sample')
    sensors=[]
    for j in range(len(samples)):
        samp=samples[j]       
        sens=samp.findall('sensor')[0].text
        if not sens in sensors:
            sensors.append(sens)
    if len(sensors)==0:
        URL1=URL.replace('service','station')
        html=urllib.request.urlopen(URL1).read().decode()
        p=html.split('Type of sensor</td><td class=nice>')
        for sect in p[1:]:
            sens=sect.split(' (')[0]
            sensors.append(sens)

    if len(sensors)>3:
        while len(sensors)>3:
            for j in range(len(sensors)):
                if not sensors[j] in 'enc,prs,rad':
                    sensors.pop(j)
                    break
    return sensors
def getListGLOSS(URL):
        import requests
        import pycountry
        resp=requests.get(URL)
        stations = resp.json()
        testo = ""
        vbTab='\t'
        n=-1
        testo=''
        for station in stations:
            if not 'ioc' in station: continue
            n +=1
            print(n,station['name'])
            names=station['ioc']
            print(names,names==list)
            if not type(names)==list:
                names=[names]
            print(names,names==list)
            for name in names:
                print(format(station['geo:lat']) + "," + format(station['geo:lon']) + "," + station['name'] + " " + name)
                cou=pycountry.pycountry.countries.lookup(station['country']).name
                    #'*lat	lon	Country	name	filename	code
                testo += format(station['geo:lat']) + vbTab + format(station['geo:lon']) + vbTab +cou + vbTab + station['name'] +vbTab
                testo += 'https://www.ioc-sealevelmonitoring.org/service.php?query=data&format=xml&code='+name+'&period=7' + vbTab
                testo +='GLOSS-'+name
                testo += vbTab + name +'\n'
        return testo


def getListTR(URL):
        import requests
        resp=requests.get(URL+'/pubSLdataKO')
        stations = resp.text.split("<br>")
        testo = ""
        vbTab='\t'
        for station in stations[2:-1]:
            link=station.split('HREF="')[1].split('"')[0]
            
            resp=requests.get(URL+link).text.split('\r\n')
            for r in resp[:10]:
                if 'ID'in r:
                    ID=r.split('=')[1]
                if 'name' in r:
                    nome=r.split('=')[1]
                    nome=nome[0].upper()+nome[1:].lower()
                if 'latitude' in r:
                    lati=r.split('=')[1]
                if 'longitude' in r:
                    long=r.split('=')[1]

            print(lati + "," + long + "," + nome )
            #'*lat	lon	Country	name	filename	code
            testo += lati + vbTab + long + vbTab +"Turkey" + vbTab + nome +vbTab
            testo += URL+link + vbTab
            
            testo +='TR-'+nome.replace(' ','_')
            testo += vbTab + ID +'\n'
        return testo

def getListINCOIS(xml):
    import json,xmltodict,requests
    resp=requests.get(xml, verify=False).text
    data=xmltodict.parse(resp)
    testo=''
    vbTab='\t'
    try:
        for j in range(len(data['stations']['station'])):
            station=data['stations']['station'][j]
            lati=station['latitude']
            long=station['longitude']
            cou=station['country']
            nome=station['statrealName']
            ID=station['statname']
            link='https://tsunami.incois.gov.in/itews/JSONS/' + nome.upper() +'_1.json'

            riga = lati + vbTab + long + vbTab + cou + vbTab + nome +vbTab
            riga += link + vbTab
            
            riga +='INCOIS-'+nome.replace(' ','_')
            riga += vbTab + ID 
            testo +=riga +'\n'
            print(j,riga)
    except:
        nome=nome
    return testo

def getListDART(URL):
    import requests,pycountry
    testo=''
    vbTab='\t'
    resp=requests.get(URL)
    kml=resp.text
    buoys=kml.split('<Folder>\n\t<name>Tsunami</name>')[1].split('</Folder>')[0].split('<Placemark')

    for buoy in buoys:
        if not 'name' in buoy: continue
        name=extractXML(buoy,'name')
        desc=extractXML(buoy,'Snippet')
        desc=desc.replace("'", ' ')
        if ',' in desc:
            iso2=desc.split(',')[1].strip()
            if iso2=='AK': iso2='US'
            if iso2=='Virgin Is': iso2='US'
            if iso2=='NY': iso2='US'
            if iso2=='OR': iso2='US'
            if iso2=='WA': iso2='US'
            if iso2=='BC': iso2='CA'
            if iso2=='HI': iso2='US'
            if iso2=='New Guinea': iso2='PG'
            try:
                cou=pycountry.pycountry.countries.lookup(iso2).name
            except:
                print('iso2 not found: ',iso2)
                cou='Off-shore'
        else:
            if ' IN' in desc:
                cou='India'
            else:
                cou='Off-Shore'
        coordinates=extractXML(buoy,'coordinates')
        lon,lat,dummy=coordinates.split(',')
        link='https://www.ndbc.noaa.gov/station_page.php?station='+name

        riga = lat + vbTab + lon + vbTab + cou + vbTab + desc +vbTab

        riga += link + vbTab
            
        riga +='DART-'+name.replace(' ','_')
        riga += vbTab + name
        testo +=riga +'\n'
        print(riga)

    return testo

def extractXML(testo,tag):
    if tag in testo:
        res=testo.split('<'+tag+'>')[1].split('</'+tag+'>')[0]
    else:
        res=''
    return res


if __name__ == "__main__":
    #  per analizzare folder  
    #  -c "D:\ar   rabsperry\Init Raspberry\Progs\pythonTAD\pyTAD\DATA\GLOSS"  -s  -gloss
    #  -c "D:\mnt\DISKD\BIG_SRG" -s  -big_id_srg
    arguments = sys.argv[1:]
    count = len(arguments)
    print (count)
    for k in range(len(arguments)):
        arg=arguments[k]
        print(arg)
        if arg=='-c':
            os.chdir(arguments[k+1])
            print("Current working directory: {0}".format(os.getcwd()))
        
        if arg=='-noaa' or arg=='-gloss' or arg=='-dart' or arg=='-big_id_srg':
            with open('listLocations.txt') as f:
                rows=f.read().split('\n')
            testo=''
            for r in rows:
                if r.strip().startswith('$'):
                    keys=r.split('\t')
                    for j in range(len(keys)):
                        if keys[j].split('=')[0]=='jsonurl':
                            jsonURL=keys[j].split('=')[1]
                            jsonURL=jsonURL.replace('$EQ','=')
                        elif keys[j].split('=')[0]=='kmlurl':
                            kmlURL=keys[j].split('=')[1]
                            kmlURL=kmlURL.replace('$EQ','=')
                            #kmlURL='https://www.ndbc.noaa.gov/kml/marineobs_as_kml.php?sort=pgm'
                    testo +=r+'\n'
                    testo +='*************************************************\n'
                    if arg=='-noaa':
                        testo+=getListNOAA(jsonURL)
                    if arg=='-big_id_srg':
                        testo+=getListBIG(jsonURL)
                    elif arg=='-gloss':
                        testo+=getListGLOSS(jsonURL)
                    elif arg=='-dart': 
                        testo+=getListDART(kmlURL)
                    break       
                else:
                    testo+=r+'\n'
            with open('listLocations.txt','w') as f:
                f.write(testo)
        if arg=='-tr':
           with open('listLocations.txt') as f:
                rows=f.read().split('\n')
           testo=''
           for r in rows:
                if r.strip().startswith('$'):
                    keys=r.split('\t')
   
                    testo +=r+'\n'
                    testo +='*************************************************'
                    testo+=getListTR('http://sea.koeri.boun.edu.tr')
                    break       
                else:
                    testo+=r+'\n'
        if arg=='-INCOIS':
           with open('listLocations.txt') as f:
                rows=f.read().split('\n')
           testo=''
           for r in rows:
                if r.strip().startswith('$'):
                    keys=r.split('\t')
   
                    testo +=r+'\n'
                    testo +='*************************************************'
                    testo+=getListINCOIS('https://tsunami.incois.gov.in/itews/homexmls/TideStations.xml')
                    break       
                else:
                    testo+=r+'\n' 
           with open('listLocations.txt','w') as f:
                f.write(testo)

        if arg=='-s':
            prepareFolders('listLocations.txt')

def virtualConfig(arguments):
    config={}
    config['pressureSensor']=''
    config['Tail']=''       
    config['TailSimple']=''
    config['folderWWW']=''
    config['ReadFile']=''
    config['PhotoCMD']=''
    config['PhotoAlertLevel']=10
    config['PhotoTimeInterval']=2
    config['MQTT_server']=''
    config['MQTT_listener']=''        
    config['MQTT_username']='' 
    config['MQTT_password']='' 
    config['MQTT_msg']=''
    config['ADC_1']=106
    config['ADC_2']=105
    config['scrapePage'] =''
    config['TCP_host']=''
    config['vmin']=-10
    config['vmax']=10
    IDdevice=''
    outFolder='/'
    for j in range(len(arguments[1:])):
        if arguments[j]=='-code':
                code=arguments[j+1]
        if arguments[j]=='-IDdevice':
                IDdevice=arguments[j+1]
        if arguments[j]=='-n30':
                n30=int(arguments[j+1])
        if arguments[j]=='-n300':
                n300=int(arguments[j+1])
        if arguments[j]=='-mult':
                mult=float(arguments[j+1])
        if arguments[j]=='-add':
                addRMS=float(arguments[j+1])
        if arguments[j]=='-th':
                th=float(arguments[j+1])
        if arguments[j]=='-mode':
                mode=arguments[j+1]
        if arguments[j]=='-out':
                outFolder=arguments[j+1]
   #  example of call  python3 scrape.py -idDevice adak -code  adak  -n300 150  -n30 15  -mult 4  -add 0.1  -th 0.08 -mode GLOSS -out e:/temp

    if IDdevice=='':  IDdevice=code
    config['IDdevice']=IDdevice
    config['Interval'] = -1
    config['n300']=n300
    config['n30']=n30
    config['threshold']=th
    config['ratioRMS']= mult
    config['AddRMS']=addRMS
    config['SaveURL']=''
    config['AlertURL']=''
    config['AlertLevel']=2
    config['outFolder']=outFolder
    if mode=='GLOSS':
        config['serverAddress']='https://www.ioc-sealevelmonitoring.org/service.php?query=data&format=xml&code='+code+'&period=7'
    elif mode=='NOAA':
        config['serverAddress']='https://tidesandcurrents.noaa.gov/api/datagetter?product$EQwater_level&application$EQNOS.COOPS.TAC.WL&begin_date$EQ$BEGINDATE&end_date$EQ$ENDDATE&datum$EQMSL&station$EQ'+code+'&time_zone$EQGMT&units$EQmetric&format$EQjson'        
    if not os.path.exists(outFolder):
        os.makedirs(outFolder)
    with open(outFolder+os.sep+'config.txt','w') as f:
        for key in config.keys():
            f.write(key+'='+format(config[key])+'\n')
    return config