#!/bin/bash
#export TAD=/tmp/TAD
# V3.12 - Please update in case of change

export TAD=/tmp/TAD
export TADsource=/home/pi/programs/TAD0
export USBon=0

source /home/script/setVars.sh
TAD=/tmp/TAD1

echo "starting check of TAD  TAD="$TAD

if [ ! "$1" == "" ];then
	echo "redefinition of TAD as  $1"
	TAD=$1
fi
if [ ! "$2" == "" ];then
	echo "redefinitino of TADsource as $2"
	TADsource=$2
fi

echo "TAD="$TAD




# se esiste usb TADsource=/usb/TAD  ?

#----1---
if [ ! -d $TAD ] ; then
  echo "1) creating exec folder in tmp"
  mkdir $TAD
  cd $TAD
  
  #----2---
  echo "2) copy files from source"
  cp $TADsource/tad $TAD
  cp $TADsource/config.txt $TAD
  cp $TADsource/*.sh $TAD
  cp $TADsource/tad $TAD/tad-retry
  cp $TADsource/emailTemplate.txt $TAD
  cp $TADsource/periodic/* $TAD
  
  chmod +x *.sh
  chmod +x tad*
  
  
  #----3---
  echo "3) get buffer.txt"
  #if [ "$USBon" == "1" ] ; then
  #  cp $TADout/buffer.txt $TAD
  #else
    echo "Downloading the buffer.txt" 
  
ftp -p -n $HOST <<END_SCRIPT
  quote USER $USER
  quote PASS $PASSWD
  cd TAD/$HOSTNAME
  get buffer.txt
  quit
END_SCRIPT
  
  #fi

else
  echo "1) TAD=$TAD already exists"
fi

ls -la $TAD > $TAD/initaTADlog.txt
#----4---
echo "4) checkRunning tad from $TAD"
source $TAD/checkRunningTAD.sh

#echo "5) checkCPU from $TAD"
#source $TAD/checkCPUTemp.sh

# retry moved to uploadAll.sh
#echo "6) resend un-transmitted data from $TAD"
#source $TAD/checkRetry.sh 

echo "---  END OF INIT ---- "

