#!/bin/bash
# V3.10 - Please update in case of changes
# On crontab. remotely execute command saved on ftp\IDSL_COMMANDS.TXT and upload the output

#  possible commands
#  		REBOOT
#  		GETCONFIG
#       DOWNLOAD_TAD

mkdir /tmp/script
source /home/script/setVars.sh
NOW=$(date +"%Y-%m-%d_%H%M%S")
SCRIPT=$HOSTNAME"_COMMANDS.TXT"
OUTFILE=$HOSTNAME"_OUTCOMMANDS_"$NOW".txt"


#cd /home/script
cd $SCRIPTexe

echo  donwloading  $SCRIPT and  uploading on $OUTFILE

ftp -p -n $HOST <<END_SCRIPT
quote USER $USER
quote PASS $PASSWD
cd $FTPDIR
binary
get $SCRIPT
rename $SCRIPT $SCRIPT.DONE
quit
END_SCRIPT

if [ -e "$SCRIPT" ]; then
command=`cat $SCRIPT`
chmod +x $SCRIPT

echo $command

if [ "$command" = "" ]; then
	exit 0
fi
./$SCRIPT  >  $OUTFILE

echo  mv $SCRIPT $SCRIPT.DONE.$NOW

mv $SCRIPT $SCRIPT.DONE.$NOW

echo "uploading output on server"
ftp -p -n $HOST <<END_SCRIPT
quote USER $USER
quote PASS $PASSWD
cd $FTPDIR
binary
put $OUTFILE
quit
END_SCRIPT

fi

exit 0
