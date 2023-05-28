#!/bin/bash
# V3.10 - Please update in case of changes
# On crontab every 15 min. Check that is runnig fine

source /home/script/setVars.sh

FILE=$HOSTNAME'.txt'

cd $SCRIPTexe


/home/script/./nagiosTXT.sh  > $SCRIPTexe/$FILE 


ftp -p -n $HOST <<END_SCRIPT
quote USER $USER
quote PASS $PASSWD
cd nagios
binary
put $FILE
quit
END_SCRIPT
exit 0
