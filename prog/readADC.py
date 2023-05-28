# Usage: getadcreading(address, hexvalue) to return value in volts from selected channel.
#
# address = adc_address1 or adc_address2 - Hex address of I2C chips as configured by board header pins.

import readConfig as rc
from ADCPi import ADCPi
import time,sys
from smbus import SMBus
#import re

ADC_1=         0x6a
ADC_2=         0x69

def init(config,adcData,readingInterval,printVals=False):
    print ("---------------------------------------------------")
    print ("Starting reading ADC")
    print ("opening ", config['batteryPin'], config['batteryMultiplier'], config['sonarTempPin'])
    print ("---------------------------------------------------")
     
    # getadcreading(adc_address1, 0x93) 
    batteryPin=         int(config['batteryPin'])
    batteryMultiplier=    float(config['batteryMultiplier'])
    panelPin=            int(config['panelPin']) 
    tempPin=            int(config['sonarTempPin'])
    SonarTempMultiplier=float( config['SonarTempMultiplier'])
    SonarTempAddConst=    float(config['SonarTempAddConst'])
    print (batteryPin,tempPin,panelPin)
    ADC_1=int(config['ADC_1'])
    ADC_2=int(config['ADC_2'])
    print('ADC_1,ADC_2',ADC_1,ADC_2)
    adc = ADCPi(ADC_1, ADC_2, 18)

    while True:
        try:
            v=adc.read_voltage(batteryPin)*batteryMultiplier
        except:
            v=12
        try:
            p=adc.read_voltage(panelPin)
        except:
            p=0.0
        try:
            t=adc.read_voltage(tempPin)
        except:
            t=0.0
        if t !=0:
          ut=1/t
          te=SonarTempAddConst+SonarTempMultiplier*ut
        else:
          te=0.0
        if printVals:
            print ('v=',v,' p=',p,' t=',te)
        adcData['batteryValue']=v
        adcData['panelValue']=p
        adcData['tempValue']=te
        
        time.sleep(readingInterval)


if __name__ == "__main__":
    arguments = sys.argv[1:]
    count = len(arguments)
    print (count)

    
    adcData={}
    config=rc.readConfig()
    #print config
    init(config,adcData,10,True) 