#!/bin/bash
# V3.00 - Please update in case of changes
# set 1 in caseand an usb drive (/dev/sda1) is insert for local storage

export USBon=1

#FTP account
export HOST='webcritech.jrc.ec.europa.eu'
export USER='*******'
export PASSWD='******'
export FTPDIR=configs

##***********************************
export modeTAD=TAD     #  TAD or pyTAD  or RIO
#***********************************
echo "setVars: modeTAD="$modeTAD

if [ $modeTAD == 'pyTAD' ];then
    export TAD=/tmp/pyTAD
    export TADsource=/home/pi/programs/pyTAD
elif [ $modeTAD == 'pyTAD' ]; then
    export TAD=/tmp/RIO
    export TADsource=/home/pi/programs/RIO
else
    export TAD=/tmp/TAD
    export TADsource=/home/pi/programs/TAD0
fi   
export SCRIPTexe=/tmp/script
export TADout=/usb

echo "exported vars: $TAD  $TADsource  $modeTAD "
