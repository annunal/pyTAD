
#!/bin/sh -e


# Absolute value
 abs() {
   [ $1 -lt 0 ] && echo $((-$1)) || echo $1
 }

MAXTIME=60

date -u '+%Y-%m-%d %H:%M:%S' > /tmp/currDate
currDate="$(cat /tmp/currDate)"

if [ "$1"x = "MAXTIME"x ] ; then
  # chkTime.sh MAXTIME 120
  MAXTIME=$2
fi

if [ "$1"x = "setDate"x ] ; then
  # chkTime.sh setDate
  echo "setting Teltonika date $currDate"
  sshpass -p 'Ecml2011' ssh root@192.168.1.1 -o ConnectTimeout=60 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "date --set='$currDate'"
fi

sshpass -p 'Ecml2011' ssh root@192.168.1.1 -o ConnectTimeout=60 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "date -u '+%Y-%m-%d %H:%M:%S'" >/tmp/TeltonikaDate

#cat  /tmp/TeltonikaDate 
#cat /tmp/currDate

TeltonikaDate="$(cat /tmp/TeltonikaDate)"

echo $currDate  $TeltonikaDate  "MAXTIME="$MAXTIME

currDateEpoch=`date -d "$currDate" +%s`
TeltonikaDateEpoch=`date -d "$TeltonikaDate" +%s`
delta=$(($currDateEpoch-$TeltonikaDateEpoch))

delta=$(abs $delta)
echo 'delta='$delta

if [ $delta -gt "$MAXTIME" ]; then
   echo 'set Teltonika Date' 
   date -u -s "$TeltonikaDate"  
fi
