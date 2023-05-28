#!/bin/bash
# V3.00 - Please update in case of changes
# Call the hw watchdog. In case of block an hw restart is triggered.
# since is a frequently called script it also telete temp files from RAMdisk

source /home/script/setVars.sh
#TAD=/tmp/TAD
parentdir=${TAD%/*}

# MOD 1
pinWD=4
cmd1=off
cmd2=on

# MOD 2
pinWD=9
cmd1=on
cmd2=off


NOW=$(date +"%Y-%m-%d")
FILE="WDLog_$NOW.txt"

echo $(date)
echo "start pinMode out Low..."
#/home/pi/programs/TAD/pinOnOff $pinWD $cmd1 
/home/script/pinOnOff 9  on

echo $(date) forzato su 9...$cmd1 pin $pinWD >> $TAD/$FILE
sleep 1

echo $(date)
echo "pinMode out High..."
#/home/pi/programs/TAD/pinOnOff $pinWD $cmd2 
/home/script/pinOnOff 9 off

echo "delete all temp from RAMdisk"
rm -f /tmp/EnterData*
rm -f /tmp/TAD/webcritech.jrc.ec.europa.eu/TAD_server/EnterData*

exit 0
