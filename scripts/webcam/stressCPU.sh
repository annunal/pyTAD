#!/bin/bash

md5sum < /dev/urandom &
cat /dev/urandom | gzip > /dev/null &
dd if=/dev/urandom of=/dev/null bs=16M &
