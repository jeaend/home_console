#!/bin/sh
# Name: Home Console
# Author: Jeanne
# DontUseFBInk

DASH_URL=http://192.168.18.26:8080/text.png
REFRESH_SECONDS=300
START_SECONDS=$((7 * 3600 + 30 * 60))
END_SECONDS=$((22 * 3600))
LOCAL_TZ="EST5EDT,M3.2.0,M11.1.0"
PIDFILE=/tmp/home_console.pid

battery_level() {
    level=$(lipc-get-prop com.lab126.powerd battLevel 2>/dev/null)
    [ -z "$level" ] && level=$(gasgauge-info -c 2>/dev/null)
    [ -z "$level" ] && level=$(cat /sys/class/power_supply/*/capacity 2>/dev/null | head -n 1)
    echo "$level" | tr -dc '0-9'
}

refresh() {
    tries=0
    while [ $tries -lt 6 ]; do
        if /usr/bin/wget -q -O /tmp/dash.png "$DASH_URL?battery=$(battery_level)"; then
            /usr/sbin/eips -g /tmp/dash.png
            return
        fi
        tries=$((tries + 1))
        sleep 5
    done
    /usr/sbin/eips 0 0 "WGET FAILED TO REACH PI"
}

seconds_until_next_wake() {
    now=$(date +%s)
    set -- $(TZ="$LOCAL_TZ" date "+%H %M %S")
    seconds_of_day=$(( ${1#0} * 3600 + ${2#0} * 60 + ${3#0} ))
    delta=$((REFRESH_SECONDS - now % REFRESH_SECONDS))
    while true; do
        wake_at=$(( (seconds_of_day + delta) % 86400 ))
        if [ $wake_at -ge $START_SECONDS ] && [ $wake_at -le $END_SECONDS ]; then
            echo $delta
            return
        fi
        delta=$((delta + REFRESH_SECONDS))
    done
}

find_rtc() {
    for rtc in /sys/class/rtc/rtc*; do
        if [ -e "$rtc/wakealarm" ]; then
            echo "$rtc"
            return
        fi
    done
}

suspend_for() {
    target=$(( $(date +%s) + $1 ))
    if [ -n "$RTC" ]; then
        echo 0 > "$RTC/wakealarm"
        echo "+$1" > "$RTC/wakealarm"
        echo mem > /sys/power/state
    fi
    remaining=$(( target - $(date +%s) ))
    if [ $remaining -gt 0 ]; then
        sleep $remaining
    fi
}

if [ "$1" = "--loop" ]; then
    echo $$ > "$PIDFILE"
    lipc-set-prop com.lab126.powerd preventScreenSaver 1
    stop lab126_gui 2>/dev/null || stop framework 2>/dev/null
    sleep 3
    RTC=$(find_rtc)
    while true; do
        refresh
        suspend_for "$(seconds_until_next_wake)"
    done
fi

if [ -f "$PIDFILE" ]; then
    kill "$(cat "$PIDFILE")" 2>/dev/null
fi

if command -v setsid >/dev/null 2>&1; then
    setsid sh "$0" --loop >/dev/null 2>&1 &
else
    sh "$0" --loop >/dev/null 2>&1 &
fi
