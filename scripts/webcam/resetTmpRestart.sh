#!/bin/bash
# V3.10 - Please update in case of changes

#  1.  check if network exists
#  2.  stop tad 
#  3. (if exists) uploadAll#
#  4. (if exists) clear all the content of /tmp
#  5.  initTAD

#  check if network exists
HTTPstatus=$(curl -o /dev/null -m 15 --silent --head --write-out '%{http_code}\n' http://webcritech.jrc.ec.europa.eu/tad_server/default.aspx)

#  stop tad
echo "Killing running tad and upload Alldata"
pidof tad |xargs sudo kill 

# Check if the network and website is ok
echo "check if I have connection"
if  [ $HTTPstatus -ne 200 ]; 
then
    echo "Website unreachable"
else
  echo "-- connection OK"
  #  uploadAll
  echo "Uploading all data"
  source /home/script/uploadAllData.sh
  #  clear all the content of /tmp
  echo "removing files in tmp"
  rm -rf /tmp/TAD
fi

#  initTAD
echo "resetting and restarting"
source /home/script/initTAD.sh
ls -la /tmp/TAD

exit 0