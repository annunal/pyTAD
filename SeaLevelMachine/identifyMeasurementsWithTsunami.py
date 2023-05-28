from calcAlgorithm import calcAlgorithm as ca
from utilities import getEventDetail,getListDevices,getValues
from listEvents import getListMeasurements_byDistance
import pandas as pd
import os
from datetime import datetime,timedelta
# The objective is to create a new table containing measurements identified 
# automatically for events which do not have a GTS message associated
# A. Annunziato (2022)
#
#  1 list all events without GTS
#  2  for each event calculate  the alert parameters  for each device at a distance deending on magnitude
#  3  if alert is generated >5  after the event,  include in the table
#
def getcalcvalues(dat,DBNAME,idDevice):
    n300=300
    n30=30
    threshold=0.1
    ratioRMS=3
    addRMS=0.0
    nmaxData=10000
    tmin=dat-timedelta(days=1)
    tmax=dat+timedelta(days=2)
    firstAlert=datetime(2050,1,1)
    values, avgDelta=getValues(DBNAME,idDevice, tmin, tmax, nmaxData)  
    if values!=[]:
      if values['x']!=[]:
        STImin=15
        LTImin=180
        n300=int(float(LTImin)*60/avgDelta)
        if n300<10:
            return [],firstAlert
        n30= int(float(STImin)*60/avgDelta)
        if n30<2:n30=2
        config={}
        config['Interval']=avgDelta
        config['n30']=n30
        config['n300']=n300
        config['ratioRMS']=float(ratioRMS)
        config['threshold']=float(threshold)
        config['AddRMS']=float(addRMS)
        config['vmin']=-1e9
        config['vmax']=1e9
        config['SaveURL']=''
        dir_path = os.path.dirname(os.path.realpath(__file__))
        fold=dir_path+os.sep+'temp'
        if not os.path.exists(fold):
            os.makedirs(fold)
        calg=ca(0,fold,config)
        values['fore30']=[]
        values['fore300']=[]
        values['rms']=[]
        values['rmsMod']=[]
        values['alertSignal']=[]
        values['alertValue']=[]
    
        AS=''

        for j in range(len(values['x'])):
            tim=values['x'][j]
            measure_Float=values['y'][j]
            forecast30,forecast300,rms,alertSignal,alertValue= calg.addMeasure(tim,measure_Float,fold,0)
            values['fore30'].append(forecast30)
            values['fore300'].append(forecast300)
            values['rms'].append(rms)
            #print(type(rms),type(ratioRMS),type(addRMS))
            values['rmsMod'].append(rms*ratioRMS+addRMS)
            values['alertSignal'].append(alertSignal)
            values['alertValue'].append(alertValue)
            if alertValue>3 and tim<firstAlert and tim>dat:
                firstAlert=tim
#            if int(j/1000)*1000==j:
#                print(j,len(values['x']), alertValue,alertSignal)
#                AS +=format(j)+' '+format(round(alertSignal,3))+'|'
    return values,firstAlert      
#
#  1 list all events without GTS
fname='data'+os.sep+'TSObserved_0913_A.xlsx';sh='TSObs5'
events=pd.read_excel(fname,sh).sort_values(by=['EventDate','Amplitude'])
events=events[events['IDSource']=='NOGTS']

devGLOSS=getListDevices('GLOSS @vliz')
devNOAA=getListDevices('NOAA TC')
devIDSL=getListDevices('JRC_TAD')
devDART=getListDevices('DART')
url='http://localhost'
#for EventIdreq in events['EventId']:
#    tabdetails,title,dat,mag,lon,lat,placeMax=getEventDetail(EventIdreq,events)
#    fileid=dat.strftime('%Y-%m-%d_%H%M%S')+'_'+format(mag)+'_'+format(lat)+'_'+format(lon)+'_'+title.replace(' ','_')
#    fileid1=dat.strftime('%Y-%m-%d_%H%M%S')+'_'+format(mag)+'_'+format(lat)+'_'+format(lon)+'_'+title.replace(' ','_').replace('.','_').replace(':','_')
#    for k in range(len(fileid)):
#        if os.path.exists('data'+os.sep+'derivedData'+os.sep+fileid[:k]+'.txt'):
#    #if os.path.exists('data'+os.sep+'derivedData'+os.sep+fileid):
#            #cmd='rename data'+os.sep+'derivedData'+os.sep+fileid[:k]+'.txt '+fileid+'.txt'
#            #os.system(cmd)
#            os.rename('data'+os.sep+'derivedData'+os.sep+fileid[:k]+'.txt','data'+os.sep+'derivedData'+os.sep+fileid1+'.txt')
#            break

for EventIdreq in events['EventId']:
    tabdetails,title,dat,mag,lon,lat,placeMax=getEventDetail(EventIdreq,events)
    
    fileid=dat.strftime('%Y-%m-%d_%H%M%S')+'_'+format(mag)+'_'+format(lat)+'_'+format(lon)+'_'+title.replace(' ','_').replace('.','_').replace(':','_')+'.txt'
    if not os.path.exists('data'+os.sep+'derivedData'+os.sep+fileid):
        if mag>0:
            distanceKM=5000/9*mag
        else:
            distanceKM=1000
        print('\n', title,dat,mag, distanceKM)
        DBs='GLOSS @vliz,DART,JRC_TAD|IDSL,JRC_TAD|Indonesia'
        tabella,evDist=getListMeasurements_byDistance(url,EventIdreq,dat,distanceKM,'',lon,lat,devGLOSS,devDART,devNOAA,devIDSL,DBs)
        if evDist==[]:
            with open('data'+os.sep+'derivedData'+os.sep+fileid,'w') as f:
                f.write('')
        else:            
            for ev in evDist:
                #print(ev)
                DBNAME=ev['DB']
                GROUP=ev['GROUP']
                CODE=ev['CODE'];print(DBNAME,CODE)
                lon=ev['LON1']
                lat=ev['LAT1']
                Place=ev['Place']
                if CODE=='darw':
                    CODE=CODE

                values,firstAlert=getcalcvalues(dat,DBNAME,CODE)
                if firstAlert<datetime(2050,1,1):
                    print(title, dat, firstAlert, Place)
                    with open('data'+os.sep+'derivedData'+os.sep+fileid,'a') as f:
                        f.write(DBNAME+'|'+format(GROUP)+'|'+format(CODE)+ '\t'+ format(lon)+'\t'+format(lat)+'\t'+Place+'\t'+ title+'\t'+ format(dat)+'\t'+ format(firstAlert)+'\n')
            if not os.path.exists('data'+os.sep+'derivedData'+os.sep+fileid):       
              with open('data'+os.sep+'derivedData'+os.sep+fileid,'w') as f:
                f.write('')                       