#!/bin/bash
# V3.10 - Please update in case of changes
# On crontab. Weekly Backup all the System files and exec logs from USB to FTP,


mkdir /usb
TARGET=/usb/
#parentdir=${TAD%/*}

source /home/script/setVars.sh
echo "$(cat /home/script/setVars.sh)"

cd $TARGET
mkdir Backup
cd Backup

sudo crontab -l > crontab.backup
cp /var/log/messages $(date +%y%m%d)-messages

rm -f *

zip TAD_home.zip /home/pi/programs/TAD/*
zip TAD0.zip /home/pi/programs/TAD0/*
zip $(date +%y%m%d)-TADout.zip $TAD/*.txt
zip HamachiConfig.zip /var/lib/logmein-hamachi/*
zip $(date +%y%m%d)-SystemConfig.zip /etc/rc.local
zip $(date +%y%m%d)-SystemConfig.zip /etc/fstab
zip $(date +%y%m%d)-SystemConfig.zip /etc/inittab
zip $(date +%y%m%d)-SystemConfig.zip /boot/cmdline.txt
zip $(date +%y%m%d)-SystemConfig.zip /etc/resolv.conf
zip $(date +%y%m%d)-SystemConfig.zip /etc/hosts
zip $(date +%y%m%d)-SystemConfig.zip /etc/network/interfaces
zip $(date +%y%m%d)-SystemConfig.zip /etc/sudoers
zip $(date +%y%m%d)-Programs.zip /home/script/*
zip $(date +%y%m%d)-Programs.zip /home/pi/programs/pinOnOff/*
zip $(date +%y%m%d)-Programs.zip /home/pi/programs/*

ftp -p -n $HOST <<END_SCRIPT
quote USER $USER
quote PASS $PASSWD
binary
cd Backup
mkdir $HOSTNAME
cd $HOSTNAME
put TAD_home.zip
put TAD0.zip
put $(date +%y%m%d)-TADout.zip
put $(date +%y%m%d)-messages
put $(date +%y%m%d)-Programs.zip
put crontab.backup
put HamachiConfig.zip
put $(date +%y%m%d)-SystemConfig.zip
quit
END_SCRIPT
exit 0
