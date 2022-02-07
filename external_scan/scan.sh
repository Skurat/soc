#!/bin/bash
if [ -z "$1" ]; then
	echo "Need argument - path to target file."
    exit
elif [ ! -f "$1" ]; then
	echo "File does not exist"
    exit
elif ! grep -Pq "([0-9]{1,3}\.){3}[0-9]{1,3}" $1; then
    echo "File does not have any IP"
    exit
fi
BOT_TOKEN="871783617:AAFcIkJ-Yytvq7IVxQkBbKAKPdDGoarve7U"
CHAT_ID="300576657"
OPTIONS="-T4"
date=`date "+%F %H:%M"`
TARGET_FILE="$1"
LOG_FILE="response.log"
file="scan-current"
compare_file="compare-file"
declare -a FOR_SED=("/Nmap/d" "/Not shown/d" "/SERVICE/d" "s/^+/%2b\ /g" "s/^-/\-\ \ /g" )
nmap $OPTIONS -iL $TARGET_FILE -oA $file > /dev/null
if [ -e $compare_file.xml ]; then
    ndiff $compare_file.xml $file.xml > diff
    for val in "${FOR_SED[@]}"; do
        sed -i "$val" diff
    done
    TEXT=$(cat diff)
    if [[ -n "$TEXT" ]]; then
        resp_code=$(curl -d "text=$TEXT&chat_id=$CHAT_ID" --silent -i -o - -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" | grep HTTP)
        echo "$date - Status code of send to telegram is $resp_code" >> $LOG_FILE
        cp $file.xml "to-approve-$(date +%F-%H).xml"
    fi
else
    echo "$date - FILE WAS CREATED" >> $LOG_FILE
    cp $file.xml $compare_file.xml
fi