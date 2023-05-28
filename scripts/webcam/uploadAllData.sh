#!/bin/bash
# V3.13 - Please update in case of changes
# ftp passive mode enabled

export TAD=/tmp/TAD
export TADsource=/home/pi/programs/TAD0
export USBon=0
source /home/script/setVars.sh


TODAY=$(date +"%Y-%m-%d")
TODAY1=$(date +"%Y-%m-%d%H%M")
YEAR=`TZ=GMT+24 date +%Y`
HTTPstatus=$(curl -o /dev/null -m 15 --silent --head --write-out '%{http_code}\n' https://webcritech.jrc.ec.europa.eu)

cd $TAD

#----0---
# Check if the network and website is ok
if  [ $HTTPstatus -ne 200 ]; 
then
    echo "Website unreachable"
    exit 0 
else
  echo "Website OK"
  
#----1---
# retry then change name to allData

FILE="AllData_$TODAY.log"
FILEUP="AllData_"$HOSTNAME"_"$TODAY1".log"
FILEUP_USB="AllData_"$HOSTNAME"_"$TODAY".log"
RETRY="retry_$TODAY.txt"
RETRYUP="retry_"$HOSTNAME"_"$TODAY".log"
echo "1) resend un-transmitted data then change name $FILE"

#source $TAD/checkRetry.sh 
./checkRetry.sh 

mv $FILE $FILE.toBeSent
mv $RETRY $RETRY.toBeSent
#cp $FILE $FILE.toBeSent   


#----2-----
# upload the AllData to server in append mode
echo "2) Upload to server"
echo "Uploading files $FILE.toBeSent into $FILEUP and buffer.txt"
ls -la buffer.txt
if [ -e "$FILE.toBeSent" ];
then
  
  ftp -p -n $HOST <<END_SCRIPT
  quote USER $USER
  quote PASS $PASSWD
  cd TAD
  mkdir $HOSTNAME
  cd $HOSTNAME
  binary
  put buffer.txt 
  mkdir $YEAR
  cd $YEAR
  append $FILE.toBeSent $FILEUP
  append $RETRY.toBeSent $RETRYUP
  quit
END_SCRIPT

#----2a-----
# if usb is present do the same

if [ "$USBon" == 1 ] ; then
  mkdir $TADout/TAD
  echo "2a) copy to USB"
  cat $FILE.toBeSent>> $TADout/TAD/$YEAR/$FILEUP_USB
  cat $RETRY.toBeSent>> $TADout/TAD/$YEAR/$RETRYUP
  cp -f buffer.txt $TADout/TAD
fi

#----3-----
# remove tmp file
echo "3) delete .toBeSent"
rm -f $FILE.toBeSent
rm -f $RETRY.toBeSent
else
  echo "file not found: $FILE.toBeSent"
fi
echo "End of script"

fi
exit 0
