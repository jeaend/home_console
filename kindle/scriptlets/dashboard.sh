#!/bin/sh
# Name: Home Console
# Author: Jeanne
# DontUseFBInk

(
    sleep 3
    /usr/bin/wget -O /tmp/dash.png http://192.168.18.26:8080/text.png
    if [ $? -eq 0 ]; then
        /usr/sbin/eips -g /tmp/dash.png
    else
        /usr/sbin/eips 0 0 "WGET FAILED TO REACH PI"
    fi
) &