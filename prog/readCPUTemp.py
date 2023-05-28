import time,os

def init(config,adcData,readingInterval):
	print ("---------------------------------------------------")
	print ("Starting reading CPUTemp")
	print ("---------------------------------------------------")
	CURRENT_CPU_T_FILE = "CurrentTempCPU.txt"
	CPUread='/sys/class/thermal/thermal_zone0/temp'
	
	while True:
		if os.path.exists(CPUread):
			fh = open(CPUread,'r')  #CURRENT_CPU_T_FILE, "r")
			testo=fh.read()
			fh.close
			#print('>>'+testo+'<<')
			if testo!="":
				#//	pi@IDSL-01:~/programs/TAD$ cat CurrentTepCPU.txt
				#//	temp=32.6'C
				temp=int(testo.split('\n')[0])/1000.
				#print ('CPUTemp='+format(temp))
				adcData['tempCPU']=temp
		
		time.sleep(readingInterval)


if __name__ == "__main__":

	import readConfig as rc
	adcData={}
	config=rc.readConfig()
	adcData['tempCPU']=-1
	#print config
	init(config,adcData,10) 