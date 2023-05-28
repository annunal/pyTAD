#!/bin/bash
# V3.11 - Please update in case of changes
# Scipt to get the config files. Use as Argument today or yesterday
echo $1

cd /home/script
source /home/script/setVars.sh
echo "$(cat /home/script/setVars.sh)"

YESTERDAY=`TZ=GMT+24 date +%Y-%m-%d`
TODAY=$(date +"%Y-%m-%d")
YEAR=`TZ=GMT+24 date +%Y`
FILE="AllData_$YESTERDAY.log"

#if [ "$1" == "YESTERDAY" ]; then
#        CURRENTDAY=$YESTERDAY
#else
#        CURRENTDAY=$TODAY
#fi  

cd $SCRIPTexe

#if [ -e "$FILE" ]; then
#  FILEZIP=AllData_$HOSTNAME_$CURRENTDAY
#  echo Zipping All data to  $FILEZIP.zip
#  zip $FILEZIP $FILE
#  FILEZIP=$FILEZIP.zip
#  echo $FILEZIP  --  $HOSTNAME
#  ls -la $FILEZIP 
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
# # rm $FILE
#fi

echo "downloading the script from the server "
SCRIPT=getConfigCommand.sh

ftp -p -n $HOST <<END_SCRIPT
quote USER $USER
quote PASS $PASSWD
cd configs
bi
get $SCRIPT
quit
END_SCRIPT

chmod +x $SCRIPT
exec ./$SCRIPT

