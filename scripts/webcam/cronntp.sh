#!/bin/sh
# V3.00 - Please update in case of changes
# On crontab. Every 30m, update UTC time on Public NTP andvia internal VPN 

sudo ntpdate -u 85.199.214.99

#sudo ntpdate 213.145.129.29
sudo ntpdate pool.ntp.org
#sudo ntpdate 85.199.214.99
#sudo ntpdate 139.191.246.199 # jrc 
exit 0
