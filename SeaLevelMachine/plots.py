import pandas as pd
from dash import Dash 
from dashImport import app,html,dcc
from dash.exceptions import PreventUpdate
from statistics import mean
from dash.dependencies import Input, Output,State
import os
import plotly.express as px
import plotly.graph_objects as go
import webbrowser,math
from utilities import numpydt64to_datetime
from urllib.parse import urlparse, parse_qs, urlencode
from datetime import datetime,timedelta,date
import numpy as np
from utilities import getEventDetail

def plotEvents(url,obs,params,ID=''):   
    MinMag=0;MinHei=0;gts=''
    if 'MinMag' in params:
        MinMag=params['MinMag'][0]
    if 'MinHei' in params:
        MinHei=params['MinHei'][0]
    if 'gts' in params:
        gts=params['gts'][0]

    obs[pd.isna(obs['Amplitude'])]=0
    if ID=='':  
        obs=obs[obs['Magnitude']>MinMag]
        obs=obs[obs['Amplitude']>MinHei]
        if gts=='GTS':
            obs=obs[obs['Place'] !='n.a.']
        if gts=='noGTS':
            obs=obs[obs['Place'] =='n.a.']
        obs=obs.sort_values(by=['Magnitude'], ascending=False).groupby('EventId').first()
        LatLabel='EventLat'
        LonLabel='EventLon'
    else:
        obs=obs[pd.isna(obs['LON1'])==False]
        obs=obs[pd.isna(obs['LAT1'])==False]
        obs=obs[obs['Amplitude']>=MinHei]
        obs[obs['Amplitude']<0]=0
        obs=obs[obs['CODE']!='nf']
        obs=obs[obs['EventId']==ID].sort_values(by='ArrivalTime',ascending=False)
        LatLabel='LAT1'
        LonLabel='LON1'
    obs['links']=''
    obs['sizePoints']=1
    obs['hover']=''
    lons=[];lats=[]
    for j in range(len(obs)):
        Mag=obs['Magnitude'].values[j]
        Amplitude=obs['Amplitude'].values[j]
        PlaceMax=obs['Place'].values[j]
        if ID=='':
            EventId=obs.index[j]
            lons=obs['EventLon']
            lats=obs['EventLat']
            link= urlparse(url).scheme+'://'+urlparse(url).netloc+'/listEvGDACS?EventId='+format(EventId)
            zoom=1;w=1000;h=500
            centerLon=0.0
            centerLat=0.0
            HovData=["EventDate","EventLocation","Magnitude","Depth"]
            colorPoint=obs['Magnitude']
            obs['sizePoints'].values[j]=max(int(((obs['Magnitude'].values[j]-4.5)**4)/5),10)
        else:            
            HovData=["Place","Amplitude","Period","DB","GROUP","CODE"]
            colorPoint=obs['Amplitude']
            dat=numpydt64to_datetime(obs['EventDate'].values[j])
            datemin=dat -timedelta(days=1)#
            datemax=dat +timedelta(days=2)
            DB=obs['DB'].values[j]
            if pd.isna(DB):
                DB='';GROUP='';idDevice=''
            else:
                GROUP=obs['GROUP'].values[j]
                idDevice=obs['CODE'].values[j]
            title='M'+format(obs['Magnitude'].values[j])+' '+obs['EventLocation'].values[j]+'<br>'+format( obs['EventDate'].values[j])
            params='DB='+DB+'&GROUP='+format(GROUP)+'&idDevice='+format(idDevice)+'&datemin='+datemin.strftime('%Y-%m-%d %H:%M:%S')+'&datemax='+datemax.strftime('%Y-%m-%d %H:%M:%S')+'&ID='+format(ID)
            link= urlparse(url).scheme+'://'+urlparse(url).netloc+'/signals?'+params
            lons.append(obs['LON1'].values[j])
            lats.append(obs['LAT1'].values[j])
            obs['sizePoints'].values[j]=max(int(obs['Amplitude'].values[j]*40),10)  #max(int(((obs['Amplitude'].values[j]-4.5)**4)/10),2)
        for lab in HovData:
            obs['hover'].values[j]+=lab+': '+format(obs[lab].values[j])
            if lab=='Amplitude': obs['hover'].values[j]+=' m'
            if lab=='Period': obs['hover'].values[j]+=' min'
            obs['hover'].values[j]+='<br>'        
        obs['links'].values[j]=link
    if ID !='':
        w=500;h=400
        if min(lons)<0 and max(lons)>0:
            for j in range(len(lons)):
                if lons[j]>0:
                    lons[j]-=360
        centerLon=np.mean(lons)
        centerLat=np.mean(lats)
        zoom_lat = abs(abs(max(lats)) - abs(min(lats)))  
        zoom_long = abs(abs(max(lons)) - abs(min(lons)))
        zoom_factor = max([zoom_lat,zoom_long])
        if zoom_factor < 0.2:
            zoom_factor = 0.2
        zoom = -1.35 * math.log(float(zoom_factor)) + 7

    data=[go.Scattermapbox(lat=lats,lon=lons, mode='markers',
                          text=obs['hover'],
                          customdata=obs["links"],
                          marker=go.scattermapbox.Marker(size=obs['sizePoints'],
                                                          color=colorPoint,colorscale='rainbow',
                                                          showscale=True,)
                                              )]
    if ID !='':
          
          markerEQ=go.Scattermapbox(lat=[obs['EventLat'].values[0]],lon=[obs['EventLon'].values[0]], 
                                       mode='markers',marker=go.scattermapbox.Marker(size=10, color='black'), 
                                       text=title  )
          data.append(markerEQ)
          

    layout = go.Layout(
    height=h, width=w, 
    showlegend=False,
    autosize=True,
    hovermode='closest',
    clickmode='event',
    mapbox=dict(zoom=zoom,center={'lat':centerLat,'lon':centerLon})

    )
    fig = go.Figure(layout=layout, data=data)
    fig.update_layout(hovermode="x")

    #fig.update_layout(mapbox_style="open-street-map")
    #Mapbox API token are 'open-street-map', 'white-bg', 'carto-positron', 'carto-darkmatter', 
    #'stamen-terrain', 'stamen-toner', 'stamen-watercolor'. Allowed values which do require a Mapbox API token 
    #are 'basic', 'streets', 'outdoors', 'light', 'dark', 'satellite', 'satellite- streets'.

    fig.update_layout(mapbox_style="carto-positron")
    #fig.update_layout(mapbox_style="open-street-map")
    #fig.update_layout(mapbox_style="white--bg",mapbox_layers=[
    #    {
    #        "below": 'traces',
    #        "sourcetype": "raster",
    #        "sourceattribution": "United States Geological Survey",
    #        "source": [
    #            "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
    #        ]
    #    }
    #  ])
    #Adjust pitch and bearing to adjust the rotation
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, 
                      mapbox=dict(
                          pitch=0,
                          bearing=0
                      ))

    plotSet =dcc.Graph(id='graph-id', figure=fig)
    return plotSet


def plotEventsNoGTS(url,evDist,params,ID,eventsGDACS):   
    if 'MinMag' in params:
        MinMag=params['MinMag'][0]
    if 'MinHei' in params:
        MinHei=params['MinHei'][0]
    if 'gts' in params:
        gts=params['gts'][0]
    obs=evDist
    if ID !='':
        tabdetails,title,dat,mag,lon,lat,PlaceMax=getEventDetail(ID,eventsGDACS)  
        title=title+'<br>'+format( dat)
        print(title)
    lons=[];lats=[];hovers=[];links=[]
    HovData=["Place","DB","GROUP","CODE"]        
    datemin=dat -timedelta(days=1)#
    datemax=dat +timedelta(days=2)
    colorPoints=[]
    for j in range(len(obs)):
        DB=obs[j]['DB']
        GROUP=obs[j]['GROUP']
        idDevice=obs[j]['CODE']
        if ID =='':
            title=obs[j]['Place']
        params='DB='+format(DB)+'&GROUP='+format(GROUP)+'&idDevice='+format(idDevice)+'&datemin='+datemin.strftime('%Y-%m-%d %H:%M:%S')+'&datemax='+datemax.strftime('%Y-%m-%d %H:%M:%S')+'&ID='+format(ID)
        link= urlparse(url).scheme+'://'+urlparse(url).netloc+'/signals?'+params
        links.append(link)
        lons.append(obs[j]['LON1'])
        lats.append(obs[j]['LAT1'])

        if obs[j]['IDSource']=='DIST':
            colorPoints.append('blue')
        elif obs[j]['IDSource']=='DETECTED':
            colorPoints.append('red')
        else:
            colorPoints.append('gray')
       
        #print(zoom_factor, zoom)
        textHover=''
        for lab in HovData:
            textHover+=lab+': '+format(obs[j][lab])
            if lab=='Amplitude': textHover+=' m'
            if lab=='Period': textHover+=' min'
            textHover+='<br>'        
        hovers.append(textHover)
        obs[j]['link']=link
    zoom=4;w=500;h=400
    if min(lons)<0 and max(lons)>0:
        for j in range(len(lons)):
            if lons[j]>0:
                lons[j]-=360
    zoom_lat = abs(abs(max(lats)) - abs(min(lats)))  
    zoom_long = abs(abs(max(lons)) - abs(min(lons)))
    zoom_factor = max([zoom_lat,zoom_long])
    if zoom_factor < 0.2:
        zoom_factor = 0.2
    zoom = -1.35 * math.log(float(zoom_factor)) + 7
    #zoom=1
    if zoom>7:zoom=7
    if zoom<1:zoom=1

    centerLon=np.mean(lons)
    centerLat=np.mean(lats)
    data=[go.Scattermapbox(lat=lats,lon=lons, mode='markers',
                          text=hovers,
                          customdata=links,
                          marker=go.scattermapbox.Marker(size=10,color=colorPoints)
                           
                                              )]
    if ID !='':
          markerEQ=go.Scattermapbox(lat=[lat],lon=[lon], 
                                       mode='markers',marker=go.scattermapbox.Marker(size=10, color='black'), 
                                       text=title                   
                                       )
          data.append(markerEQ)

    layout = go.Layout(
    height=h, width=w, 
    showlegend=False,
    autosize=True,
    hovermode='closest',
    clickmode='event',
    mapbox=dict(zoom=zoom,center={'lat':centerLat,'lon':centerLon})

    )
    fig = go.Figure(layout=layout, data=data)
    fig.update_layout(hovermode="x")
    fig.update_layout(mapbox_style="carto-positron")   
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, 
                      mapbox=dict(
                          pitch=0,
                          bearing=0
                      ))

    plotSet =dcc.Graph(id='graph-id', figure=fig)
    return plotSet

@app.callback(
        Output('graph-id', 'children'), 
        Input('graph-id', 'clickData'))
def open_url(clickData):

    if clickData != 'null' and clickData != None:
         print (clickData)
         print (clickData['points'][0])
         if 'customdata' in clickData['points'][0]:
             url = clickData['points'][0]['customdata']
             print('url=',url)
             webbrowser.open_new_tab(url)
    else:
         raise PreventUpdate

if __name__ == "__main__":
    app.run_server(debug=True)