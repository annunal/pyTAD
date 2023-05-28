#!/bin/bash
# V3.00 - Please update in case of changes

source /home/script/setVars.sh
#echo "$(cat /home/script/setVars.sh)"

FILE=$HOSTNAME'.txt'

cd $SCRIPTexe

echo  "status ROUTER (sim_status, operator, signal, network_data, temperature_dC)"
# sshpass -p 'Ecml2011' ssh root@192.168.1.1 -o StrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null "gsmget -z -o -l -s -c" 
sshpass -p 'Ecml2011' ssh root@192.168.1.1 -o ConnectTimeout=59 -o StrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null "gsmget -z -o -l -s -c"

echo ""
echo "---------------------------"
echo ""

echo "status " $HOSTNAME
uptime
#/opt/vc/bin/vcgencmd measure_temp
cat $TAD/CurrentTempCPU.txt
echo ""
echo ""


echo "checking disk status..."
echo $HOSTNAME
/home/script/./check_disk.pl -v

echo ""
echo "checking TAD process..."
echo $HOSTNAME
/home/script/./check_ps.sh -p TAD

echo ""
echo "checking TAD_log last modification ..."
echo $HOSTNAME
/home/script/./check_newest.sh  -d $TAD/ -w 1 -c 12 -t hours -V

echo ""
/etc/init.d/watchdog status

echo ""
echo "partitions check..."
sudo tune2fs -l /dev/mmcblk0p2  | grep -iE '(state)' > diskstaus.log
sudo tune2fs -l /dev/mmcblk0p5  | grep -iE '(state)' >> diskstaus.log
echo $HOSTNAME
while read p; do
if [ "$p" != "Filesystem state:         clean" ] ; then
    echo "CRITICAL - There's an error on the filesystem"
    echo $p
        else
        echo "OK - Filesystem CLEAN"
fi
done <diskstaus.log
sudo tune2fs -l /dev/mmcblk0p5 | grep "First error t"
sudo tune2fs -l /dev/mmcblk0p5 | grep "Last error t"
sudo tune2fs -l /dev/mmcblk0p5 | grep "Lifetime writes"


exit 0
