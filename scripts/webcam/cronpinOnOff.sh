#!/bin/bash
# V3.10 - Please update in case of changes
# On crontab. Daily restart of the router via relè

source /home/script/setVars.sh
echo "$(cat /home/script/setVars.sh)"

#parentdir=${TAD%/*}
cd /home/pi/programs/pinOnOff/

# MOD 1
mode1=off
mode2=on

echo $(date)
#echo "Router uptime: " 
#sshpass -p 'Ecml2011' ssh root@192.168.1.1 -o StrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null "uptime" 
echo "IDSL initiated the ROUTER poweroff...$mode1"
#./pinOnOff 7  $mode1
sudo /home/script/pinOnOff 7  $mode1

sleep 4

echo $(date)
echo "IDSL initiated the poweron...$mode2"
#./pinOnOff 7  $mode2
sudo /home/script/pinOnOff 7  $mode2
sshpass -p 'Ecml2011' ssh root@192.168.1.1 -o ConnectTimeout=60 -o StrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null "uptime" 

echo $(date) Teltonika reset $mode1 - $mode2
echo ""
exit 0

