#!/bin/bash
#
# V3.12 - Please update in case of changes

source /home/script/setVars.sh

NOW=$(date +"%Y-%m-%d")
FILE="checkCPUTempLog_$NOW.txt"
logfile="$TAD/$FILE"

echo "$(date)" >> $logfile

# Check log file last modified date: if older than 45', the CPU check stopped working
# properly and a reboot is needed

NOWSEC=$(date +%s)
FILSEC=$(stat -c%Y $TAD/CurrentTempCPU.txt)
AGE=`echo $NOWSEC - $FILSEC | bc`

echo "File age="$AGE >>$logfile

if [ "$AGE" -gt 2700 ];
then
        rm -f /tmp/script/resetWD9.sh
        echo $(date) forced shutdown due to CPU temp $AGE > /usb/forcedshutdown.log
        echo $(date) forced shutdown due to CPU temp $AGE
        sudo shutdown -rf 21
		exit 0
fi



CPURAW=$(cat /sys/class/thermal/thermal_zone0/temp)
# echo $CPURAW
CPUOUT="`echo $CPURAW |cut -c1-2`.`echo $CPURAW |cut -c3-5`"
# echo $CPUOUT
printf -v CPUOUT  "%.1f" "$CPUOUT"
# echo $CPUOUT

if [ "$CPUOUT" = "0.0" ];
then
	echo "CPU Temp =0.0 not stored ">>$logfile
else
	CPU="temp="$CPUOUT"'C" 
	echo $CPU > $TAD/CurrentTempCPU.txt
	echo $CPU >>$logfile
	echo  "Temp CPU="$CPUOUT
fi
