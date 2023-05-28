#!/bin/sh
# V3.10 - Please update in case of changes
# On crontab. Every 30m, update UTC time on Public NTP and via internal VPN 

#sudo ntpdate -u 25.103.159.185
sudo ntpdate -u 185.19.184.35
sudo service  ntp stop
sudo ntpdate 213.145.129.29
sudo ntpdate pool.ntp.org
#sudo ntpdate 25.103.159.185
sudo service ntp start

sudo fake-hwclock
