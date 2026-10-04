#!/bin/sh
# Name: Home Console
# Author: Jeanne
# DontUseFBInk

REFRESH_SECONDS=900
START_HHMM=730
END_HHMM=2200
LOCAL_TZ="EST5EDT,M3.2.0,M11.1.0"
PIDFILE=/tmp/home_console.pid

if [ -f "$PIDFILE" ]; then
    kill "$(cat "$PIDFILE")" 2>/dev/null
fi

refresh() {
    /usr/bin/wget -O /tmp/dash.png http://192.168.18.26:8080/text.png
    if [ $? -eq 0 ]; then
        /usr/sbin/eips -g /tmp/dash.png
    else
        /usr/sbin/eips 0 0 "WGET FAILED TO REACH PI"
    fi
}

(
    lipc-set-prop com.lab126.powerd preventScreenSaver 1
    sleep 3
    refresh
    while true; do
        now=$(date +%s)
        sleep $((REFRESH_SECONDS - now % REFRESH_SECONDS))
        hhmm=$(TZ="$LOCAL_TZ" date +%H%M)
        if [ "$hhmm" -ge "$START_HHMM" ] && [ "$hhmm" -le "$END_HHMM" ]; then
            refresh
        fi
    done
) &
echo $! > "$PIDFILE"
