import json
import requests
from urllib.request import urlopen
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from datetime import datetime,timedelta

def getData(URLtype):
    if URLtype=='GLOSS':
        url = "http://www.vliz.be/sls/service.php?query=stationlist&format=json"
    elif URLtype=='SeaLevelDB':
        url="https://webcritech.jrc.ec.europa.eu/worldsealevelinterface/?list=true&format=txt"
    elif URLtype=='JRC_TAD':
        url='https://webcritech.jrc.ec.europa.eu/TAD_Server/api/Groups/GetGeoJSON?group=&maxLatency=2880&test=false'
    resp=urlopen(url)
    dataJson = resp.read().decode("utf-8")
    data=json.loads(dataJson)
    return data

def getValues(type,ID,tmin,tmax,nmaxData=500000):
    if type=='JRC_TAD':
        tminS=tmin.strftime('%Y-%m-%dT%H:%M:%SZ')
        tmaxS=tmax.strftime('%Y-%m-%dT%H:%M:%SZ')
        url='https://webcritech.jrc.ec.europa.eu/TAD_server/api/Data/Get/'+ID +'?tMin='+tminS+'&tMax='+tmaxS+'&nRec='+format(nmaxData)+'&mode=json'
        print(url)
        resp=urlopen(url)
        dataJson = resp.read().decode("utf-8")
        data=json.loads(dataJson)
        print(len(data))
        list={'x':[], 'y':[]}
        avgDelta=0
        for j in range(len(data)):
            v=data[j]
            ts=v['Timestamp']
            ts1=datetime.strptime(ts,'%Y-%m-%dT%H:%M:%SZ')
            va=v['Values']['inp1']            
            list['x'].append(ts1)
            list['y'].append(va)
            if j>0:
                avgDelta +=(ts1-ts0).seconds
            ts0=ts1
        avgDelta /=(len(data)-1)
        print('avgDelta',avgDelta)
        return list,avgDelta

def getFigure(values, definition):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    for q in definition:
        xf,yf=q
        fig.add_trace(go.Scatter(x=values[xf], y=values[yf], name="Level"))
    
    return fig

def getList(what,data, groupID=None):
    list=[]
    if what=='GROUPS':
        
        for group in data:
            Name=group['properties']['Name']
            Color=group['properties']['Color']
            groupID=group['properties']['Id']
            list.append({'label':Name,'value':groupID})
        
        return list
    elif what=='DEVICES':
        if groupID==None:
            return []
        else:
            for group in data:
                if groupID==group['properties']['Id']:
                    for device in group['features']:
                        ID=device['id']
                        NAME=device['properties']['Name']
                        try:
                            Location=device['properties']['Location']+' ('+device['properties']['Country']+')'
                        except Exception as e:
                            Location=''
                            print(e)
                        list.append({'label':NAME+' '+Location,'value':ID})
#{'type': 'Feature', 'id': '208', 'geometry': {'type': 'Point', 'coordinates': [99.585453, -2.037654]}, 'properties': {'Name': 'IDSL-303', 'Sensor': 'RAD', 'Location': 'Mentawai Tua Pejat', 'Country': 'Indonesia', 'Region': 'West Sumatra', 'Provider': 'JRC-MMAF', 'LastData': {'Date': '03 Jul 2022 02:06:38', 'Value': 1.712382}, 'Latency': {'Literal': '1 Days', 'Seconds': 100214, 'Color': '#FF0000'}, 'GroupColor': '#D20950'}},                    
            return list
