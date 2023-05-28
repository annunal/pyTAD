#!/bin/bash
#export TAD=/tmp/TAD
# V3.12 - Please update in case of change



source /home/script/setVars.sh

echo 'initTAD: modeTAD='$modeTAD

if [ $modeTAD == 'pyTAD' ];then
    export TAD=/tmp/pyTAD
    export TADsource=/home/pi/programs/pyTAD
fi
if [ $modeTAD == 'RIO' ];then
    export TAD=/tmp/RIO
    export TADsource=/home/pi/programs/RIO
fi
if [ $modeTAD == 'TAD' ];then
    export TAD=/tmp/TAD
    export TADsource=/home/pi/programs/TAD0    
fi   
export USBon=0


echo "starting check of TAD  TAD="$TAD"  TADsource="$TADsource

# se esiste usb TADsource=/usb/TAD  ?

#----1---
if [ ! -d $TAD ] ; then
  echo "1) creating exec folder in tmp"
  mkdir $TAD
  cd $TAD
  
  #----2---
  echo "2) copy files from source"
  if [ $modeTAD == 'pyTAD' ];then
    mkdir -p $TAD
    touch  createdFolder.txt
  fi
  if [ $modeTAD == 'RIO' ];then
    mkdir -p $TAD
    touch  createdFolder.txt
  fi
  if [ $modeTAD == 'TAD' ];then
      cp $TADsource/tad $TAD
      cp $TADsource/config.txt $TAD
      cp $TADsource/*.sh $TAD
      cp $TADsource/tad $TAD/tad-retry
      cp $TADsource/emailTemplate.txt $TAD
      cp $TADsource/periodic/* $TAD 
  fi
  chmod +x *.sh
  chmod +x tad*
  
   
  #----3---
  echo "3) get buffer.txt"
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

#----4---
echo "4) checkRunning tad from $TAD"
if [ $modeTAD == 'pyTAD' ];then
    cd $TADsource
    python3 $TADsource/checkRunningpyTAD.py
fi
if [ $modeTAD == 'RIO' ];then
    cd $TADsource
    ./TAD    
fi    
if [ $modeTAD == 'TAD' ];then
    source $TAD/checkRunningTAD.sh
fi
#echo "5) checkCPU from $TAD"
#source $TAD/checkCPUTemp.sh

# retry moved to uploadAll.sh
#echo "6) resend un-transmitted data from $TAD"
#source $TAD/checkRetry.sh 

echo "---  END OF INIT ---- "

