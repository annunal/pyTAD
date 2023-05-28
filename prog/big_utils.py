import ssl
import urllib
import requests
import json

import requests

vbTab='\t'

def getListBIG(URL):
    context = ssl._create_unverified_context()
    resp=urllib.request.urlopen(URL,context=context)
    #URL='https://srgi.big.go.id/api/pasut/stations'
    #resp=requests.get(URL)
    respText=resp.read().decode("utf-8")
    stations = json.loads(respText)

    testo=''
    for sta in stations['features']:
        lon,lat=sta['geometry']['coordinates']
        IDstation=sta['properties']['KODE_STS']
        location=sta['properties']['NAMA_STS']
        cou='Indonesia'
        testo += format(lat) + vbTab + format(lon) + vbTab +cou + vbTab + location +vbTab
        url0='https://srgi.big.go.id/tides_data/pasut_'+IDstation+'?date=$DAY&datestart=$DAY&status=auto'
        testo +=url0  + vbTab
        testo +='BIG-'+IDstation
        testo += vbTab + IDstation +'\n'

    return testo



def combineDict(a,b):
    for key in b.keys():
        if not key in a:
            a[key]=b[key]
    return a

