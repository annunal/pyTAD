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
ras=$(pidof raspistill | wc -w)
rav=$(pidof raspivid | wc -w)
echo $ras  $rav
if [ "$ras" = "1" ];then
  echo 'raspistill in execution, retry later'
  exit 0
fi
if [ "$rav" = "1" ];then
  echo 'raspivid in execution, retry later'
  exit 0
fi

LEV=$2
ALERT_LEVEL=$3
echo 'LEV='$LEV'  ALERT_LEVEL='$ALERT_LEVEL


#OPTIONS='-w 800 -h 600 -q 80 -x'

# default is 1.2 Mega pixels
OPTIONS0='-w 1280 -h 960 -n -e jpg -q 50 -co 50 -ex auto -vf -hf'
#OPTIONS0='-w 640 -h 480 -n -e jpg -q 50 -co 50 '

MINDIM=100000
#MINDIM=40000

if [ "$1" = "large" ];then
  OPTIONS0='-n -e jpg -q 50 -co 50 '
fi

if [ "$1" = "tiny" ];then
  OPTIONS0='-w 320 -h 240 -n -e jpg -q 50 -co 50 '
fi

if [ "$1" = "small" ];then
  OPTIONS0='-w 640 -h 480 -n -e jpg -q 50 -co 50 '
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
  OPTIONS1=' -ISO 2000 -ss 7000000 -br 90 -co 100 -e jpg -vs'
fi



echo $filename
cd /tmp

echo raspistill -n -o $filename $OPTIONS0 $OPTIONS1
/usr/bin/raspistill  -n -o $filename $OPTIONS0 $OPTIONS1
#filename=/tmp/IMG_20181016_0408.jpg

FILESIZE=$(stat -c%s "$filename")

if [ $NIGHTMODE = .true. ];then
  if [[ $FILESIZE -lt $MINDIM ]];then
     OPTIONS1=''
     echo 'repeat, '$FILESIZE' < '$MINDIM:'  raspistill -n -o' $filename $OPTIONS0 $OPTIONS1 
    /usr/bin/raspistill  -n -o $filename $OPTIONS0 $OPTIONS1
  else
    echo 'file ok ' $FILESIZE
  fi
else
  if [[ $FILESIZE -lt $MINDIM ]];then
    OPTIONS1=' -ISO 2000 -ss 7000000 -br 90 -co 100 -e jpg -vs'
    echo 'repeat, '$FILESIZE' < '$MINDIM:'  raspistill -n -o ' $filename $OPTIONS0 $OPTIONS1
    /usr/bin/raspistill  -n -o $filename $OPTIONS0 $OPTIONS1
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




#raspistill Camera App v1.3.11

#Runs camera for specific time, and take JPG capture at end if requested#

#usage: raspistill [options]

#Image parameter commands

#-?, --help      : This help information
#-w, --width     : Set image width <size>
#-h, --height    : Set image height <size>
#-q, --quality   : Set jpeg quality <0 to 100>
#-r, --raw       : Add raw bayer data to jpeg metadata
#-o, --output    : Output filename <filename> (to write to stdout, use '-o -'). If not specified, no file is saved
#-l, --latest    : Link latest complete image to filename <filename>
#-v, --verbose   : Output verbose information during run
#-t, --timeout   : Time (in ms) before takes picture and shuts down (if not specified, set to 5s)
#-th, --thumb    : Set thumbnail parameters (x:y:quality) or none
#-d, --demo      : Run a demo mode (cycle through range of camera options, no capture)
#-e, --encoding  : Encoding to use for output file (jpg, bmp, gif, png)
#-x, --exif      : EXIF tag to apply to captures (format as 'key=value') or none
#-tl, --timelapse        : Timelapse mode. Takes a picture every <t>ms. %d == frame number (Try: -o img_%04d.jpg)
#-fp, --fullpreview      : Run the preview using the still capture resolution (may reduce preview fps)
#-k, --keypress  : Wait between captures for a ENTER, X then ENTER to exit
#-s, --signal    : Wait between captures for a SIGUSR1 or SIGUSR2 from another process
#-g, --gl        : Draw preview to texture instead of using video render component
#-gc, --glcapture        : Capture the GL frame-buffer instead of the camera image
#-set, --settings        : Retrieve camera settings and write to stdout
#-cs, --camselect        : Select camera <number>. Default 0
#-bm, --burst    : Enable 'burst capture mode'
#-md, --mode     : Force sensor mode. 0=auto. See docs for other modes available
#-dt, --datetime : Replace output pattern (%d) with DateTime (MonthDayHourMinSec)
#-ts, --timestamp        : Replace output pattern (%d) with unix timestamp (seconds since 1970)
#-fs, --framestart       : Starting frame number in output pattern(%d)
#-rs, --restart  : JPEG Restart interval (default of 0 for none)#
#
#Preview parameter commands#
#
#-p, --preview   : Preview window settings <'x,y,w,h'>
#-f, --fullscreen        : Fullscreen preview mode
#-op, --opacity  : Preview window opacity (0-255)
#-n, --nopreview : Do not display a preview window#
#
#Image parameter commands#
#
#-sh, --sharpness        : Set image sharpness (-100 to 100)
#-co, --contrast : Set image contrast (-100 to 100)
#-br, --brightness       : Set image brightness (0 to 100)
#-sa, --saturation       : Set image saturation (-100 to 100)
#-ISO, --ISO     : Set capture ISO
#-vs, --vstab    : Turn on video stabilisation
#-ev, --ev       : Set EV compensation - steps of 1/6 stop
#-ex, --exposure : Set exposure mode (see Notes)
#-fli, --flicker : Set flicker avoid mode (see Notes)
#-awb, --awb     : Set AWB mode (see Notes)
#-ifx, --imxfx   : Set image effect (see Notes)
#-cfx, --colfx   : Set colour effect (U:V)
#-mm, --metering : Set metering mode (see Notes)
#-rot, --rotation        : Set image rotation (0-359)
#-hf, --hflip    : Set horizontal flip
#-vf, --vflip    : Set vertical flip
#-roi, --roi     : Set region of interest (x,y,w,d as normalised coordinates [0.0-1.0])
#-ss, --shutter  : Set shutter speed in microseconds
#-awbg, --awbgains       : Set AWB gains - AWB mode must be off
#-drc, --drc     : Set DRC Level (see Notes)
#-st, --stats    : Force recomputation of statistics on stills capture pass
#-a, --annotate  : Enable/Set annotate flags or text
#-3d, --stereo   : Select stereoscopic mode
#-dec, --decimate        : Half width/height of stereo image
#-3dswap, --3dswap       : Swap camera order for stereoscopic
#-ae, --annotateex       : Set extra annotation parameters (text size, text colour(hex YUV), bg colour(hex YUV))
#-ag, --analoggain       : Set the analog gain (floating point)
#-dg, --digitalgain      : Set the digtial gain (floating point)


#Notes

#Exposure mode options :
#off,auto,night,nightpreview,backlight,spotlight,sports,snow,beach,verylong,fixedfps,antishake,fireworks#

#Flicker avoid mode options :
#off,auto,50hz,60hz

#AWB mode options :
#off,auto,sun,cloud,shade,tungsten,fluorescent,incandescent,flash,horizon

#Image Effect mode options :
#none,negative,solarise,sketch,denoise,emboss,oilpaint,hatch,gpen,pastel,watercolour,film,blur,saturation,colourswap,washedout,posterise,colourpoint,colourbalance,cartoon

#Metering Mode options :
#average,spot,backlit,matrix

#Dynamic Range Compression (DRC) options :
#off,low,med,high

#Preview parameter commands

#-gs, --glscene  : GL scene square,teapot,mirror,yuv,sobel,vcsm_square
#-gw, --glwin    : GL window settings <'x,y,w,h'>
