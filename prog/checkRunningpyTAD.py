#!/usr/bin/python3
import os,time,sys
from CONF import folderOut
import readConfig as rc
import psutil
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

def checkHighLatency(config,pid):
    idDevice=config['IDdevice'].replace('$HOSTNAME',os.uname()[1])
    folderOut='/tmp/pyTAD'
    if 'folderOut' in config:
        folderOut=config['folderOut']
    URL='https://webcritech.jrc.ec.europa.eu/TAD_server/api/Data/Get/'+idDevice+'?mode=txt'
    print(URL)
    try:
      response=urlopen(URL)
    except Exception as e:
      print(e)
      return False
    testo=response.read().decode("utf-8")
    #  lat=37.031078 lon=27.430335 hei=  Location: Test location  Last Date: 22 Jan 2022 17:33:06  Latency: 13:11:04.6314752
    rows=testo.split('\n')
    seconds=0
    for row in rows:
        if 'Last Date:' in row:
            latency=row.split('Latency: ')[1].replace('\r','')
            p=latency.split(':')
            if '.' in p[0]:
                days=p[0].split('.')[0]
                p[0]=p[0].split('.')[1]
                seconds=1e6
            else:
                days=0
                seconds=int(p[0])*3600+int(p[1])*60+float(p[2])
            #print(row)
            break
    if seconds>10*60:
        if os.path.exists(folderOut+os.sep+'buffer.txt'):
            os.remove(folderOut+os.sep+'buffer.txt')
        os.kill(pid, 9)
        print('    latency too high, latency=',latency,'s')
        return True
    else:
         print('    latency OK, quitting latency=',latency,'s')
         return False

arguments = sys.argv[1:]
folderConfig='./'
for j in range(len(arguments)-1):
    if arguments[j]=='-c':
        folderConfig=arguments[j+1]

procs=[]
for i in psutil.pids():
    try:
        proc=' '.join(psutil.Process(i).cmdline())
        
        if 'tad.py -c '+folderConfig in proc:
           print(proc)
           if not '-f True' in proc:
             procs.append(i)
           else:
             print('process running with -f')
             procs.append(-1)
    except:
        i=i  #print(i)

nitems=len(procs)

from pathlib import Path
parent = Path(__file__).resolve().parent
#print('execution folder xx',parent)
#  cosi'parto sempre da
os.chdir(format(parent))
#print('nitems=',nitems)
if nitems==0:
    cmd='python3 '+format(parent)+os.sep+'tad.py -c '+folderConfig+'>> /tmp/outpyTAD.txt &'
    print(cmd)
    os.system(cmd)
    print('**   Process submitted')
elif nitems==1:
    print('-- 1 process running, process=',procs[0],' checking latency')
    
    config=rc.readConfig(folderConfig)
    if checkHighLatency(config,procs[0]):
        cmd='python3 '+format(parent)+os.sep+'tad.py -c '+folderConfig+'>> /tmp/outpyTad.txt &'
        print('    '+cmd)
        os.system(cmd)
        print('**   Latency too high, process submitted')

else:
    print('** multiple processes running, deleting all but one')
    for pr in procs[1:]:
        print('     killing ',pr)
        os.kill(pr,9)

