from dashImport import app,html,dcc
from dash.dependencies import Input, Output,State
from io import StringIO
import os
from datetime import datetime,timedelta,date
# pip install python-dateutil
from dateutil.parser import parse
from navbar import Navbar
from urllib.parse import urlparse, parse_qs, urlencode
from utilities import numpydt64to_datetime,haversine,getListDevices,getMaxDistances,getList,tds,getEventDetail
from plots import plotEvents,plotEventsNoGTS
from searchDevices import searchDevice

import pandas as pd


def getTableEvents(params, url):
    events=eventsGDACS.sort_values(by=['Amplitude'], ascending=False).groupby('EventId').first().sort_values(by=['EventDate'], ascending=False)
    year0=-1;startYear=1000;endYear=10000
    print(params)
    tabrows=[]
    if 'MinMag' in params:
        MinMag=params['MinMag'][0]
    if 'MinHei' in params:
        MinHei=params['MinHei'][0]
    if 'gts' in params:
        gts=params['gts'][0]
    if 'year0' in params:
        startYear=params['year0'][0]
    if 'year1' in params:
        endYear=params['year1'][0]
    for j in range(len(events)):
        dat=numpydt64to_datetime(events['EventDate'].values[j])
        if not (dat.year>=startYear and dat.year<=endYear):
            continue
        EventId=events.index[j]
        Mag=format(events['Magnitude'].values[j])
        depth=format(events['Depth'].values[j])
        #print(EventId,EventIdreq,EventId==EventIdreq)
        Location=events['EventLocation'].values[j]
        Country=''
        EventLat=events['EventLat'].values[j]
        EventLon=events['EventLon'].values[j]    
        PlaceMax=events['Place'].values[j]  
        
        PlaceMaxCountry=''
        Amplitude=events['Amplitude'].values[j]            
        if PlaceMax=='n.a.':
            Amplitude='n.a.'
            title='M'+format(Mag)+' '+ Location    
            fileid=dat.strftime('%Y-%m-%d_%H%M%S')+'_'+format(Mag)+'_'+format(EventLat)+'_'+format(EventLon)+'_'+title.replace(' ','_').replace('.','_').replace(':','_')+'.txt'
            #print('data'+os.sep+'derivedData'+os.sep+fileid,os.path.exists('data'+os.sep+'derivedData'+os.sep+fileid))
            if os.path.exists('data'+os.sep+'derivedData'+os.sep+fileid):
                with open('data'+os.sep+'derivedData'+os.sep+fileid) as f:
                    lines=f.read().strip()
                
                if lines !='':
                    n=len(lines.split('\n'))
                    mode='DET. '+format(n)+' devices'
                else:
                    mode=''
        else:
            mode=''
        linkEvent= urlparse(url).scheme+'://'+urlparse(url).netloc+'/listEvents?EventId='+format(EventId)
        if PlaceMax=='n.a.':
            linkEvent +='&NoPlace=True'
        
        if float(Mag)>=MinMag and ((PlaceMax !='n.a.' and Amplitude>MinHei) or MinHei==0) and (gts=='' or (gts=='GTS' and PlaceMax !='n.a.') or (gts=='noGTS' and PlaceMax =='n.a.')):
            tdDate=html.Td(dat.strftime('%d-%m-%Y %H:%M:%S'),style=tds(180))
            if float(Mag)>0:
                tdMag=html.Td(html.B('M'+format(Mag)),style=tds(80))
            else:
                tdMag=html.Td('n.a.',style=tds(80))
            tdplace=html.Td(html.A(Location+' '+Country,href=linkEvent,target='_event'),style=tds(300))
            tdplace1=html.Td(format(EventLon)+'/'+format(EventLat),style=tds(150))

        
            if PlaceMax !='n.a.':
                tdLoc=html.Td(PlaceMax +', '+PlaceMaxCountry,style=tds(200) )   
                tdLoc1=html.Td([html.B(format(Amplitude)),' m '],style=tds(150))
                tdquality=html.Td('GTS' ,style=tds(150) )        
            else:
                tdLoc=html.Td(PlaceMax,style=tds(200) )   
                tdLoc1=html.Td('',style=tds(150))                
                tdquality=html.Td(mode ,style=tds(150) )        


            if dat.year !=  year0:
                tabrows.append(html.Tr(html.Td(html.B(dat.year),style={'colspan':5})))
            year0=dat.year
        
            tr=html.Tr([tdDate,tdMag,tdplace,tdplace1,tdLoc,tdLoc1,tdquality])
            tabrows.append(tr)
    tabella=html.Table(tabrows)
    return tabella

def getListMeasurements_byDistance(url,EventId,dat,distanceKM,searchDev,lon,lat,devGLOSS,devDART,devNOAA,devIDSL,DBs='', fileID=''):
    datemin=dat -timedelta(days=1)#
    datemax=dat +timedelta(days=2)

    list=[]

    if 'GLOSS @vliz' in DBs or DBs=='' or DBs==[]:
        listG=[]
        for k in range(len(devGLOSS)):
            dev=devGLOSS[k]
            idDevice=dev['Code']
            if not idDevice in listG:
                lonMeas=float(dev['Lon'])
                latMeas=float(dev['Lat'])
                dc=dev['date_created']
                try:
                    dc=datetime.strptime(dc,'%Y-%m-%d %H:%M:%S.%f')
                except:
                    dc=datetime(1900,1,1)
                Place=dev['Location']
                dist=haversine(lon,lat,lonMeas,latMeas)/1000
                if dist<distanceKM and dc<=dat and (searchDev =='' or searchDev in Place or searchDev in dev['Code']):
                    DB='GLOSS @vliz';GROUP=DB;idDevice=dev['Code']
                    params='DB='+DB+'&GROUP='+format(GROUP)+'&idDevice='+format(idDevice)+'&datemin='+datemin.strftime('%Y-%m-%d %H:%M:%S')+'&datemax='+datemax.strftime('%Y-%m-%d %H:%M:%S')+'&ID='+format(EventId)
                    list.append((params,Place,dist,lonMeas,latMeas,DB,GROUP,idDevice,'DIST'))
                    listG.append(idDevice)
    if 'NOAA TC' in  DBs or DBs=='' or DBs==[]:
        for k in range(len(devNOAA['stations'])):
            station=devNOAA['stations'][k]
            #print(format(station['lat']) + "," + format(station['lng']) + "," + station['name'] + " " + format(station['id']))
            idDevice = station['id']
            Place=station['name']
            lonMeas=station['lng']
            latMeas=station['lat']
            dist=haversine(lon,lat,lonMeas,latMeas)/1000
            if dist<distanceKM  and (searchDev =='' or searchDev in Place or searchDev in idDevice):
                DB='NOAA TC';GROUP=DB
                params='DB='+DB+'&GROUP='+format(GROUP)+'&idDevice='+format(idDevice)+'&datemin='+datemin.strftime('%Y-%m-%d %H:%M:%S')+'&datemax='+datemax.strftime('%Y-%m-%d %H:%M:%S')+'&ID='+format(EventId)
                list.append((params,Place,dist,lonMeas,latMeas,DB,GROUP,idDevice,'DIST'))
    if 'DART' in DBs or DBs=='' or DBs==[]:
        for elem in devDART:
            name,desc,cou,lonMeas,latMeas,link,sy,ey=elem
            sd=datetime(sy,1,1)
            ed=datetime(ey,12,31)
            Place='Station '+name
            Place=(desc.split('-')[0]+' - '+desc.split('-')[1]).strip()
            lonMeas=float(lonMeas)
            latMeas=float(latMeas)
            dist=haversine(lon,lat,lonMeas,latMeas)/1000
            if dist<distanceKM  and dat>=sd and dat<=ed  and (searchDev =='' or searchDev in Place or searchDev in name):
                DB='DART';GROUP=DB;idDevice=name
                params='DB='+DB+'&GROUP='+format(GROUP)+'&idDevice='+format(idDevice)+'&datemin='+datemin.strftime('%Y-%m-%d %H:%M:%S')+'&datemax='+datemax.strftime('%Y-%m-%d %H:%M:%S')+'&ID='+format(EventId)
                list.append((params,Place,dist,lonMeas,latMeas,DB,GROUP,idDevice,'DIST'))

    if ('JRC_TAD' in DBs or DBs=='' or DBs==[]) and dat.year>2014:
        gr=''
        if ',' in DBs:
            p=DBs.split(',')
            for d in p:
                if 'JRC_TAD' in d and '|' in d:
                    gr=d.split('|')[1]
                    break
        for k in range(len(devIDSL)):
            for L in range(len(devIDSL[k]['features'])):                
                Place=devIDSL[k]['features'][L]['properties']['Location']
                if pd.isna(Place):continue
                ID=devIDSL[k]['features'][L]['properties']['Name']
                lonMeas,latMeas=devIDSL[k]['features'][L]['geometry']['coordinates']
                lonMeas=float(lonMeas);latMeas=float(latMeas)
                #print(lon,lat,lonMeas,latMeas)
                dist=haversine(lon,lat,lonMeas,latMeas)/1000
                if dist<distanceKM  and (searchDev =='' or searchDev in Place or searchDev in ID):
                    GROUP=devIDSL[k]['properties']['Name']
                    if gr=='' or gr==GROUP:
                        DB='JRC_TAD';idDevice=ID
                        params='DB='+DB+'&GROUP='+format(GROUP)+'&idDevice='+format(idDevice)+'&datemin='+datemin.strftime('%Y-%m-%d %H:%M:%S')+'&datemax='+datemax.strftime('%Y-%m-%d %H:%M:%S')+'&ID='+format(EventId)
                        list.append((params,Place,dist,lonMeas,latMeas,DB,GROUP,idDevice,'DIST'))
    if fileID !='':
        if os.path.exists(fileID):
            with open(fileID) as f:
                testo=f.read()
            if testo !='':
                lines=testo.split('\n')
                for row in lines:
                    if row=='':continue
                    p=row.split('\t')
                    DB,GROUP,idDevice=p[0].split('|')
                    lonMeas,latMeas,Place=p[1:4]
                    lonMeas=float(lonMeas);latMeas=float(latMeas)
                    dist=haversine(lon,lat,lonMeas,latMeas)/1000
                    params='DB='+DB+'&GROUP='+format(GROUP)+'&idDevice='+format(idDevice)+'&datemin='+datemin.strftime('%Y-%m-%d %H:%M:%S')+'&datemax='+datemax.strftime('%Y-%m-%d %H:%M:%S')+'&ID='+format(EventId)
                    for k in range(len(list)):
                        if list[k][5:8]==(DB,GROUP,idDevice):
                            list.pop(k)
                            break
                    list.append((params,Place,dist,lonMeas,latMeas,DB,GROUP,idDevice,'DETECTED'))

    listsort=sorted(list, key=lambda tup: tup[2])
    tabrows=[]
    
    evDist=pd.DataFrame(columns=['IDSource', 'EventId', 'EventDate', 'EventLocation', 'EventLat', 'EventLon', 
                                 'Magnitude', 'Depth', 'GTSName', 'Pubdate', 'Place', 'Lat', 'Lon', 'ArrivalTime', 'Amplitude', 'Period', 'DB', 'GROUP', 'CODE', 'LAT1', 'LON1']
                        )
    evDist=[]
    for l in range(len(listsort)):
        params,Place,dist,lonMeas,latMeas,DB,GROUP,idDevice,mode=listsort[l]
        link= urlparse(url).scheme+'://'+urlparse(url).netloc+'/signals?'+listsort[l][0]
        #linkGDACS='https://www.gdacs.org/report.aspx?eventtype=EQ&eventid='+format(EventId)
        tdLoc=html.Td(html.A(format(listsort[l][1]) ,href=link, target='_new1'),style=tds(300) )
        tdDist=html.Td(format(int(listsort[l][2]))+' km' ,style=tds(200) )
        tdparams=html.Td(','.join(params.split('&')[:3]) ,style=tds(400) )
        tdquality=html.Td(mode ,style=tds(100) )
        tr=html.Tr([tdLoc,tdDist,tdparams,tdquality])
        tabrows.append(tr)
        
        ev={'LAT1':latMeas,'LON1':lonMeas,'Place':Place,'DB':DB,'GROUP':GROUP,'CODE':idDevice,'Amplitude':1,'Period':-1,
            'Magnitude':0,'ArrivalTime':'00:00','EventLon':-1,'EventLat':-1,'Lon':-1,'Lat':-1,'IDSource':mode}
        evDist.append(ev)
        #evDist=pd.concat([evDist,pd.DataFrame(ev)], ignore_index=True)
 
    tabella=html.Center(html.Table(tabrows))
    return tabella,evDist

def getListMeasurements(EventId,url):
    ev=eventsGDACS[eventsGDACS['EventId']==EventId].sort_values(by='ArrivalTime',ascending=False)
    print(ev)
    tabrows=[]
    for j in range(len(ev)):
        dat=numpydt64to_datetime(ev['EventDate'].values[j])
        datemin=dat -timedelta(days=1)#
        datemax=dat +timedelta(days=2)
        Provider=ev['IDSource'].values[j]
        GTSName=ev['GTSName'].values[j]
        Place=ev['Place'].values[j]
        Lon=ev['Lon'].values[j]
        Lat=ev['Lat'].values[j]
        Lon1=ev['LON1'].values[j]
        Lat1=ev['LAT1'].values[j]
        ArrivalTime=ev['ArrivalTime'].values[j]
        Amplitude=format(ev['Amplitude'].values[j])+' m'
        Period=format(ev['Period'].values[j])+' min'
        source=ev['IDSource'].values[j] 
        if Place=='n.a.':
            DB='';GROUP='';idDevice=''
        else:
            if Lon1==-1 and Lat1==-1:
                testo=searchDevice(Place,Lon,Lat).split('\n')[0].split('\t')
                print(testo)
                DB=testo[0]
                GROUP=testo[1]
                idDevice=testo[2]
            else:
                DB=ev['DB'].values[j]
                GROUP=ev['GROUP'].values[j]
                idDevice=ev['CODE'].values[j]

        params='DB='+DB+'&GROUP='+format(GROUP)+'&idDevice='+format(idDevice)+'&datemin='+datemin.strftime('%Y-%m-%d %H:%M:%S')+'&datemax='+datemax.strftime('%Y-%m-%d %H:%M:%S')+'&ID='+format(EventId)
        linkEvent= urlparse(url).scheme+'://'+urlparse(url).netloc+'/listEvents?EventId='+format(EventId)
        link= urlparse(url).scheme+'://'+urlparse(url).netloc+'/signals?'+params
        linkGDACS='https://www.gdacs.org/report.aspx?eventtype=EQ&eventid='+format(EventId)
        tdLoc=html.Td(html.A(format(Place) ,href=link, target='_new1'),style=tds(200) )   
        tdLoc1=html.Td(ArrivalTime,style=tds(100))
        tdLoc2=html.Td([html.B(format(Amplitude)),' m ('+format(Period)+')'],style=tds(150))
        tdsource=html.Td(source,style=tds(100))
        tr=html.Tr([tdLoc,tdLoc1,tdLoc2,tdsource])
        tabrows.append(tr)
    tabella=html.Center(html.Table(tabrows))
    return tabella
 
fname='tsu_archive.tsv'
#events=pd.read_csv(fname,sep='\t')
#fname='data'+os.sep+'TSObserved_0912.xlsx'
fname='data'+os.sep+'TSObserved_0913_A.xlsx';sh='TSObs5'
eventsGDACS=pd.read_excel(fname,sh).sort_values(by=['EventDate','Amplitude'])

devGLOSS=getListDevices('GLOSS @vliz')
devNOAA=getListDevices('NOAA TC')
devIDSL=getListDevices('JRC_TAD')
devDART=getListDevices('DART')


#EventId=1028737
#dat=getEventDetail(EventId)
   

def showEvents(url):
    params=parse_qs(urlparse(url).query)
    EventIdreq='';searchDev=''
    if 'EventId' in params:
        EventIdreq=int(params['EventId'][0])
        #dat=getEventDetail(EventIdreq)
    if 'searchDev' in params:
        searchDev=params['searchDev'][0]
    #print('params, EventIdreq',params,EventIdreq)
    #print(eventsGDACS)
    print('PID=....',os.getpid())

    if EventIdreq=='':
        title='List of events with measured Tsunami records (since 2000)'
        description=['The map shows the Tsunami events for which measuremsnts are available and have been reported in GTS messages.  There may have been other events for which a GTS message was not available (restricted GTS) or the measurement has not been reported. Clicking on the first link,  after the date, you will open the event and you can then see whcih sensor have been reported and their maximum height']
        description=html.Div(description, style={'width':'1000px'})
        tabdetails=''
        params={'MinMag':[0],'MinHei':[0],'gts':['']}
        tabella=getTableEvents(params,url)
        back=''
        listMinMag=[]
        for mag in range(50,100,5):
            listMinMag.append({'label':'M '+format(mag/10) ,'value':mag/10})
        listMinHei=[]
        listMinHei.append({'label':'Any' ,'value':-1})
        for hei in range(0,100,5):
            listMinHei.append({'label':format(hei/10)+' m' ,'value':hei/10})
        listyears=[]
        now=datetime.utcnow()
        for y in range(2000,now.year+1):
            listyears.append({'label':format(y) ,'value':y})
        listGTS=[]
        listGTS.append({'label':'Any event' ,'value':''})
        listGTS.append({'label':'Only events with GTS data' ,'value':'GTS'})
        listGTS.append({'label':'Only events w/o GTS data' ,'value':'noGTS'})
        tdhead=tds('','italic',12)
        filters=html.Table([
        html.Tr([html.Td('Min. Magnitude',style=tdhead),html.Td('Min. Height',style=tdhead),
                 html.Td('From',style=tdhead),html.Td('To',style=tdhead),
                 html.Td('GTS derived',style=tdhead)]),
        html.Tr([html.Td(dcc.Dropdown(id='MinMag',options=listMinMag),style=tds(150)),
                 html.Td(dcc.Dropdown(id='MinHei',options=listMinHei),style=tds(150)), 
                 html.Td(dcc.Dropdown(id='year0',options=listyears),style=tds(100)), 
                 html.Td(dcc.Dropdown(id='year1',options=listyears),style=tds(150)), 
                 html.Td(dcc.Dropdown(id='gts',options=listGTS),style=tds(250)),                 
                 html.Td(html.Button('Filter events',id='filterEvents'),style=tds(200)),
                         ])
        ])

        plot=html.Div(plotEvents(url,eventsGDACS,params),id='grafico')

        layout=html.Div([Navbar(),html.Br(),html.Center([html.H2(title),plot,tabdetails,
                         description, back,filters,html.Center(tabella,id='tabEvents')])])    
    else:
        #title='List of Tsunami records for one specific event'
        description=['Clicking on the measurement location link, you will visualize the measured signals and apply the Tsunami detection algorithm.'        ]
        tabdetails,title,dat,mag,lon,lat,PlaceMax=getEventDetail(EventIdreq,eventsGDACS)
        listDists=getMaxDistances()
        listDBs=getList('DB')

        if PlaceMax=='n.a.':
            description.append(html.Br())
            description.append('As for this event the GTS message is unavailable,  all the measurements at a specified distance are shown; it is not sure that the measurements will show an event. In case the distance is too small you can modify using the dropdown menu below.')
            description.append(html.Br())
            description.append('A flag DETECTED and a red color in the map  indicates that the Detection model identified an event; this does not mean that a real event is measured by the device because in some cases the signal is faulty and an event is not present. This is particularly true for gauges detected only far from the epicentre.')
            filters=html.Table([
            html.Tr([html.Td('Max Distance'),html.Td('Databases'),html.Td('Search device')]),
            html.Tr([html.Td(dcc.Dropdown(id='MaxDistance',options=listDists),style=tds(200)),
                     html.Td(dcc.Dropdown(id='DBs',options=listDBs,multi=True),style=tds(250)),
                     html.Td(dcc.Input(searchDev,id='searchDev'),style=tds(300)),
                     html.Td(html.Button('Filter devices',id='filterDev'),style=tds(200)),
                             ])
            ])
        else:
            filters=''

        description=html.Div(description, style={'width':'1000px', 'font-style':'italic'})
        tabella,evDist=getTableDevices(params,url)

        linkURL=urlparse(url).scheme+'://'+urlparse(url).netloc+'/listEvents'
        back=html.Center(html.A('Back to list of events',href=linkURL))
        params={'MinMag':[5],'MinHei':[0],'gts':['GTS']}
        if evDist ==[]:
            plot0=plotEvents(url,eventsGDACS,params,EventIdreq)
        else:
            plot0=plotEventsNoGTS(url,evDist,params,EventIdreq,eventsGDACS)

        plot=html.Div(plot0,id='graficoEvents')
        layout=html.Div([Navbar(),html.Br(),html.Center(
                [
                html.H2(title),
                html.Table(
                    html.Tr([
                        html.Td(tabdetails,style={'width':'60%','verticalAlign':'top'}),
                        html.Td(plot,style={'width':'40%'})
                           ])
                          ),
                description, back,filters,html.Center(tabella,id='tabMeasurements')
                ])])
    
    return  layout
            
def getTableDevices(params,url):   
    #print('getTableDevices, params=',params)
    NoPlace=False;MaxDistanceKM='';DBs='';searchDev=''

    print('PID=....',os.getpid())
    if 'NoPlace' in params:
        NoPlace=params['NoPlace'][0]=='True'
    if 'MaxDistance' in params:
        if params['MaxDistance'][0] !='':
            MaxDistanceKM=float(params['MaxDistance'][0])
        else:
            MaxDistanceKM=''
    if 'DBs' in params:
        DBs=params['DBs'][0]
    if 'searchDev' in params:
        searchDev=params['searchDev'][0]
    if 'EventId' in params:
        EventIdreq=int(params['EventId'][0])
    
    tabdetails,title,dat,mag,lon,lat,placeMax=getEventDetail(EventIdreq,eventsGDACS)
    if NoPlace==False:
        tabella=getListMeasurements(EventIdreq,url)
        evDist=[]
    else:
        if MaxDistanceKM=='':
            if mag>0:
                distanceKM=2000/9*mag
            else:
                distanceKM=100
        else:
            distanceKM=MaxDistanceKM
        fileid=dat.strftime('%Y-%m-%d_%H%M%S')+'_'+format(mag)+'_'+format(lat)+'_'+format(lon)+'_'+title.replace(' ','_').replace('.','_').replace(':','_')+'.txt'
        fileid='data'+os.sep+'derivedData'+os.sep+fileid
        tabella,evDist=getListMeasurements_byDistance(url,EventIdreq,dat,distanceKM,searchDev,lon,lat,devGLOSS,devDART,devNOAA,devIDSL,DBs,fileid)

    return tabella,evDist

#url='http://localhost:8050/listEvents'
#params={'MinMag':[5],'MinHei':[0],'gts':['']}
#plot=plotEvents(url,eventsGDACS,params)
#tab=getTableEvents('')
#tab=showEventsGDACS('http://localhost:8050/listEvents?EventId=1048&NoPlace=True&MaxDistance=5000&DBs=DART,NOAA%20TC')
#EventId=1232
#meas=getListMeasurements(EventId,'')

@app.callback(Output('tabEvents','children'),Output('grafico','children'),
              Input('filterEvents', 'n_clicks'),State('MinMag','value'),State('MinHei','value'),
              State('year0','value'),State('year1','value'),
              State('gts','value'),State('url', 'href'))

def updateTableEvents(nclick,MinMag,MinHei,year0,year1,gts,url):

    if MinMag==None:
        MinMag=0
    if MinHei==None:
        MinHei=0
    if gts==None:
        gts=''
    if year0==None:
        year0=1000
    if year1==None:
        year1=10000
    params={'MinMag':[MinMag],'MinHei':[MinHei],'gts':[gts],'year0':[year0],'year1':[year1] }
    #print('updateTableEvents  params',params,url)
    tabella=getTableEvents(params,url)
    plot=plotEvents(url,eventsGDACS,params)
    return tabella,plot



@app.callback(Output('tabMeasurements','children'),Output('graficoEvents','children'),
              Input('filterDev', 'n_clicks'),State('DBs','value'),State('MaxDistance','value'),
              State('searchDev','value'),State('evID','children'),State('PlaceMax','children'),State('url', 'href'))

def updateTableDevices(nclick,DBs,MaxDistance,searchDev,evID,placeMax,url):
    #print('placeMax=','>'+placeMax+'<',placeMax=='n.a.')
    if DBs==None:
        DBs=[]
    if MaxDistance==None:
        MaxDistance=''
    if searchDev==None:
        searchDev=''
    if placeMax=='n.a.':
        NoPlace='True'
    else:
        NoPlace='False'

    params={'DBs':[DBs],'MaxDistance':[MaxDistance],'searchDev':[searchDev],'EventId':[evID], 'NoPlace':[NoPlace]}
    #print('updateTableDevices  params',params,url)
    tabella,evDist=getTableDevices(params,url)
    if evDist ==[]:
        plot=plotEvents(url,eventsGDACS,params,evID)
    else:
        plot=plotEventsNoGTS(url,evDist,params,evID,eventsGDACS)
    
    return tabella,plot

if __name__ == '__main__':
    print('PID=',os.getpid())

    appserver=app.server
    app.run_server(debug=True)