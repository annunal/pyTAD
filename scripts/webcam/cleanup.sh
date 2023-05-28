#!/bin/bash
# V3.14 - Please update in case of changes
# On crontab. Delete all logs older than 7 days on TADout (Alldata archives are kept).

source /home/script/setVars.sh
echo "$(cat /home/script/setVars.sh)"

NOW=$(date +"%Y-%m-%d %H:%M")
echo $NOW
myyear=`date +'%Y'`
days=+7
YESTERDAY=`TZ=GMT+24 date +%Y-%m-%d`
FILE="AllData_"$HOSTNAME"_"$YESTERDAY".log"
echo $FILE

rm -f /home/pi/*DLog.txt
rm -f /home/pi/programs/pinOnOff.log
rm -f /home/pi/programs/cronLOG.txt
rm -f /home/pi/programs/TAD/retryLog.txt


Target=/home/pi/
find $Target  -maxdepth 3 -type f -mtime $days -name '*.log' -exec rm -f -v  {} \;
find $Target -maxdepth 3 -type f -mtime $days -name 'retry_*' -exec rm -f -v {}  \;
find $Target -maxdepth 3 -type f -mtime $days -name 'checkLog*' -exec rm -f -v {} \;
find $Target -maxdepth 3 -type f -mtime $days -name '*'$myyear'*' -exec rm -f -v {} \;


Target=/usb/
mkdir $Target/TAD/
mkdir $Target/TAD/$myyear

cd $Target/TAD/$myyear
if [ -e "$FILE" ]; then
FILEZIP=AllData_"$HOSTNAME"_"$YESTERDAY"
echo Zipping All data to  $FILEZIP.zip
zip $FILEZIP $FILE
FILEZIP=$FILEZIP.zip
#  ftp -p -n $HOST <<END_SCRIPT
#  quote USER $USER
#  quote PASS $PASSWD
#  cd TAD/$HOSTNAME
#  mkd $YEAR
#  cd $YEAR
#  bi 
#  put $FILEZIP
#  quit
#END_SCRIPT
if [ -e "$FILEZIP" ]; then
rm $FILE
fi
fi

find $Target  -maxdepth 5 -type f -mtime $days -mtime -3650 -name '*.log' -exec rm -f -v  {} \;

exit