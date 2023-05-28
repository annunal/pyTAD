import datetime
import os
 
def getdelta(t1):
	d1=datetime.date.fromtimestamp((t1-25569.)*24.*3600.)
	#print t1,d1
	
	ore=(t1-int(t1))*24
	#print 'ore=',ore
	hh=int(ore)
	mm=int((ore-hh)*60)
	ss=int((ore-hh)*3600-mm*60)
	dat=datetime.datetime(d1.year,d1.month,d1.day,hh,mm,ss)
	#print 'dat=',dat
	now=datetime.datetime.utcnow()
	#print now
	if dat<now:
		#print (now-dat)
		return now-dat
	else:
		#print (-now+dat)
		return dat-now

def timeToMin(t):
	mins=t.days*24.*60.0
	mins += t.seconds/60.0
	return mins
	

fname='/tmp/TAD/buffer.txt'
if os.path.exists(fname):
	fi=open(fname,'r')
	l=fi.readlines()
	fi.close()

	l1=l[1]
	t1=float(l1.split(',')[0])
	delta1=getdelta(t1)

	l2=l[len(l)-1]
	t2=float(l2.split(',')[0])
	delta2=getdelta(t2)

	tmin1=timeToMin(delta1)
	tmin2=timeToMin(delta2)

	#print 'delta1,delta2', delta1,delta2
	#print tmin2,tmin1
else:
	tmin1=1000
	tmin2=1000 

today=datetime.datetime.utcnow()
if tmin2>100  or tmin1>100:
	cmd='sudo kill $(pidof tad)';os.system(cmd)
	cmd='sudo mv /tmp/TAD/buffer.txt /tmp/TAD/bufferOld.txt';os.system(cmd)
	cmd='sudo /tmp/TAD/checkRunningTAD.sh';os.system(cmd)
	print today, 'tad restarted deltat1,2=',delta1,delta2
	cmd='sudo touch /usb/TADrestarted.txt';os.system(cmd)
else:
	print today, 'regular delta times deltat1,2=',delta1,delta2
