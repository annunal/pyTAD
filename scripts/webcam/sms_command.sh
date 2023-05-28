#! /bin/sh  
#-x
#  vers. 24.03.2018 07:00 
#
#  sms_command.sh  by A. Annunziato, D. Galliano
#  
#  objective:  to realize a command listener on Teltnika remote device based on SMS
#
# how to install
#
#1. on RPI go in /home/script and launch this script with 
#   bash sms_command.sh config
#  give the teltonika password several times
#2. copy the public part in authorized_keys of RPI 
#        (public part is: ssh-rsa AAAAB3NzaC1yc....57j5ip3x root@Teltonika)
#    edit the file /home/pi/.ssh/authorized_keys  and include the public key of Teltonika
#    give permission 600 to /home/pi/.ssh/authorized_keys:  chmod 600 /home/pi/.ssh/authorized_keys
#3. change permissions
#    chmod og-w /home/pi
#
#4. login into Teltonika router from client machine 
#    ssh root@192.168.1.1
#    check connection on Teltonika:  
#          ssh -i /root/.ssh/id_rsa pi@192.168.1.100 ls (or any other Ip of raspberry)  
#    check sending a SMS: wget "http://192.168.1.1/cgi-bin/sms_send?username=user1&password=user_pass&number=00393480352661&text=IDSL-19" -O out.txt
#  if you are unable to send check the allowed numbers in the teltonika web interface
#
#
#  how to use the system:
#    send an SMS to the number of the SIM on the device, with one of the commands
#       ex:  CMDTELT  [cmd]  to execute commands on Teltonika
#            CMDRPI   [cmd]  to execute commands on Raspberry
#       you will receive a SMS reply


filename_log='/root/sms_log.txt'
filename_out='/tmp/sms_out_send.txt'

USER=root
OLDPWD=/tmp
HOME=/root
SSH_TTY=/dev/pts/0
PS1=\u@\h:\w\$
LOGNAME=root
TERM=xterm
PATH=/bin:/sbin:/usr/bin:/usr/sbin
SHELL=/bin/ash
PWD=/root


if [ "$1" = "config" ];then
	echo 'configuration started'
	echo $HOSTNAME > sms_config.txt
	ip=192$(ifconfig | sed -En 's/127.0.0.1//;s/.*inet (addr:192)?(([0-9]*\.){3}[0-9]*).*/\2/p')
	echo 'my IP is:' $ip
	echo $ip>sms_IP.txt
	echo 'copying config.txt on Teltonika'
	scp sms_config.txt root@192.168.1.1:/sbin/sms_config.txt
	echo 'copying ip.txt on Teltonika'
	scp sms_IP.txt root@192.168.1.1:/sbin/sms_IP.txt
	echo 'copying the script on Teltonika'
	scp sms_command.sh root@192.168.1.1:/sbin/sms_command.sh
	echo "#! /bin/sh"  > sms_init.sh
	echo 'mkdir ~/.ssh'>> sms_init.sh
    echo "dropbearkey -t rsa -f ~/.ssh/id_rsa">> sms_init.sh
	echo "crontab -l>crontab.txt">> sms_init.sh
	echo "echo '*/1 * * * * /bin/sh /sbin/sms_command.sh read > /root/sms_log.txt'>>crontab.txt">>sms_init.sh
	echo "crontab crontab.txt">>sms_init.sh
	scp sms_init.sh root@192.168.1.1:sms_init.sh
	ssh root@192.168.1.1 'chmod +x sms_init.sh;sh sms_init.sh'
	cd /home/pi
	
	cd /home/pi/.ssh
	echo 'vi authorized_keys'
	
	exit 0
fi
if [ ! -f /sbin/sms_config.txt ];then
	echo 'first launch with config from raspberry'
	exit 0
fi
# number authorized to send commands
ALLOWED_NUMBER1="+393480352661"
ALLOWED_NUMBER2="+32460213831"
REPLYNUMBER="+393480352661"

#HOSTNAME_TAD="$(cat /sbin/sms_config.txt)" #"IDSL-32"
HOSTNAME_TAD=$(cat /sbin/sms_config.txt)
IP_TAD=$(cat /sbin/sms_IP.txt)
echo 'Hostname: '$HOSTNAME
filename='/tmp/sms_listaSMS.txt'
filename_cmd='/tmp/sms_cmd.txt'
filename_out='/tmp/sms_out.txt'
filename_delete='/tmp/sms_delete.txt'
filename_log='/root/sms_log.txt'
#if [ -e /tmp/sms_running ];then
#	echo 'sms_command.sh already running, exiting'
#	exit 0
#fi
touch /tmp/sms_running
if [ "$1" = "read" ];then
        echo "wget http://192.168.1.1/cgi-bin/sms_list?username=user1&password=user_pass -O $filename"
        wget "http://192.168.1.1/cgi-bin/sms_list?username=user1&password=user_pass" -O $filename
fi
if [ "$1" = "debug" ];then
        filename='/root/sms_listaSMS_debug.txt'
fi
echo "reading "$filename
IFS=$'\n'
for next in `cat $filename`
do
    if [[ ${next:1:3} = 'pre' ]];then
      next=${next:5}
    fi
    if [[ ${next:0:6} = "Index:" ]];then
      index0=${next:7}
      index=${index0/^ *//}
    fi
    if [[ ${next:0:7} = "Sender:" ]];then
      sender=${next:8}
	  if [ "$sender" = "$ALLOWED_NUMBER2" ];then
		sender=$ALLOWED_NUMBER1
	  fi
	  sender1=${sender/+/00}
    fi
    if [[ ${next:0:5} = "Text:" ]];then
       text0=${next:6}
       text=${text0/^ *//}
	   text="$(echo $text| sed -e 's/^[ \t]*//')"
    fi
    if [[ ${next:0:7} = "Status:" ]];then
       status=${next:8}
	   cmd=''
       echo $sender  ">>"$text"<< "$status
		   
           if [ "$sender" = "$ALLOWED_NUMBER1" ] ;then
                echo "$text" | fgrep "REBOOT_RPI"
                if [ "$?" -eq "0" ];then
						cmd="reboot"
						target="RPI"
				fi
                echo "$text" | fgrep "CMDRPI"
                if [ "$?" -eq "0" ];then
						cmd=${text:7}
						target="RPI"
						echo 'command found in SMS list from '$sender' cmd='$cmd
				fi
                echo "$text" | fgrep "CMDTELT"
                if [ "$?" -eq "0" ];then
						cmd=${text:8}
						target="TELT"
						echo 'command found in SMS list from '$sender' cmd='$cmd
				fi
				
				if [ "$cmd" != "" ];then
					cmd="$(echo $cmd| sed -e 's/^[ \t]*//')"
					cmdwget="$(echo $cmd | sed 's/ /%20/g')"
					
					if [ "$target" = "RPI" ];then
						echo $(date)': /usr/bin/ssh   -i /root/.ssh/id_rsa pi@'$IP_TAD' '$cmd >>$filename_log
						echo '/usr/bin/ssh -i /root/.ssh/id_rsa -I 120 pi@'$IP_TAD' "'$cmd'"'
						echo '"'$cmd'>'$filename_cmd'"' | xargs /usr/bin/ssh  -i /root/.ssh/id_rsa -I 120 pi@$IP_TAD 
						/usr/bin/scp -i /root/.ssh/id_rsa pi@$IP_TAD:$filename_cmd $filename_cmd
					fi  
					if [ "$target" = "TELT" ]; then	
						echo $(date)': '$cmd >>$filename_log
						echo "command on teltonika: >>"$cmd'<<'
						echo $cmd | /bin/ash &> $filename_cmd
					fi
					reply="$(cat $filename_cmd)" 
					echo $reply
					replywget0="$(cat $filename_cmd | tr '\n' '|'  | sed 's/|/%0A/g'  | sed 's/ /%20/g')"
					replywget=${replywget0:0:200} 
					echo replywget
					echo $(date)': '$reply >>$filename_log
					
					desc=$HOSTNAME_TAD" cmd:"$cmd"  reply:"$replywget
					descwget="$(echo $desc | sed 's/ /%20/g')"
					
					echo wget "http://192.168.1.1/cgi-bin/sms_send?username=user1&password=user_pass&number="$sender1"&text="$descwget
					if [ "$1" != "debug" ];then
						wget "http://192.168.1.1/cgi-bin/sms_send?username=user1&password=user_pass&number=$sender1&text=$descwget" -O $filename_out

						echo wget "http://192.168.1.1/cgi-bin/sms_delete?number="$index
						wget "http://192.168.1.1/cgi-bin/sms_delete?username=user1&password=user_pass&number="$index -O $filename_delete
					fi			
					echo "scp "$filename_log" -i ~/.ssh/id_rsa pi@"$IP_TAD" /home/script/sms_log.txt"
					scp $filename_log -i ~/.ssh/id_rsa pi@$IP_TAD:/home/script/sms_log.txt
					sleep 2
                fi
           fi
    fi

done
echo 'removing running file'
if [ "$cmd" != "" ];then
	echo $(date)': removing running file' >>$filename_log
fi
rm /tmp/sms_running

