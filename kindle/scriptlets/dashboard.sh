#!/bin/sh
# Name: Home Console
# Author: Jeanne
# DontUseFBInk

REFRESH_SECONDS=900
PIDFILE=/tmp/home_console.pid

if [ -f "$PIDFILE" ]; then
    kill "$(cat "$PIDFILE")" 2>/dev/null
fi

(
    lipc-set-prop com.lab126.powerd preventScreenSaver 1
    sleep 3
    while true; do
        /usr/bin/wget -O /tmp/dash.png http://192.168.18.26:8080/text.png
        if [ $? -eq 0 ]; then
            /usr/sbin/eips -g /tmp/dash.png
        else
            /usr/sbin/eips 0 0 "WGET FAILED TO REACH PI"
        fi
        now=$(date +%s)
        sleep $((REFRESH_SECONDS - now % REFRESH_SECONDS))
    done
) &
echo $! > "$PIDFILE"
