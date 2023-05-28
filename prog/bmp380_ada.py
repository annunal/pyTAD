#sudo apt-get install python3
#sudo apt-get install python3-pip
#sudo pip3 install adafruit-circuitpython-bmp3xx
#sudo pip install --upgrade --no-deps --force-reinstall

# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time,os
import board
import adafruit_bmp3xx
from datetime import datetime as dt
# I2C setup
i2c = board.I2C()  # uses board.SCL and board.SDA
bmp = adafruit_bmp3xx.BMP3XX_I2C(i2c)

# SPI setup
# from digitalio import DigitalInOut, Direction
# spi = board.SPI()
# cs = DigitalInOut(board.D5)
# bmp = adafruit_bmp3xx.BMP3XX_SPI(spi, cs)

bmp.pressure_oversampling = 8
bmp.temperature_oversampling = 2

#bmp.sea_level_pressure = 1013.25

def init(config,adcData,readingInterval, folderOut):
    print ("---------------------------------------------------")
    print ("Starting reading BMP380 ADA")
    print ("opening ", config['pressureSensor'])
    print ("---------------------------------------------------")

    while True:
        nowString=dt.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        pressure,cTemp=(bmp.pressure,bmp.temperature)
        #print (nowString+','+format(pressure)+','+format(cTemp))
        f=open(folderOut+os.sep+'pt_ada388.txt','a')
        f.write(nowString+','+format(pressure)+','+format(cTemp)+'\n')
        f.close()
        f=open(folderOut+os.sep+'pt_ada388_current.txt','w')
        f.write(nowString+','+format(pressure)+','+format(cTemp)+'\n')
        f.close()
        adcData['pressure']=pressure
        adcData['temperature380']=cTemp
        time.sleep(readingInterval)    
