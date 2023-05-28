#  TO DO LIST
# DONE      Minimum Magnitude to show in the list
# DONE      Minimum height to show in the list
# DONE      Only GTS events
# DONE but include also information on the event and name the file accordingly     Download (original data  or our data)
#
from dashImport import app,html,dcc
from dash.dependencies import Input, Output,State
import plotly.graph_objects as go
import os,platform,json
from datetime import datetime,timedelta,date
from utilities import getList,getListDevicesbyDBs,powspec,interpData,extractLabel,tds

# pip install python-dateutil
from dateutil.parser import parse
from calcAlgorithm import calcAlgorithm as ca
from navbar import Navbar
from listEvents import  showEvents,eventsGDACS
from utilities import haversine,getEventDetail
from urllib.parse import urlparse, parse_qs, urlencode

from utilities import getListDevicesbyDBs,getValues,getFigure
from APIs import devicesDB

VERSION='2.1'
print('importing list of devices')
dataList=getListDevicesbyDBs()
app.layout = html.Div([ 
    dcc.Location(id = 'url', refresh = False),
    html.Div(id = 'page-content')
])

data=[]

appserver=app.server

def showSignals(url):
    params=parse_qs(urlparse(url).query)
    if 'n30' in params: n30=int(params['n30'][0])
    else: n30=30

    if 'n300' in params: n300=int(params['n300'][0])
    else: n300=300

    if 'DB' in params: DB=params['DB'][0]
    else: DB='JRC_TAD'

    if 'GROUP' in params: GROUP=params['GROUP'][0]
    else: GROUP=''

    if 'idDevice' in params: idDevice=params['idDevice'][0]
    else: idDevice=''
    
    if 'addRMS' in params: addRMS=float(params['addRMS'][0]) 
    else: addRMS=0.
    
    if 'threshold' in params: threshold=float(params['threshold'][0])
    else: threshold=0.1
    
    if 'ratioRMS' in params: ratioRMS=float(params['ratioRMS'][0])
    else: ratioRMS=3

    if 'nmax' in params: nmax=int(params['nmax'][0])
    else: nmax=10000

    if 'STImin' in params: STImin=int(params['STImin'][0])
    else: STImin='15'

    if 'LTImin' in params: LTImin=int(params['LTImin'][0])
    else: LTImin='180'

    if 'datemin' in params: datemin=parse(params['datemin'][0])
    else: datemin=datetime.utcnow()-timedelta(days=3)

    if 'datemax' in params: datemax=parse(params['datemax'][0])
    else: datemax=datetime.utcnow()

    if 'ID' in params:
        EventId=int(params['ID'][0])
        print('EventId, SeaLevelMachine',EventId)
        tabdetails,title,dat,mag,lon,lat,placeMax=getEventDetail(EventId,eventsGDACS)
        tabdetails=html.Center(html.B('Event: '+title+', '+format(dat)))
    else:
        EventId=''
        tabdetails=''

    print('PID=....',os.getpid())

    #print (DB,GROUP,idDevice,n300,n30,ratioRMS,addRMS,threshold,STImin,LTImin,datemin,datemax,nmax)
    params='&'.join(['DB='+DB,'GROUP='+format(GROUP),'idDevice='+format(idDevice),
                    'n300='+format(n300),'n30='+format(n30),'ratioRMS='+format(ratioRMS),
                    'addRMS='+format(addRMS),'threshold='+format(threshold),
                    'STImin='+format(STImin),'LTImin='+format(LTImin),
                    'nmax='+format(nmax),'datemin='+datemin.strftime('%Y-%m-%d %H:%M:%S'),
                    'datemax='+datemax.strftime('%Y-%m-%d %H:%M:%S')+'&ID='+format(EventId)])
    linkURL=urlparse(url).scheme+'://'+urlparse(url).netloc+'?'+params
    listNmax=[]
    n=1000;listNmax.append({'label':n,'value':n})
    n=5000;listNmax.append({'label':n,'value':n})
    n=10000;listNmax.append({'label':n,'value':n})
    n=15000;listNmax.append({'label':n,'value':n})
    n=20000;listNmax.append({'label':n,'value':n})
    n=30000;listNmax.append({'label':n,'value':n})
    n=40000;listNmax.append({'label':n,'value':n})
    n=50000;listNmax.append({'label':n,'value':n})
    n=75000;listNmax.append({'label':n,'value':n})
    n=100000;listNmax.append({'label':n,'value':n})
    n=-1;listNmax.append({'label':'All','value':n})

    ldb=getList('DB')
    lg=[]
    lg1=[]
    
    downloadLinkD=html.Div([dcc.Textarea(id='textCsv',style={'display':'none'}),
                            html.Button("Download CSV file", id="btn-download-txt"),
                            dcc.Download(id='download-text')])

    link=dcc.Textarea(id="textarea_id",value="Copy and paste here",style={"height": 100, 'display':'none'},)
    EventIdtext=html.Div(EventId,id='EventIdtext',style={'display':'none'})
    copyLink=dcc.Clipboard(target_id="textarea_id",title="copy link",style={"display": "inline-block","fontSize": 20,"verticalAlign": "top",})
    selectDevice=html.Center(html.Table([
            html.Tr([html.Td('DB',style=tds('','italic',14)),html.Td('Group',style=tds('','italic',14)),
                     html.Td('Device',style=tds('','italic',14)),
                     html.Td('Nmax',style=tds('','italic',14)),
                     html.Td('DateMin',style=tds('','italic',14)),html.Td('DateMax',style=tds('','italic',14)),
                     html.Td(html.A('Copy link',href=linkURL,id='linkURL', style={'display':'none'}))]),

            html.Tr([
                html.Td(dcc.Dropdown(id='DB',options=ldb,value=DB,style=tds(120))),
                html.Td(dcc.Dropdown(id='GROUPS',options=lg,value=GROUP,style=tds(120))),
                html.Td(dcc.Dropdown(id='DEVICES',options=lg1,value=idDevice,style=tds(400))),
                html.Td(dcc.Dropdown(id='numMaxdata',options=listNmax,value=nmax, style=tds(120))),                
                html.Td(dcc.DatePickerSingle(id='dateMin', min_date_allowed=date(2000, 1, 1),max_date_allowed=datetime.utcnow(),date=datemin),tds(200)),
                html.Td(dcc.DatePickerSingle(id='dateMax', min_date_allowed=date(2000, 1, 1),max_date_allowed=datetime.utcnow(),date=datemax),tds(200)),
                html.Td([html.Button('Get Data',id='getData',n_clicks=-1),link,' ', copyLink])
                ], style=tds(300))            
            ]))
    rowLoading=dcc.Loading(id="loading",children=[html.Div([html.Center(id="loading-output",style={'backgroundColor':'Gainsboro','font-style':'italic', 'font-size':'14px'})])],type="default",)
    descPoints='Click 5 times on the curve: first point is Arrival time, other 4 points for Zero, a minimum (or max), a maximum (or min) and another zero'
    rowpoints=html.Div(html.Center(descPoints,id="rowpoints",style={'backgroundColor':'yellow','font-style':'italic', 'font-size':'14px'}))
    #downloadLinkD=html.A('Download data',id='download-link',download="level_data.csv",href="",target="_blank")
    paramsModel=html.Center(html.Table([
        html.Tr([html.Td('n300',style=tds('','italic',14)),
                 html.Td('n30',style=tds('','italic',14)),
                 html.Td('threshold',style=tds('','italic',14)),
                 html.Td('ratioRMS',style=tds('','italic',14)),
                 html.Td('AddRMS',style=tds('','italic',14)),
                 #html.Td(html.Button('Calculate',id='calcData',n_clicks=-1))
                 ]),
        html.Tr([html.Td(dcc.Input(id='n300',value=n300), style=tds(200)),
                 html.Td(dcc.Input(id='n30',value=n30), style=tds(200)),
                 html.Td(dcc.Input(id='threshold',value=threshold), style=tds(200)),
                 html.Td(dcc.Input(id='ratioRMS',value=ratioRMS), style=tds(200)),
                 html.Td(dcc.Input(id='AddRMS',value=addRMS), style=tds(200))
                 ]),
        html.Tr([html.Td('Long Term (min)',style=tds('','italic',14)),
                 html.Td('Short Term (min)',style=tds('','italic',14)),
                 html.Td(''),
                 html.Td(''),
                 html.Td(''),
                 #html.Td(html.Button('Calculate',id='calcData',n_clicks=-1))
                 ]),
        html.Tr([html.Td(dcc.Input(id='LTI',value=LTImin), style=tds(200)),
                 html.Td(dcc.Input(id='STI',value=STImin), style=tds(200)),
                 html.Td(html.Center('If you specify these, the n300, n30 will be superseded ',style=tds('','italic',14)),style={'colspan':2}),
                 html.Td(downloadLinkD)
                 ]),

        #html.Tr(html.Td(html.Div(id='status'),style={'colspan':5}))
            ]) )
    graf=html.Div('',id='grafici')
    #tabobjects=html.Table(html.Tr([html.Td(tabdetails, style={'width':'400 px'}),
    #                               html.Td(selectDevice,html.Br(),paramsModel)]
    #                              )
    #                      )
    layout=html.Div([Navbar(),html.Br(),tabdetails,html.Br(),selectDevice,html.Br(),paramsModel,html.Br(),
                     rowLoading,rowpoints,EventIdtext,
                     html.Br(),graf])    
    
    return  layout



@app.callback(Output('page-content', 'children'),
            Input('url', 'pathname'),Input('url', 'href'))
def display_page(pathname,url):
    authState=False
    #print('pathname=',pathname,'listEvents' in pathname)
    if 'listEvents' in pathname:
        #print(1)
        return showEvents(url)
    elif 'signals' in pathname:
        return showSignals(url)
    elif 'api/devices' in pathname:
        return devicesDB(url)
    else:
        #print(2)
        return showEvents(url)
        
@app.callback(Output('GROUPS','options'),Output('GROUPS','value'),Input('DB','value'))

def selgroup(db):
    if db=='':
        return []
    data=dataList[db]
    options=getList('GROUPS',data,db)
    if len(options)==1:
        outGroup=options[0]['value'] 
    else:
        outGroup=''
    return options,outGroup

@app.callback(Output('DEVICES','options'),Input('GROUPS','value'),State('DB','value'))

def selgroup(groupID,db):
    if groupID=='' or db=='':
        return []
    data=dataList[db]
    options=getList('DEVICES',data,db,groupID)
    return options

from dash.exceptions import PreventUpdate
@app.callback(
    Output('rowpoints', 'children'),Output('plot1','figure'),
    Input('plot1', 'clickData'),State('rowpoints', 'children'), State('plot1','figure'),
    )
def display_click_data(clickData,rp,fig):
    if clickData==None:
        raise PreventUpdate
    x=clickData['points'][0]['x']
    x=parse(x)
    y=clickData['points'][0]['y']
    print(rp)
    if rp=='' or rp==None or 'props' in rp or 'Click 5 times' in rp:
        np=1
        j=[]
        foundPoints=False
        for n in range(len(fig['data'])):
            if fig['data'][n]['name']=='Points':
                foundPoints=True
        if not foundPoints:
            newtrace={'name': 'Points','type':'Scatter','x': [x],'y':[y], 'mode': 'markers', 'marker':go.Marker(color='red', size=10)}
            fig['data'].append(newtrace)
        else:
          for n in range(len(fig['data'])):
            if fig['data'][n]['name']=='Points':
                fig['data'][n]['x']=[x]
                fig['data'][n]['y']=[y]
                break

    else:
        for n in range(len(fig['data'])):
            if fig['data'][n]['name']=='Points':
                fig['data'][n]['x'].append(x)
                fig['data'][n]['y'].append(y)
                break
        
        j=json.loads(rp)
    np=len(j)
    rpadd='{"poi":'+format(np)+', "x":"'+format(x)+'", "y":'+format(y)+'}'
    j.append(json.loads(rpadd))
    if np<4:
        testo=json.dumps(j, indent=2)
    else:
        t=[];y=[]
        for n in range(5):
            t.append(datetime.strptime(j[n]['x'],'%Y-%m-%d %H:%M:%S'))
            y.append(j[n]['y'])

        period=abs(round((t[4]-t[1]).seconds/60,1))

        d1=y[1]+(y[4]-y[0])/(t[4]-t[1]).seconds*(t[2]-t[1]).seconds
        d2=y[1]+(y[4]-y[0])/(t[4]-t[1]).seconds*(t[3]-t[1]).seconds
        amp1=abs(y[2]-d1)
        amp2=abs(y[3]-d2)
        MaxMinusMin=round(abs((y[2]-d1)-(y[3]-d2)),1)
        amplitude=round(max(amp1,amp2),1)
        amplitude2=round((amp1+amp2)/2,1)
        testo=html.Div(['Arrival Time: ',html.B(t[0].strftime('%Y-%m-%d %H:%M:%S')),
                        ', Amplitude (half trough to crest): ',html.B(format(amplitude2)+' m'), 
                        ' Max Amplitude (max between trough and crest minus tide): ',html.B(format(amplitude)+' m'), ', Through to Crest:',format(MaxMinusMin),
                        ' m, Period: ',html.B(format(period)+' min')])
    return testo,fig

@app.callback(Output('loading-output','children'),Output('grafici','children'), Output('textarea_id','value'),
              Output('textCsv', 'value'),
              Input('getData', 'n_clicks'),State('DB','value'),State('GROUPS','value'),
              State('DEVICES','value'), State('n300','value'), 
              State('n30','value'), State('threshold','value'), State('ratioRMS','value'),
              State('AddRMS','value'), State('numMaxdata','value'), State('LTI','value'), State('STI','value'),
              State('dateMin','date'),State('dateMax','date'), State('DB','options'), State('DEVICES','options'), 
              State('linkURL','href'),
              )

def updatePlots(nclick,DB,GROUP,idDevice,n300,n30,threshold,ratioRMS,addRMS,nmaxData,LTImin, STImin, dmin,dmax,optdb,opts,linkURL):
    if idDevice=='' or idDevice==None:
        return 'select a device with data - (Sea Level Machine, version '+VERSION+')','',linkURL
    #print('78****] opts=',opts)
    #print('**** linkURL',linkURL)
    
    params=parse_qs(urlparse(linkURL).query)
    if 'ID'in params:
        EventId=int(params['ID'][0])
    else:
        EventId=''
    #print('**** eventId',EventId)
    n300=int(n300)
    n30=int(n30)
    threshold=float(threshold)
    ratioRMS=float(ratioRMS)
    addRMS=float(addRMS)
    nmaxData=int(nmaxData)

    dmin=parse(dmin)  #datetime.strptime(dmin,'%Y-%m-%dT%H:%M:%S.%f')
    dmax=parse(dmax)  #datetime.strptime(dmax,'%Y-%m-%dT%H:%M:%S.%f')
    #print(dmin, dmax, type(dmin))
    tmax=datetime.utcnow()
    tmin=tmax-timedelta(days=0.2)
    DBNAME=extractLabel(optdb,DB)
    if DBNAME=='':DBNAME='JRC_TAD'
    #print('DB=',DBNAME,optdb, DB)
    
    values, avgDelta=getValues(DBNAME,idDevice, tmin, tmax, 500000)  
    
    tmax=dmax #+timedelta(days=1) #datetime.utcnow()
    #tmin=tmax-timedelta(days=3)
    tmin=dmin
    values, avgDelta1=getValues(DBNAME,idDevice, tmin, tmax, nmaxData)  
    if values==[]:
        return 'No data found. Select a device with data - (Sea Level Machine, version '+VERSION+')','',linkURL,''
    #xvalue, signal=interpData(values['x'],values['y'])
    #values['xvalue']=xvalue
    #values['signal']=signal
    if avgDelta==0:
        avgDelta=avgDelta1
    freq,period_min,powsp,perS,powS=powspec(values['x'],values['y'])
    values['period_min']=period_min
    values['powspec']=powsp
    values['perS']=perS
    values['powS']=powS

    #print(n300, avgDelta, avgDelta1)
    params='&'.join(['DB='+DB,'GROUP='+format(GROUP),'idDevice='+format(idDevice),
                    'n300='+format(n300),'n30='+format(n30),'ratioRMS='+format(ratioRMS),
                    'addRMS='+format(addRMS),'threshold='+format(threshold),
                    'STImin='+format(STImin),'LTImin='+format(LTImin),
                    'nmax='+format(nmaxData),'datemin='+tmin.strftime('%Y-%m-%d %H:%M:%S'),
                    'datemax='+tmax.strftime('%Y-%m-%d %H:%M:%S')])
    linkURL=linkURL.split('?')[0]+'?'+params
    if STImin=='' and LTImin=='':
        n300=int(n300*avgDelta/avgDelta1)
        n30=int(n30*avgDelta/avgDelta1)
        try:
            LTImin=int(avgDelta1*n300/60)
            STImin=int(avgDelta1*n30/60)
            status='delta/orig Delta Status: '+format(round(avgDelta/avgDelta1,2))+' n300 and n30 adjusted to respect the current time interval, n300='+format(n300)+' STImin='+format(STImin)+' LTImin='+format(LTImin)
        except Exception as e:
            status=e
        if n30<2:n30=2
    else:
        if avgDelta1>0:
            n300=int(float(LTImin)*60/avgDelta1)
            n30= int(float(STImin)*60/avgDelta1)
            try:
                status=' n300 and n30 adjusted to respect the specified STI and LTI, n300='+format(n300)+' n30='+format(n30)
            except Exception as e:
                status=e
        else:
            n300=300
            n30=30
            status='n300 and n30 imposed to 300 and 30 because avgDelta1=0'
    config={}
    config['Interval']=-1
    config['n30']=n30
    config['n300']=n300
    config['ratioRMS']=float(ratioRMS)
    config['threshold']=float(threshold)
    config['AddRMS']=float(addRMS)
    config['vmin']=-1e9
    config['vmax']=1e9
    config['SaveURL']=''
    import os 
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
    #print(len(values['x']))
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
        if int(j/1000)*1000==j:
            print(j,len(values['x']), alertValue,alertSignal)
            AS +=format(j)+' '+format(round(alertSignal,3))+'|'
    #print('(1)',opts,idDevice, GROUP)
    #status +=AS
    if opts==[]:
        data=dataList[DB]
        opts=getList('DEVICES',data,GROUP)
    #print('(2)',opts,idDevice)
    testoS=''
    if opts==[]:
        data=dataList[DB]
        opts=getList('DEVICES',data,DB,GROUP)
    label=extractLabel(opts,idDevice)
    if EventId !='':
        tabdetails,title,dat,mag,lon,lat,PlaceMax=getEventDetail(EventId,eventsGDACS)
        testoS='*  Joint Research Centre,  Sea Level Machine (c) 2022 by A. Annunziato \n'
        testoS+='* '+title+'\n'
        testoS +='* Date:                ' +dat.strftime ('%Y-%m-%d %H:%M:%S')+'\n'
        testoS +='* Magnitude:           M' +format(mag)+'\n'
        testoS +='* Lat/Lon:             ' +format(lat)+'/'+format(lon)+'\n'
        testoS +='* Measurement Location:' +label+'\n'
        print(DB,GROUP,idDevice)
        testoS +='* Measurement ID      :' +DB+'/'+format(GROUP)+'/'+format(idDevice)+'\n'
        if label=='':
            label=title
        title1='Measured data '+label+ ' for event: '+title+' '+dat.strftime ('%Y-%m-%d %H:%M:%S')
        fig1=getFigure(values,[('x','y','Level')],title1,False,False,[],[],dat)
        if label=='':
            label=title
    else:
        fig1=getFigure(values,[('x','y','Level')],'Original measured data '+label,False,False,[],[],dat)

    
    

    fig2=getFigure(values,[('x','y','Level'),('x','fore30','Short term forecast'),('x','fore300','Long Term Forecast')], 'Computed Long and Short Term forecasts',False,False,[],[],dat)
    fig3=getFigure(values,[('x','rms',''),('x','alertSignal',''),('x','rmsMod','')], 'Alerting parameters',False,False,[],[],dat)
    fig4=getFigure(values,[('x','alertValue', 'Alert Value 0-10')], 'Resulting Alert Value',False,False,[],[0,10],dat)
    fig5=getFigure(values,[('period_min','powspec', 'Power Spectrum'),('perS','powS','Mov average')], 'Signal power spectrum',True)
    
    testo=[['DateTime','Level (m)', 'STF', 'LTF', 'alert Signal','rms', 'Alert Value', 'Period (min)', 'PowSpectrum()']]
    for j in range(len(values['x'])):
        row=[values['x'][j],values['y'][j],values['fore30'][j],values['fore300'][j],values['rms'][j],values['alertSignal'][j],values['alertValue'][j]]
        testo.append(row)
    nfields=len(row)+2
    for j in range(1,len(values['powspec'])):
        if j<len(testo):
            row=testo[j]
            row.append(values['period_min'][j])
            row.append(values['powspec'][j])
            testo[j]=row
        else:
            row=['','','','','','','',values['period_min'][j],values['powspec'][j]]
            testo.append(row)
    
    for r in testo:
        if len(r)<nfields:
            r.append('')
            r.append('')
        testoS +=", ".join(map(str,r))+'\n'
    #print(testoS)
    grafico1=dcc.Graph(id='plot1', figure=fig1)
    grafico2=dcc.Graph(id='plot2', figure=fig2)
    grafico3=dcc.Graph(id='plot3', figure=fig3)
    grafico4=dcc.Graph(id='plot4', figure=fig4)
    grafico5=dcc.Graph(id='plot5', figure=fig5)
    #grafico6=dcc.Graph(id='plot6', figure=fig6)
    print('PID=',os.getpid())
    return status,html.Center([grafico1,grafico2,grafico3,grafico4, grafico5]),linkURL,testoS

@app.callback(
    Output("download-text", "data"),
    Input("btn-download-txt", "n_clicks"),State('textCsv','value'),
    prevent_initial_call=True,
)
def func(n_clicks,csv):
    return dict(content=csv, filename="data_values.csv")

if __name__ == '__main__':
    print('PID=',os.getpid())

    appserver=app.server
    app.run_server(debug=True)