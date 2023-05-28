#! /bin/sh
mkdir ~/.ssh
dropbearkey -t rsa -f ~/.ssh/id_rsa
crontab -l>crontab.txt
echo '*/1 * * * * /bin/sh /sbin/sms_command.sh read > /root/sms_log.txt'>>crontab.txt
crontab crontab.txt
