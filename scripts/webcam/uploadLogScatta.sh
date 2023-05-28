#!/bin/bash
#parameters:  scatta.sh [mode]
source /home/script/setVars.sh
DATE=$(date +"%Y%m%d")
HOUR=$(date +"%H%M")
year=`date +'%Y'`

DAY=$(date +"%d")
MONTH=$(date +"%m")


filename='logScattaOut.txt'

echo $filename
echo $HOSTNAME
echo $year
echo $MONTH
echo $DAY
echo webcams/$HOSTNAME/$year/$MONTH/$DAY/$filename
cd /tmp

echo  $HOST
echo $USER
echo $PASSWD
echo "uploading on server "

ftp -p -n $HOST <<END_SCRIPT
quote USER $USER
quote PASS $PASSWD
bi
mkd webcams/$HOSTNAME
mkd webcams/$HOSTNAME/$year
mkd webcams/$HOSTNAME/$year/$MONTH
mkd webcams/$HOSTNAME/$year/$MONTH/$DAY
put /tmp/$filename webcams/$HOSTNAME/$year/$MONTH/$DAY/$filename
quit
END_SCRIPT

