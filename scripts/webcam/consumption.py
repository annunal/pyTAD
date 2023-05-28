#! /usr/bin/python  
import os
import socket
import sys
import os.path
from os import path

def printdata(hostname,device,channel,rx,tx,rxGB,txGB,uptimeDays,consGB_per_month,saveData):
	print hostname+":"+channel,rxGB,txGB,rxGB+txGB,uptimeDays,consGB_per_month
	if saveData==1:
		url="http://139.191.244.76/SimTelemetry/SetTelementry.aspx?idDevice=$IDDEVICE\&device=$DEVICE\&channel=$CHANNEL\&tx=$TX\&rx=$RX\&DayUp=$DAYUP\&ConsMonth=$CONS"
		#print url 
		url=url.replace("$IDDEVICE",hostname)
		url=url.replace("$DEVICE",device)
		url=url.replace("$CHANNEL",channel)
		url=url.replace("$TX",format(int(tx)))
		url=url.replace("$RX",format(int(rx)))
		url=url.replace("$DAYUP",format(uptimeDays))
		url=url.replace("$CONS",format(consGB_per_month))
		print url
		cmd='wget -O /tmp/outconsumption.txt '+url
		#print '========================================'
		#print cmd
		#print '========================================'
		os.system(cmd)


def analizza(whatToAnalyse,saveData,suffix=''):
	fname='/tmp/ifconfig.txt'
	hostname=socket.gethostname()
	if path.exists(fname):
		os.remove(fname)
	if whatToAnalyse=='RPI':
		cmd='uptime > '+fname
		print cmd
		os.system(cmd)
		cmd='/sbin/ifconfig >> '+fname
		print cmd
		os.system(cmd)
		
	if whatToAnalyse=='TELTONIKA':
		cmd='/usr/bin/sshpass -p "Ecml2011" /usr/bin/ssh root@192.168.1.1 -o StrictHostKeyChecking=no "uptime"> '+fname
		print cmd
		os.system(cmd)
		cmd='/usr/bin/sshpass -p "Ecml2011" /usr/bin/ssh root@192.168.1.1 -o StrictHostKeyChecking=no "ifconfig" >> '+fname
		print cmd
		os.system(cmd)
		#hostname=socket.gethostname()+'_TELTONIKA'


	print 'hostname:channel RX_(GB) TX_(GB) RX+TX_(GB) Days_Uptime GB_per_month'

	if os.path.exists(fname):
		fi=open(fname,'r')
		l=fi.readlines()
		fi.close()
		for riga in l:
			if ' up ' in riga:
				#08:48:12 up 3 days,  4:19,  1 user,  load average: 0.00, 0.00, 0.00
				#05:26:03 up 17:24,  1 user,  load average: 0.32, 0.40, 0.42
				riga=riga.strip()
				p=riga.split(' ')
				if 'day' in riga:
					da=float(p[2])
					hou=float(riga.split(',')[1].strip().split(':')[0])
					mi= float(riga.split(',')[1].strip().split(':')[1])
					
				else:
					if 'min,' in riga:
						da=0.
						hou=0.
						mi=float(p[2]) 
					else:
						da=0.
						#print riga 
						try:
							hou=float(p[2].split(':')[0])
							mi=float(p[2].split(':')[1].split(',')[0])
						except:
							p=riga.split(',')[0].strip().split(' ')
							ic=2
							if p[ic]=='':
								ic=3
								hou=float(p[ic].split(':')[0])
								mi= float(p[ic].split(':')[1])					
								
				uptimeDays=round(da+(hou+mi/60.)/24.,2)
			else:
				if riga[:5].strip()<>'':
					channel=riga.split(' ')[0].replace(':','')
				else:
					if ('B)' in riga)  and (not 'packets' in riga):
						rx=float(riga.split('RX bytes:')[1].split(' ')[0])
						tx=float(riga.split('TX bytes:')[1].split(' ')[0])
						rxGB=round(rx/1024./1024./1024.,2)
						txGB=round(tx/1024./1024./1024.,2)
						consGB_per_month=round((rx+tx)/(1024.*1024.*1024.)/uptimeDays*30.,2)
						printdata(hostname,whatToAnalyse+suffix,channel,rx,tx,rxGB,txGB,uptimeDays,consGB_per_month,saveData)
					if ('B)' in riga)  and ('packets' in riga):
						if 'RX packets' in riga:
							rx=float(riga.split('bytes ')[1].split(' ')[0])
						if 'TX packets' in riga:
							tx=float(riga.split('bytes ')[1].split(' ')[0])
							rxGB=round(rx/1024./1024./1024.,2)
							txGB=round(tx/1024./1024./1024.,2)
							consGB_per_month=round((rx+tx)/(1024.*1024.*1024.)/uptimeDays*30.,2)
							printdata(hostname,whatToAnalyse+suffix,channel,rx,tx,rxGB,txGB,uptimeDays,consGB_per_month,saveData)
							
		print '----------------------------------------------'
		for riga in l:
			print riga.replace('\n','')

		print '----------------------------------------------'

args=sys.argv
whatToAnalyse=''
suffix=''
saveData=1 
if len(args)>0:
	for arg in args:
		if arg=='TELTONIKA':
			whatToAnalyse=arg 
		if arg=='RPI':
			whatToAnalyse=arg
		if 'suffix' in arg:
			suffix='_'+arg.replace('suffix=','')
	
		if arg=='NoSaveData':
			saveData=0

if whatToAnalyse=='':
	analizza('RPI',saveData,suffix)
	analizza('TELTONIKA',saveData)
else:
	analizza(whatToAnalyse,saveData,suffix)
