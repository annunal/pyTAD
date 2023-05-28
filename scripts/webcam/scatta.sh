#!/bin/bash
#parameters:  scatta.sh [mode]
#
# mode can be
#   large:  5   Mpixels 2592x1944 2960 kbytes
#   medium: 1.2 Mpixels 1280x960  806  kbytes  <<<defaulr
#   small:  0.3 Mpixel  640x480   236  kbytes
#   tiny:  0.08 MPixels 320x240

source /home/script/setVars.sh

DATE=$(date +"%Y%m%d")
HOUR=$(date +"%H%M") 

DAY=$(date +"%d")
MONTH=$(date +"%m")

echo $DATE $HOUR ': Received a request to take a picture ' $1 $2 $3 >> /tmp/logScattaRASP.txt   
ras=$(pidof libcamera-jpeg | wc -w)
rav=$(pidof libcamera-vid | wc -w)
echo $ras  $rav
if [ "$ras" = "1" ];then
  echo 'libcamera-jpeg in execution, retry later'
  exit 0
fi
if [ "$rav" = "1" ];then
  echo 'libcamera-vid in execution, retry later'
  exit 0
fi

LEV=$2
ALERT_LEVEL=$3
echo 'LEV='$LEV'  ALERT_LEVEL='$ALERT_LEVEL


#OPTIONS='-w 800 -h 600 -q 80 -x'

# default is 1.2 Mega pixels
OPTIONS0='--width 1280 --height 960  --rotation 180'
#OPTIONS0='-w 640 -h 480 -n -e jpg -q 50 -co 50 '

MINDIM=140000
#MINDIM=40000

if [ "$1" = "large" ];then
  OPTIONS0='  --rotation 180'
fi

if [ "$1" = "tiny" ];then
  OPTIONS0='--width 320 --height 240    --rotation 180'
fi

if [ "$1" = "small" ];then
  OPTIONS0='--width 640 --height 480   --rotation 180'
fi




FILE='IMG_'$DATE'_'$HOUR'.jpg'
filename='/tmp/'$FILE
year=`date +'%Y'`

NHour=`date +%H`

nh=$(echo "("`date +%H`+`date +%M`"/60)*100" | bc -l)
NHour=$(echo  $nh | cut -d. -f1)
echo $NHour

hou=$(echo "("`date +%H`+`date +%M`"/60)*100" | bc -l)
echo $hou

Nhou=$(echo  $hou | cut -d. -f1)
da=$(echo "("`date +%H`+`date +%M`"/60)/24" | bc -l)
hou00=$(echo "("-0.000087025*$da^4 + 0.0023466*$da^3 - 0.017485*$da^2 + 0.021255*$da + 0.25975")"*24   | bc -l)
hou0=$(echo $hou00*100-150 | bc -l) 
Nhou0=$(echo  $hou0 | cut -d. -f1) 

hou10=$(echo "("0.000115884*$da^4 - 0.00312329*$da^3 + 0.0244516*$da^2 - 0.047678*$da + 0.732922")"*24 | bc -l)
hou1=$(echo $hou10*100 | bc -l)
Nhou1=$(echo  $hou1 | cut -d. -f1)

echo $hou00  $hou10
echo 'current hour=' $Nhou '  start day at' $Nhou0  '   end day at' $Nhou1
if [[ $Nhou -ge $Nhou0 && $Nhou -lt $Nhou1 ]];then
  echo ' giorno '
  NIGHTMODE=.false.
  OPTIONS1=''
else
  echo 'notte'
  NIGHTMODE=.true.
  OPTIONS1=' --shutter 7000000 --brightness 0.9 --contrast 3 '
fi



echo $filename
cd /tmp

echo libcamera-jpeg -n -o $filename $OPTIONS0 $OPTIONS1
/usr/bin/libcamera-jpeg  -o $filename $OPTIONS0 $OPTIONS1
#filename=/tmp/IMG_20181016_0408.jpg

FILESIZE=$(stat -c%s "$filename")

if [ $NIGHTMODE = .true. ];then
  if [[ $FILESIZE -lt $MINDIM ]];then
     OPTIONS1=''
     echo 'repeat, '$FILESIZE' < '$MINDIM:'  libcamera-jpeg -o' $filename $OPTIONS0 $OPTIONS1 
    /usr/bin/libcamera-jpeg  -o $filename $OPTIONS0 $OPTIONS1
  else
    echo 'file ok ' $FILESIZE
  fi
else
  if [[ $FILESIZE -lt $MINDIM ]];then
    OPTIONS1=' --shutter 7000000 --brightness 0.9 --contrast 3 '
    echo 'repeat, '$FILESIZE' < '$MINDIM:'  libcamera-jpeg  -o ' $filename $OPTIONS0 $OPTIONS1
    /usr/bin/libcamera-jpeg  -n -o $filename $OPTIONS0 $OPTIONS1
  else
    echo 'file ok ' $FILESIZE
  fi
fi

ls -la $filename

echo "adding JRC overlay"
#/home/script/addJRCOverlay.sh $filename /tmp "$LOCATION"
echo /home/script/addJRCOverlay.sh $filename /tmp $LOCATION $LEV $ALERT_LEVEL
/home/script/addJRCOverlay.sh $filename /tmp "$LOCATION" "$LEV" "$ALERT_LEVEL"


echo "uploading on server "

# This instruction is to respect the rule on JRC server of _CAM for the webcam
HOSTNAME=${HOSTNAME/-CAM/_CAM}

ftp -p -n $HOST <<END_SCRIPT
quote USER $USER
quote PASS $PASSWD
bi
mkd  webcams/$HOSTNAME
mkd  webcams/$HOSTNAME/$year
mkd  webcams/$HOSTNAME/$year/$MONTH
mkd  webcams/$HOSTNAME/$year/$MONTH/$DAY
put $filename webcams/$HOSTNAME/$year/$MONTH/$DAY/$FILE
quit
END_SCRIPT

rm $filename




